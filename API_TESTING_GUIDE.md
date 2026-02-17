# API Testing & Usage Guide

## Quick Start

Your Skylark Drones AI API is running at **http://127.0.0.1:8000**

### Three Ways to Test

#### 1. **Interactive Swagger UI** (Recommended)
- Visit: http://127.0.0.1:8000/docs
- Click on any endpoint
- Click "Try it out"
- Fill in parameters
- Click "Execute"

#### 2. **ReDoc Documentation**
- Visit: http://127.0.0.1:8000/redoc
- Read full API documentation with examples

#### 3. **Command Line (curl/PowerShell)**
```powershell
# Test health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health"

# Chat with AI agent
$body = @{
    "session_id" = "user123"
    "message" = "Who is available for a mapping mission?"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/chat" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

---

## Core Endpoints

### 1. Health & Status

#### GET /health
Check if system is running
```
Response:
{
  "status": "healthy",
  "timestamp": "2024-02-17T10:30:00",
  "ml_model_loaded": true,
  "sheets_connected": false
}
```

#### GET /
System information and features
```
Response:
{
  "project": "Skylark Drones - Operations Coordinator AI Agent",
  "version": "1.0.0",
  "core_features": [
    "Roster Management",
    "Assignment Tracking",
    "Drone Inventory",
    "Conflict Detection",
    "Urgent Reassignment",
    "Conversational Interface"
  ]
}
```

---

## Conversational AI Endpoints

### 1. POST /api/chat
**Natural language chat interface**

**Request Example:**
```json
{
  "session_id": "user123",
  "message": "Who is the best pilot for a critical mapping mission in Bangalore?"
}
```

**Response:**
```json
{
  "session_id": "user123",
  "ai_response": "I can help you rank pilots for missions...",
  "recommended_action": "rank_pilots",
  "confidence": 0.95
}
```

**Sample Queries:**
- "Who is available for a mapping mission next week?"
- "Can you check if Arjun is suitable for Project PRJ001?"
- "Show me all available pilots with thermal imaging skills"
- "Is there a conflict if we assign Neha to the Mumbai inspection?"
- "Urgently reassign a pilot for the critical inspection mission"
- "Which drones can fly in rainy weather?"

---

### 2. GET /api/chat-history/{session_id}
**Retrieve conversation history**

Example: `GET /api/chat-history/user123`

**Response:**
```json
{
  "session_id": "user123",
  "messages": [
    {
      "role": "user",
      "content": "Who is available?",
      "timestamp": "2024-02-17T10:00:00"
    },
    {
      "role": "assistant",
      "content": "I can help you find...",
      "timestamp": "2024-02-17T10:00:05"
    }
  ],
  "message_count": 2
}
```

---

### 3. DELETE /api/chat-history/{session_id}
**Clear conversation history**

Example: `DELETE /api/chat-history/user123`

**Response:**
```json
{
  "success": true,
  "message": "Cleared history for session user123"
}
```

---

### 4. POST /api/chat-with-action
**Chat + Auto-Execute Recommended Action**

**Request:**
```json
{
  "session_id": "user123",
  "message": "Rank all pilots for the Bangalore mission",
  "context": {
    "pilots": [
      {
        "id": "PLT001",
        "name": "Arjun",
        "skills": "Thermal_Imaging,Photogrammetry",
        "certifications": "PPL",
        "experience_years": 5,
        "location": "Bangalore",
        "cost_per_day": 500,
        "days_available": 30
      }
    ],
    "missions": [
      {
        "id": "PRJ001",
        "name": "Thermal Mapping",
        "required_skills": "Thermal_Imaging",
        "location": "Bangalore"
      }
    ]
  }
}
```

**Response:**
```json
{
  "action_executed": true,
  "action_result": {
    "ranked_pilots": [
      {
        "pilot_id": "PLT001",
        "pilot_name": "Arjun",
        "probability": 0.92
      }
    ]
  }
}
```

---

## ML Model Endpoints

### 1. POST /api/train-model
**Train/retrain the ML model**

**Request:**
```json
{
  "pilots_file": "data/pilot_roster.csv",
  "missions_file": "data/missions.csv"
}
```

**Response:**
```json
{
  "success": true,
  "model_path": "models/pilot_match_model.pkl",
  "metrics": {
    "accuracy": 0.85,
    "precision": 0.82,
    "recall": 0.78,
    "roc_auc": 0.87
  },
  "feature_importance": {
    "skill_match": 0.35,
    "cost_fit": 0.33,
    "location_match": 0.28
  }
}
```

---

### 2. GET /api/feature-importance
**Get feature importance from trained model**

**Response:**
```json
{
  "feature_importance": {
    "skill_match": 0.3492,
    "cost_fit": 0.3333,
    "location_match": 0.2794,
    "cert_match": 0.0381
  }
}
```

---

## Matching & Assignment Endpoints

### 1. POST /api/match-pilot
**Get suitability score for a pilot-mission pair**

**Request:**
```json
{
  "pilot": {
    "id": "PLT001",
    "name": "Arjun",
    "skills": "Thermal_Imaging,Photogrammetry",
    "certifications": "PPL,ATPL",
    "experience_years": 5,
    "location": "Bangalore",
    "cost_per_day": 500,
    "days_available": 30
  },
  "mission": {
    "id": "PRJ001",
    "required_skills": "Thermal_Imaging",
    "required_cert": "PPL",
    "duration_days": 5,
    "budget": 3000,
    "location": "Bangalore"
  }
}
```

**Response:**
```json
{
  "pilot_id": "PLT001",
  "pilot_name": "Arjun",
  "suitable": true,
  "probability": 0.92,
  "confidence": "HIGH"
}
```

---

### 2. POST /api/rank-pilots
**Rank all pilots by suitability for a mission**

**Request:**
```json
{
  "pilots": [
    { "id": "PLT001", "name": "Arjun", ... },
    { "id": "PLT002", "name": "Neha", ... }
  ],
  "mission": { "id": "PRJ001", ... }
}
```

**Response:**
```json
{
  "ranked_pilots": [
    {
      "pilot_id": "PLT001",
      "pilot_name": "Arjun",
      "probability": 0.92,
      "is_viable": true
    },
    {
      "pilot_id": "PLT002",
      "pilot_name": "Neha",
      "probability": 0.85,
      "is_viable": true
    }
  ]
}
```

---

### 3. POST /api/assign-pilot
**Assign a pilot to a mission with conflict checking**

**Request:**
```json
{
  "assignment_req": {
    "mission_id": "PRJ001",
    "pilot_id": "PLT001",
    "auto_select": false
  },
  "mission": { ... },
  "pilots": [ ... ]
}
```

**Response:**
```json
{
  "success": true,
  "assignment_id": "ASN-PRJ001-PLT001",
  "pilot_name": "Arjun",
  "confidence": 0.92,
  "conflicts": [],
  "message": "✅ Assigned Arjun to mission PRJ001"
}
```

---

## Conflict Detection Endpoints

### 1. POST /api/detect-conflicts
**Detect all potential conflicts**

**Request:**
```json
{
  "pilot": { "id": "PLT001", ... },
  "mission": { "id": "PRJ001", ... }
}
```

**Response:**
```json
{
  "has_conflicts": false,
  "conflict_count": 0,
  "critical_conflicts": [],
  "warnings": [],
  "summary": "No conflicts detected"
}
```

**Sample Conflicts Detected:**
- 🔴 Double-booking (HIGH)
- 🔴 Budget overrun (HIGH)
- 🟡 Location mismatch (MEDIUM)
- 🟡 Missing certification (HIGH)

---

## Drone Endpoints

### 1. POST /api/match-drone
**Check drone-mission compatibility**

**Request:**
```json
{
  "drone": {
    "id": "DJI001",
    "name": "DJI M300",
    "weather_rating": "IP54",
    "flight_range_km": 50,
    "payload_capacity_kg": 6
  },
  "mission": {
    "id": "PRJ001",
    "weather": "Rainy",
    "required_range_km": 40,
    "required_payload_kg": 5
  }
}
```

**Response:**
```json
{
  "drone_id": "DJI001",
  "compatible": true,
  "reason": "Drone meets all mission requirements",
  "warnings": []
}
```

---

### 2. POST /api/rank-drones
**Rank drones by suitability for mission**

**Request:**
```json
{
  "drones": [ ... ],
  "mission": { ... }
}
```

---

## Urgent Reassignment Endpoint

### 1. POST /api/urgent-reassign
**Handle urgent mission reassignment**

**Request:**
```json
{
  "mission": {
    "id": "PRJ001",
    "priority": "CRITICAL",
    ...
  },
  "current_pilot": {
    "id": "PLT001",
    "name": "Arjun",
    ...
  },
  "pilots": [ ... ]
}
```

**Response:**
```json
{
  "success": true,
  "reassignment": {...},
  "new_pilot": {
    "id": "PLT002",
    "name": "Neha",
    "confidence": 0.88
  },
  "candidates": [
    { "id": "PLT002", "name": "Neha", "score": 0.88 },
    { "id": "PLT003", "name": "Rohit", "score": 0.82 }
  ]
}
```

---

## Data Sync Endpoints

### 1. GET /api/sync/pilots
**Sync pilots from Google Sheets**
*(Requires Google Sheets setup)*

### 2. GET /api/sync/missions
**Sync missions from Google Sheets**
*(Requires Google Sheets setup)*

### 3. GET /api/sync/drones
**Sync drones from Google Sheets**
*(Requires Google Sheets setup)*

---

## Testing Recommendations

### Test Order
1. ✅ Health check (`/health`)
2. ✅ Chat endpoint (`POST /api/chat`)
3. ✅ ML features (`GET /api/feature-importance`)
4. ✅ If you have CSVs: Train model (`POST /api/train-model`)
5. ✅ Test matching endpoints with sample data
6. ✅ Test conflict detection
7. ✅ Set up Google Sheets (see GOOGLE_SHEETS_SETUP.md)

### Sample Test Script
Run included test: `python test_system.py`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Missing required field: mission"
}
```

### 404 Not Found
```json
{
  "detail": "Pilot not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Model not loaded. Train it first."
}
```

---

## Performance Notes

| Operation | Time |
|-----------|------|
| Single pilot match | ~10ms |
| Rank 10 pilots | ~150ms |
| Conflict detection | ~20ms |
| Chat response | ~500ms |
| Google Sheets sync | ~1-2s |

---

## Support

- Check README.md for architecture
- See DECISION_LOG.md for design decisions
- Review GOOGLE_SHEETS_SETUP.md for integration
- View /docs for interactive API explorer

