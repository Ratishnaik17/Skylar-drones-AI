import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("API TESTING REPORT")
print("=" * 80)

# Test 1: Health Check
print("\n1. HEALTH CHECK")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Feature Importance
print("\n2. FEATURE IMPORTANCE")
try:
    response = requests.get(f"{BASE_URL}/api/feature-importance")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Full response: {result}")
    if isinstance(result, dict) and "feature_importance" in result:
        for feature, importance in result["feature_importance"].items():
            if isinstance(importance, (int, float)):
                print(f"   {feature}: {importance:.4f}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Rank Pilots for PRJ001 (Mapping mission in Bangalore)
print("\n3. RANK PILOTS FOR MISSION PRJ001 (Mapping, Bangalore, High Priority)")
try:
    payload = {
        "pilots": [
            {"id": "P001", "name": "Arjun", "skills": "Mapping, Survey", "certifications": "DGCA, Night Ops", "experience_years": 3, "location": "Bangalore", "cost_per_day": 1500, "days_available": 30},
            {"id": "P002", "name": "Neha", "skills": "Inspection", "certifications": "DGCA", "experience_years": 3, "location": "Mumbai", "cost_per_day": 3000, "days_available": 30},
            {"id": "P003", "name": "Rohit", "skills": "Inspection, Mapping", "certifications": "DGCA", "experience_years": 3, "location": "Mumbai", "cost_per_day": 1500, "days_available": 30},
            {"id": "P004", "name": "Sneha", "skills": "Survey, Thermal", "certifications": "DGCA, Night Ops", "experience_years": 3, "location": "Bangalore", "cost_per_day": 5000, "days_available": 30}
        ],
        "mission": {
            "id": "PRJ001", "name": "Mapping Mission", "required_skills": "Mapping", "required_cert": "DGCA",
            "location": "Bangalore", "duration_days": 3, "budget": 10500, "priority": "High",
            "start_date": "2026-02-06", "end_date": "2026-02-08", "weather": "Rainy"
        }
    }
    response = requests.post(f"{BASE_URL}/api/rank-pilots", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    for pilot in result.get("ranked_pilots", []):
        print(f"   {pilot['pilot_name']}: probability={pilot['probability']:.4f}, suitable={pilot['suitable']}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Detect Conflicts for Pilot-Mission pair
print("\n4. DETECT CONFLICTS (Arjun for PRJ002 - Inspection in Mumbai)")
try:
    payload = {
        "pilot": {"id": "P001", "name": "Arjun", "skills": "Mapping, Survey", "certifications": "DGCA, Night Ops", "experience_years": 3, "location": "Bangalore", "cost_per_day": 1500, "days_available": 30},
        "mission": {
            "id": "PRJ002", "name": "Inspection Mission", "required_skills": "Inspection", "required_cert": "DGCA, Night Ops",
            "location": "Mumbai", "duration_days": 3, "budget": 10500, "priority": "Urgent",
            "start_date": "2026-02-07", "end_date": "2026-02-09", "weather": "Sunny"
        }
    }
    response = requests.post(f"{BASE_URL}/api/detect-conflicts", json=payload)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Has conflicts: {result.get('has_conflicts')}")
        print(f"   Conflict count: {result.get('conflict_count')}")
        critical = result.get("critical_conflicts", [])
        warnings = result.get("warnings", [])
        if critical:
            print(f"   Critical conflicts:")
            for conf in critical:
                print(f"      - {conf.get('conflict_type')}: {conf.get('message')}")
        if warnings:
            print(f"   Warnings:")
            for warn in warnings:
                print(f"      - {warn.get('conflict_type')}: {warn.get('message')}")
        if not critical and not warnings:
            print(f"   ✓ No conflicts detected")
    else:
        print(f"   ERROR: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Match Drone
print("\n5. MATCH DRONE (DJI M300 for thermal mission)")
try:
    payload = {
        "drone": {"id": "DJI-M3", "name": "DJI M300", "location": "Bangalore", "weather_rating": "IP54", "flight_range_km": 55, "payload_capacity_kg": 2.7},
        "mission": {
            "id": "PRJ003", "name": "Thermal Mission", "required_skills": "Thermal", "required_cert": "DGCA",
            "location": "Bangalore", "duration_days": 3, "budget": 10500, "priority": "Standard",
            "start_date": "2026-02-10", "end_date": "2026-02-12", "weather": "Cloudy",
            "required_range_km": 50, "required_payload_kg": 2.5, "estimated_flight_time_minutes": 25
        }
    }
    response = requests.post(f"{BASE_URL}/api/match-drone", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Compatible: {result.get('compatible')}")
    if "matches" in result:
        print(f"   Suitable: {result.get('matches', {}).get('suitable', False)}")
        issues = result.get('matches', {}).get('issues', [])
    else:
        issues = []
        print(f"   Reason: {result.get('reason')}")
        print(f"   Warnings: {result.get('warnings')}")
    if issues:
        print(f"   Issues: {issues}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
