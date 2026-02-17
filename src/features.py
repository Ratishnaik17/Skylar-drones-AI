"""
Feature engineering module for pilot-mission matching
"""

import pandas as pd
from typing import Dict, List, Tuple
import math


class FeatureEngineer:
    """Handles feature engineering for pilot-mission matching"""
    
    @staticmethod
    def calculate_skill_match(pilot_skills: str, required_skills: str) -> float:
        """
        Calculate skill match percentage
        
        Args:
            pilot_skills: Comma-separated string of pilot skills
            required_skills: Comma-separated string of required skills
            
        Returns:
            float: Number of matched skills
        """
        if not pilot_skills or not required_skills:
            return 0.0
        
        pilot_skill_set = set([s.strip().lower() for s in pilot_skills.split(",")])
        required_skill_set = set([s.strip().lower() for s in required_skills.split(",")])
        
        if len(required_skill_set) == 0:
            return 0.0
        
        matches = len(pilot_skill_set & required_skill_set)
        return float(matches)
    
    @staticmethod
    def calculate_certification_match(pilot_certs: str, required_cert: str) -> int:
        """
        Check if pilot has all required certifications
        
        Args:
            pilot_certs: Comma-separated string of pilot certifications
            required_cert: Comma-separated required certification(s)
            
        Returns:
            int: 1 if pilot has all required certs, 0 otherwise
        """
        if not required_cert or not pilot_certs:
            return 0
        
        pilot_cert_list = set([c.strip().lower() for c in pilot_certs.split(",")])
        required_cert_list = set([c.strip().lower() for c in required_cert.split(",")])
        
        # Check if all required certs are in pilot's certs
        return 1 if required_cert_list.issubset(pilot_cert_list) else 0
    
    @staticmethod
    def calculate_location_match(pilot_location: str, mission_location: str) -> int:
        """
        Check if pilot is in same location as mission
        
        Args:
            pilot_location: Pilot's current location
            mission_location: Mission location
            
        Returns:
            int: 1 if same city, 0 otherwise
        """
        if not pilot_location or not mission_location:
            return 0
        return 1 if pilot_location.strip().lower() == mission_location.strip().lower() else 0
    
    @staticmethod
    def calculate_cost_fit(
        pilot_cost_per_day: float,
        mission_duration_days: int,
        mission_budget: float,
        margin_buffer: float = 0.1
    ) -> float:
        """
        Calculate cost fit (budget minus estimated cost)
        
        Args:
            pilot_cost_per_day: Pilot's daily rate
            mission_duration_days: Mission duration in days
            mission_budget: Mission total budget
            margin_buffer: Safety margin (default 10%)
            
        Returns:
            float: Remaining budget after assignment (negative if over budget)
        """
        estimated_cost = pilot_cost_per_day * mission_duration_days
        adjusted_budget = mission_budget * (1 - margin_buffer)
        return adjusted_budget - estimated_cost
    
    @staticmethod
    def calculate_availability_score(
        days_available: int,
        mission_duration_days: int
    ) -> float:
        """
        Calculate availability score
        
        Args:
            days_available: Days pilot has available
            mission_duration_days: Required days for mission
            
        Returns:
            float: Availability metric (capped at 1.0)
        """
        if days_available <= 0 or mission_duration_days <= 0:
            return 0.0
        
        score = min(days_available / mission_duration_days, 1.0)
        return score
    
    @staticmethod
    def create_training_sample(
        pilot: Dict,
        mission: Dict
    ) -> Dict:
        """
        Create a single training sample from pilot and mission data
        
        Args:
            pilot: Dictionary with pilot information
            mission: Dictionary with mission information
            
        Returns:
            dict: Training sample with all features
        """
        # Extract features
        skill_match = FeatureEngineer.calculate_skill_match(
            pilot.get("skills", ""),
            mission.get("required_skills", "")
        )
        
        cert_match = FeatureEngineer.calculate_certification_match(
            pilot.get("certifications", ""),
            mission.get("required_cert", "")
        )
        
        location_match = FeatureEngineer.calculate_location_match(
            pilot.get("location", ""),
            mission.get("location", "")
        )
        
        cost_fit = FeatureEngineer.calculate_cost_fit(
            float(pilot.get("cost_per_day", 0)),
            int(mission.get("duration_days", 1)),
            float(mission.get("budget", 0))
        )
        
        experience = float(pilot.get("experience_years", 0))
        
        # Determine label (basic heuristic)
        label = 1 if (skill_match > 0 and cert_match == 1 and cost_fit >= 0) else 0
        
        return {
            "skill_match": skill_match,
            "cert_match": cert_match,
            "location_match": location_match,
            "cost_fit": cost_fit,
            "experience": experience,
            "label": label,
            "pilot_id": pilot.get("id", ""),
            "mission_id": mission.get("id", "")
        }
    
    @staticmethod
    def create_training_dataset(
        pilots: pd.DataFrame,
        missions: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create full training dataset from pilots and missions
        
        Args:
            pilots: DataFrame with pilot information
            missions: DataFrame with mission information
            
        Returns:
            pd.DataFrame: Training dataset with all samples
        """
        training_data = []
        
        for _, mission in missions.iterrows():
            for _, pilot in pilots.iterrows():
                sample = FeatureEngineer.create_training_sample(
                    pilot.to_dict(),
                    mission.to_dict()
                )
                training_data.append(sample)
        
        return pd.DataFrame(training_data)
    
    @staticmethod
    def engineer_features_for_prediction(
        pilot: Dict,
        mission: Dict
    ) -> Dict:
        """
        Engineer features for a single prediction
        
        Args:
            pilot: Pilot information
            mission: Mission information
            
        Returns:
            dict: Features ready for model prediction
        """
        return {
            "skill_match": FeatureEngineer.calculate_skill_match(
                pilot.get("skills", ""),
                mission.get("required_skills", "")
            ),
            "cert_match": FeatureEngineer.calculate_certification_match(
                pilot.get("certifications", ""),
                mission.get("required_cert", "")
            ),
            "location_match": FeatureEngineer.calculate_location_match(
                pilot.get("location", ""),
                mission.get("location", "")
            ),
            "cost_fit": FeatureEngineer.calculate_cost_fit(
                float(pilot.get("cost_per_day", 0)),
                int(mission.get("duration_days", 1)),
                float(mission.get("budget", 0))
            ),
            "experience": float(pilot.get("experience_years", 0))
        }
