"""
OpenAI Integration Example
Shows how to use the AI Operations Brain with OpenAI Function Calling
"""

import json
import requests
from typing import Optional

# Configuration
API_BASE = "http://localhost:8000"
OPENAI_API_KEY = "sk-your-key-here"  # Set via environment variable


def get_available_functions():
    """Fetch function definitions from API"""
    response = requests.get(f"{API_BASE}/api/functions")
    return response.json()["functions"]


def create_system_prompt():
    """Create system prompt for LLM"""
    return """You are an AI Operations Brain for a drone company.
    
Your job is to help assign pilots to missions intelligently.

You have access to functions that:
- Check pilot availability
- Assign pilots to missions
- Find the best pilot for a mission
- Detect conflicts  
- Check drone compatibility
- Handle urgent reassignments

Always:
1. Check for conflicts before assigning
2. Recommend the best pilot based on ML scores
3. Handle urgent high-priority missions with urgency
4. Keep the user informed about conflicts and recommendations

Be helpful, specific, and explain your recommendations."""


def process_ai_response(messages):
    """
    Process conversation with OpenAI, handling function calls
    
    This is a skeleton - requires actual OpenAI SDK
    """
    import openai
    
    openai.api_key = OPENAI_API_KEY
    
    # Get function definitions
    functions = get_available_functions()
    
    # Call OpenAI with function calling
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        functions=functions,
        function_call="auto"
    )
    
    return response


def handle_function_call(function_name: str, arguments: dict) -> dict:
    """
    Execute function based on LLM selection
    
    Maps OpenAI function calls to API endpoints
    """
    
    function_map = {
        "check_pilot_availability": {
            "endpoint": "/api/detect-conflicts",
            "method": "POST"
        },
        "assign_pilot_to_mission": {
            "endpoint": "/api/assign-pilot",
            "method": "POST"
        },
        "find_best_pilot": {
            "endpoint": "/api/rank-pilots",
            "method": "POST"
        },
        "detect_mission_conflicts": {
            "endpoint": "/api/detect-conflicts",
            "method": "POST"
        },
        "check_drone_compatibility": {
            "endpoint": "/api/match-drone",
            "method": "POST"
        },
        "urgent_reassign_mission": {
            "endpoint": "/api/urgent-reassign",
            "method": "POST"
        }
    }
    
    if function_name not in function_map:
        return {"error": f"Unknown function: {function_name}"}
    
    func_info = function_map[function_name]
    
    try:
        response = requests.request(
            method=func_info["method"],
            url=f"{API_BASE}{func_info['endpoint']}",
            json=arguments,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def example_conversation():
    """
    Example multi-turn conversation showing function calling
    
    Note: Requires OpenAI SDK - pip install openai
    """
    
    messages = []
    
    # System message
    messages.append({
        "role": "system",
        "content": create_system_prompt()
    })
    
    # User query 1
    user_message = "Can you assign the best available pilot to Mission M001?"
    messages.append({"role": "user", "content": user_message})
    
    print(f"\n👤 User: {user_message}")
    
    # This would call OpenAI
    # response = process_ai_response(messages)
    
    # For demo, show what would happen:
    print("\n🧠 AI Operations Brain is thinking...")
    print("   - Fetching mission details for M001")
    print("   - Ranking pilots by suitability")
    print("   - Checking for conflicts")
    print("   - Verifying drone compatibility")
    
    # Simulated API response
    simulated_response = {
        "success": True,
        "assignment_id": "ASN-M001-P002",
        "pilot_id": "P002",
        "pilot_name": "Sarah Johnson",
        "mission_id": "M001",
        "confidence": 0.87,
        "conflicts": [],
        "message": "✅ Assigned Sarah Johnson to mission M001"
    }
    
    print(f"\n🎯 AI: {simulated_response['message']}")
    print(f"   Confidence: {simulated_response['confidence']:.0%}")
    print(f"   Assignment ID: {simulated_response['assignment_id']}")
    
    # User query 2
    user_message = "Mission M003 is urgent and critical. Can you reassign?"
    messages.append({"role": "user", "content": user_message})
    
    print(f"\n👤 User: {user_message}")
    print("\n🧠 AI Operations Brain is thinking...")
    print("   - Detecting high priority (CRITICAL)")
    print("   - Ranking pilots for urgent reassignment")
    print("   - Executing reassignment chain")
    
    simulated_response = {
        "success": True,
        "reassignment": {
            "action_type": "urgent_reassignment",
            "mission_id": "M003",
            "new_pilot_id": "P003",
            "new_pilot_name": "Mike Chen",
            "previous_pilot_name": "Emily Davis"
        },
        "notification": "🚨 URGENT REASSIGNMENT EXECUTED\nMission: M003 (Priority: critical)\nNew Assignment: Mike Chen (P003)\nPrevious: Emily Davis"
    }
    
    print(f"\n🚨 AI: {simulated_response['notification']}")
    print(f"\n✅ Reassignment complete and Google Sheets updated")


def example_batch_processing():
    """
    Example showing how to process multiple missions
    """
    
    missions = [
        {"id": "M001", "name": "Building Inspection"},
        {"id": "M002", "name": "Bridge Survey"},
        {"id": "M003", "name": "Emergency Assessment"}
    ]
    
    print("\n" + "=" * 70)
    print("BATCH ASSIGNMENT EXAMPLE")
    print("=" * 70)
    
    for mission in missions:
        # In real usage, would call API
        print(f"\n📋 Processing {mission['name']} ({mission['id']})...")
        
        # Simulate ranking pilots
        simulated_ranking = [
            {"pilot_name": "John Smith", "probability": 0.82},
            {"pilot_name": "Sarah Johnson", "probability": 0.79},
            {"pilot_name": "Mike Chen", "probability": 0.76}
        ]
        
        best = simulated_ranking[0]
        print(f"   ✅ Assigning {best['pilot_name']} ({best['probability']:.0%} confidence)")


def example_error_handling():
    """
    Example showing error handling
    """
    
    print("\n" + "=" * 70)
    print("ERROR HANDLING EXAMPLE")
    print("=" * 70)
    
    scenarios = [
        {
            "scenario": "Budget Overrun",
            "conflict": "Budget overrun by $500",
            "action": "Suggest cheaper pilot or increase budget"
        },
        {
            "scenario": "Double Booking",
            "conflict": "Pilot already assigned during same dates",
            "action": "Choose different pilot or reschedule mission"
        },
        {
            "scenario": "Location Mismatch",
            "conflict": "Pilot in NYC, mission in LA",
            "action": "Alert about travel costs, confirm or choose local pilot"
        },
        {
            "scenario": "Missing Certification",
            "conflict": "Pilot lacks required Advanced certification",
            "action": "Recommend other pilots or request certified pilot"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n⚠️  {scenario['scenario']}")
        print(f"   Issue: {scenario['conflict']}")
        print(f"   Solution: {scenario['action']}")


def main():
    """Run examples"""
    
    print("\n" + "=" * 70)
    print("AI OPERATIONS BRAIN - OPENAI INTEGRATION EXAMPLES")
    print("=" * 70)
    
    # Show available functions
    print("\n1️⃣ AVAILABLE FUNCTIONS:")
    functions = get_available_functions()
    for func in functions:
        print(f"   • {func['name']}")
    
    # Example conversation
    print("\n2️⃣ EXAMPLE CONVERSATION:")
    example_conversation()
    
    # Batch processing
    print("\n3️⃣ BATCH PROCESSING:")
    example_batch_processing()
    
    # Error handling
    print("\n4️⃣ ERROR HANDLING:")
    example_error_handling()
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
To use this in production:

1. Install OpenAI SDK:
   pip install openai

2. Set API key:
   export OPENAI_API_KEY=sk-your-key

3. Start the API server:
   python src/main.py

4. Use with LLM framework (LangChain, etc):
   
   from langchain.chat_models import ChatOpenAI
   from langchain.agents import initialize_agent, tool
   
   llm = ChatOpenAI()
   agent = initialize_agent(tools, llm)
   response = agent.run("Assign John to Mission M001")

5. Or build your own integration:
   - Fetch functions from /api/functions
   - Call ChatGPT with function_call="auto"
   - Parse function responses
   - Call appropriate API endpoints
   - Feed results back to LLM

The AI Operations Brain is fully function-calling compatible!
""")


if __name__ == "__main__":
    main()
