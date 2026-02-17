"""
Unit tests for core components
"""

import unittest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '../src')

from features import FeatureEngineer
from conflict_detector import ConflictDetector, ConflictResult
from drone_matcher import DroneMatcher


class TestFeatureEngineer(unittest.TestCase):
    """Test feature engineering functions"""
    
    def test_skill_match(self):
        """Test skill matching calculation"""
        pilot_skills = "Aerial Survey, Photography, Thermal Imaging"
        required = "Aerial Survey, Video"
        result = FeatureEngineer.calculate_skill_match(pilot_skills, required)
        self.assertEqual(result, 1.0)  # One skill matches
    
    def test_skill_match_empty(self):
        """Test skill match with empty inputs"""
        result = FeatureEngineer.calculate_skill_match("", "")
        self.assertEqual(result, 0.0)
    
    def test_certification_match_true(self):
        """Test certification matching when pilot has cert"""
        pilot_certs = "FAA Part 107, Advanced"
        required = "FAA Part 107"
        result = FeatureEngineer.calculate_certification_match(pilot_certs, required)
        self.assertEqual(result, 1)
    
    def test_certification_match_false(self):
        """Test certification matching when pilot lacks cert"""
        pilot_certs = "FAA Part 107"
        required = "Advanced"
        result = FeatureEngineer.calculate_certification_match(pilot_certs, required)
        self.assertEqual(result, 0)
    
    def test_location_match_true(self):
        """Test location matching same city"""
        result = FeatureEngineer.calculate_location_match("New York", "New York")
        self.assertEqual(result, 1)
    
    def test_location_match_false(self):
        """Test location matching different city"""
        result = FeatureEngineer.calculate_location_match("New York", "San Francisco")
        self.assertEqual(result, 0)
    
    def test_cost_fit_positive(self):
        """Test cost fit calculation with remaining budget"""
        cost_fit = FeatureEngineer.calculate_cost_fit(500, 3, 2000, margin_buffer=0.1)
        # Budget 2000 * 0.9 = 1800, Cost = 500*3 = 1500, Fit = 300
        self.assertGreater(cost_fit, 0)
    
    def test_cost_fit_negative(self):
        """Test cost fit calculation exceeding budget"""
        cost_fit = FeatureEngineer.calculate_cost_fit(700, 5, 2000, margin_buffer=0.1)
        # Budget 2000 * 0.9 = 1800, Cost = 700*5 = 3500, Fit = -1700
        self.assertLess(cost_fit, 0)
    
    def test_availability_score_full(self):
        """Test availability when fully available"""
        score = FeatureEngineer.calculate_availability_score(10, 5)
        self.assertEqual(score, 1.0)
    
    def test_availability_score_partial(self):
        """Test availability when partially available"""
        score = FeatureEngineer.calculate_availability_score(3, 5)
        self.assertEqual(score, 0.6)


class TestConflictDetector(unittest.TestCase):
    """Test conflict detection functions"""
    
    def test_double_booking_true(self):
        """Test double booking detection when conflict exists"""
        today = datetime.now().date()
        pilot = {
            "id": "P001",
            "active_assignments": [
                {
                    "mission_id": "M001",
                    "start_date": today.isoformat(),
                    "end_date": (today + timedelta(days=2)).isoformat()
                }
            ]
        }
        mission = {
            "id": "M002",
            "start_date": (today + timedelta(days=1)).isoformat(),
            "end_date": (today + timedelta(days=3)).isoformat()
        }
        
        has_overlap, conflicting_id = ConflictDetector.check_double_booking(pilot, mission)
        self.assertTrue(has_overlap)
        self.assertEqual(conflicting_id, "M001")
    
    def test_double_booking_false(self):
        """Test double booking detection when no conflict"""
        today = datetime.now().date()
        pilot = {
            "id": "P001",
            "active_assignments": [
                {
                    "mission_id": "M001",
                    "start_date": today.isoformat(),
                    "end_date": (today + timedelta(days=2)).isoformat()
                }
            ]
        }
        mission = {
            "id": "M002",
            "start_date": (today + timedelta(days=5)).isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat()
        }
        
        has_overlap, conflicting_id = ConflictDetector.check_double_booking(pilot, mission)
        self.assertFalse(has_overlap)
    
    def test_budget_check_overrun(self):
        """Test budget overrun detection"""
        pilot = {"cost_per_day": 1000}
        mission = {"duration_days": 5, "budget": 4000}
        
        is_over, remaining = ConflictDetector.check_budget_overrun(pilot, mission)
        self.assertTrue(is_over)
        self.assertEqual(remaining, -1000)
    
    def test_location_match(self):
        """Test location mismatch detection"""
        pilot = {"location": "New York"}
        mission = {"location": "San Francisco"}
        
        has_mismatch, reason = ConflictDetector.check_location_mismatch(pilot, mission)
        self.assertTrue(has_mismatch)
    
    def test_certification_check(self):
        """Test certification checking"""
        pilot = {"certifications": "FAA Part 107"}
        mission = {"required_cert": "Advanced"}
        
        is_certified, reason = ConflictDetector.check_certification(pilot, mission)
        self.assertFalse(is_certified)
    
    def test_detect_all_conflicts(self):
        """Test comprehensive conflict detection"""
        pilot = {
            "id": "P001",
            "cost_per_day": 1000,
            "location": "New York",
            "days_available": 2,
            "certifications": "FAA Part 107",
            "active_assignments": []
        }
        mission = {
            "id": "M001",
            "duration_days": 5,
            "budget": 3000,
            "location": "San Francisco",
            "required_cert": "FAA Part 107"
        }
        
        conflicts = ConflictDetector.detect_all_conflicts(pilot, mission)
        
        # Should detect: budget overrun, location mismatch, low availability
        self.assertGreater(len(conflicts), 0)
        conflict_types = [c.conflict_type for c in conflicts]
        self.assertIn("budget", conflict_types)


class TestDroneMatcher(unittest.TestCase):
    """Test drone matching functions"""
    
    def test_weather_compatibility_ok(self):
        """Test weather compatibility check success"""
        drone = {"weather_rating": "IP54"}
        mission = {"weather": "rainy"}
        
        is_ok, reason = DroneMatcher.check_weather_compatibility(drone, mission)
        self.assertTrue(is_ok)
    
    def test_weather_compatibility_fail(self):
        """Test weather compatibility check failure"""
        drone = {"weather_rating": "IP43"}
        mission = {"weather": "rainy"}
        
        is_ok, reason = DroneMatcher.check_weather_compatibility(drone, mission)
        self.assertFalse(is_ok)
    
    def test_flight_range_ok(self):
        """Test flight range check success"""
        drone = {"flight_range_km": 100}
        mission = {"required_range_km": 80}
        
        is_ok, reason, utilization = DroneMatcher.check_flight_range(drone, mission)
        self.assertTrue(is_ok)
        self.assertLess(utilization, 100)
    
    def test_payload_capacity_fail(self):
        """Test payload capacity check failure"""
        drone = {"payload_capacity_kg": 2.0}
        mission = {"required_payload_kg": 5.0}
        
        is_ok, reason, utilization = DroneMatcher.check_payload_capacity(drone, mission)
        self.assertFalse(is_ok)
    
    def test_battery_endurance_ok(self):
        """Test battery endurance check success"""
        drone = {"battery_endurance_minutes": 45}
        mission = {"estimated_flight_time_minutes": 30}
        
        is_ok, reason, utilization = DroneMatcher.check_battery_endurance(drone, mission)
        self.assertTrue(is_ok)


if __name__ == '__main__':
    unittest.main()
