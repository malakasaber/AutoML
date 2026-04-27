from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class MLTaskType(str, Enum):
    """Machine Learning task types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"

class BaseSchema(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: str = Field(..., description="Unique file identifier")
    filename: str = Field(..., description="Original filename")
    rows: int = Field(..., description="Number of rows in dataset")
    columns: List[str] = Field(..., description="Column names")
    shape: tuple = Field(..., description="Dataset shape (rows, columns)")
    message: str = Field(..., description="Success message")


class DataPreviewResponse(BaseModel):
    """Response for data preview"""
    file_id: str = Field(..., description="File identifier")
    preview_rows: int = Field(..., description="Number of rows in preview")
    columns: List[str] = Field(..., description="Column names")
    data: List[Dict[str, Any]] = Field(..., description="Preview data")
    statistics: Dict[str, Any] = Field(..., description="Basic statistics")


class DataValidationRequest(BaseModel):
    """Request to validate dataset with ML task"""
    file_id: str = Field(..., description="File identifier")
    task_type: MLTaskType = Field(..., description="Type of ML task")
    target_column: Optional[str] = Field(None, description="Target column (for supervised tasks)")


class DataValidationResponse(BaseModel):
    """Response for data validation"""
    is_valid: bool = Field(..., description="Whether dataset is valid")
    message: str = Field(..., description="Validation message")
    issues: List[str] = Field(default_factory=list, description="Any validation issues found")
    target_info: Optional[Dict[str, Any]] = Field(None, description="Info about target column")


class TargetColumnRequest(BaseModel):
    """Request to get available target columns"""
    file_id: str = Field(..., description="File identifier")

class TargetColumnSuggestion(BaseModel):
    column: str
    type: str
    unique_values: int

class TargetColumnResponse(BaseModel):
    file_id: str
    suggestions: List[TargetColumnSuggestion]
    message: str

class TrainRequest(BaseSchema):
    file_id: str
    task_type: MLTaskType
    target_column: Optional[str] = None


class TrainResponse(BaseSchema):
    file_id: str
    model_id: str
    model_name: str
    report: Dict[str, Any]
    message: str

'''
class TrainingRequest(BaseModel):
    """Request to start model training"""
    file_id: str = Field(..., description="File identifier")
    task_type: MLTaskType = Field(..., description="Type of ML task")
    target_column: Optional[str] = Field(None, description="Target column for supervised learning")


class TrainingResponse(BaseModel):
    """Response from training"""
    model_id: str = Field(..., description="Trained model identifier")
    task_type: MLTaskType = Field(..., description="ML task type")
    metrics: Dict[str, Any] = Field(..., description="Performance metrics")
    message: str = Field(..., description="Success message")
'''

class ModelDownloadRequest(BaseModel):
    """Request to download trained model"""
    model_id: str = Field(..., description="Model identifier")

class PredictRequest(BaseSchema):
    model_id: str
    data: List[Dict[str, Any]]

class PredictResponse(BaseSchema):
    model_id: str
    task_type: str
    predictions: List[Any]
    probabilities: Optional[List[List[float]]] = None
    message: str

class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")