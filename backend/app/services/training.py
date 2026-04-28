import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error
from typing import Tuple, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Train and select best model for ML tasks."""
    
    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state
        self.best_model = None
        self.best_model_name = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
    
    def split_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        stratify: bool = False
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """
        Split data into training and testing sets.
        
        Args:
            X: Feature dataframe
            y: Target series
            stratify: Whether to stratify the split by y.
            
        Returns:
            Tuple of (X_train, X_test, y_train, y_test)
        """
        # Ensure y is a Series
        if isinstance(y, np.ndarray):
            y = pd.Series(y)
        
        stratify_target = None
        if stratify and isinstance(y, pd.Series) and len(y.unique()) > 1:
            stratify_target = y
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=stratify_target
        )
        
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        logger.info(f"Data split: {len(X_train)} train, {len(X_test)} test")
        return X_train, X_test, y_train, y_test
    
    def train_classification_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> Dict[str, Any]:
        """
        Train multiple classification algorithms.
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            Dict with trained models and cross-validation scores
        """
        models = {
            'Logistic Regression': LogisticRegression(max_iter=1000, random_state=self.random_state),
            'Random Forest': RandomForestClassifier(n_estimators=100, random_state=self.random_state, n_jobs=-1),
            'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=self.random_state),
            'SVM': SVC(kernel='rbf', random_state=self.random_state),
        }
        
        trained_models = {}
        cv_scores = {}
        
        for name, model in models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                trained_models[name] = model
                
                # Get cross-validation score
                cv_score = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy').mean()
                cv_scores[name] = cv_score
                
                logger.info(f"{name} - CV Accuracy: {cv_score:.4f}")
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
        
        return trained_models, cv_scores
    
    def train_regression_models(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series
    ) -> Dict[str, Any]:
        """
        Train multiple regression algorithms.
        
        Args:
            X_train: Training features
            y_train: Training target
            
        Returns:
            Dict with trained models and cross-validation scores
        """
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=self.random_state, n_jobs=-1),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=self.random_state),
            'SVR': SVR(kernel='rbf'),
        }
        
        trained_models = {}
        cv_scores = {}
        
        for name, model in models.items():
            try:
                # Train model
                model.fit(X_train, y_train)
                trained_models[name] = model
                
                # Get cross-validation score (R² score)
                cv_score = cross_val_score(model, X_train, y_train, cv=5, scoring='r2').mean()
                cv_scores[name] = cv_score
                
                logger.info(f"{name} - CV R² Score: {cv_score:.4f}")
            except Exception as e:
                logger.error(f"Error training {name}: {str(e)}")
        
        return trained_models, cv_scores
    
    def train_clustering_models(
        self,
        X: pd.DataFrame,
        n_clusters: int = None
    ) -> Dict[str, Any]:
        """
        Train clustering model.
        
        Args:
            X: Feature dataframe
            n_clusters: Number of clusters (auto-detect if None)
            
        Returns:
            Dict with trained model
        """
        # Auto-detect optimal number of clusters using elbow method
        if n_clusters is None:
            n_clusters = self._optimal_clusters(X)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=self.random_state, n_init=10)
        kmeans.fit(X)
        
        logger.info(f"KMeans clustering with {n_clusters} clusters trained")
        
        return {
            'KMeans': kmeans,
            'n_clusters': n_clusters,
        }
    
    def _optimal_clusters(self, X: pd.DataFrame, max_k: int = 10) -> int:
        """
        Find optimal number of clusters using elbow method.
        
        Args:
            X: Feature dataframe
            max_k: Maximum number of clusters to test
            
        Returns:
            Optimal number of clusters
        """
        inertias = []
        silhouette_scores = []
        
        from sklearn.metrics import silhouette_score
        
        K_range = range(2, min(max_k, len(X)))
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=self.random_state, n_init=10)
            kmeans.fit(X)
            inertias.append(kmeans.inertia_)
            silhouette_scores.append(silhouette_score(X, kmeans.labels_))
        
        # Use silhouette score to find optimal k
        optimal_k = list(K_range)[np.argmax(silhouette_scores)]
        logger.info(f"Optimal clusters detected: {optimal_k}")
        
        return optimal_k
    
    def select_best_model(
        self,
        trained_models: Dict,
        cv_scores: Dict
    ) -> Tuple[Any, str, float]:
        """
        Select best model based on cross-validation scores.
        
        Args:
            trained_models: Dict of trained models
            cv_scores: Dict of CV scores
            
        Returns:
            Tuple of (best_model, best_model_name, best_score)
        """
        if not cv_scores or len(cv_scores) == 0:
            raise ValueError("No trained models available - cv_scores is empty")
        
        if not trained_models or len(trained_models) == 0:
            raise ValueError("No trained models available - trained_models is empty")
        
        best_name = max(cv_scores, key=cv_scores.get)
        best_score = cv_scores[best_name]
        best_model = trained_models[best_name]
        
        self.best_model = best_model
        self.best_model_name = best_name
        
        logger.info(f"Selected best model: {best_name} with score {best_score:.4f}")
        
        return best_model, best_name, best_score
    
    def train_classification(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[Any, str, Dict[str, Any]]:
        """
        Complete classification training pipeline.
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Tuple of (best_model, best_model_name, training_info)
        """
        # Validate inputs
        if X is None or len(X) == 0:
            raise ValueError("X is empty or None")
        if y is None or len(y) == 0:
            raise ValueError("y is empty or None")
        if len(X) != len(y):
            raise ValueError(f"X and y have different lengths: {len(X)} vs {len(y)}")
        
        # Split data with stratification for classification
        X_train, X_test, y_train, y_test = self.split_data(X, y, stratify=True)
        
        # Train models
        trained_models, cv_scores = self.train_classification_models(X_train, y_train)
        
        # Select best
        best_model, best_name, best_score = self.select_best_model(trained_models, cv_scores)
        
        training_info = {
            'best_model': best_model,
            'best_model_name': best_name,
            'best_cv_score': best_score,
            'all_models': trained_models,
            'all_scores': cv_scores,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
        }
        
        return best_model, best_name, training_info
    
    def train_regression(
        self,
        X: pd.DataFrame,
        y: pd.Series
    ) -> Tuple[Any, str, Dict[str, Any]]:
        """
        Complete regression training pipeline.
        
        Args:
            X: Features
            y: Target
            
        Returns:
            Tuple of (best_model, best_model_name, training_info)
        """
        # Validate inputs
        if X is None or len(X) == 0:
            raise ValueError("X is empty or None")
        if y is None or len(y) == 0:
            raise ValueError("y is empty or None")
        if len(X) != len(y):
            raise ValueError(f"X and y have different lengths: {len(X)} vs {len(y)}")
        
        # Split data
        X_train, X_test, y_train, y_test = self.split_data(X, y, stratify=False)
        
        # Train models
        trained_models, cv_scores = self.train_regression_models(X_train, y_train)
        
        # Select best
        best_model, best_name, best_score = self.select_best_model(trained_models, cv_scores)
        
        training_info = {
            'best_model': best_model,
            'best_model_name': best_name,
            'best_cv_score': best_score,
            'all_models': trained_models,
            'all_scores': cv_scores,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
        }
        
        return best_model, best_name, training_info
    
    def train_clustering(
        self,
        X: pd.DataFrame,
        n_clusters: int = None
    ) -> Tuple[Any, Dict[str, Any]]:
        """
        Complete clustering training pipeline.
        
        Args:
            X: Features
            n_clusters: Number of clusters (auto-detect if None)
            
        Returns:
            Tuple of (best_model, training_info)
        """
        # Validate inputs
        if X is None or len(X) == 0:
            raise ValueError("X is empty or None")
        
        clustering_info = self.train_clustering_models(X, n_clusters)
        best_model = clustering_info['KMeans']
        
        training_info = {
            'best_model': best_model,
            'best_model_name': 'KMeans',
            'n_clusters': clustering_info['n_clusters'],
            'X': X,
            'labels': best_model.labels_,
        }
        
        return best_model, training_info