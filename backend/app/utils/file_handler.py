import os
import uuid
from pathlib import Path
from typing import Tuple, List, Dict, Any
import pandas as pd
import numpy as np
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

# Import from config
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE, PREVIEW_ROWS


class FileHandler:
    """Handle file uploads and operations"""
    
    @staticmethod
    def generate_file_id() -> str:
        """Generate unique file ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    async def save_uploaded_file(upload_file: UploadFile) -> Tuple[str, Path]:
        """
        Save uploaded file and return file_id and path
        
        Args:
            upload_file: UploadFile from FastAPI
            
        Returns:
            Tuple of (file_id, file_path)
            
        Raises:
            HTTPException: If file validation fails
        """
        # Validate file extension
        file_ext = Path(upload_file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content into memory
        contents = await upload_file.read()
        
        # Validate file size
        if len(contents) > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {MAX_UPLOAD_SIZE / (1024*1024)}MB"
            )
        
        if len(contents) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )
        
        # Generate unique file ID and save
        file_id = FileHandler.generate_file_id()
        file_path = UPLOAD_DIR / f"{file_id}{file_ext}"
        
        try:
            with open(file_path, "wb") as f:
                f.write(contents)
            logger.info(f"File saved: {file_id}{file_ext}")
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to save file"
            )
        
        return file_id, file_path
    
    @staticmethod
    def load_dataframe(file_id: str) -> pd.DataFrame:
        """
        Load dataset from saved file
        
        Args:
            file_id: File identifier
            
        Returns:
            pandas DataFrame
            
        Raises:
            HTTPException: If file not found or can't be loaded
        """
        # Find file with any allowed extension
        file_path = None
        for ext in ALLOWED_EXTENSIONS:
            potential_path = UPLOAD_DIR / f"{file_id}{ext}"
            if potential_path.exists():
                file_path = potential_path
                break
        
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found"
            )
        
        try:
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
            elif file_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Unsupported file format"
                )
            
            if df.empty:
                raise HTTPException(
                    status_code=400,
                    detail="Dataset is empty"
                )
            
            return df
            
        except pd.errors.ParserError as e:
            logger.error(f"Error parsing file: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid file format or corrupted data"
            )
        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to load file"
            )
    
    @staticmethod
    def get_file_info(file_id: str) -> Dict[str, Any]:
        """
        Get basic information about uploaded file
        
        Args:
            file_id: File identifier
            
        Returns:
            Dictionary with file info
        """
        df = FileHandler.load_dataframe(file_id)
        
        return {
            "file_id": file_id,
            "rows": len(df),
            "columns": list(df.columns),
            "shape": df.shape,
        }
    
    @staticmethod
    def get_preview(file_id: str, n_rows: int = PREVIEW_ROWS) -> Dict[str, Any]:
        """
        Get preview of dataset
        
        Args:
            file_id: File identifier
            n_rows: Number of rows to preview
            
        Returns:
            Dictionary with preview data and statistics
        """
        df = FileHandler.load_dataframe(file_id)
        
        # Get preview rows
        preview_df = df.head(n_rows)
        preview_data = preview_df.to_dict(orient="records")
        
        # Calculate basic statistics
        statistics = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
        }
        
        return {
            "file_id": file_id,
            "preview_rows": len(preview_data),
            "columns": list(df.columns),
            "data": preview_data,
            "statistics": statistics,
        }
    
    @staticmethod
    def cleanup_file(file_id: str) -> None:
        """
        Delete uploaded file
        
        Args:
            file_id: File identifier
        """
        for ext in ALLOWED_EXTENSIONS:
            file_path = UPLOAD_DIR / f"{file_id}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Deleted file: {file_id}{ext}")
                except Exception as e:
                    logger.error(f"Error deleting file: {str(e)}")


class DataValidator:
    """Validate dataset for ML tasks"""
    
    @staticmethod
    def validate_for_task(
        df: pd.DataFrame,
        task_type: str,
        target_column: str = None
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate dataset for a specific ML task
        
        Args:
            df: DataFrame to validate
            task_type: Type of ML task (classification, regression, clustering)
            target_column: Target column name (for supervised tasks)
            
        Returns:
            Tuple of (is_valid, issues, target_info)
        """
        issues = []
        target_info = None
        
        # Check minimum rows
        if len(df) < 10:
            issues.append(f"Dataset too small: {len(df)} rows (minimum 10 recommended)")
        
        # Check for all null columns
        all_null_cols = df.columns[df.isnull().all()].tolist()
        if all_null_cols:
            issues.append(f"Columns with all null values: {', '.join(all_null_cols)}")
        
        # Task-specific validation
        if task_type in ["classification", "regression"]:
            if not target_column:
                issues.append(f"Target column required for {task_type}")
            else:
                if target_column not in df.columns:
                    issues.append(f"Target column '{target_column}' not found in dataset")
                else:
                    # Check target column
                    target_col = df[target_column]
                    target_type = target_col.dtype
                    
                    # Check for null values in target
                    null_count = target_col.isnull().sum()
                    if null_count > 0:
                        issues.append(f"Target column has {null_count} null values")
                    
                    # Task-specific target validation
                    if task_type == "classification":
                        unique_values = target_col.nunique()
                        if unique_values < 2:
                            issues.append(f"Classification needs at least 2 classes, found {unique_values}")
                        target_info = {
                            "column": target_column,
                            "type": str(target_type),
                            "unique_classes": unique_values,
                            "class_distribution": target_col.value_counts().to_dict(),
                        }
                    elif task_type == "regression":
                        if not pd.api.types.is_numeric_dtype(target_col):
                            issues.append(f"Regression target must be numeric, got {target_type}")
                        else:
                            target_info = {
                                "column": target_column,
                                "type": str(target_type),
                                "min": float(target_col.min()),
                                "max": float(target_col.max()),
                                "mean": float(target_col.mean()),
                            }
        
        elif task_type == "clustering":
            # Clustering doesn't need target column
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if not numeric_cols:
                issues.append("Clustering requires at least one numeric column")
            target_info = {
                "numeric_columns": numeric_cols,
                "categorical_columns": df.select_dtypes(include=["object"]).columns.tolist(),
            }
        
        is_valid = len(issues) == 0
        
        return is_valid, issues, target_info