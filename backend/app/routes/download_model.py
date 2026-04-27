from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.services.model_io import ModelIO
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

model_io = ModelIO(model_dir=Path("models"))

#force format by this > /api/model/{model_id}/download?format=joblib
@router.get(
    "/api/model/{model_id}/download",
    tags=["Model"],
    summary="Download trained model (.joblib or .pkl)"
)
async def download_model(model_id: str):
    try:
        model_package = model_io.load_model(model_id)

        # Find actual file path
        joblib_path = model_io.model_dir / f"model_{model_id}.joblib"
        pickle_path = model_io.model_dir / f"model_{model_id}.pkl"

        if joblib_path.exists():
            file_path = joblib_path
            filename = f"model_{model_id}.joblib"

        elif pickle_path.exists():
            file_path = pickle_path
            filename = f"model_{model_id}.pkl"

        else:
            raise HTTPException(status_code=404, detail="Model not found")

        logger.info(f"Downloading model: {file_path}")

        return FileResponse(
            path=str(file_path),
            media_type="application/octet-stream",
            filename=filename
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download model")