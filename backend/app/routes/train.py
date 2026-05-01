import pandas as pd

from fastapi import APIRouter, HTTPException
from app.schemas.schemas import TrainRequest, TrainResponse
from app.utils.file_handler import FileHandler
from app.services.preprocessing import DataPreprocessor, ImbalanceHandler, TargetEncoder
from app.services.training import ModelTrainer
from app.services.evaluation import ModelEvaluator, ReportGenerator
from app.services.model_io import ModelIO
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize model storage
model_io = ModelIO(model_dir=Path("models"))


@router.post(
    "/api/train",
    response_model=TrainResponse,
    tags=["Training"],
    summary="Train ML model end-to-end"
)
async def train_model(request: TrainRequest):
    try:
        print(f"[DEBUG] Starting train_model with task_type={request.task_type}, file_id={request.file_id}, target_column={request.target_column}")
        
        # =========================
        # 1. Load dataset
        # =========================
        print("[DEBUG] Loading dataframe...")
        df = FileHandler.load_dataframe(request.file_id)
        print(f"[DEBUG] Dataframe loaded: shape={df.shape}, columns={df.columns.tolist()}")

        # For clustering, target_column is not required
        if request.task_type != "clustering":
            if not request.target_column or request.target_column not in df.columns:
                raise HTTPException(status_code=400, detail="Invalid target column")

            X = df.drop(columns=[request.target_column])
            y = df[request.target_column]
        else:
            # For clustering, use all columns as features
            X = df
            y = None

        # =========================
        # 2. Preprocessing
        # =========================
        print("[DEBUG] Starting preprocessing...")
        preprocessor = DataPreprocessor()
        X_processed = preprocessor.fit_transform(X)
        print(f"[DEBUG] Preprocessing complete: shape={X_processed.shape}")

        target_encoder = None

        # Encode target for classification
        if request.task_type == "classification" and y is not None:
            print(f"[DEBUG] Encoding target for classification... y type={type(y)}, len={len(y) if hasattr(y, '__len__') else 'N/A'}")
            target_encoder = TargetEncoder()
            encoded_y = target_encoder.fit_transform(y)
            target_col_name = request.target_column if request.target_column else "target"
            y = pd.Series(encoded_y, name=target_col_name)
            print(f"[DEBUG] Target encoded successfully")

        # =========================
        # 3. Handle imbalance (for classification only)
        # =========================
        if request.task_type == "classification" and y is not None:
            print(f"[DEBUG] Handling imbalance... X_processed shape={X_processed.shape}, y len={len(y)}")
            X_processed, y = ImbalanceHandler.handle_imbalance(X_processed, y)
            print(f"[DEBUG] Imbalance handled: X_processed shape={X_processed.shape}, y len={len(y)}")

        # =========================
        # 4. Train models
        # =========================
        print(f"[DEBUG] Starting model training for {request.task_type}...")
        trainer = ModelTrainer()

        if request.task_type == "classification":
            print(f"[DEBUG] Training classification models... X_processed shape={X_processed.shape}, y len={len(y)}")
            best_model, best_name, training_info = trainer.train_classification(
                X_processed, y
            )

        elif request.task_type == "regression":
            print(f"[DEBUG] Training regression models... X_processed shape={X_processed.shape}, y len={len(y)}")
            best_model, best_name, training_info = trainer.train_regression(
                X_processed, y
            )

        elif request.task_type == "clustering":
            print(f"[DEBUG] Training clustering models... X_processed shape={X_processed.shape}")
            best_model, training_info = trainer.train_clustering(X_processed, linkage='ward')
            best_name = training_info['best_model_name']
            print(f"[DEBUG] Clustering complete: best_name={best_name}, n_clusters={training_info['n_clusters']}")

        else:
            raise HTTPException(status_code=400, detail="Invalid task type")
        
        print(f"[DEBUG] Model training complete: best_model={best_name}")

        # =========================
        # 5. Predictions for evaluation
        # =========================
        evaluator = ModelEvaluator()

        X_test = training_info.get("X_test", X_processed)
        y_test = training_info.get("y_test", y) if request.task_type != "clustering" else None

        y_pred = best_model.predict(X_test)

        # =========================
        # 6. Metrics + report
        # =========================
        visualizations = {}

        if request.task_type == "classification":
            metrics = evaluator.evaluate_classification(y_test, y_pred)

            visualizations["confusion_matrix"] = evaluator.generate_confusion_matrix_plot(
                y_test, y_pred
            )

            report = ReportGenerator.generate_classification_report(
                model_name=best_name,
                metrics=metrics,
                cv_score=training_info["best_cv_score"],
                all_cv_scores=training_info["all_scores"],
                visualizations=visualizations
            )

        elif request.task_type == "regression":
            metrics = evaluator.evaluate_regression(y_test, y_pred)

            visualizations["actual_vs_pred"] = evaluator.generate_regression_plot(
                y_test, y_pred
            )

            report = ReportGenerator.generate_regression_report(
                model_name=best_name,
                metrics=metrics,
                cv_score=training_info["best_cv_score"],
                all_cv_scores=training_info["all_scores"],
                visualizations=visualizations
            )

        else:  # clustering
            metrics = evaluator.evaluate_clustering(X_processed, y_pred)

            visualizations["silhouette"] = evaluator.generate_silhouette_plot(
                X_processed, y_pred
            )

            # Updated clustering report with multi-model comparison
            report = ReportGenerator.generate_clustering_report(
                metrics=metrics,
                n_clusters=training_info["n_clusters"],
                best_model_name=training_info["best_model_name"],
                model_comparison=training_info.get("model_comparison"),
                visualizations=visualizations
            )

        # =========================
        # 7. Save model
        # =========================
        model_id, model_path = model_io.save_model(
            model=best_model,
            preprocessor=preprocessor,
            target_encoder=target_encoder,
            metadata={
                "task_type": request.task_type,
                "model_name": best_name,
                "metrics": metrics,
                # For clustering, store additional info
                "n_clusters": training_info.get("n_clusters") if request.task_type == "clustering" else None,
                "all_models": training_info.get("all_models") if request.task_type == "clustering" else None,
            }
        )

        # =========================
        # 8. Return response
        # =========================
        return TrainResponse(
            file_id=request.file_id,
            model_id=model_id,
            model_name=best_name,
            report=report,
            message="Model trained successfully"
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n{'='*80}")
        print(f"TRAINING ERROR: {str(e)}")
        print(f"{'='*80}")
        print(error_details)
        print(f"{'='*80}\n")
        logger.error(f"Training error: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")