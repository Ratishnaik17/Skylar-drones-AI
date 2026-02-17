# Quick Start - Skylark Drones AI Operations Brain

## ⚡ 30-Second Startup

```powershell
cd C:\Users\naikr\OneDrive\Desktop\Skylar_ml_model
python start_server.py
```

That's it! Your API will be running at **http://127.0.0.1:8000**

---

## 🎯 What You Get (Ready to Use)

✅ **ML-Based Pilot Matching** - Trained model ready for predictions  
✅ **Conversational AI** - Chat interface for natural language queries  
✅ **Conflict Detection** - Automatic conflict identification  
✅ **Drone Matching** - Rule-based drone-mission compatibility  
✅ **Urgent Reassignment** - Critical mission handling  
✅ **Interactive Documentation** - Try endpoints at /docs  

---

## 🔍 Access Points (After Starting Server)

| Resource | URL |
|----------|-----|
| **API Root** | http://127.0.0.1:8000 |
| **Interactive Docs** | http://127.0.0.1:8000/docs |
| **Alternative Docs** | http://127.0.0.1:8000/redoc |
| **Health Check** | http://127.0.0.1:8000/health |

---

## 📊 Sample Data Included

Your system comes pre-loaded with:

| Resource | Count | File |
|----------|-------|------|
| **Pilots** | 4 | data/pilot_roster.csv |
| **Missions** | 3 | data/missions.csv |
| **Drones** | 4 | data/drones.csv |
| **ML Model** | Trained | models/pilot_match_model.pkl |

### Sample Pilots
- **Arjun** - Thermal Imaging, Photogrammetry (Bangalore, ₹500/day)
- **Neha** - Aerial Photography, Mapping (Delhi, ₹450/day)
- **Rohit** - Inspection, Survey (Mumbai, ₹550/day)
- **Sneha** - LiDAR, Environmental (Bangalore, ₹600/day)

### Sample Missions
- **PRJ001** - Thermal Mapping (Bangalore, HIGH priority)
- **PRJ002** - Aerial Survey (Delhi, MEDIUM priority)
- **PRJ003** - Infrastructure Inspection (Mumbai, CRITICAL priority)

---

## 🧪 Test the System (After Starting Server)

### Option 1: Run Test Script
```powershell
python test_system.py
```

Expected output:
```
✅ System is fully operational!
```

### Option 2: Use Interactive Swagger UI
1. Open http://127.0.0.1:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

### Option 3: Test via PowerShell
```powershell
# Health check
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" | ConvertTo-Json

# Chat with AI
$body = @{
    "session_id" = "test_user"
    "message" = "Who is available for a thermal imaging mission?"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/chat" `
  -Method POST `
  -Body $body `
  -ContentType "application/json" | ConvertTo-Json
```

---

## 💬 Try These Conversational Queries

Send these to `POST /api/chat` endpoint:

1. **Pilot Availability**
   ```
   "Who is available for a critical mapping mission in Bangalore?"
   ```

2. **Drone Compatibility**
   ```
   "Can you find a drone suitable for thermal imaging in rainy weather?"
   ```

3. **Conflict Detection**
   ```
   "Will there be conflicts if we assign Arjun to the Mumbai inspection?"
   ```

4. **Assignment Help**
   ```
   "Rank all available pilots for Project PRJ001"
   ```

5. **Urgent Situations**
   ```
   "I need urgent reassignment for the critical inspection mission"
   ```

---

## 🔧 API Endpoints (Quick Reference)

### Core
- `GET /health` - System health
- `GET /` - Project info
- `GET /docs` - Interactive API docs

### Chat (Conversational)
- `POST /api/chat` - Chat with AI
- `GET /api/chat-history/{session_id}` - View conversation
- `DELETE /api/chat-history/{session_id}` - Clear conversation

### Pilot Matching
- `POST /api/match-pilot` - Score single pilot
- `POST /api/rank-pilots` - Rank all pilots
- `POST /api/assign-pilot` - Assign pilot with conflict check

### Conflict Detection
- `POST /api/detect-conflicts` - Find all issues for assignment

### Drone Matching
- `POST /api/match-drone` - Check drone compatibility
- `POST /api/rank-drones` - Rank drones for mission

### Other
- `POST /api/urgent-reassign` - Emergency reassignment
- `GET /api/feature-importance` - ML model insights
- `POST /api/train-model` - Retrain model with new data

---

## 📝 Example API Calls

### Example 1: Chat with AI Agent
```bash
POST http://127.0.0.1:8000/api/chat

{
  "session_id": "user_123",
  "message": "Who is the best pilot for thermal imaging in Bangalore?"
}
```

**Response:**
```json
{
  "session_id": "user_123",
  "ai_response": "I can help you find the best pilot for thermal imaging in Bangalore...",
  "recommended_action": "rank_pilots",
  "confidence": 0.95
}
```

### Example 2: Rank Pilots for Mission
```bash
POST http://127.0.0.1:8000/api/rank-pilots

{
  "pilots": [
    {
      "id": "PLT001",
      "name": "Arjun",
      "skills": "Thermal_Imaging,Photogrammetry",
      "certifications": "PPL,ATPL",
      "experience_years": 5,
      "location": "Bangalore",
      "cost_per_day": 500,
      "days_available": 30
    }
  ],
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
  "ranked_pilots": [
    {
      "pilot_id": "PLT001",
      "pilot_name": "Arjun",
      "probability": 0.92,
      "is_viable": true
    }
  ]
}
```

### Example 3: Detect Conflicts
```bash
POST http://127.0.0.1:8000/api/detect-conflicts

{
  "pilot": {
    "id": "PLT001",
    "name": "Arjun",
    "location": "Bangalore"
  },
  "mission": {
    "id": "PRJ001",
    "location": "Mumbai",
    "budget": 3000,
    "duration_days": 5
  }
}
```

**Response:**
```json
{
  "has_conflicts": false,
  "conflict_count": 0,
  "critical_conflicts": [],
  "summary": "No conflicts detected"
}
```

---

## 🛠️ Troubleshooting

### Server won't start
```powershell
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill existing process if needed
taskkill /PID <PID> /F

# Then try again
python start_server.py
```

### Module not found errors
```powershell
# Make sure virtual environment is activated
.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Model not loaded error
```powershell
# Train the model
python -m src.train_model data/pilot_roster.csv data/missions.csv

# Then start server
python start_server.py
```

### Port 8000 permission error
Try a different port:
```powershell
C:/Users/naikr/OneDrive/Desktop/Skylar_ml_model/.venv/Scripts/python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 3000
```

Then access at http://127.0.0.1:3000

---

## 🚀 Next Steps

### For Local Testing
1. ✅ Start server: `python start_server.py`
2. ✅ Test endpoints: Visit http://127.0.0.1:8000/docs
3. ✅ Try chat: Use `/api/chat` endpoint
4. ✅ Run tests: `python test_system.py`

### For Production Deployment
See **DEPLOYMENT_GUIDE.md** for:
- Railway.app deployment
- Docker containerization
- Environment variable setup
- Multi-instance scaling

### For Google Sheets Integration
See **GOOGLE_SHEETS_SETUP.md** for:
- Google Cloud setup
- Sheet structure
- 2-way sync configuration

---

## 📖 Full Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | Architecture and system overview |
| **DECISION_LOG.md** | Design decisions and tradeoffs |
| **API_TESTING_GUIDE.md** | Detailed endpoint examples |
| **GOOGLE_SHEETS_SETUP.md** | Google Sheets integration |
| **DEPLOYMENT_GUIDE.md** | Production deployment |
| **QUICK_START.md** | This file - quick reference |

---

## ✅ System Status

**Model**: ✅ Trained and ready  
**API**: ✅ All endpoints operational  
**Conversational**: ✅ AI agent ready  
**Dependencies**: ✅ All installed  
**Sample Data**: ✅ Included  

**Ready to Use!** 🎉

---

## 💡 Pro Tips

1. **Keep conversation history** - The system maintains chat history per session
2. **Use session IDs** - Different users can have different session_ids to maintain separate conversations
3. **Trust the conflicts** - The conflict detector is strict for safety
4. **Batch operations** - Send multiple pilots/drones for ranking at once
5. **Check feature importance** - See which ML features matter most

---

## 📞 Support

- **API Issues**: Check /health endpoint
- **Model Issues**: Retrain with `python -m src.train_model data/pilot_roster.csv data/missions.csv`
- **Data Issues**: Verify CSV format matches sample files
- **Deployment**: Follow DEPLOYMENT_GUIDE.md

---

**Ready to deploy?** Check DEPLOYMENT_GUIDE.md  
**Want more features?** See DECISION_LOG.md Phase 2 roadmap  

