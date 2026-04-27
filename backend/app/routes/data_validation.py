from fastapi import APIRouter, HTTPException
from app.schemas.schemas import ErrorResponse, DataValidationRequest, DataValidationResponse
from app.utils.file_handler import FileHandler, DataValidator

router = APIRouter()

@router.post(
    "/api/validate",
    response_model=DataValidationResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Data Validation"],
    summary="Validate dataset for ML task"
)
async def validate_data(request: DataValidationRequest):
    df = FileHandler.load_dataframe(request.file_id)
    is_valid, issues, target_info = DataValidator.validate_for_task(
        df,
        request.task_type,
        request.target_column
    )
    
    message = "Dataset is valid for this task" if is_valid else "Dataset has validation issues"
    
    return DataValidationResponse(
        is_valid=is_valid,
        message=message,
        issues=issues,
        target_info=target_info,
    )
    

"""
    Validate if the dataset is compatible with the selected ML task.
    
    For classification/regression: requires a target column.
    For clustering: works with numeric features only.
    
    Returns validation status and any issues found.
    """