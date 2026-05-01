import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score,
    silhouette_score, silhouette_samples
)
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance and generate metrics."""
    
    @staticmethod
    def evaluate_classification(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None
    ) -> Dict[str, Any]:
        """
        Evaluate classification model.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities (optional)
            
        Returns:
            Dict with metrics
        """
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_true, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_true, y_pred, average='weighted', zero_division=0),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist(),
            'classification_report': classification_report(y_true, y_pred, output_dict=True, zero_division=0),
        }
        
        logger.info(f"Classification metrics calculated - Accuracy: {metrics['accuracy']:.4f}")
        
        return metrics
    
    @staticmethod
    def evaluate_regression(
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate regression model.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dict with metrics
        """
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        metrics = {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2_score': r2,
        }
        
        logger.info(f"Regression metrics - R²: {r2:.4f}, RMSE: {rmse:.4f}")
        
        return metrics
    
    @staticmethod
    def evaluate_clustering(
        X: np.ndarray,
        labels: np.ndarray
    ) -> Dict[str, Any]:
        """
        Evaluate clustering model.
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            
        Returns:
            Dict with metrics
        """
        # Calculate silhouette score
        silhouette_avg = silhouette_score(X, labels)
        
        # Calculate silhouette for each sample
        sample_silhouette_values = silhouette_samples(X, labels)
        
        metrics = {
            'silhouette_score': silhouette_avg,
            'silhouette_samples': sample_silhouette_values.tolist(),
            'n_clusters': len(np.unique(labels)),
        }
        
        logger.info(f"Clustering metrics - Silhouette Score: {silhouette_avg:.4f}")
        
        return metrics
    
    @staticmethod
    def generate_confusion_matrix_plot(
        y_true: np.ndarray,
        y_pred: np.ndarray,
        class_names: list = None
    ) -> str:
        """
        Generate confusion matrix plot.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            class_names: Names of classes
            
        Returns:
            Base64 encoded plot image
        """
        cm = confusion_matrix(y_true, y_pred)
        
        # Generate class names if not provided
        if class_names is None:
            class_names = [str(i) for i in range(cm.shape[0])]
        
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                    xticklabels=class_names, yticklabels=class_names)
        ax.set_xlabel('Predicted')
        ax.set_ylabel('Actual')
        ax.set_title('Confusion Matrix')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_feature_importance_plot(
        model: Any,
        feature_names: list,
        top_n: int = 10
    ) -> str:
        """
        Generate feature importance plot.
        
        Args:
            model: Trained model with feature_importances_
            feature_names: Names of features
            top_n: Number of top features to show
            
        Returns:
            Base64 encoded plot image
        """
        if not hasattr(model, 'feature_importances_'):
            logger.warning("Model does not have feature_importances_ attribute")
            return None
        
        importances = model.feature_importances_
        indices = np.argsort(importances)[-top_n:][::-1]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(range(len(indices)), importances[indices])
        ax.set_xticks(range(len(indices)))
        ax.set_xticklabels([feature_names[i] for i in indices], rotation=45, ha='right')
        ax.set_ylabel('Importance')
        ax.set_title(f'Top {top_n} Feature Importance')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_regression_plot(
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> str:
        """
        Generate actual vs predicted plot for regression.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Base64 encoded plot image
        """
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Scatter plot
        ax.scatter(y_true, y_pred, alpha=0.5, edgecolors='k')
        
        # Perfect prediction line
        min_val = min(y_true.min(), y_pred.min())
        max_val = max(y_true.max(), y_pred.max())
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2)
        
        ax.set_xlabel('Actual Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title('Actual vs Predicted Values')
        ax.grid(True, alpha=0.3)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    @staticmethod
    def generate_silhouette_plot(
        X: np.ndarray,
        labels: np.ndarray
    ) -> str:
        """
        Generate silhouette plot for clustering.
        
        Args:
            X: Feature matrix
            labels: Cluster labels
            
        Returns:
            Base64 encoded plot image
        """
        silhouette_avg = silhouette_score(X, labels)
        sample_silhouette_values = silhouette_samples(X, labels)
        
        n_clusters = len(np.unique(labels))
        fig, ax = plt.subplots(figsize=(8, 6))
        
        y_lower = 10
        for i in range(n_clusters):
            cluster_silhouette_values = sample_silhouette_values[labels == i]
            cluster_silhouette_values.sort()
            
            size_cluster_i = cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i
            
            ax.fill_betweenx(np.arange(y_lower, y_upper),
                            0, cluster_silhouette_values,
                            alpha=0.7, label=f'Cluster {i}')
            y_lower = y_upper + 10
        
        ax.set_xlabel('Silhouette Coefficient')
        ax.set_ylabel('Cluster Label')
        ax.axvline(x=silhouette_avg, color='red', linestyle='--',
                   label=f'Average: {silhouette_avg:.3f}')
        ax.set_title('Silhouette Plot for Clusters')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64


class ReportGenerator:
    """Generate comprehensive model reports."""
    
    @staticmethod
    def generate_classification_report(
        model_name: str,
        metrics: Dict[str, Any],
        cv_score: float,
        all_cv_scores: Dict[str, float],
        visualizations: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Generate classification report.
        
        Args:
            model_name: Name of best model
            metrics: Evaluation metrics
            cv_score: Best CV score
            all_cv_scores: All models' CV scores
            visualizations: Dict of visualizations
            
        Returns:
            Complete report dict
        """
        report = {
            'task_type': 'classification',
            'best_model': model_name,
            'cross_validation_score': cv_score,
            'all_models_cv_scores': all_cv_scores,
            'metrics': {
                'accuracy': metrics['accuracy'],
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
            },
            'confusion_matrix': metrics['confusion_matrix'],
            'classification_report': metrics['classification_report'],
            'visualizations': visualizations or {},
        }
        
        return report
    
    @staticmethod
    def generate_regression_report(
        model_name: str,
        metrics: Dict[str, Any],
        cv_score: float,
        all_cv_scores: Dict[str, float],
        visualizations: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Generate regression report.
        
        Args:
            model_name: Name of best model
            metrics: Evaluation metrics
            cv_score: Best CV score
            all_cv_scores: All models' CV scores
            visualizations: Dict of visualizations
            
        Returns:
            Complete report dict
        """
        report = {
            'task_type': 'regression',
            'best_model': model_name,
            'cross_validation_score': cv_score,
            'all_models_cv_scores': all_cv_scores,
            'metrics': {
                'mae': metrics['mae'],
                'mse': metrics['mse'],
                'rmse': metrics['rmse'],
                'r2_score': metrics['r2_score'],
            },
            'visualizations': visualizations or {},
        }
        
        return report
    
    @staticmethod
    def generate_clustering_report(
        metrics: Dict[str, Any],
        n_clusters: int,
        best_model_name: str = None,
        model_comparison: Dict[str, Any] = None,
        visualizations: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive clustering report with multi-model comparison.
        
        Args:
            metrics: Evaluation metrics (from training_info)
            n_clusters: Number of clusters
            best_model_name: Name of the best performing model
            model_comparison: Dict with silhouette scores for each model
            visualizations: Dict of visualizations
            
        Returns:
            Complete report dict with metrics and comparisons
        """
        # Build metrics section
        metrics_section = {
            'silhouette_score': metrics.get('silhouette_score', None),
        }
        
        # Add model-specific metrics if available
        if 'inertia' in metrics:
            metrics_section['inertia'] = metrics['inertia']
        
        if 'linkage' in metrics:
            metrics_section['linkage'] = metrics['linkage']
        
        # Build model comparison section
        comparison_section = {}
        if model_comparison:
            comparison_section = model_comparison
            logger.info(f"Model Comparison:\n"
                    f"  {comparison_section}")
        
        report = {
            'task_type': 'clustering',
            'n_clusters': n_clusters,
            'best_model': best_model_name,
            'metrics': metrics_section,
            'model_comparison': comparison_section,
            'visualizations': visualizations or {},
            'summary': {
                'total_models': len(comparison_section) if comparison_section else 1,
                'best_performer': best_model_name,
            }
        }
        
        logger.info(f"Clustering report generated:\n"
                f"  Best Model: {best_model_name}\n"
                f"  Clusters: {n_clusters}\n"
                f"  Silhouette Score: {metrics_section.get('silhouette_score', 'N/A'):.4f}")
        
        return report