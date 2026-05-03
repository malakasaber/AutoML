import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.impute import SimpleImputer
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataPreprocessor:
    
    def __init__(self):
        self.scaler = None
        self.label_encoders = {}
        self.categorical_columns = []
        self.numerical_columns = []
        self.imputer = SimpleImputer(strategy='mean')
        
    def fit_preprocessor(self, X: pd.DataFrame, y: pd.Series = None) -> None:
        # y target is optional
        self.categorical_columns = X.select_dtypes(include=['object']).columns.tolist()
        self.numerical_columns = X.select_dtypes(include=[np.number]).columns.tolist()

        X_temp = X.copy()

        # Fit imputer FIRST
        if self.numerical_columns:
            self.imputer.fit(X_temp[self.numerical_columns])
            X_temp[self.numerical_columns] = self.imputer.transform(X_temp[self.numerical_columns])

            # THEN fit scaler on CLEAN data
            self.scaler = StandardScaler()
            self.scaler.fit(X_temp[self.numerical_columns])

        # Fit label encoders
        for col in self.categorical_columns:
            le = LabelEncoder()
            le.fit(X_temp[col].astype(str))
            self.label_encoders[col] = le
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X_transformed = X.copy()
        
        # Handle missing values
        X_transformed = self._handle_missing_values(X_transformed)
        
        # Encode categorical variables
        X_transformed = self._encode_categorical(X_transformed)
        
        # Scale numerical features
        X_transformed = self._scale_features(X_transformed)
        
        return X_transformed
    
    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        X_processed = X.copy()
        
        # For numerical columns, use mean imputation
        if self.numerical_columns:
            X_processed[self.numerical_columns] = self.imputer.transform(
                X_processed[self.numerical_columns]
            )
        
        # For categorical columns, fill with mode
        for col in self.categorical_columns:
            if X_processed[col].isnull().any():
                mode_val = X_processed[col].mode()
                if len(mode_val) > 0:
                    X_processed[col].fillna(mode_val[0], inplace=True)
                else:
                    # If no mode available, fill with 'unknown'
                    X_processed[col].fillna('unknown', inplace=True)
        
        logger.info(f"Handled missing values. Remaining nulls: {X_processed.isnull().sum().sum()}")
        return X_processed
    
    def _encode_categorical(self, X: pd.DataFrame) -> pd.DataFrame:
        X_encoded = X.copy()
        
        for col in self.categorical_columns:
            if col in self.label_encoders:
                # Handle unseen categories by replacing with most common
                X_encoded[col] = X_encoded[col].astype(str)
                
                known_values = self.label_encoders[col].classes_
                X_encoded[col] = X_encoded[col].apply(
                    lambda x: x if x in known_values else known_values[0]
                )
                X_encoded[col] = self.label_encoders[col].transform(X_encoded[col])
        
        logger.info(f"Encoded {len(self.categorical_columns)} categorical columns")
        return X_encoded
    
    def _scale_features(self, X: pd.DataFrame) -> pd.DataFrame:
        X_scaled = X.copy()
        
        if self.scaler and self.numerical_columns:
            X_scaled[self.numerical_columns] = self.scaler.transform(
                X_scaled[self.numerical_columns]
            )
            logger.info(f"Scaled {len(self.numerical_columns)} numerical columns")
        
        return X_scaled
    
    def fit_transform(self, X: pd.DataFrame, y: pd.Series = None) -> pd.DataFrame:
        if X is None or len(X) == 0:
            raise ValueError("X is empty or None")
        
        self.fit_preprocessor(X, y)
        result = self.transform(X)
        
        if result is None or len(result) == 0:
            raise ValueError("Preprocessing resulted in empty dataframe")
        
        return result


class ImbalanceHandler:
    
    @staticmethod
    def check_imbalance(y: pd.Series, threshold: float = 0.4) -> Tuple[bool, Dict[str, Any]]:
        # Ensure y is a Series and not None
        if y is None:
            return False, {'is_imbalanced': False, 'message': 'Empty target'}
        
        if not isinstance(y, pd.Series):
            y = pd.Series(y)
        
        if len(y) == 0:
            return False, {'is_imbalanced': False, 'message': 'Empty target'}
        
        value_counts = y.value_counts()
        
        if len(value_counts) < 2:
            return False, {
                'is_imbalanced': False,
                'class_distribution': value_counts.to_dict(),
                'message': 'Only one class'
            }
        
        majority_count = value_counts.max()
        minority_count = value_counts.min()
        ratio = minority_count / majority_count
        is_imbalanced = ratio < threshold
        
        info = {
            'is_imbalanced': is_imbalanced,
            'class_distribution': value_counts.to_dict(),
            'minority_class': value_counts.idxmin(),
            'majority_class': value_counts.idxmax(),
            'imbalance_ratio': ratio,
            'minority_count': int(minority_count),
            'majority_count': int(majority_count),
        }
        
        logger.info(f"Class imbalance check: {info}")
        return is_imbalanced, info
    
    @staticmethod
    def handle_imbalance(
        X: pd.DataFrame,
        y: pd.Series,
        method: str = 'smote'
    ) -> Tuple[pd.DataFrame, pd.Series]:
        # class imbalance handled with SMOTE and undersampling
        # Ensure y is a Series
        if not isinstance(y, pd.Series):
            y = pd.Series(y)
        
        is_imbalanced, info = ImbalanceHandler.check_imbalance(y)
        
        if not is_imbalanced:
            logger.info("No significant class imbalance detected. Skipping resampling.")
            return X, y
        
        logger.info(f"Applying {method} to handle class imbalance")
        
        try:
            if method == 'smote':
                # SMOTE for oversampling minority class
                try:
                    smote = SMOTE(random_state=42, k_neighbors=min(5, info['minority_count'] - 1))
                    X_resampled, y_resampled = smote.fit_resample(X, y)
                    # Convert numpy array back to Series
                    y_resampled = pd.Series(y_resampled, name=y.name)
                except ValueError:
                    # If k_neighbors is too large, fall back to undersampling
                    logger.warning("SMOTE failed (too few minority samples). Using undersampling.")
                    return ImbalanceHandler.handle_imbalance(X, y, method='undersample')
            
            elif method == 'undersample':
                # Random undersampling of majority class
                undersampler = RandomUnderSampler(random_state=42)
                X_resampled, y_resampled = undersampler.fit_resample(X, y)
                # Convert numpy array back to Series
                y_resampled = pd.Series(y_resampled, name=y.name)
            
            else:
                raise ValueError(f"Unknown resampling method: {method}")
            
            new_dist = pd.Series(y_resampled).value_counts().to_dict()
            logger.info(f"Resampled data. New distribution: {new_dist}")
            
            return X_resampled, y_resampled
        
        except Exception as e:
            logger.error(f"Error in imbalance handling: {str(e)}. Returning original data.")
            return X, y


class TargetEncoder:
    #for classification
    
    def __init__(self):
        self.label_encoder = LabelEncoder()
        self.classes_ = None
    
    def fit(self, y: pd.Series) -> None:
        self.label_encoder.fit(y)
        self.classes_ = self.label_encoder.classes_
        logger.info(f"Fitted target encoder. Classes: {self.classes_}")
    
    def transform(self, y: pd.Series) -> np.ndarray:
        return self.label_encoder.transform(y)
    
    def inverse_transform(self, y_encoded: np.ndarray) -> np.ndarray:
        return self.label_encoder.inverse_transform(y_encoded)
    
    def fit_transform(self, y: pd.Series) -> np.ndarray:
        self.fit(y)
        return self.transform(y)