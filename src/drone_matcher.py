"""
Drone matching rules engine
"""

from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class DroneMatchResult:
    """Result of drone matching"""
    is_compatible: bool
    reason: str
    warnings: list


class DroneMatcher:
    """Handles drone-mission compatibility matching with rule-based logic"""
    
    # Weather rating mappings
    WEATHER_RATINGS = {
        "IP43": ["clear", "cloudy", "light_rain"],
        "IP54": ["clear", "cloudy", "light_rain", "rainy"],
        "IP65": ["clear", "cloudy", "light_rain", "rainy", "heavy_rain"],
        "IP67": ["clear", "cloudy", "light_rain", "rainy", "heavy_rain", "storm"]
    }
    
    @staticmethod
    def check_weather_compatibility(
        drone: Dict,
        mission: Dict
    ) -> Tuple[bool, str]:
        """
        Check if drone can handle mission weather conditions
        
        Args:
            drone: Drone information with weather_rating
            mission: Mission information with weather
            
        Returns:
            tuple: (is_compatible, reason)
        """
        drone_rating = drone.get("weather_rating", "IP43")
        mission_weather = mission.get("weather", "clear").lower()
        
        compatible_weathers = DroneMatcher.WEATHER_RATINGS.get(drone_rating, ["clear"])
        
        if mission_weather not in compatible_weathers:
            return False, f"Drone {drone_rating} cannot handle {mission_weather} weather"
        
        return True, f"Drone compatible with {mission_weather} weather"
    
    @staticmethod
    def check_flight_range(
        drone: Dict,
        mission: Dict
    ) -> Tuple[bool, str, float]:
        """
        Check if drone has sufficient range for mission
        
        Args:
            drone: Drone with flight_range_km
            mission: Mission with required_range_km (estimated distance * 2 for round trip)
            
        Returns:
            tuple: (is_compatible, reason, utilization_percent)
        """
        drone_range = float(drone.get("flight_range_km", 0))
        required_range = float(mission.get("required_range_km", 0))
        
        if drone_range <= 0:
            return False, "Drone range not specified", 0.0
        
        if required_range > drone_range:
            return False, f"Mission requires {required_range}km, drone has {drone_range}km", 100.0
        
        utilization = (required_range / drone_range) * 100 if drone_range > 0 else 0
        return True, f"Drone has sufficient range", utilization
    
    @staticmethod
    def check_payload_capacity(
        drone: Dict,
        mission: Dict
    ) -> Tuple[bool, str, float]:
        """
        Check if drone can carry mission payload
        
        Args:
            drone: Drone with payload_capacity_kg
            mission: Mission with required_payload_kg
            
        Returns:
            tuple: (is_compatible, reason, utilization_percent)
        """
        drone_capacity = float(drone.get("payload_capacity_kg", 0))
        required_payload = float(mission.get("required_payload_kg", 0))
        
        if drone_capacity <= 0:
            return False, "Drone payload capacity not specified", 0.0
        
        if required_payload > drone_capacity:
            return False, f"Mission needs {required_payload}kg, drone carries {drone_capacity}kg", 100.0
        
        utilization = (required_payload / drone_capacity) * 100 if drone_capacity > 0 else 0
        return True, f"Drone has sufficient payload capacity", utilization
    
    @staticmethod
    def check_battery_endurance(
        drone: Dict,
        mission: Dict
    ) -> Tuple[bool, str, float]:
        """
        Check if drone has sufficient battery for mission duration
        
        Args:
            drone: Drone with battery_endurance_minutes
            mission: Mission with estimated_flight_time_minutes
            
        Returns:
            tuple: (is_compatible, reason, utilization_percent)
        """
        endurance = float(drone.get("battery_endurance_minutes", 0))
        flight_time = float(mission.get("estimated_flight_time_minutes", 0))
        
        # Add 20% buffer for safety
        required_time = flight_time * 1.2
        
        if endurance <= 0:
            return False, "Drone endurance not specified", 0.0
        
        if required_time > endurance:
            return False, f"Mission needs {flight_time}min (+ 20% buffer), drone can fly {endurance}min", 100.0
        
        utilization = (required_time / endurance) * 100 if endurance > 0 else 0
        return True, f"Drone has sufficient battery", utilization
    
    @staticmethod
    def check_drone_availability(
        drone: Dict,
        mission: Dict
    ) -> Tuple[bool, str]:
        """
        Check if drone is available for mission period
        
        Args:
            drone: Drone with status and active_missions
            mission: Mission with start_date and end_date
            
        Returns:
            tuple: (is_available, reason)
        """
        status = drone.get("status", "available").lower()
        
        if status != "available":
            return False, f"Drone status is {status}"
        
        # Check for conflicts (simplified)
        active_missions = drone.get("active_missions", [])
        if active_missions and len(active_missions) > 0:
            return False, f"Drone has {len(active_missions)} active mission(s)"
        
        return True, "Drone is available"
    
    @staticmethod
    def match_drone_to_mission(
        drone: Dict,
        mission: Dict
    ) -> DroneMatchResult:
        """
        Comprehensive drone-mission matching with all checks
        
        Args:
            drone: Drone information
            mission: Mission information
            
        Returns:
            DroneMatchResult: Matching result with details
        """
        warnings = []
        critical_issues = []
        
        # Check availability first
        available, reason = DroneMatcher.check_drone_availability(drone, mission)
        if not available:
            return DroneMatchResult(
                is_compatible=False,
                reason=reason,
                warnings=[]
            )
        
        # Check weather compatibility
        weather_ok, weather_reason = DroneMatcher.check_weather_compatibility(drone, mission)
        if not weather_ok:
            critical_issues.append(weather_reason)
        else:
            warnings.append(weather_reason)
        
        # Check range
        range_ok, range_reason, range_util = DroneMatcher.check_flight_range(drone, mission)
        if not range_ok:
            critical_issues.append(range_reason)
        else:
            if range_util > 80:
                warnings.append(f"⚠️ High range utilization: {range_util:.1f}%")
        
        # Check payload
        payload_ok, payload_reason, payload_util = DroneMatcher.check_payload_capacity(drone, mission)
        if not payload_ok:
            critical_issues.append(payload_reason)
        else:
            if payload_util > 80:
                warnings.append(f"⚠️ High payload utilization: {payload_util:.1f}%")
        
        # Check battery
        battery_ok, battery_reason, battery_util = DroneMatcher.check_battery_endurance(drone, mission)
        if not battery_ok:
            critical_issues.append(battery_reason)
        else:
            if battery_util > 90:
                warnings.append(f"⚠️ High battery utilization: {battery_util:.1f}%")
        
        # Determine overall compatibility
        is_compatible = len(critical_issues) == 0
        reason = " | ".join(critical_issues) if critical_issues else "All checks passed"
        
        return DroneMatchResult(
            is_compatible=is_compatible,
            reason=reason,
            warnings=warnings
        )
    
    @staticmethod
    def rank_drones_for_mission(
        drones: list,
        mission: Dict
    ) -> list:
        """
        Rank drones by compatibility with mission
        
        Args:
            drones: List of drone dictionaries
            mission: Mission information
            
        Returns:
            list: Drones ranked by compatibility score
        """
        ranked_drones = []
        
        for drone in drones:
            match_result = DroneMatcher.match_drone_to_mission(drone, mission)
            
            # Calculate compatibility score
            score = 1.0 if match_result.is_compatible else 0.0
            warning_count = len(match_result.warnings)
            score = score - (warning_count * 0.05)  # Penalize warnings
            
            ranked_drones.append({
                "drone_id": drone.get("id", ""),
                "drone_name": drone.get("name", "Unknown"),
                "score": max(0.0, score),
                "compatible": match_result.is_compatible,
                "reason": match_result.reason,
                "warnings": match_result.warnings
            })
        
        # Sort by score descending
        ranked_drones.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked_drones
