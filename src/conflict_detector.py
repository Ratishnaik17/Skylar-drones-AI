"""
Conflict Detection Engine for pilot assignments
"""

from typing import Dict, List, Tuple
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ConflictResult:
    """Result of conflict detection"""
    has_conflict: bool
    conflict_type: str  # "none", "double_booking", "budget", "location", "availability"
    message: str
    severity: str  # "low", "medium", "high"


class ConflictDetector:
    """Detects conflicts in pilot assignments"""
    
    @staticmethod
    def check_double_booking(
        pilot: Dict,
        mission: Dict
    ) -> Tuple[bool, str]:
        """
        Check if pilot has overlapping assignments
        
        Args:
            pilot: Pilot information with active_assignments
            mission: Mission with start_date and end_date
            
        Returns:
            tuple: (has_overlap, conflicting_mission_id)
        """
        mission_start = datetime.fromisoformat(mission.get("start_date", ""))
        mission_end = datetime.fromisoformat(mission.get("end_date", ""))
        
        active_assignments = pilot.get("active_assignments", [])
        
        for assignment in active_assignments:
            active_start = datetime.fromisoformat(assignment.get("start_date", ""))
            active_end = datetime.fromisoformat(assignment.get("end_date", ""))
            
            # Check for overlap
            if mission_start <= active_end and mission_end >= active_start:
                return True, assignment.get("mission_id", "unknown")
        
        return False, ""
    
    @staticmethod
    def check_budget_overrun(
        pilot: Dict,
        mission: Dict
    ) -> Tuple[bool, float]:
        """
        Check if pilot cost exceeds mission budget
        
        Args:
            pilot: Pilot with cost_per_day
            mission: Mission with budget and duration_days
            
        Returns:
            tuple: (is_over_budget, remaining_budget)
        """
        cost_per_day = float(pilot.get("cost_per_day", 0))
        duration_days = int(mission.get("duration_days", 1))
        budget = float(mission.get("budget", 0))
        
        estimated_cost = cost_per_day * duration_days
        remaining = budget - estimated_cost
        
        return estimated_cost > budget, remaining
    
    @staticmethod
    def check_location_mismatch(
        pilot: Dict,
        mission: Dict,
        drone: Dict = None
    ) -> Tuple[bool, str]:
        """
        Check if pilot/drone location mismatches mission location
        
        Args:
            pilot: Pilot with location
            mission: Mission with location
            drone: Optional drone with location
            
        Returns:
            tuple: (has_mismatch, reason)
        """
        pilot_location = pilot.get("location", "").strip().lower()
        mission_location = mission.get("location", "").strip().lower()
        
        if pilot_location != mission_location:
            return True, f"Pilot in {pilot_location}, mission in {mission_location}"
        
        if drone:
            drone_location = drone.get("location", "").strip().lower()
            if drone_location != mission_location:
                return True, f"Drone in {drone_location}, mission in {mission_location}"
        
        return False, ""
    
    @staticmethod
    def check_availability(
        pilot: Dict,
        mission: Dict
    ) -> Tuple[bool, str]:
        """
        Check if pilot is available for the required period
        
        Args:
            pilot: Pilot with availability info
            mission: Mission with duration_days
            
        Returns:
            tuple: (is_available, reason)
        """
        days_available = int(pilot.get("days_available", 0))
        duration_needed = int(mission.get("duration_days", 1))
        
        if days_available < duration_needed:
            return False, f"Pilot has {days_available} days, mission needs {duration_needed}"
        
        return True, ""
    
    @staticmethod
    def check_certification(
        pilot: Dict,
        mission: Dict
    ) -> Tuple[bool, str]:
        """
        Check if pilot has required certification
        
        Args:
            pilot: Pilot with certifications
            mission: Mission with required_cert
            
        Returns:
            tuple: (is_certified, reason)
        """
        pilot_certs = pilot.get("certifications", "").lower()
        required_cert = mission.get("required_cert", "").lower()
        
        if not required_cert:
            return True, ""
        
        if required_cert not in pilot_certs:
            return False, f"Pilot missing {required_cert} certification"
        
        return True, ""
    
    @staticmethod
    def detect_all_conflicts(
        pilot: Dict,
        mission: Dict,
        drone: Dict = None
    ) -> List[ConflictResult]:
        """
        Run all conflict checks and return results
        
        Args:
            pilot: Pilot information
            mission: Mission information
            drone: Optional drone information
            
        Returns:
            list: List of ConflictResult objects
        """
        conflicts = []
        
        # Check double booking
        has_overlap, conflicting_id = ConflictDetector.check_double_booking(pilot, mission)
        if has_overlap:
            conflicts.append(ConflictResult(
                has_conflict=True,
                conflict_type="double_booking",
                message=f"Pilot already assigned to mission {conflicting_id}",
                severity="high"
            ))
        
        # Check budget
        is_over_budget, remaining = ConflictDetector.check_budget_overrun(pilot, mission)
        if is_over_budget:
            conflicts.append(ConflictResult(
                has_conflict=True,
                conflict_type="budget",
                message=f"Budget overrun by ${-remaining:.2f}",
                severity="high"
            ))
        
        # Check location
        has_mismatch, reason = ConflictDetector.check_location_mismatch(pilot, mission, drone)
        if has_mismatch:
            conflicts.append(ConflictResult(
                has_conflict=True,
                conflict_type="location",
                message=reason,
                severity="medium"
            ))
        
        # Check availability
        is_available, reason = ConflictDetector.check_availability(pilot, mission)
        if not is_available:
            conflicts.append(ConflictResult(
                has_conflict=True,
                conflict_type="availability",
                message=reason,
                severity="high"
            ))
        
        # Check certification
        is_certified, reason = ConflictDetector.check_certification(pilot, mission)
        if not is_certified:
            conflicts.append(ConflictResult(
                has_conflict=True,
                conflict_type="certification",
                message=reason,
                severity="high"
            ))
        
        return conflicts
    
    @staticmethod
    def has_critical_conflict(conflicts: List[ConflictResult]) -> bool:
        """
        Check if any critical (high severity) conflicts exist
        
        Args:
            conflicts: List of conflict results
            
        Returns:
            bool: True if any high-severity conflict exists
        """
        return any(c.severity == "high" for c in conflicts)
    
    @staticmethod
    def get_conflict_summary(conflicts: List[ConflictResult]) -> str:
        """
        Get human-readable conflict summary
        
        Args:
            conflicts: List of conflict results
            
        Returns:
            str: Conflict summary message
        """
        if not conflicts:
            return "No conflicts detected"
        
        return " | ".join([f"[{c.conflict_type.upper()}] {c.message}" for c in conflicts])
