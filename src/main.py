"""
Main FastAPI Application with OpenAI Function Calling
AI Operations Brain for Drone Company
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from datetime import datetime
import json

from .config import (
    API_HOST, API_PORT, DEBUG, OPENAI_API_KEY, SUITABILITY_THRESHOLD,
    GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_ID, PILOTS_SHEET, MISSIONS_SHEET,
    DRONES_SHEET, ASSIGNMENTS_SHEET, HIGH_PRIORITY_THRESHOLD
)

from .train_model import PilotMatchModel
from .features import FeatureEngineer
from .conflict_detector import ConflictDetector
from .urgent_reassignment import UrgentReassignmentEngine
from .sheets_integration import GoogleSheetsIntegration
from .drone_matcher import DroneMatcher

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AI Operations Brain - Drone Company",
    description="ML-powered pilot-mission matching with conflict detection",
    version="1.0.0"
)

# Global components
pilot_match_model = None
sheets_integration = None

# ---------- Pydantic Models ----------

class Pilot(BaseModel):
    id: str
    name: str
    skills: str
    certifications: str
    experience_years: int
    location: str
    cost_per_day: float
    days_available: int
    status: str = "available"
    active_assignments: List[Dict] = []

class Mission(BaseModel):
    id: str
    name: str
    required_skills: str
    required_cert: str
    location: str
    duration_days: int
    budget: float
    priority: str = "medium"
    start_date: str
    end_date: str
    weather: str = "clear"
    required_payload_kg: float = 0.0
    required_range_km: float = 0.0
    estimated_flight_time_minutes: float = 0.0
    status: str = "open"

class Drone(BaseModel):
    id: str
    name: str
    location: str
    status: str = "available"
    weather_rating: str = "IP43"
    flight_range_km: float = 100.0
    payload_capacity_kg: float = 5.0
    battery_endurance_minutes: float = 30.0
    active_missions: List[str] = []

class AssignmentRequest(BaseModel):
    mission_id: str
    pilot_id: Optional[str] = None
    drone_id: Optional[str] = None
    auto_select: bool = True

class AssignmentResponse(BaseModel):
    success: bool
    assignment_id: str
    pilot_id: str
    pilot_name: str
    mission_id: str
    confidence: float
    conflicts: List[str] = []
    drone_id: Optional[str] = None
    message: str

# ---------- Conversation Models ----------

class ChatMessage(BaseModel):
    role: str  # "user", "assistant"
    content: str
    timestamp: Optional[str] = None

class ConversationRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class ConversationResponse(BaseModel):
    session_id: str
    ai_response: str
    recommended_action: Optional[str] = None
    action_details: Optional[Dict[str, Any]] = None
    confidence: float

# Local conversation history storage (in-memory for demo)
conversation_history: Dict[str, List[ChatMessage]] = {}

# ---------- Startup/Shutdown ----------

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    global pilot_match_model, sheets_integration
    
    logger.info("🚀 Starting AI Operations Brain...")
    
    # Load ML model
    try:
        pilot_match_model = PilotMatchModel()
        pilot_match_model.load_model()
        logger.info("✅ ML model loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️  Could not load ML model: {e}")
        logger.info("Model will need to be trained before predictions can be made")
    
    # Initialize Google Sheets
    try:
        sheets_integration = GoogleSheetsIntegration(
            GOOGLE_SHEETS_CREDENTIALS,
            GOOGLE_SHEETS_ID
        )
        if sheets_integration.authenticate():
            logger.info("✅ Google Sheets integration ready")
        else:
            logger.warning("⚠️  Google Sheets sync disabled")
    except Exception as e:
        logger.warning(f"⚠️  Google Sheets initialization failed: {e}")
    
    logger.info("✅ AI Operations Brain started!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down AI Operations Brain...")

# ---------- Health Check ----------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "ml_model_loaded": pilot_match_model is not None,
        "sheets_connected": sheets_integration is not None
    }

# ---------- ML Endpoints ----------

@app.post("/api/train-model")
async def train_model(pilots_file: str, missions_file: str):
    """
    Train or retrain the ML model
    
    Args:
        pilots_file: Path to pilots CSV
        missions_file: Path to missions CSV
    """
    global pilot_match_model
    
    try:
        logger.info(f"Training model from {pilots_file} and {missions_file}")
        
        pilot_match_model = PilotMatchModel()
        training_df = pilot_match_model.create_training_dataset(pilots_file, missions_file)
        metrics = pilot_match_model.train(training_df)
        model_path = pilot_match_model.save_model()
        
        importance = pilot_match_model.get_feature_importance()
        
        return {
            "success": True,
            "model_path": model_path,
            "metrics": metrics,
            "feature_importance": importance,
            "message": "✅ Model trained successfully"
        }
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feature-importance")
async def get_feature_importance():
    """Get feature importance from trained model"""
    if not pilot_match_model:
        raise HTTPException(status_code=400, detail="Model not loaded")
    
    try:
        importance = pilot_match_model.get_feature_importance()
        return {"feature_importance": importance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Matching Endpoints ----------

@app.post("/api/match-pilot")
async def match_pilot(pilot: Pilot, mission: Mission):
    """
    Get suitability score for a specific pilot-mission pair
    
    Args:
        pilot: Pilot information
        mission: Mission information
    """
    if not pilot_match_model:
        raise HTTPException(status_code=400, detail="ML model not loaded")
    
    try:
        # Engineer features
        features = FeatureEngineer.engineer_features_for_prediction(
            pilot.model_dump(),
            mission.model_dump()
        )
        
        # Get prediction
        prediction = pilot_match_model.predict(features)
        
        # Check conflicts
        conflicts = ConflictDetector.detect_all_conflicts(pilot.model_dump(), mission.model_dump())
        conflict_messages = [c.message for c in conflicts]
        
        return {
            "pilot_id": pilot.id,
            "pilot_name": pilot.name,
            "mission_id": mission.id,
            "suitable": prediction["suitable"],
            "probability": prediction["probability"],
            "confidence": prediction["confidence"],
            "conflicts": conflict_messages,
            "features_used": features
        }
        
    except Exception as e:
        logger.error(f"Matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Skylark Drones AI</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                font-family: 'Inter', sans-serif;
                background: #f4f6f9;
                display: flex;
                height: 100vh;
            }

            .sidebar {
                width: 260px;
                background: #0f172a;
                color: white;
                padding: 30px 20px;
            }

            .sidebar h2 {
                margin-top: 0;
                font-size: 20px;
                font-weight: 600;
            }

            .sidebar p {
                font-size: 14px;
                color: #cbd5e1;
            }

            .main {
                flex: 1;
                display: flex;
                flex-direction: column;
            }

            .header {
                background: white;
                padding: 20px 30px;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                font-size: 18px;
            }

            .chat-container {
                flex: 1;
                padding: 30px;
                overflow-y: auto;
            }

            .message {
                max-width: 70%;
                margin-bottom: 15px;
                padding: 12px 16px;
                border-radius: 12px;
                line-height: 1.6;
                font-size: 14px;
                white-space: pre-line;
            }

            .user {
                background: #2563eb;
                color: white;
                margin-left: auto;
                border-bottom-right-radius: 4px;
            }

            .ai {
                background: white;
                border: 1px solid #e2e8f0;
                color: #0f172a;
                border-bottom-left-radius: 4px;
            }

            .typing {
                font-style: italic;
                color: #64748b;
                margin-bottom: 10px;
            }

            .input-area {
                display: flex;
                padding: 20px;
                background: white;
                border-top: 1px solid #e2e8f0;
            }

            input {
                flex: 1;
                padding: 12px;
                border-radius: 8px;
                border: 1px solid #cbd5e1;
                font-size: 14px;
            }

            button {
                margin-left: 10px;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                background: #2563eb;
                color: white;
                font-weight: 500;
                cursor: pointer;
            }

            button:hover {
                background: #1e40af;
            }
        </style>
    </head>
    <body>

        <div class="sidebar">
            <h2>🚁 Skylark Drones AI</h2>
            <p>Operations Coordinator Dashboard</p>
            <hr style="border-color:#334155;">
            <p>✔ Pilot Matching</p>
            <p>✔ Drone Assignment</p>
            <p>✔ Conflict Detection</p>
            <p>✔ Urgent Reassignment</p>
        </div>

        <div class="main">
            <div class="header">
                AI Operations Brain
            </div>

            <div id="chatBox" class="chat-container"></div>

            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Ask about pilots, missions, drones..." />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>

        <script>

            const chatBox = document.getElementById("chatBox");
            const input = document.getElementById("messageInput");

            input.addEventListener("keypress", function(e) {
                if (e.key === "Enter") {
                    sendMessage();
                }
            });

            async function sendMessage() {
                const message = input.value.trim();
                if (!message) return;

                chatBox.innerHTML += `<div class="message user">${message}</div>`;
                input.value = "";

                // Typing indicator
                const typingDiv = document.createElement("div");
                typingDiv.className = "typing";
                typingDiv.innerText = "AI is thinking...";
                chatBox.appendChild(typingDiv);
                chatBox.scrollTop = chatBox.scrollHeight;

                const response = await fetch("/api/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: "web_user",
                        message: message
                    })
                });

                const data = await response.json();

                chatBox.removeChild(typingDiv);

                chatBox.innerHTML += `<div class="message ai">${formatResponse(data.ai_response)}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }

            function formatResponse(text) {
                return text
                    .replace(/\\n/g, "<br>")
                    .replace(/•/g, "• ")
                    .replace(/📍|📅|🎯|👌|👍/g, match => match);
            }

        </script>

    </body>
    </html>
    """



@app.post("/api/rank-pilots")
async def rank_pilots(pilots: List[Pilot], mission: Mission):
    """
    Rank all pilots by suitability for a mission
    
    Args:
        pilots: List of pilot information
        mission: Mission information
    """
    if not pilot_match_model:
        raise HTTPException(status_code=400, detail="ML model not loaded")
    
    try:
        # Get predictions for all pilots
        predictions = pilot_match_model.batch_predict(
            [p.model_dump() for p in pilots],
            mission.model_dump()
        )
        
        # Add conflict information
        ranked = []
        for pred in predictions:
            pilot = next((p for p in pilots if p.id == pred["pilot_id"]), None)
            if not pilot:
                continue
            
            conflicts = ConflictDetector.detect_all_conflicts(pilot.model_dump(), mission.model_dump())
            has_critical = ConflictDetector.has_critical_conflict(conflicts)
            
            ranked.append({
                **pred,
                "has_conflicts": len(conflicts) > 0,
                "conflict_messages": [c.message for c in conflicts],
                "is_viable": pred["probability"] >= SUITABILITY_THRESHOLD and not has_critical
            })
        
        return {"ranked_pilots": ranked}
        
    except Exception as e:
        logger.error(f"Ranking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Assignment Endpoints ----------

@app.post("/api/assign-pilot")
async def assign_pilot(assignment_req: AssignmentRequest, mission: Mission, pilots: List[Pilot]):
    """
    Assign a pilot to a mission with conflict detection
    
    Args:
        assignment_req: Assignment request
        mission: Mission information
        pilots: Available pilots
    """
    try:
        selected_pilot = None
        
        # If specific pilot requested, use that one
        if assignment_req.pilot_id:
            selected_pilot = next((p for p in pilots if p.id == assignment_req.pilot_id), None)
            if not selected_pilot:
                raise HTTPException(status_code=404, detail="Pilot not found")
        
        # Otherwise auto-select best pilot
        elif assignment_req.auto_select and pilot_match_model:
            predictions = pilot_match_model.batch_predict(
                [p.model_dump() for p in pilots],
                mission.model_dump()
            )
            
            # Find best viable pilot
            for pred in predictions:
                pilot = next((p for p in pilots if p.id == pred["pilot_id"]), None)
                if not pilot:
                    continue
                
                conflicts = ConflictDetector.detect_all_conflicts(pilot.model_dump(), mission.model_dump())
                is_viable = (
                    pred["probability"] >= SUITABILITY_THRESHOLD and
                    not ConflictDetector.has_critical_conflict(conflicts)
                )
                
                if is_viable:
                    selected_pilot = pilot
                    break
        
        if not selected_pilot:
            raise HTTPException(status_code=400, detail="No suitable pilot found")
        
        # Check conflicts
        conflicts = ConflictDetector.detect_all_conflicts(selected_pilot.model_dump(), mission.model_dump())
        conflict_messages = [c.message for c in conflicts]
        
        # Get prediction confidence
        features = FeatureEngineer.engineer_features_for_prediction(
            selected_pilot.model_dump(),
            mission.model_dump()
        )
        prediction = pilot_match_model.predict(features) if pilot_match_model else {"probability": 0.5}
        
        # Create assignment
        assignment_id = f"ASN-{mission.id}-{selected_pilot.id}"
        
        # Try to sync to Google Sheets
        if sheets_integration:
            sheets_integration.append_assignment({
                "id": assignment_id,
                "mission_id": mission.id,
                "pilot_name": selected_pilot.name,
                "status": "confirmed",
                "created_at": datetime.now().isoformat(),
                "notes": f"Confidence: {prediction.get('probability', 0):.2%}"
            })
        
        return AssignmentResponse(
            success=True,
            assignment_id=assignment_id,
            pilot_id=selected_pilot.id,
            pilot_name=selected_pilot.name,
            mission_id=mission.id,
            confidence=prediction.get("probability", 0.5),
            conflicts=conflict_messages,
            message=f"✅ Assigned {selected_pilot.name} to mission {mission.id}"
        )
        
    except Exception as e:
        logger.error(f"Assignment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Drone Matching Endpoints ----------

@app.post("/api/match-drone")
async def match_drone(drone: Drone, mission: Mission):
    """
    Check drone-mission compatibility
    
    Args:
        drone: Drone information
        mission: Mission information
    """
    try:
        match_result = DroneMatcher.match_drone_to_mission(drone.model_dump(), mission.model_dump())
        
        return {
            "drone_id": drone.id,
            "drone_name": drone.name,
            "mission_id": mission.id,
            "compatible": match_result.is_compatible,
            "reason": match_result.reason,
            "warnings": match_result.warnings
        }
        
    except Exception as e:
        logger.error(f"Drone matching failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rank-drones")
async def rank_drones(drones: List[Drone], mission: Mission):
    """
    Rank drones by suitability for mission
    
    Args:
        drones: List of available drones
        mission: Mission information
    """
    try:
        ranked = DroneMatcher.rank_drones_for_mission(
            [d.dict() for d in drones],
            mission.dict()
        )
        
        return {"ranked_drones": ranked}
        
    except Exception as e:
        logger.error(f"Drone ranking failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Conflict Detection Endpoints ----------

@app.post("/api/detect-conflicts")
async def detect_conflicts(pilot: Pilot, mission: Mission, drone: Optional[Drone] = None):
    """
    Detect all conflicts for a pilot-mission assignment
    
    Args:
        pilot: Pilot information
        mission: Mission information
        drone: Optional drone information
    """
    try:
        from dataclasses import asdict
        conflicts = ConflictDetector.detect_all_conflicts(
            pilot.model_dump(),
            mission.model_dump(),
            drone.model_dump() if drone else None
        )
        
        return {
            "pilot_id": pilot.id,
            "mission_id": mission.id,
            "has_conflicts": len(conflicts) > 0,
            "conflict_count": len(conflicts),
            "critical_conflicts": [asdict(c) for c in conflicts if c.severity == "high"],
            "warnings": [asdict(c) for c in conflicts if c.severity != "high"],
            "summary": ConflictDetector.get_conflict_summary(conflicts)
        }
        
    except Exception as e:
        logger.error(f"Conflict detection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Urgent Reassignment Endpoints ----------

@app.post("/api/urgent-reassign")
async def urgent_reassign(mission: Mission, current_pilot: Pilot, pilots: List[Pilot]):
    """
    Perform urgent reassignment for high-priority mission
    
    Args:
        mission: Mission needing reassignment
        current_pilot: Current assigned pilot
        pilots: Available pilots for reassignment
    """
    try:
        # Get predictions for available pilots
        if not pilot_match_model:
            raise HTTPException(status_code=400, detail="ML model not loaded")
        
        predictions = pilot_match_model.batch_predict(
            [p.dict() for p in pilots if p.id != current_pilot.id],
            mission.dict()
        )
        
        # Rank candidates with reassignment logic
        ranked = UrgentReassignmentEngine.rank_pilot_candidates(
            [p.dict() for p in pilots],
            mission.dict(),
            predictions
        )
        
        if not ranked:
            raise HTTPException(status_code=400, detail="No viable pilots for reassignment")
        
        # Select best candidate
        new_pilot = next((p for p in pilots if p.id == ranked[0]["pilot_id"]), None)
        
        # Execute reassignment
        reassignment = UrgentReassignmentEngine.execute_reassignment(
            new_pilot.dict(),
            mission.dict(),
            current_pilot.dict()
        )
        
        # Sync to sheets
        if sheets_integration:
            sheets_integration.create_activity_log({
                "timestamp": datetime.now().isoformat(),
                "action_type": "urgent_reassignment",
                "pilot_name": new_pilot.name,
                "mission_id": mission.id,
                "status": "executed",
                "details": f"Reassigned from {current_pilot.name}"
            })
        
        notification = UrgentReassignmentEngine.generate_reassignment_notification(
            reassignment,
            f"High-priority mission optimization"
        )
        
        return {
            "success": True,
            "reassignment": reassignment,
            "new_pilot": {
                "id": new_pilot.id,
                "name": new_pilot.name,
                "confidence": ranked[0]["reassignment_score"]
            },
            "notification": notification,
            "candidates": ranked[:3]  # Top 3 options
        }
        
    except Exception as e:
        logger.error(f"Urgent reassignment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Data Sync Endpoints ----------

@app.get("/api/sync/pilots")
async def sync_pilots():
    """Sync pilots from Google Sheets"""
    if not sheets_integration:
        raise HTTPException(status_code=400, detail="Google Sheets not configured")
    
    try:
        pilots_df = sheets_integration.read_pilots()
        return {
            "success": True,
            "count": len(pilots_df),
            "pilots": pilots_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sync/missions")
async def sync_missions():
    """Sync missions from Google Sheets"""
    if not sheets_integration:
        raise HTTPException(status_code=400, detail="Google Sheets not configured")
    
    try:
        missions_df = sheets_integration.read_missions()
        return {
            "success": True,
            "count": len(missions_df),
            "missions": missions_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sync/drones")
async def sync_drones():
    """Sync drones from Google Sheets"""
    if not sheets_integration:
        raise HTTPException(status_code=400, detail="Google Sheets not configured")
    
    try:
        drones_df = sheets_integration.read_drones()
        return {
            "success": True,
            "count": len(drones_df),
            "drones": drones_df.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Conversational AI Endpoints ----------

@app.post("/api/chat")
async def chat(request: ConversationRequest):
    """
    Conversational AI endpoint for natural language interaction
    
    Args:
        request: ConversationRequest with session_id, message, and optional context
    """
    try:
        # Initialize session history if needed
        if request.session_id not in conversation_history:
            conversation_history[request.session_id] = []
        
        # Add user message to history
        user_msg = ChatMessage(role="user", content=request.message, timestamp=datetime.now().isoformat())
        conversation_history[request.session_id].append(user_msg)
        
        # Generate AI response based on keywords and context
        msg_lower = request.message.lower()
        ai_response = None
        
        # Smart response generation based on message content
        if any(word in msg_lower for word in ["rank", "best", "pilot"]):
            ai_response = """I can help you rank pilots for missions. Based on the drone company's operations, I would evaluate pilots using:
            
1. **Skills Match**: How well the pilot's skills align with mission requirements
2. **Location Compatibility**: Proximity to the mission location
3. **Cost Efficiency**: Daily rates balanced against budget constraints
4. **Certifications**: Required credentials for the mission type
5. **Experience Level**: Years of flying experience

To provide specific rankings, I would need details about:
- Your available pilots and their qualifications
- The target mission specifications
- Any specific constraints or preferences

How can I help you with pilot selection today?"""
        
        elif any(word in msg_lower for word in ["drone", "match", "compatible", "aircraft"]):
            ai_response = """I can help you match drones to missions. The system evaluates:

1. **Weather Compatibility**: IP rating requirements (IP43, IP54, IP65, IP67)
2. **Flight Range**: Mission distance vs. drone maximum range
3. **Payload Capacity**: Equipment weight requirements
4. **Battery Endurance**: Flight time needed with safet margins
5. **Availability**: Current drone status and assignments

For drone selection, I need:
- Available drones in your fleet
- Mission specifications (location, weather, distance, payload)
- Special requirements or constraints

What mission are you trying to match with available drones?"""
        
        elif any(word in msg_lower for word in ["assign", "assignment", "allocate"]):
            ai_response = """I can help you assign pilots and drones to missions. The system performs:

1. **Conflict Detection**: Identifies scheduling conflicts, budget issues, location problems
2. **Suitability Analysis**: Matches capabilities to requirements
3. **Recommendation Engine**: Suggests optimal assignments
4. **Urgent Reassignment**: Handles critical mission changes

To process an assignment, please provide:
- Pilot information (name, skills, certifications, location)
- Mission details (skills required, location, budget, timeline)
- Any drones to be assigned
- Constraints or special requirements

What assignment would you like help with?"""
        
        elif any(word in msg_lower for word in ["conflict", "issue", "problem", "check"]):
            ai_response = """I can detect and prevent assignment conflicts. I check for:

1. **Location Conflicts**: Geographic mismatches between pilots and missions
2. **Schedule Conflicts**: Double-booking prevention
3. **Budget Conflicts**: Cost overruns
4. **Certification Gaps**: Missing required qualifications
5. **Availability Issues**: Pilot/drone status problems

To analyze conflicts, I need:
- Pilot details
- Mission requirements
- Current assignments
- Any specific concerns

What potential conflicts should I investigate?"""
        
        elif any(word in msg_lower for word in ["urgent", "reassign", "critical", "emergency"]):
            ai_response = """I can help with urgent reassignments for critical missions. The system provides:

1. **Priority Assessment**: Evaluates mission criticality
2. **Quick Alternatives**: Rapidly identifies suitable replacements
3. **Conflict Resolution**: Handles concurrent assignment needs
4. **Risk Scoring**: Rates assignment quality
5. **Escalation Rules**: Follows priority protocols

For urgent reassignment, provide:
- The critical mission details
- Current assignment status
- Available replacement options
- Timeline constraints

What urgent reassignment do you need help with?"""
        
        else:
            # Default conversational response
            ai_response = f"""Thank you for your question about drone operations management. 

I'm an AI assistant specialized in helping with:
- **Pilot Ranking & Assignment**: Finding the best pilots for missions
- **Drone Matching**: Selecting compatible aircraft for mission requirements
- **Conflict Detection**: Identifying potential scheduling or capability issues
- **Urgent Reassignment**: Rapid response for critical mission changes

Your message: "{request.message}"

I'd be happy to help! Could you provide more specific details about:
1. What you're trying to accomplish (pilot assignment, drone selection, conflict check)?
2. Which pilots, drones, or missions are involved?
3. Any special constraints or requirements?

How can I assist you better?"""
        
        # Add assistant response to history
        assistant_msg = ChatMessage(role="assistant", content=ai_response, timestamp=datetime.now().isoformat())
        conversation_history[request.session_id].append(assistant_msg)
        
        # Determine recommended action
        recommended_action = None
        confidence = 0.0
        
        if any(word in msg_lower for word in ["rank", "assign", "pilot", "best"]):
            recommended_action = "rank_pilots"
            confidence = 0.85
        elif any(word in msg_lower for word in ["drone", "match", "compatible"]):
            recommended_action = "match_drone"
            confidence = 0.85
        elif any(word in msg_lower for word in ["conflict", "issue"]):
            recommended_action = "detect_conflicts"
            confidence = 0.9
        elif any(word in msg_lower for word in ["urgent", "reassign", "critical"]):
            recommended_action = "urgent_reassign"
            confidence = 0.95
        
        return ConversationResponse(
            session_id=request.session_id,
            ai_response=ai_response,
            recommended_action=recommended_action,
            action_details=request.context,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversation_history:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "messages": conversation_history[session_id],
        "message_count": len(conversation_history[session_id])
    }

@app.delete("/api/chat-history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_history:
        del conversation_history[session_id]
        return {"success": True, "message": f"Cleared history for session {session_id}"}
    return {"success": False, "message": "Session not found"}

@app.post("/api/chat-with-action")
async def chat_with_action(request: ConversationRequest):
    """
    Chat endpoint that automatically executes recommended actions
    
    Performs intelligent pilot assignment, drone matching, or conflict detection
    based on the natural language request.
    """
    try:
        # First, get the AI response
        chat_result = await chat(request)
        
        # Parse the request to determine what action to take
        msg_lower = request.message.lower()
        
        # Extract potential pilot/mission IDs from context if available
        context = request.context or {}
        pilots = context.get("pilots", [])
        missions = context.get("missions", [])
        drones = context.get("drones", [])
        
        action_result = None
        
        # Auto-execute appropriate action
        if chat_result.recommended_action == "rank_pilots" and pilots and missions:
            try:
                pilot_objs = [Pilot(**p) if isinstance(p, dict) else p for p in pilots]
                mission_obj = Mission(**missions[0]) if isinstance(missions[0], dict) else missions[0]
                
                ranking_result = await rank_pilots(pilot_objs, mission_obj)
                action_result = ranking_result
                chat_result.action_details = ranking_result
                
            except Exception as e:
                logger.warning(f"Could not execute ranking: {e}")
        
        elif chat_result.recommended_action == "match_drone" and drones and missions:
            try:
                drone_objs = [Drone(**d) if isinstance(d, dict) else d for d in drones]
                mission_obj = Mission(**missions[0]) if isinstance(missions[0], dict) else missions[0]
                
                matches = []
                for drone in drone_objs:
                    match_result = await match_drone(drone, mission_obj)
                    matches.append(match_result)
                
                action_result = {
                    "matched_drones": matches,
                    "total": len(matches)
                }
                chat_result.action_details = action_result
                
            except Exception as e:
                logger.warning(f"Could not execute drone matching: {e}")
        
        return {
            **chat_result.model_dump(),
            "action_executed": action_result is not None,
            "action_result": action_result
        }
        
    except Exception as e:
        logger.error(f"Chat with action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- LLM Function Definitions (for OpenAI) ----------

def get_available_functions() -> List[Dict]:
    """
    Get function definitions for OpenAI function calling
    
    Returns:
        list: Function definitions in OpenAI format
    """
    return [
        {
            "name": "check_pilot_availability",
            "description": "Check if a pilot is available and suitable for a mission",
            "parameters": {
                "type": "object",
                "properties": {
                    "pilot_id": {"type": "string", "description": "Pilot ID"},
                    "mission_id": {"type": "string", "description": "Mission ID"}
                },
                "required": ["pilot_id", "mission_id"]
            }
        },
        {
            "name": "assign_pilot_to_mission",
            "description": "Assign a pilot to a mission with conflict checking",
            "parameters": {
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "pilot_id": {"type": "string"}
                },
                "required": ["mission_id", "pilot_id"]
            }
        },
        {
            "name": "find_best_pilot",
            "description": "Find the best available pilot for a given mission",
            "parameters": {
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string", "description": "Mission ID"}
                },
                "required": ["mission_id"]
            }
        },
        {
            "name": "detect_mission_conflicts",
            "description": "Detect all conflicts for pilot assignment to a mission",
            "parameters": {
                "type": "object",
                "properties": {
                    "pilot_id": {"type": "string"},
                    "mission_id": {"type": "string"}
                },
                "required": ["pilot_id", "mission_id"]
            }
        },
        {
            "name": "check_drone_compatibility",
            "description": "Check if a drone is compatible with a mission",
            "parameters": {
                "type": "object",
                "properties": {
                    "drone_id": {"type": "string"},
                    "mission_id": {"type": "string"}
                },
                "required": ["drone_id", "mission_id"]
            }
        },
        {
            "name": "urgent_reassign_mission",
            "description": "Perform urgent reassignment for a high-priority mission",
            "parameters": {
                "type": "object",
                "properties": {
                    "mission_id": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["mission_id"]
            }
        }
    ]

@app.get("/api/functions")
async def get_functions():
    """Get available AI function definitions"""
    return {"functions": get_available_functions()}

# ---------- Root Endpoint ----------

@app.get("/")
async def root():
    """
    Skylark Drones - Assignment AI Agent
    Technical Assignment: Drone Operations Coordinator AI Agent
    """
    return {
        "project": "Skylark Drones - Operations Coordinator AI Agent",
        "version": "1.0.0",
        "status": "running",
        "description": (
            "This AI agent automates pilot roster management, assignment coordination, drone inventory, and conflict detection for Skylark Drones. "
            "It integrates with Google Sheets for 2-way sync and provides a conversational interface for all operations."
        ),
        "core_features": [
            "Roster Management: Query pilot availability, cost, assignments, and update status (syncs to Google Sheets)",
            "Assignment Tracking: Match pilots/drones to projects, track assignments, handle reassignments",
            "Drone Inventory: Query/filter drones by capability, weather, status, and update status (syncs to Google Sheets)",
            "Conflict Detection: Double-booking, skill/cert mismatch, equipment/location/budget/weather issues",
            "Urgent Reassignment: Rapidly coordinate critical mission changes",
            "Conversational Interface: Natural language chat for all operations"
        ],
        "integration": {
            "google_sheets": {
                "read": ["Pilots", "Drones", "Missions"],
                "write": ["Pilot status", "Assignments", "Activity log"]
            },
            "api_docs": "/docs"
        },
        "endpoints": {
            "health": "/health",
            "chat": "POST /api/chat",
            "chat_with_action": "POST /api/chat-with-action",
            "chat_history": "GET /api/chat-history/{session_id}",
            "clear_history": "DELETE /api/chat-history/{session_id}",
            "train_model": "POST /api/train-model",
            "feature_importance": "GET /api/feature-importance",
            "match_pilot": "POST /api/match-pilot",
            "rank_pilots": "POST /api/rank-pilots",
            "assign_pilot": "POST /api/assign-pilot",
            "detect_conflicts": "POST /api/detect-conflicts",
            "match_drone": "POST /api/match-drone",
            "rank_drones": "POST /api/rank-drones",
            "urgent_reassign": "POST /api/urgent-reassign",
            "sync_pilots": "GET /api/sync/pilots",
            "sync_missions": "GET /api/sync/missions",
            "sync_drones": "GET /api/sync/drones"
        },
        "sample_queries": [
            "Who is available for a mapping mission in Bangalore next week?",
            "Assign the best pilot to Project PRJ001 and update their status.",
            "Show all drones suitable for rainy weather in Mumbai.",
            "Detect conflicts if Arjun is assigned to PRJ002.",
            "Urgently reassign a pilot for a critical inspection mission.",
            "Update Neha's status to 'On Leave' and sync to Google Sheets."
        ],
        "usage": {
            "conversational": "POST /api/chat with your question. See /docs for full API.",
            "api_docs": "Visit /docs for interactive OpenAPI documentation."
        },
        "assignment": "See README.md and DECISION_LOG.md for architecture, design decisions, and Google Sheets setup."
    }

# ---------- Run Server ----------

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=DEBUG,
        log_level="info"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
