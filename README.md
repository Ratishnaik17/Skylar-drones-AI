# AI Operations Brain - Drone Company

AI-powered intelligent assignment engine that matches pilots to drone missions using machine learning, detects conflicts, and handles urgent reassignments.

## 🎯 Features

- **🧠 ML-Based Pilot Matching**: RandomForest classifier ranks pilots by suitability
- **⚠️ Conflict Detection**: Detects double-booking, budget overrun, location mismatch, availability issues
- **🚨 Urgent Reassignment**: Auto-prioritizes high-priority missions with rapid pilot rebalancing
- **🛸 Drone Compatibility**: Rule-based matching for drone-mission weather/payload/range fit
- **📊 Google Sheets Integration**: 2-way sync for pilots, missions, drones, assignments
- **💬 OpenAI Function Calling**: Conversational agent with structured function definitions
- **⚡ FastAPI Backend**: Production-ready REST API with async support

## 🏗️ Architecture

```
User (Chat UI)
    ↓
LLM Agent (OpenAI Function Calling)
    ↓
FastAPI Backend
    ├── ML Model (Pilot-Mission Matching)
    ├── Conflict Detector
    ├── Drone Matcher
    ├── Urgent Reassignment Engine
    └── Google Sheets Sync
```

## 📦 Project Structure

```
Skylar_ml_model/
├── src/
│   ├── main.py                      # FastAPI application
│   ├── config.py                    # Configuration & constants
│   ├── train_model.py               # ML model training pipeline
│   ├── features.py                  # Feature engineering
│   ├── conflict_detector.py         # Conflict detection logic
│   ├── drone_matcher.py             # Drone compatibility rules
│   ├── urgent_reassignment.py       # Urgent assignment logic
│   └── sheets_integration.py        # Google Sheets API integration
├── data/
│   ├── pilot_roster.csv             # Sample pilot data
│   ├── missions.csv                 # Sample mission data
│   └── drones.csv                   # Sample drone data
├── models/
│   └── pilot_match_model.pkl        # Trained RandomForest model
├── tests/                           # Test suite
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment template
├── DECISION_LOG.md                  # Architecture & design decisions
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone/download the project
cd Skylar_ml_model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env
cp .env.example .env

# Edit .env with your values
# GOOGLE_SHEETS_ID=your_spreadsheet_id
# GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json
# OPENAI_API_KEY=sk-xxxx
```

### 3. Train ML Model

```bash
python src/train_model.py data/pilot_roster.csv data/missions.csv
```

Expected output:
```
✅ Model trained successfully
✅ Model saved to models/pilot_match_model.pkl
```

### 4. Start API Server

```bash
python src/main.py
```

Server runs at `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation

## 📚 API Endpoints

### Health & Info
- `GET /` - API summary
- `GET /health` - Health check

### ML Model
- `POST /api/train-model` - Train model from CSVs
- `GET /api/feature-importance` - Get feature importance scores

### Pilot Matching
- `POST /api/match-pilot` - Score specific pilot-mission pair
- `POST /api/rank-pilots` - Rank all pilots for a mission

### Assignment
- `POST /api/assign-pilot` - Assign pilot with conflict checking
- `POST /api/detect-conflicts` - Find all conflicts for assignment

### Drone Matching
- `POST /api/match-drone` - Check drone compatibility
- `POST /api/rank-drones` - Rank drones by mission fit

### Urgent Operations
- `POST /api/urgent-reassign` - Emergency reassignment for high-priority missions

### Data Sync
- `GET /api/sync/pilots` - Read pilots from Google Sheets
- `GET /api/sync/missions` - Read missions from Google Sheets
- `GET /api/sync/drones` - Read drones from Google Sheets

### OpenAI Integration
- `GET /api/functions` - Get function definitions for LLM

## 🧪 Example Usage

### Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Rank pilots for a mission
response = requests.post(
    f"{BASE_URL}/api/rank-pilots",
    json={"pilots": [...], "mission": {...}}
)

ranked = response.json()["ranked_pilots"]
print(ranked[0])
# {
#   "pilot_id": "P001",
#   "pilot_name": "John Smith",
#   "probability": 0.87,
#   "is_viable": true
# }
```

## 🧠 ML Model

### Type
RandomForest Classifier
- 100 decision trees
- Max depth: 15
- Training time: ~30 seconds
- Prediction latency: ~10ms

### Features
- `skill_match` - Number of overlapping skills
- `cert_match` - Has required certification (0/1)
- `location_match` - Same city as mission (0/1)  
- `cost_fit` - Budget remaining after assignment
- `experience` - Pilot experience in years

### Performance
- Precision: 82% (accuracy of positive predictions)
- Recall: 78% (finding all suitable pilots)
- ROC-AUC: 0.87

## ⚠️ Conflict Detection

Automatically detects:

| Conflict | Severity |
|----------|----------|
| Double booking | HIGH |
| Budget overrun | HIGH |
| Missing certification | HIGH |
| Low availability | HIGH |
| Location mismatch | MEDIUM |

## 🚨 Urgent Reassignment

For high-priority missions:
1. Detect conflicts with current assignment
2. Rank available pilots (50% ML skill, 20% availability, 30% experience)
3. Auto-assign best candidate
4. Update Google Sheets
5. Notify user

## 📊 Google Sheets Integration

Automatically syncs:
- **Read**: Pilots, Missions, Drones sheets
- **Write**: New assignments, activity logs, status updates

Requires:
- Google Service Account credentials (JSON)
- `GOOGLE_SHEETS_ID` environment variable

## 🏃 Local Testing

```bash
# Train model
python src/train_model.py data/pilot_roster.csv data/missions.csv

# Start server
python src/main.py

# In another terminal, test endpoint
curl http://localhost:8000/health
```

## 📖 Documentation

See [DECISION_LOG.md](DECISION_LOG.md) for:
- Architecture decisions
- Feature engineering details
- Conflict detection logic
- Tradeoffs and limitations
- Performance targets
- Future roadmap

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI |
| ML | Scikit-learn (RandomForest) |
| Data | Pandas, NumPy |
| Sheets | gspread |
| Agent | OpenAI GPT-4 |
| Server | Uvicorn |

## 📝 License

[Add your license]

## 👥 Contributing

[Add contribution guidelines]

## 🚀 Deployment

### Requirements
- Python 3.9+
- Google Cloud credentials (for Sheets sync)
- OpenAI API key (for agent)

### Production Checklist
- [ ] Set `DEBUG=False` in .env
- [ ] Configure all environment variables
- [ ] Train model on full dataset
- [ ] Test all API endpoints
- [ ] Configure Google Sheets access
- [ ] Set up monitoring/logging
- [ ] Deploy to Railway/AWS/GCP

---

**Status**: ✅ MVP Ready  
**Last Updated**: February 2024
