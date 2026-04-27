from fastapi import APIRouter, HTTPException
from app.schemas.schemas import PredictRequest, PredictResponse
from app.services.model_io import ModelIO, PipelineManager
from pathlib import Path
import pandas as pd
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

model_io = ModelIO(model_dir=Path("models"))
pipeline_manager = PipelineManager(model_io)


@router.post(
    "/api/predict",
    response_model=PredictResponse,
    tags=["Prediction"],
    summary="Make predictions using trained model"
)
async def predict(request: PredictRequest):
    try:
        # =========================
        # 1. Load model package
        # =========================
        model_package = model_io.load_model(request.model_id)

        model = model_package["model"]
        preprocessor = model_package["preprocessor"]
        metadata = model_package["metadata"]
        target_encoder = model_package.get("target_encoder")

        # =========================
        # 2. Convert input to DataFrame
        # =========================
        X = pd.DataFrame(request.data)

        # =========================
        # 3. Preprocess input
        # =========================
        X_processed = preprocessor.transform(X)

        # =========================
        # 4. Predict
        # =========================
        predictions = model.predict(X_processed)

        task_type = metadata.get("task_type")

        # Decode labels for classification
        if task_type == "classification" and target_encoder:
            predictions = target_encoder.inverse_transform(predictions)

        # =========================
        # 5. Probabilities (classification only)
        # =========================
        probabilities = None
        if task_type == "classification" and hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X_processed).tolist()

        # =========================
        # 6. Response
        # =========================
        return PredictResponse(
            model_id=request.model_id,
            task_type=task_type,
            predictions=predictions.tolist() if hasattr(predictions, "tolist") else predictions,
            probabilities=probabilities,
            message="Prediction successful"
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Model not found")

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")