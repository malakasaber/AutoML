from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from config import CORS_ORIGINS
from schemas import (
    FileUploadResponse,
    DataPreviewResponse,
    DataValidationRequest,
    DataValidationResponse,
    TargetColumnRequest,
    TargetColumnResponse,
    TrainingRequest,
    TrainingResponse,
    ErrorResponse,
)
from file_handler import FileHandler, DataValidator

# Initialize FastAPI app
app = FastAPI(
    title="ML Auto-Pipeline API",
    description="Automated ML pipeline for classification, regression, and clustering",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== FILE UPLOAD & PREVIEW ROUTES ====================

@app.post(
    "/api/upload",
    response_model=FileUploadResponse,
    responses={400: {"model": ErrorResponse}, 413: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["File Upload"],
    summary="Upload dataset file"
)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file for ML analysis.
    
    Supported formats:
    - .csv
    - .xlsx
    - .xls
    
    Max file size: 50MB
    """
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Unexpected error during upload")


@app.get(
    "/api/preview/{file_id}",
    response_model=DataPreviewResponse,
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
    tags=["Data Preview"],
    summary="Get data preview"
)
async def get_preview(file_id: str):
    """
    Get a preview of the uploaded dataset.
    
    Returns:
    - First N rows of data
    - Column names
    - Basic statistics (data types, missing values, numeric/categorical columns)
    """
    try:
        preview_data = FileHandler.get_preview(file_id)
        
        return DataPreviewResponse(
            file_id=preview_data["file_id"],
            preview_rows=preview_data["preview_rows"],
            columns=preview_data["columns"],
            data=preview_data["data"],
            statistics=preview_data["statistics"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting preview: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving preview")


# ==================== DATA VALIDATION ROUTES ====================

@app.post(
    "/api/validate",
    response_model=DataValidationResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Data Validation"],
    summary="Validate dataset for ML task"
)
async def validate_data(request: DataValidationRequest):
    """
    Validate if the dataset is compatible with the selected ML task.
    
    For classification/regression: requires a target column.
    For clustering: works with numeric features only.
    
    Returns validation status and any issues found.
    """
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        raise HTTPException(status_code=500, detail="Error validating dataset")


@app.post(
    "/api/target-columns",
    response_model=TargetColumnResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    tags=["Data Validation"],
    summary="Get suggested target columns"
)
async def get_target_columns(request: TargetColumnRequest):
    """
    Get a list of columns suitable as target variables.
    
    Suggestions are based on data types:
    - For classification: columns with few unique values
    - For regression: numeric columns
    """
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


# ==================== HEALTH CHECK ====================

@app.get(
    "/api/health",
    tags=["Health"],
    summary="Health check"
)
async def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "message": "ML Auto-Pipeline API is running"
    }


# ==================== ERROR HANDLERS ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)