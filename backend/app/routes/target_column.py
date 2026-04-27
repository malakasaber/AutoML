from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ErrorResponse, TargetColumnRequest, TargetColumnResponse
from app.utils.file_handler import FileHandler
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post(
    "/api/target-columns",
    response_model=TargetColumnResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Data Validation"],
    summary="Get suggested target columns"
)
async def get_target_columns(request: TargetColumnRequest):
    try:
        df = FileHandler.load_dataframe(request.file_id)
        
        # Find potential target columns
        suggestions = []
        
        # Numeric columns (good for regression)
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        for col in numeric_cols:
            suggestions.append({
                "column": col,
                "type": "numeric (suitable for regression)",
                "unique_values": int(df[col].nunique())
            })
        
        # Categorical columns with limited unique values (good for classification)
        categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 10:  # Reasonable class count
                suggestions.append({
                    "column": col,
                    "type": f"categorical ({unique_count} classes)",
                    "unique_values": unique_count
                })
        
        if not suggestions:
            raise HTTPException(
                status_code=400,
                detail="No suitable target columns found in dataset"
            )
        
        return TargetColumnResponse(
            file_id=request.file_id,
            suggestions=suggestions,
            message=f"Found {len(suggestions)} potential target columns"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting target columns: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving target columns")
