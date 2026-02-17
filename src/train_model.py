"""
ML Model Training Pipeline for Pilot-Mission Matching
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib
from pathlib import Path
import logging
from typing import Tuple

from .features import FeatureEngineer
from .config import (
    MODEL_PATH, TEST_SIZE, RANDOM_STATE, FEATURE_COLUMNS, TARGET_COLUMN
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PilotMatchModel:
    """Handles ML model training, evaluation, and prediction"""
    
    def __init__(self, model_path: str = None):
        """Initialize with optional pre-trained model"""
        self.model_path = model_path or str(MODEL_PATH)
        self.model = None
        self.feature_columns = FEATURE_COLUMNS
        
    def create_training_dataset(
        self,
        pilots_csv: str,
        missions_csv: str
    ) -> pd.DataFrame:
        """
        Create training dataset from CSV files
        
        Args:
            pilots_csv: Path to pilots CSV
            missions_csv: Path to missions CSV
            
        Returns:
            pd.DataFrame: Training dataset
        """
        logger.info(f"Loading pilots from {pilots_csv}")
        pilots_df = pd.read_csv(pilots_csv)
        
        logger.info(f"Loading missions from {missions_csv}")
        missions_df = pd.read_csv(missions_csv)
        
        # Normalize column names to expected format
        pilots_df = self._normalize_pilot_columns(pilots_df)
        missions_df = self._normalize_mission_columns(missions_df)
        
        logger.info(f"Creating training dataset with {len(pilots_df)} pilots and {len(missions_df)} missions")
        
        training_df = FeatureEngineer.create_training_dataset(pilots_df, missions_df)
        
        logger.info(f"Training dataset created with {len(training_df)} samples")
        logger.info(f"Label distribution:\n{training_df[TARGET_COLUMN].value_counts()}")
        
        return training_df
    
    def _normalize_pilot_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize pilot CSV column names to expected format"""
        mapping = {
            'pilot_id': 'id',
            'daily_rate_inr': 'cost_per_day',
            'current_assignment': 'active_assignments'
        }
        df = df.rename(columns=mapping)
        
        # Set default values for missing columns
        if 'id' not in df.columns and 'pilot_id' in df.columns:
            df['id'] = df['pilot_id']
        if 'experience_years' not in df.columns:
            df['experience_years'] = 3  # Default experience
        if 'active_assignments' not in df.columns:
            df['active_assignments'] = []
        
        return df
    
    def _normalize_mission_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize mission CSV column names to expected format"""
        mapping = {
            'project_id': 'id',
            'mission_budget_inr': 'budget',
            'required_certs': 'required_cert',
            'weather_forecast': 'weather'
        }
        df = df.rename(columns=mapping)
        
        # Set default values for missing columns
        if 'id' not in df.columns and 'project_id' in df.columns:
            df['id'] = df['project_id']
        if 'duration_days' not in df.columns:
            # Calculate from dates if available
            if 'start_date' in df.columns and 'end_date' in df.columns:
                df['start_date'] = pd.to_datetime(df['start_date'])
                df['end_date'] = pd.to_datetime(df['end_date'])
                df['duration_days'] = (df['end_date'] - df['start_date']).dt.days + 1
            else:
                df['duration_days'] = 3  # Default duration
        
        return df
    
    def train(
        self,
        training_df: pd.DataFrame,
        test_size: float = TEST_SIZE,
        random_state: int = RANDOM_STATE
    ) -> dict:
        """
        Train Random Forest classifier
        
        Args:
            training_df: Training dataset with features and labels
            test_size: Test/train split ratio
            random_state: Random seed for reproducibility
            
        Returns:
            dict: Training metrics
        """
        logger.info("Preparing features and labels")
        X = training_df[self.feature_columns]
        y = training_df[TARGET_COLUMN]
        
        logger.info(f"Splitting data: {(1-test_size)*100:.0f}% train, {test_size*100:.0f}% test")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        logger.info("Training Random Forest Classifier")
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        logger.info("Evaluating model")
        y_pred = self.model.predict(X_test)
        
        # Handle single-class case
        y_pred_proba_full = self.model.predict_proba(X_test)
        if y_pred_proba_full.shape[1] == 1:
            logger.warning("⚠️ Single-class predictions detected. Using class 0 probabilities.")
            y_pred_proba = y_pred_proba_full[:, 0]
        else:
            y_pred_proba = y_pred_proba_full[:, 1]
        
        metrics = {
            "test_size": len(X_test),
            "train_size": len(X_train),
            "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }
        
        # Only compute ROC-AUC if we have 2 classes
        if len(np.unique(y_test)) > 1:
            metrics["roc_auc"] = roc_auc_score(y_test, y_pred_proba)
            logger.info(f"ROC-AUC Score: {metrics['roc_auc']:.4f}")
        else:
            logger.warning("ROC-AUC not available for single-class test set")
            metrics["roc_auc"] = None
        
        logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred, zero_division=0)}")
        
        return metrics
    
    def save_model(self) -> str:
        """
        Save trained model to disk
        
        Returns:
            str: Path where model was saved
        """
        if self.model is None:
            raise ValueError("No model to save. Train model first.")
        
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
        return self.model_path
    
    def load_model(self) -> None:
        """Load pre-trained model from disk"""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        self.model = joblib.load(self.model_path)
        logger.info(f"Model loaded from {self.model_path}")
    
    def predict(self, features_dict: dict) -> dict:
        """
        Predict suitability for a single pilot-mission pair
        
        Args:
            features_dict: Dictionary with feature values
            
        Returns:
            dict: Prediction and probability
        """
        if self.model is None:
            raise ValueError("Model not loaded. Load or train a model first.")
        
        # Create feature array in correct order
        features = np.array([[
            features_dict[col] for col in self.feature_columns
        ]])
        
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1]
        
        return {
            "suitable": bool(prediction),
            "probability": float(probability),
            "confidence": abs(probability - 0.5) * 2  # 0-1 confidence measure
        }
    
    def get_feature_importance(self) -> dict:
        """Get feature importance from trained model"""
        if self.model is None:
            raise ValueError("Model not trained")
        
        importance_dict = {
            col: float(importance)
            for col, importance in zip(self.feature_columns, self.model.feature_importances_)
        }
        
        # Sort by importance
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def batch_predict(
        self,
        pilots: list,
        mission: dict
    ) -> list:
        """
        Predict for multiple pilots against one mission
        
        Args:
            pilots: List of pilot dictionaries
            mission: Mission dictionary
            
        Returns:
            list: Ranked pilots with scores
        """
        results = []
        
        for pilot in pilots:
            try:
                features = FeatureEngineer.engineer_features_for_prediction(pilot, mission)
                prediction = self.predict(features)
                
                results.append({
                    "pilot_id": pilot.get("id", ""),
                    "pilot_name": pilot.get("name", ""),
                    "suitable": prediction["suitable"],
                    "probability": prediction["probability"],
                    "confidence": prediction["confidence"]
                })
            except Exception as e:
                logger.warning(f"Error predicting for pilot {pilot.get('id')}: {e}")
        
        # Sort by probability descending
        results.sort(key=lambda x: x["probability"], reverse=True)
        
        return results


def main():
    """Example training pipeline"""
    import sys
    
    # Check for CSV file arguments
    if len(sys.argv) < 3:
        print("Usage: python train_model.py <pilots.csv> <missions.csv>")
        print("\nThis script trains a Random Forest model for pilot-mission matching")
        print("The model is saved to models/pilot_match_model.pkl")
        return
    
    pilots_csv = sys.argv[1]
    missions_csv = sys.argv[2]
    
    try:
        # Initialize model
        model = PilotMatchModel()
        
        # Create dataset
        training_df = model.create_training_dataset(pilots_csv, missions_csv)
        
        # Train model
        metrics = model.train(training_df)
        
        # Save model
        model.save_model()
        
        # Print feature importance
        importance = model.get_feature_importance()
        print("\nFeature Importance:")
        for feature, score in importance.items():
            print(f"  {feature}: {score:.4f}")
        
        print("\n✅ Model training complete!")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise


if __name__ == "__main__":
    main()
