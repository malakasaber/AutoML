from fastapi import APIRouter, HTTPException
from app.services.model_io import ModelIO
from pathlib import Path

router = APIRouter()

model_io = ModelIO(model_dir=Path("models"))


@router.delete(
    "/api/model/{model_id}",
    summary="Delete a saved model",
    tags=["Model Management"]
)
async def delete_model(model_id: str):
    try:
        deleted = model_io.delete_model(model_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Model with id '{model_id}' not found"
            )

        return {
            "model_id": model_id,
            "message": "Model deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting model: {str(e)}"
        )