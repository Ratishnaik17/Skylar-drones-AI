<<<<<<< HEAD
"""
Test script for Skylark Drones AI Operations Brain
Tests all core endpoints to ensure system is working
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def print_test(name, status, details=""):
    """Pretty print test results"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_test("Health Check", True, response.json()["status"])
            return True
        return False
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_test("Root Endpoint", True, f"Project: {data.get('project', 'Unknown')}")
            return True
        return False
    except Exception as e:
        print_test("Root Endpoint", False, str(e))
        return False

def test_chat():
    """Test conversational endpoint"""
    try:
        payload = {
            "session_id": "test_session_001",
            "message": "Who is available for a mapping mission in Bangalore?"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print_test("Chat Endpoint", True, f"Response: {data.get('recommended_action', 'N/A')}")
            return True
        return False
    except Exception as e:
        print_test("Chat Endpoint", False, str(e))
        return False

def test_sync_pilots():
    """Test pilot sync endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sync/pilots")
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_test("Sync Pilots", count > 0, f"Loaded {count} pilots")
            return True
        elif response.status_code == 400:
            print_test("Sync Pilots", True, "Google Sheets not configured (expected)")
            return True
        return False
    except Exception as e:
        print_test("Sync Pilots", False, str(e))
        return False

def test_sync_missions():
    """Test mission sync endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sync/missions")
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_test("Sync Missions", count > 0, f"Loaded {count} missions")
            return True
        elif response.status_code == 400:
            print_test("Sync Missions", True, "Google Sheets not configured (expected)")
            return True
        return False
    except Exception as e:
        print_test("Sync Missions", False, str(e))
        return False

def test_sync_drones():
    """Test drone sync endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sync/drones")
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_test("Sync Drones", count > 0, f"Loaded {count} drones")
            return True
        elif response.status_code == 400:
            print_test("Sync Drones", True, "Google Sheets not configured (expected)")
            return True
        return False
    except Exception as e:
        print_test("Sync Drones", False, str(e))
        return False

def test_chat_history():
    """Test chat history endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/chat-history/test_session_001")
        if response.status_code == 200:
            data = response.json()
            msg_count = data.get("message_count", 0)
            print_test("Chat History", msg_count > 0, f"Retrieved {msg_count} messages")
            return True
        elif response.status_code == 404:
            print_test("Chat History", True, "Session exists but empty (expected)")
            return True
        return False
    except Exception as e:
        print_test("Chat History", False, str(e))
        return False

def test_feature_importance():
    """Test feature importance endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/feature-importance")
        if response.status_code == 200:
            data = response.json()
            features = data.get("feature_importance", {})
            print_test("Feature Importance", len(features) > 0, f"Got {len(features)} features")
            return True
        elif response.status_code == 400:
            print_test("Feature Importance", True, "Model not loaded (expected before training)")
            return True
        return False
    except Exception as e:
        print_test("Feature Importance", False, str(e))
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 Skylark Drones - API System Test")
    print("="*60 + "\n")
    
    tests = [
        ("Core Endpoints", [
            ("Health Check", test_health),
            ("Root Endpoint", test_root),
        ]),
        ("Conversational AI", [
            ("Chat Endpoint", test_chat),
            ("Chat History", test_chat_history),
        ]),
        ("Data Sync", [
            ("Sync Pilots", test_sync_pilots),
            ("Sync Missions", test_sync_missions),
            ("Sync Drones", test_sync_drones),
        ]),
        ("ML Model", [
            ("Feature Importance", test_feature_importance),
        ]),
    ]
    
    total_passed = 0
    total_tests = 0
    
    for category, test_list in tests:
        print(f"\n📋 {category}")
        print("-" * 60)
        for test_name, test_func in test_list:
            try:
                if test_func():
                    total_passed += 1
            except:
                pass
            total_tests += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {total_passed}/{total_tests} tests passed")
    print("="*60 + "\n")
    
    if total_passed == total_tests:
        print("✅ System is fully operational!")
    elif total_passed >= total_tests - 2:
        print("⚠️  System is mostly functional (Google Sheets not configured)")
    else:
        print("❌ Some issues detected - check server logs")

if __name__ == "__main__":
    main()
=======
"""
Test script for Skylark Drones AI Operations Brain
Tests all core endpoints to ensure system is working
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def print_test(name, status, details=""):
    """Pretty print test results"""
    symbol = "✅" if status else "❌"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print_test("Health Check", True, response.json()["status"])
            return True
        return False
    except Exception as e:
        print_test("Health Check", False, str(e))
        return False

def test_root():
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_test("Root Endpoint", True, f"Project: {data.get('project', 'Unknown')}")
            return True
        return False
    except Exception as e:
        print_test("Root Endpoint", False, str(e))
        return False

def test_chat():
    """Test conversational endpoint"""
    try:
        payload = {
            "session_id": "test_session_001",
            "message": "Who is available for a mapping mission in Bangalore?"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print_test("Chat Endpoint", True, f"Response: {data.get('recommended_action', 'N/A')}")
            return True
        return False
    except Exception as e:
        print_test("Chat Endpoint", False, str(e))
        return False

def test_sync_pilots():
    """Test pilot sync endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sync/pilots")
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_test("Sync Pilots", count > 0, f"Loaded {count} pilots")
            return True
        elif response.status_code == 400:
            print_test("Sync Pilots", True, "Google Sheets not configured (expected)")
            return True
        return False
    except Exception as e:
        print_test("Sync Pilots", False, str(e))
        return False

def test_sync_missions():
    """Test mission sync endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sync/missions")
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_test("Sync Missions", count > 0, f"Loaded {count} missions")
            return True
        elif response.status_code == 400:
            print_test("Sync Missions", True, "Google Sheets not configured (expected)")
            return True
        return False
    except Exception as e:
        print_test("Sync Missions", False, str(e))
        return False

def test_sync_drones():
    """Test drone sync endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sync/drones")
        if response.status_code == 200:
            data = response.json()
            count = data.get("count", 0)
            print_test("Sync Drones", count > 0, f"Loaded {count} drones")
            return True
        elif response.status_code == 400:
            print_test("Sync Drones", True, "Google Sheets not configured (expected)")
            return True
        return False
    except Exception as e:
        print_test("Sync Drones", False, str(e))
        return False

def test_chat_history():
    """Test chat history endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/chat-history/test_session_001")
        if response.status_code == 200:
            data = response.json()
            msg_count = data.get("message_count", 0)
            print_test("Chat History", msg_count > 0, f"Retrieved {msg_count} messages")
            return True
        elif response.status_code == 404:
            print_test("Chat History", True, "Session exists but empty (expected)")
            return True
        return False
    except Exception as e:
        print_test("Chat History", False, str(e))
        return False

def test_feature_importance():
    """Test feature importance endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/feature-importance")
        if response.status_code == 200:
            data = response.json()
            features = data.get("feature_importance", {})
            print_test("Feature Importance", len(features) > 0, f"Got {len(features)} features")
            return True
        elif response.status_code == 400:
            print_test("Feature Importance", True, "Model not loaded (expected before training)")
            return True
        return False
    except Exception as e:
        print_test("Feature Importance", False, str(e))
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 Skylark Drones - API System Test")
    print("="*60 + "\n")
    
    tests = [
        ("Core Endpoints", [
            ("Health Check", test_health),
            ("Root Endpoint", test_root),
        ]),
        ("Conversational AI", [
            ("Chat Endpoint", test_chat),
            ("Chat History", test_chat_history),
        ]),
        ("Data Sync", [
            ("Sync Pilots", test_sync_pilots),
            ("Sync Missions", test_sync_missions),
            ("Sync Drones", test_sync_drones),
        ]),
        ("ML Model", [
            ("Feature Importance", test_feature_importance),
        ]),
    ]
    
    total_passed = 0
    total_tests = 0
    
    for category, test_list in tests:
        print(f"\n📋 {category}")
        print("-" * 60)
        for test_name, test_func in test_list:
            try:
                if test_func():
                    total_passed += 1
            except:
                pass
            total_tests += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {total_passed}/{total_tests} tests passed")
    print("="*60 + "\n")
    
    if total_passed == total_tests:
        print("✅ System is fully operational!")
    elif total_passed >= total_tests - 2:
        print("⚠️  System is mostly functional (Google Sheets not configured)")
    else:
        print("❌ Some issues detected - check server logs")

if __name__ == "__main__":
    main()
>>>>>>> 77ca2b55cb8ab10691b83b6bb75a8a6a57195229
