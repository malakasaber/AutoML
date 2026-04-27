from fastapi import APIRouter
from app.services.model_io import ModelIO
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

model_io = ModelIO(model_dir=Path("models"))


@router.get(
    "/api/models",
    tags=["Model"],
    summary="List all saved models"
)
async def list_models():
    try:
        model_files = model_io.list_models()

        models = []

        for file_path in model_files:
            file_path = Path(file_path)

            # Extract model_id from filename: model_<id>.joblib
            filename = file_path.stem
            model_id = filename.replace("model_", "")

            try:
                # Load metadata (lightweight load)
                model_package = model_io.load_model(model_id)
                metadata = model_package.get("metadata", {})

                models.append({
                    "model_id": model_id,
                    "file_name": file_path.name,
                    "task_type": metadata.get("task_type"),
                    "model_name": metadata.get("model_name"),
                    "created_at": model_package.get("created_at")
                })

            except Exception as e:
                logger.warning(f"Skipping corrupted model {file_path}: {str(e)}")

        return {
            "total_models": len(models),
            "models": models
        }

    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        return {
            "total_models": 0,
            "models": []
        }