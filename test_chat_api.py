import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
SESSION_ID = "demo_conversation_1"

print("=" * 80)
print("CONVERSATIONAL AI TESTING")
print("=" * 80)

# First, let's check the updated root endpoint
print("\n1. API OVERVIEW")
try:
    response = requests.get(f"{BASE_URL}/")
    result = response.json()
    print(f"   API Name: {result.get('name')}")
    print(f"   Version: {result.get('version')}")
    print(f"   Mode: {result.get('mode')}")
    print(f"   Conversation Endpoints:")
    for endpoint, url in result.get('endpoints', {}).get('conversation', {}).items():
        print(f"     - {endpoint}: {url}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 1: Simple greeting
print("\n2. CONVERSATION TEST 1: Greeting")
try:
    payload = {
        "session_id": SESSION_ID,
        "message": "Hello! I need help organizing drone assignments for the next week."
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   AI Response: {result['ai_response'][:200]}...")
    print(f"   Recommended Action: {result.get('recommended_action')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Pilot ranking request
print("\n3. CONVERSATION TEST 2: Pilot Assignment Question")
try:
    payload = {
        "session_id": SESSION_ID,
        "message": "I have a critical mapping mission in Bangalore next week. Who would be the best pilot?"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   AI Response: {result['ai_response'][:200]}...")
    print(f"   Recommended Action: {result.get('recommended_action')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Drone matching question
print("\n4. CONVERSATION TEST 3: Drone Selection Question")
try:
    payload = {
        "session_id": SESSION_ID,
        "message": "Can you check if our DJI M300 drone is suitable for thermal imaging in cloudy weather? We need around 50km range."
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   AI Response: {result['ai_response'][:200]}...")
    print(f"   Recommended Action: {result.get('recommended_action')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Conflict detection question
print("\n5. CONVERSATION TEST 4: Conflict Detection Question")
try:
    payload = {
        "session_id": SESSION_ID,
        "message": "I'm thinking of assigning Arjun to the Mumbai inspection mission. Will there be any conflicts?"
    }
    response = requests.post(f"{BASE_URL}/api/chat", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   AI Response: {result['ai_response'][:200]}...")
    print(f"   Recommended Action: {result.get('recommended_action')}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Get conversation history
print("\n6. CONVERSATION HISTORY")
try:
    response = requests.get(f"{BASE_URL}/api/chat-history/{SESSION_ID}")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Session ID: {result['session_id']}")
    print(f"   Total Messages: {result['message_count']}")
    print(f"   Conversation:")
    for i, msg in enumerate(result['messages'], 1):
        role = msg['role'].upper()
        content = msg['content'][:100] + ("..." if len(msg['content']) > 100 else "")
        print(f"     {i}. [{role}] {content}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 6: Chat with automatic action
print("\n7. CONVERSATION WITH ACTION")
try:
    payload = {
        "session_id": "demo_with_action",
        "message": "Can you rank all pilots for mapping missions?",
        "context": {
            "pilots": [
                {"id": "P001", "name": "Arjun", "skills": "Mapping, Survey", "certifications": "DGCA, Night Ops", "experience_years": 3, "location": "Bangalore", "cost_per_day": 1500, "days_available": 30},
                {"id": "P002", "name": "Neha", "skills": "Inspection", "certifications": "DGCA", "experience_years": 3, "location": "Mumbai", "cost_per_day": 3000, "days_available": 30},
            ],
            "missions": [
                {"id": "PRJ001", "name": "Mapping Mission", "required_skills": "Mapping", "required_cert": "DGCA", "location": "Bangalore", "duration_days": 3, "budget": 10500, "priority": "High", "start_date": "2026-02-06", "end_date": "2026-02-08", "weather": "Rainy"}
            ]
        }
    }
    response = requests.post(f"{BASE_URL}/api/chat-with-action", json=payload)
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   AI Response: {result['ai_response'][:150]}...")
    print(f"   Action Executed: {result.get('action_executed')}")
    if result.get('action_result'):
        print(f"   Action Result:")
        if 'ranked_pilots' in result['action_result']:
            for pilot in result['action_result']['ranked_pilots'][:2]:
                print(f"     - {pilot['pilot_name']}: {pilot['probability']:.2%} suitable")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 7: Clear conversation history
print("\n8. CLEAR CONVERSATION HISTORY")
try:
    response = requests.delete(f"{BASE_URL}/api/chat-history/{SESSION_ID}")
    print(f"   Status: {response.status_code}")
    result = response.json()
    print(f"   Success: {result['success']}")
    print(f"   Message: {result['message']}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("✅ CONVERSATIONAL AI DEMONSTRATION COMPLETE")
print("=" * 80)
print("\nKey Features:")
print("  • Natural language understanding using OpenAI")
print("  • Conversational context management")
print("  • Smart action recommendations")
print("  • Automatic execution of suggested actions")
print("  • Persistent conversation history per session")
print("\nUsage Example:")
print('  POST /api/chat')
print('  {')
print('    "session_id": "user123",')
print('    "message": "Which pilot is best for the Bangalore mapping mission?"')
print('  }')
