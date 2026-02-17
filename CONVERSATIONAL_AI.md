# 🤖 Conversational AI - Drone Operations Brain

## Overview

Your AI Operations Brain is now fully conversational! The system can now:
- **Understand natural language** queries about pilots, missions, and drones
- **Provide intelligent recommendations** for assignments and matching
- **Maintain conversation history** across a session for context
- **Automatically execute actions** based on user intent

## New Conversational Endpoints

### 1. **POST /api/chat** - Chat with AI
Natural language conversation interface for the AI operations brain.

**Request:**
```json
{
  "session_id": "user123",
  "message": "Which pilot is best for the Bangalore mapping mission?",
  "context": {}
}
```

**Response:**
```json
{
  "session_id": "user123",
  "ai_response": "I can help you rank pilots for missions. Based on the drone company's operations, I would evaluate pilots using...",
  "recommended_action": "rank_pilots",
  "confidence": 0.85
}
```

**Supported Queries:**
- "Rank pilots for the mapping mission"
- "Which drone should we use for thermal imaging?"
- "Can you detect conflicts with this assignment?"
- "We need urgent reassignment for a critical mission"
- "Help me organize drone assignments"

### 2. **POST /api/chat-with-action** - Chat with Automatic Actions
Chat endpoint that automatically executes recommended actions.

**Request:**
```json
{
  "session_id": "user123",
  "message": "Rank all pilots for the Bangalore mapping mission",
  "context": {
    "pilots": [
      {"id": "P001", "name": "Arjun", "skills": "Mapping, Survey", ...}
    ],
    "missions": [
      {"id": "PRJ001", "name": "Mapping Mission", ...}
    ]
  }
}
```

**Response:**
```json
{
  "session_id": "user123",
  "ai_response": "I can help you rank pilots...",
  "action_executed": true,
  "action_result": {
    "ranked_pilots": [
      {"pilot_id": "P001", "pilot_name": "Arjun", "probability": 0.18, "suitable": false},
      {"pilot_id": "P002", "pilot_name": "Neha", "probability": 0.09, "suitable": false}
    ]
  }
}
```

### 3. **GET /api/chat-history/{session_id}** - Get Conversation History
Retrieve the complete conversation history for a session.

**Response:**
```json
{
  "session_id": "user123",
  "message_count": 4,
  "messages": [
    {
      "role": "user",
      "content": "Which pilot is best for the Bangalore mapping mission?",
      "timestamp": "2026-02-17T10:30:00"
    },
    {
      "role": "assistant",
      "content": "I can help you rank pilots for missions...",
      "timestamp": "2026-02-17T10:30:05"
    }
  ]
}
```

### 4. **DELETE /api/chat-history/{session_id}** - Clear Conversation
Clear the conversation history for a session.

**Response:**
```json
{
  "success": true,
  "message": "Cleared history for session user123"
}
```

## Conversation Intelligence

The AI assistant understands and responds to queries about:

### Pilot Ranking & Assignment
**Keywords:** "rank", "assign", "pilot", "best", "allocate"

Provides guidance on:
- Skills evaluation and matching
- Certification requirements
- Cost efficiency analysis
- Experience assessment
- Availability checking

### Drone Matching
**Keywords:** "drone", "match", "compatible", "aircraft", "equipment"

Evaluates:
- Weather compatibility (IP ratings)
- Flight range requirements
- Payload capacity
- Battery endurance
- Drone availability

### Conflict Detection
**Keywords:** "conflict", "issue", "problem", "check", "validate"

Identifies:
- Location conflicts (geographic mismatches)
- Schedule conflicts (double-booking)
- Budget conflicts (cost overruns)
- Certification gaps
- Availability issues

### Urgent Reassignment
**Keywords:** "urgent", "reassign", "critical", "emergency"

Handles:
- Priority assessment
- Quick alternatives
- Conflict resolution
- Risk scoring
- Escalation protocols

## Session Management

Each conversation is tied to a **session_id**:
- Sessions maintain conversation history
- Multiple users can have independent sessions
- Clear history when done with a session
- Sessions persist until explicitly cleared

### Example Session Flow:
```
1. User initiates chat with session_id "user123"
2. Multiple back-and-forth messages in same session
3. AI maintains context across messages
4. Get history to review conversation
5. Clear history when session ends
```

## Smart Action Recommendations

The AI system automatically recommends actions based on intent:

| User Intent | Recommended Action | Confidence |
|---|---|---|
| "Rank pilots for..." | `rank_pilots` | 85% |
| "Match drone for..." | `match_drone` | 85% |
| "Detect conflicts..." | `detect_conflicts` | 90% |
| "Urgent reassignment..." | `urgent_reassign` | 95% |

## Integration with ML Pipeline

The conversational AI integrates seamlessly with existing ML features:
- Rankings use the trained RandomForest model
- Conflict detection uses the ConflictDetector engine
- Drone matching uses the DroneMatcher rules
- Urgent reassignment uses the ReassignmentEngine

## Example Usage

### Simple Chat Example:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "manager1",
    "message": "Can you help me find the best pilot for a critical mapping mission?"
  }'
```

### Chat with Action Example:
```bash
curl -X POST http://localhost:8000/api/chat-with-action \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "manager1",
    "message": "Rank all available pilots for the Bangalore thermal imaging mission",
    "context": {
      "pilots": [...],
      "missions": [...]
    }
  }'
```

### View Conversation History:
```bash
curl http://localhost:8000/api/chat-history/manager1
```

## Features Enabled

✅ **Natural Language Processing**: Understand user intent from queries  
✅ **Conversational Context**: Maintain context across messages  
✅ **Session Management**: Separate conversations for different users  
✅ **Smart Recommendations**: Auto-recommend actions based on queries  
✅ **Automatic Action Execution**: Execute suggested actions on demand  
✅ **Persistent History**: Review past conversations  
✅ **ML Integration**: Leverage trained models for recommendations  

## API Documentation

Full API documentation available at: **http://localhost:8000/docs**

## Status

🟢 **Conversational AI**: ACTIVE
🟢 **Chat Endpoints**: OPERATIONAL  
🟢 **Session Management**: OPERATIONAL  
🟢 **ML Integration**: OPERATIONAL  
🟢 **History Tracking**: OPERATIONAL  

---

**Last Updated:** February 17, 2026  
**API Version:** 1.0.0  
**Mode:** Conversational AI + ML-Powered Operations
