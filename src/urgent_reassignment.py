"""
Urgent Reassignment Engine for high-priority missions
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class UrgentReassignmentEngine:
    """Handles urgent reassignment logic for high-priority missions"""
    
    # Priority levels
    PRIORITY_LEVELS = {
        "low": 1,
        "medium": 2,
        "high": 3,
        "critical": 4
    }
    
    @staticmethod
    def should_trigger_reassignment(
        mission: Dict,
        conflicts: List,
        current_confidence: float
    ) -> bool:
        """
        Determine if urgent reassignment should be triggered
        
        Args:
            mission: Mission information with priority
            conflicts: List of detected conflicts
            current_confidence: ML confidence score for current assignment
            
        Returns:
            bool: True if reassignment should be triggered
        """
        mission_priority = UrgentReassignmentEngine.PRIORITY_LEVELS.get(
            mission.get("priority", "low").lower(), 1
        )
        
        # Trigger conditions:
        # 1. High or critical priority + conflicts exist
        # 2. Critical priority alone (regardless of confidence)
        # 3. High priority + low confidence
        
        has_critical = any(c.severity == "high" for c in conflicts)
        
        triggers = [
            mission_priority >= 3 and has_critical,  # High/critical + conflicts
            mission_priority >= 4,  # Critical priority
            mission_priority >= 3 and current_confidence < 0.7  # High priority + low confidence
        ]
        
        return any(triggers)
    
    @staticmethod
    def rank_pilot_candidates(
        available_pilots: List[Dict],
        mission: Dict,
        model_predictions: List[Dict]
    ) -> List[Dict]:
        """
        Rank pilot candidates for reassignment
        
        Args:
            available_pilots: List of available pilots
            mission: Mission needing reassignment
            model_predictions: List of ML prediction results
            
        Returns:
            list: Ranked pilots with reassignment scores
        """
        ranked = []
        
        for prediction in model_predictions:
            pilot_id = prediction.get("pilot_id")
            
            # Find matching pilot
            pilot = next((p for p in available_pilots if p.get("id") == pilot_id), None)
            if not pilot:
                continue
            
            # Calculate reassignment score
            # Weighted combination of:
            # - ML probability (weight 0.5)
            # - Availability (weight 0.2)
            # - Urgency fit (weight 0.3)
            
            ml_score = prediction.get("probability", 0.0) * 0.5
            
            availability = float(pilot.get("availability_score", 0.5)) * 0.2
            
            # Urgency fit: higher experience penalizes cost, but helps high-priority
            experience_boost = min(float(pilot.get("experience_years", 0)) / 20.0, 1.0)
            urgency_fit = experience_boost * 0.3
            
            total_score = ml_score + availability + urgency_fit
            
            ranked.append({
                "pilot_id": pilot_id,
                "pilot_name": pilot.get("name", "Unknown"),
                "experience_years": pilot.get("experience_years", 0),
                "current_assignments": len(pilot.get("active_assignments", [])),
                "cost_per_day": pilot.get("cost_per_day", 0),
                "ml_probability": prediction.get("probability", 0.0),
                "availability_score": availability / 0.2,  # Denormalize
                "reassignment_score": total_score,
                "reason": f"ML: {prediction.get('probability', 0):.2%}, "
                         f"Experience: {experience_boost:.2%}, "
                         f"Availability: {availability/0.2:.2%}"
            })
        
        # Sort by reassignment score
        ranked.sort(key=lambda x: x["reassignment_score"], reverse=True)
        
        return ranked
    
    @staticmethod
    def validate_reassignment(
        pilot: Dict,
        mission: Dict,
        conflicts: List
    ) -> dict:
        """
        Validate that reassignment is safe
        
        Args:
            pilot: Candidate pilot
            mission: Mission being reassigned
            conflicts: Current conflict list
            
        Returns:
            dict: Validation result
        """
        critical_conflicts = [c for c in conflicts if c.severity == "high"]
        warnings = [c for c in conflicts if c.severity != "high"]
        
        is_valid = len(critical_conflicts) == 0
        
        return {
            "valid": is_valid,
            "critical": [c.message for c in critical_conflicts],
            "warnings": [c.message for c in warnings],
            "pilot_id": pilot.get("id"),
            "pilot_name": pilot.get("name")
        }
    
    @staticmethod
    def execute_reassignment(
        pilot: Dict,
        mission: Dict,
        current_assignee: Optional[Dict] = None
    ) -> Dict:
        """
        Execute urgent reassignment
        
        Args:
            pilot: New pilot being assigned
            mission: Mission
            current_assignee: Previous pilot (if any)
            
        Returns:
            dict: Reassignment action details
        """
        action = {
            "action_type": "urgent_reassignment",
            "timestamp": datetime.now().isoformat(),
            "mission_id": mission.get("id"),
            "mission_priority": mission.get("priority", "unknown"),
            "new_pilot_id": pilot.get("id"),
            "new_pilot_name": pilot.get("name", "Unknown"),
            "previous_pilot_id": current_assignee.get("id") if current_assignee else None,
            "previous_pilot_name": current_assignee.get("name") if current_assignee else None,
            "reason": "Urgent reassignment due to conflicts or optimization",
            "status": "pending_confirmation"
        }
        
        logger.info(f"Urgent reassignment created: {action}")
        
        return action
    
    @staticmethod
    def cancel_current_assignment(
        pilot: Dict,
        assignment_id: str
    ) -> Dict:
        """
        Cancel existing assignment for a pilot
        
        Args:
            pilot: Pilot whose assignment is being cancelled
            assignment_id: Assignment ID to cancel
            
        Returns:
            dict: Cancellation action
        """
        action = {
            "action_type": "cancel_assignment",
            "timestamp": datetime.now().isoformat(),
            "pilot_id": pilot.get("id"),
            "pilot_name": pilot.get("name"),
            "assignment_id": assignment_id,
            "status": "pending"
        }
        
        logger.info(f"Assignment cancellation queued: {action}")
        
        return action
    
    @staticmethod
    def generate_reassignment_notification(
        reassignment: Dict,
        reason: str
    ) -> str:
        """
        Generate human-readable notification for reassignment
        
        Args:
            reassignment: Reassignment action
            reason: Reason for reassignment
            
        Returns:
            str: Notification message
        """
        message = f"""
🚨 URGENT REASSIGNMENT EXECUTED

Mission: {reassignment['mission_id']} (Priority: {reassignment['mission_priority']})
Reason: {reason}

New Assignment:
  Pilot: {reassignment['new_pilot_name']} ({reassignment['new_pilot_id']})

Previous Assignment:
  Pilot: {reassignment['previous_pilot_name'] or 'None'} ({reassignment['previous_pilot_id'] or 'N/A'})

Status: {reassignment['status']}
Time: {reassignment['timestamp']}

⏳ Action pending confirmation and Google Sheets sync
"""
        return message.strip()
    
    @staticmethod
    def create_reassignment_chain(
        mission: Dict,
        new_pilot: Dict,
        current_pilot: Dict,
        next_best_pilot: Dict
    ) -> List[Dict]:
        """
        Create chain of reassignments if pilot is being moved
        
        Args:
            mission: Current mission needing reassignment
            new_pilot: Who the mission is being assigned to
            current_pilot: Who the mission is being taken from
            next_best_pilot: Backup option
            
        Returns:
            list: Chain of reassignment actions
        """
        chain = []
        
        # Remove from current pilot
        if current_pilot:
            chain.append(UrgentReassignmentEngine.cancel_current_assignment(
                current_pilot,
                mission.get("id")
            ))
        
        # Assign to new pilot
        chain.append(UrgentReassignmentEngine.execute_reassignment(
            new_pilot,
            mission,
            current_pilot
        ))
        
        # Optionally assign previous mission/task to next best
        if current_pilot and next_best_pilot:
            # This would be handled by business logic
            pass
        
        return chain
