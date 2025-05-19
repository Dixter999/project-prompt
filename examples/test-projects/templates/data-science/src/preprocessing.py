"""
Data preprocessing utilities for the data science project.
Contains functions for cleaning, transforming, and preparing data for analysis.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler, OneHotEncoder
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.pipeline import Pipeline
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """
    A class for preprocessing data with common data cleaning and transformation operations.
    
    Features:
    - Missing value imputation
    - Outlier detection and handling
    - Feature scaling
    - Categorical encoding
    - Feature transformation
    """
    
    def __init__(self, config=None):
        """
        Initialize the preprocessor with configuration options.
        
        Args:
            config (dict, optional): Configuration parameters for preprocessing steps.
        """
        self.config = config or {}
        self.numeric_features = []
        self.categorical_features = []
        self.preprocessor = None
        self.fitted = False
        
        # Set default configuration if not provided
        if not self.config:
            self.config = {
                'impute_strategy': 'mean',
                'scaling': 'standard',
                'categorical_encoding': 'onehot',
                'handle_outliers': True,
                'outlier_threshold': 3.0
            }
    
    def fit(self, data):
        """
        Fit the preprocessor on the training data.
        
        Args:
            data (pd.DataFrame): The input data to fit on
            
        Returns:
            self: The fitted preprocessor instance
        """
        logger.info("Fitting data preprocessor")
        
        # Identify feature types
        self._identify_feature_types(data)
        
        # Create preprocessing pipeline
        self._create_pipeline()
        
        # Fit the pipeline
        if self.preprocessor and len(data) > 0:
            self.preprocessor.fit(data)
            self.fitted = True
            logger.info("Preprocessor fitted successfully")
        else:
            logger.warning("No data available for fitting preprocessor")
            
        return self
    
    def transform(self, data):
        """
        Transform the input data using the fitted preprocessor.
        
        Args:
            data (pd.DataFrame): The input data to transform
            
        Returns:
            pd.DataFrame: The transformed data
        """
        if not self.fitted:
            logger.error("Preprocessor has not been fitted yet")
            raise ValueError("You must fit the preprocessor before transforming data")
        
        logger.info("Transforming data")
        transformed_data = self.preprocessor.transform(data)
        
        # If the output is not a DataFrame, convert it back
        if not isinstance(transformed_data, pd.DataFrame):
            # Get feature names from the pipeline if available
            try:
                feature_names = self.preprocessor.get_feature_names_out()
            except:
                feature_names = [f'feature_{i}' for i in range(transformed_data.shape[1])]
                
            transformed_data = pd.DataFrame(
                transformed_data,
                index=data.index,
                columns=feature_names
            )
        
        logger.info(f"Data transformation complete. Shape: {transformed_data.shape}")
        return transformed_data
    
    def fit_transform(self, data):
        """
        Fit the preprocessor and transform the input data in one step.
        
        Args:
            data (pd.DataFrame): The input data to fit and transform
            
        Returns:
            pd.DataFrame: The transformed data
        """
        return self.fit(data).transform(data)
    
    def _identify_feature_types(self, data):
        """
        Identify numeric and categorical features from the data.
        
        Args:
            data (pd.DataFrame): The input data
        """
        self.numeric_features = data.select_dtypes(include=['number']).columns.tolist()
        self.categorical_features = data.select_dtypes(include=['object', 'category']).columns.tolist()
        
        logger.info(f"Identified {len(self.numeric_features)} numeric features and {len(self.categorical_features)} categorical features")
    
    def _create_pipeline(self):
        """
        Create a preprocessing pipeline based on the configuration.
        """
        # Numeric feature preprocessing steps
        numeric_steps = []
        
        # Imputation for missing values
        if self.config['impute_strategy'] == 'mean':
            numeric_steps.append(('imputer', SimpleImputer(strategy='mean')))
        elif self.config['impute_strategy'] == 'median':
            numeric_steps.append(('imputer', SimpleImputer(strategy='median')))
        elif self.config['impute_strategy'] == 'knn':
            numeric_steps.append(('imputer', KNNImputer(n_neighbors=5)))
            
        # Scaling
        if self.config['scaling'] == 'standard':
            numeric_steps.append(('scaler', StandardScaler()))
        elif self.config['scaling'] == 'minmax':
            numeric_steps.append(('scaler', MinMaxScaler()))
            
        # Categorical feature preprocessing
        categorical_steps = []
        
        # Imputation for missing values in categorical features
        categorical_steps.append(('imputer', SimpleImputer(strategy='most_frequent')))
        
        # Encoding
        if self.config['categorical_encoding'] == 'onehot':
            categorical_steps.append(('encoder', OneHotEncoder(sparse=False, handle_unknown='ignore')))
            
        # Create separate pipelines for numeric and categorical features
        numeric_pipeline = Pipeline(steps=numeric_steps)
        categorical_pipeline = Pipeline(steps=categorical_steps)
        
        # Combine pipelines into a preprocessor
        from sklearn.compose import ColumnTransformer
        
        preprocessor_steps = []
        
        if self.numeric_features:
            preprocessor_steps.append(('numeric', numeric_pipeline, self.numeric_features))
            
        if self.categorical_features:
            preprocessor_steps.append(('categorical', categorical_pipeline, self.categorical_features))
        
        if preprocessor_steps:
            self.preprocessor = ColumnTransformer(
                transformers=preprocessor_steps,
                remainder='passthrough'
            )
        
    def handle_outliers(self, data, method='clip', threshold=None):
        """
        Detect and handle outliers in the data.
        
        Args:
            data (pd.DataFrame): The input data
            method (str): Method to handle outliers ('clip', 'remove', or 'transform')
            threshold (float, optional): Standard deviation threshold for outlier detection
            
        Returns:
            pd.DataFrame: Data with handled outliers
        """
        if not self.config['handle_outliers']:
            return data
            
        threshold = threshold or self.config['outlier_threshold']
        result_data = data.copy()
        
        for feature in self.numeric_features:
            feature_data = result_data[feature]
            feature_mean = feature_data.mean()
            feature_std = feature_data.std()
            
            # Identify outliers
            lower_bound = feature_mean - threshold * feature_std
            upper_bound = feature_mean + threshold * feature_std
            
            outliers = (feature_data < lower_bound) | (feature_data > upper_bound)
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                logger.info(f"Found {outlier_count} outliers in feature '{feature}'")
                
                if method == 'clip':
                    result_data[feature] = feature_data.clip(lower_bound, upper_bound)
                elif method == 'remove':
                    result_data = result_data[~outliers]
                elif method == 'transform':
                    # Log transform or other transformation can be applied here
                    pass
                    
        return result_data
