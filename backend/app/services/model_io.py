import joblib
import pickle
from pathlib import Path
from typing import Tuple, Dict, Any
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelIO:
    """Handle model serialization and deserialization."""
    
    def __init__(self, model_dir: Path):
        """
        Initialize ModelIO.
        
        Args:
            model_dir: Directory to store models
        """
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
    
    def save_model(
        self,
        model: Any,
        preprocessor: Any,
        target_encoder: Any,
        metadata: Dict[str, Any],
        model_format: str = 'joblib'
    ) -> Tuple[str, str]:
        model_id = str(uuid.uuid4())[:8]
        
        # Determine file extension
        ext = '.joblib' if model_format == 'joblib' else '.pkl'
        model_path = self.model_dir / f"model_{model_id}{ext}"
        
        # Prepare complete model package
        model_package = {
            'model': model,
            'preprocessor': preprocessor,
            'target_encoder': target_encoder,
            'metadata': metadata,
            'created_at': datetime.now().isoformat(),
        }
        
        # Save model
        try:
            if model_format == 'joblib':
                joblib.dump(model_package, model_path)
            else:
                with open(model_path, 'wb') as f:
                    pickle.dump(model_package, f)
            
            logger.info(f"Model saved: {model_path}")
            return model_id, str(model_path)
        
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise
    
    def load_model(self, model_id: str) -> Dict[str, Any]:
        """
        Load saved model with preprocessing pipeline.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dict with model, preprocessor, and metadata
        """
        # Try both formats
        joblib_path = self.model_dir / f"model_{model_id}.joblib"
        pickle_path = self.model_dir / f"model_{model_id}.pkl"
        
        model_path = None
        if joblib_path.exists():
            model_path = joblib_path
        elif pickle_path.exists():
            model_path = pickle_path
        else:
            raise FileNotFoundError(f"Model {model_id} not found")
        
        try:
            if model_path.suffix == '.joblib':
                model_package = joblib.load(model_path)
            else:
                with open(model_path, 'rb') as f:
                    model_package = pickle.load(f)
            
            logger.info(f"Model loaded: {model_path}")
            return model_package
        
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def list_models(self) -> list:
        """
        List all saved models.
        
        Returns:
            List of model file paths
        """
        models = list(self.model_dir.glob("model_*.joblib")) + \
                 list(self.model_dir.glob("model_*.pkl"))
        return [str(m) for m in models]
    
    def delete_model(self, model_id: str) -> bool:
        """
        Delete a saved model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            True if successful, False otherwise
        """
        joblib_path = self.model_dir / f"model_{model_id}.joblib"
        pickle_path = self.model_dir / f"model_{model_id}.pkl"
        
        deleted = False
        
        if joblib_path.exists():
            joblib_path.unlink()
            deleted = True
            logger.info(f"Deleted model: {joblib_path}")
        
        if pickle_path.exists():
            pickle_path.unlink()
            deleted = True
            logger.info(f"Deleted model: {pickle_path}")
        
        return deleted


class PipelineManager:
    """Manage complete ML pipeline (preprocessing + model + evaluation)."""
    
    def __init__(self, model_io: ModelIO):
        """
        Initialize PipelineManager.
        
        Args:
            model_io: ModelIO instance
        """
        self.model_io = model_io
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get information about a saved model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dict with model information
        """
        model_package = self.model_io.load_model(model_id)
        
        metadata = model_package.get('metadata', {})
        created_at = model_package.get('created_at', 'Unknown')
        
        info = {
            'model_id': model_id,
            'task_type': metadata.get('task_type'),
            'model_name': metadata.get('model_name'),
            'created_at': created_at,
            'metrics': metadata.get('metrics', {}),
        }
        
        return info
    
    def make_prediction(
        self,
        model_id: str,
        X: Any
    ) -> Dict[str, Any]:
        """
        Make prediction using saved model.
        
        Args:
            model_id: Model identifier
            X: Feature data
            
        Returns:
            Dict with predictions
        """
        model_package = self.model_io.load_model(model_id)
        model = model_package['model']
        preprocessor = model_package['preprocessor']
        target_encoder = model_package.get('target_encoder')
        metadata = model_package['metadata']
        
        # Preprocess data
        X_processed = preprocessor.transform(X)
        
        # Make prediction
        task_type = metadata.get('task_type')
        
        if task_type == 'clustering':
            predictions = model.predict(X_processed)
        else:
            predictions = model.predict(X_processed)
            
            # For classification, decode labels
            if task_type == 'classification' and target_encoder:
                predictions = target_encoder.inverse_transform(predictions)
        
        result = {
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else predictions,
            'task_type': task_type,
            'model_id': model_id,
            'model_name': metadata.get('model_name'),
        }
        
        # Add probabilities for classification
        if task_type == 'classification' and hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(X_processed)
            result['probabilities'] = probabilities.tolist()
        
        return result