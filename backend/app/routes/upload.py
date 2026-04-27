from fastapi import APIRouter, UploadFile, File
from app.schemas.schemas import FileUploadResponse, ErrorResponse
from app.utils.file_handler import FileHandler

router = APIRouter()

@router.post(
    "/api/upload",
    response_model=FileUploadResponse, 
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}, 
    tags=["File Upload"], 
    summary="Upload dataset file"
    )
async def upload_file(file: UploadFile = File(...)):
    #supports formats: .csv, .xlsx, .xls
    #max file size: 50MB
    file_id, file_path = await FileHandler.save_uploaded_file(file)
    file_info = FileHandler.get_file_info(file_id)

    return FileUploadResponse(
        file_id=file_id,
        filename=file.filename,
        rows=file_info["rows"],
        columns=file_info["columns"],
        shape=file_info["shape"],
        message=f"File uploaded successfully. Shape: {file_info['shape']}"
    )