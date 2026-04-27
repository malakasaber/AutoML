from fastapi import APIRouter
from app.schemas.schemas import ErrorResponse, DataPreviewResponse
from app.utils.file_handler import FileHandler

router = APIRouter()

@router.get( 
    "/api/preview/{file_id}", 
    response_model=DataPreviewResponse, 
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}, 
    tags=["Data Preview"], 
    summary="Get data preview"
    )
async def get_preview(file_id: str):
    preview_data = FileHandler.get_preview(file_id)
        
    return DataPreviewResponse(
        file_id=preview_data["file_id"],
        preview_rows=preview_data["preview_rows"],
        columns=preview_data["columns"],
        data=preview_data["data"],
        statistics=preview_data["statistics"], #just basic stats like data types, missing values, numeric/categorical columns
    )