# AI Operations Brain - Complete Architecture

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                            │
│              (Chat UI / Web Dashboard / Mobile App)               │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                   OPENAI FUNCTION CALLING                         │
│    (Conversational Layer with Structured Function Definitions)   │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                              │
│                  (REST API with Async Support)                    │
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │               ROUTE HANDLERS (Endpoints)                   │  │
│  │                                                             │  │
│  │  /api/rank-pilots          → RankPilotsHandler             │  │
│  │  /api/assign-pilot         → AssignmentHandler             │  │
│  │  /api/detect-conflicts     → ConflictDetectionHandler      │  │
│  │  /api/match-drone          → DroneMatchingHandler          │  │
│  │  /api/urgent-reassign      → UrgentReassignmentHandler     │  │
│  │  /api/train-model          → ModelTrainingHandler          │  │
│  │  /api/sync/*               → SyncHandler                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                         │                                          │
│                         ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              BUSINESS LOGIC LAYER                          │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │    ML Engine (train_model.py)                        │  │  │
│  │  │  • Feature engineering                               │  │  │
│  │  │  • Model training (RandomForest)                     │  │  │
│  │  │  • Prediction & ranking                              │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │    Conflict Detection (conflict_detector.py)         │  │  │
│  │  │  • Double booking checks                             │  │  │
│  │  │  • Budget overrun detection                          │  │  │
│  │  │  • Availability verification                         │  │  │
│  │  │  • Location matching                                 │  │  │
│  │  │  • Certification validation                          │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │    Drone Matching (drone_matcher.py)                 │  │  │
│  │  │  • Weather compatibility                             │  │  │
│  │  │  • Payload capacity checking                         │  │  │
│  │  │  • Range verification                                │  │  │
│  │  │  • Battery endurance calculation                     │  │  │
│  │  │  • Drone ranking & scoring                           │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │    Urgent Reassignment (urgent_reassignment.py)      │  │  │
│  │  │  • High-priority detection                           │  │  │
│  │  │  • Rapid pilot candidate ranking                     │  │  │
│  │  │  • Reassignment chain execution                      │  │  │
│  │  │  • Notification generation                           │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  │                                                             │  │
│  │  ┌──────────────────────────────────────────────────────┐  │  │
│  │  │    Data Sync (sheets_integration.py)                 │  │  │
│  │  │  • Google Sheets authentication                      │  │  │
│  │  │  • Read operations (pilots, missions, drones)        │  │  │
│  │  │  • Write operations (assignments, updates)           │  │  │
│  │  │  • Activity logging                                  │  │  │
│  │  └──────────────────────────────────────────────────────┘  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                         │                                          │
│                         ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              DATA & PERSISTENCE LAYER                      │  │
│  │                                                             │  │
│  │  ┌──────────────────┐     ┌──────────────────────────┐   │  │
│  │  │  ML Model File   │     │   Google Sheets API      │   │  │
│  │  │ (pilot_match_    │     │  (2-way sync)            │   │  │
│  │  │  model.pkl)      │     │                          │   │  │
│  │  └──────────────────┘     │  • Pilots spreadsheet    │   │  │
│  │                           │  • Missions spreadsheet  │   │  │
│  │                           │  • Drones spreadsheet    │   │  │
│  │                           │  • Assignments tracking  │   │  │
│  │                           │  • Activity log          │   │  │
│  │                           └──────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. ML Engine (train_model.py)

**Responsibility**: Pilot-mission suitability prediction

**Key Functions**:
- Feature engineering from CSV data
- RandomForest model training
- Model persistence (pickling)
- Single prediction & batch ranking

**Algorithm**:
```
Pilot-Mission Matching
Input: Pilot features + Mission requirements
Process: RandomForest binary classification
Output: Probability (0-1) of suitability
```

**Features Used**:
- `skill_match` - Overlapping skill count
- `cert_match` - Has required certification
- `location_match` - Same city match
- `cost_fit` - Budget remaining
- `experience` - Years of experience

### 2. Conflict Detection Engine (conflict_detector.py)

**Responsibility**: Identify assignment obstacles

**Conflict Types**:

| Type | Check | Severity | Example |
|------|-------|----------|---------|
| Double Booking | Date overlap | HIGH | Already assigned March 1-3 |
| Budget Overrun | Cost > Budget | HIGH | Mission pays $1500, pilot costs $600/day |
| Missing Cert | Required cert not found | HIGH | Needs "Advanced" certification |
| Low Availability | Days needed > Days available | HIGH | 5-day mission, pilot free 2 days |
| Location Mismatch | Pilot ≠ Mission location | MEDIUM | Pilot NYC, Mission LA |

**Return Format**:
```python
{
    "has_conflicts": bool,
    "critical_conflicts": [{type, message, severity}],
    "warnings": [{type, message, severity}],
    "summary": "Combined summary string"
}
```

### 3. Drone Matching Engine (drone_matcher.py)

**Responsibility**: Drone-mission compatibility verification

**Checks Performed**:
1. **Weather Rating** - IP43/IP54/IP65/IP67 compatibility
2. **Flight Range** - Mission range ≤ Drone range
3. **Payload Capacity** - Mission payload ≤ Drone capacity
4. **Battery Endurance** - Mission time + 20% buffer ≤ Battery
5. **Drone Availability** - Status = "available"

**Output**:
```python
{
    "compatible": bool,
    "reason": "Why compatible/incompatible",
    "warnings": ["High utilization: 85%", ...]
}
```

### 4. Urgent Reassignment Engine (urgent_reassignment.py)

**Responsibility**: Rapid pilot rebalancing for critical missions

**Trigger Conditions**:
- Mission priority = HIGH/CRITICAL
- Conflicts detected with current pilot
- Current confidence < 70% (for high priority)

**Ranking Formula**:
```
Score = (ML_probability × 0.5) 
      + (Availability_score × 0.2)
      + (Experience_bonus × 0.3)
```

**Output**:
- Ranked candidates with scores
- Reassignment action details
- Notification message
- Activity log entry

### 5. Google Sheets Integration (sheets_integration.py)

**Responsibility**: 2-way data synchronization

**Operations**:
- **Read**: Update pilots, missions, drones on startup
- **Write**: Create/update assignments
- **Sync**: Update pilot availability
- **Log**: Record all activities

**Sheet Requirements**:
```
Pilots: [ID, Name, Skills, Certs, Years, Location, Cost, Days, Status]
Missions: [ID, Name, ReqSkills, Cert, Location, Days, Budget, Priority, ...]
Drones: [ID, Name, Location, Status, Weather, Range, Payload, Battery]
Assignments: [ID, MissionID, Pilot, Status, CreatedAt, Notes]
ActivityLog: [Timestamp, Action, Pilot, Mission, Status, Details]
```

### 6. FastAPI Backend (main.py)

**Responsibility**: HTTP API and request routing

**Endpoint Categories**:

1. **Health & Info**
   - `GET /` - API summary
   - `GET /health` - Status check

2. **ML Operations**
   - `POST /api/train-model` - Train from CSVs
   - `GET /api/feature-importance` - Feature scores

3. **Matching**
   - `POST /api/match-pilot` - Single pair score
   - `POST /api/rank-pilots` - Rank all pilots

4. **Assignment**
   - `POST /api/assign-pilot` - Assign with validations
   - `POST /api/detect-conflicts` - Find issues

5. **Drone Matching**
   - `POST /api/match-drone` - Compatibility check
   - `POST /api/rank-drones` - Rank drones

6. **Urgent Operations**
   - `POST /api/urgent-reassign` - Emergency assignments

7. **Data Sync**
   - `GET /api/sync/pilots` - Read from Sheets
   - `GET /api/sync/missions` - Read from Sheets
   - `GET /api/sync/drones` - Read from Sheets

8. **LLM Integration**
   - `GET /api/functions` - Function definitions for OpenAI

## Data Flow Examples

### Example 1: Rank Pilots for Mission

```
1. User Query
   "Find best pilot for Mission M001"
   
2. API Request
   POST /api/rank-pilots
   {
     "mission": {...},
     "pilots": [...]
   }
   
3. Feature Engineering
   For each pilot:
     - Extract features
     - Engineer values
     - Create feature vector
   
4. ML Prediction
   For each feature vector:
     - RandomForest.predict_proba()
     - Get probability score
   
5. Conflict Detection
   For each pilot:
     - Check double booking
     - Check budget
     - Check certs
     - Check location
   
6. Ranking
   Sort by (probability × viable)
   
7. Response
   Return ranked list with:
     - Probability
     - Conflicts
     - Viability
```

### Example 2: Urgent Reassignment

```
1. High-Priority Mission Detected
   Mission status = CRITICAL
   Current pilot has conflicts
   
2. Trigger Reassignment Engine
   - Detect: Does current pilot have conflicts?
   - Rank: Get all available pilots
   - Score: ML prob + availability + experience
   
3. Candidate Validation
   For top candidate:
     - Check all conflicts
     - Validate no critical issues
   
4. Execute Reassignment
   - Create cancellation action for old pilot
   - Create assignment action for new pilot
   
5. Data Sync
   - Update Google Sheet assignments
   - Log activity
   - Update pilot status
   
6. Notify User
   - Alert about change
   - Provide reassignment details
```

### Example 3: LLM Function Calling

```
1. User Query (via Chat)
   "Assign John to Mission M001"
   
2. LLM Processing
   - Parse function definitions from /api/functions
   - Determine: Use "assign_pilot_to_mission"
   - Extract arguments: pilot_id=P001, mission_id=M001
   
3. Function Call
   POST /api/assign-pilot
   {
     "mission": {...},
     "pilot_id": "P001",
     "auto_select": false
   }
   
4. API Processing
   - Extract pilot P001
   - Check conflicts
   - Verify suitability
   - Create assignment
   
5. Sync & Response
   - Update Google Sheets
   - Return assignment details
   
6. LLM Response
   "✅ Assigned John Smith to Mission M001.
    Confidence: 87%. No conflicts detected."
```

## Performance Characteristics

| Operation | Latency | Throughput | Bottleneck |
|-----------|---------|-----------|-----------|
| Single Prediction | ~10ms | 100/sec | ML model |
| Rank 10 Pilots | ~150ms | 6/sec | ML predictions |
| Conflict Detection | ~20ms | 50/sec | DB lookups |
| Drone Matching | ~30ms | 33/sec | Rule evaluation |
| Sheets Read | ~500ms | 2/sec | Network I/O |
| Full Assignment | ~300ms | 3/sec | Multiple checks |

## Scaling Considerations

### Horizontal Scaling
- Add API server instances behind load balancer
- Use Redis for caching ML predictions
- Implement request queuing for spike handling

### Vertical Scaling
- Increase server RAM for larger datasets
- Use GPU for ML inference acceleration
- Optimize Sheets API with batch operations

### Database Migration
- Current: Google Sheets (good for <100 pilots)
- Scale to: PostgreSQL (1000+ pilots)
- Cache layer: Redis (ML predictions)

## Security Considerations

### Current Implementation
- Environment variable for API keys
- No authentication on endpoints

### Production Recommendations
- Add OAuth2/JWT authentication
- Rate limiting per API key
- HTTPS only
- Input validation on all endpoints
- Audit logging for all operations
- Service account scoping for Sheets

## Monitoring & Logging

### Key Metrics to Track
- Model prediction accuracy
- Assignment conflict rate
- Urgent reassignment frequency
- API response times
- Sheets sync failures

### Health Checks
- `/health` endpoint for service status
- Model file existence verification
- Sheets API connectivity test
- Feature engineering validation

---

**This architecture ensures**:
✅ Fast pilot assignment (< 500ms)
✅ Reliable conflict detection
✅ Urgent mission handling
✅ Data consistency via Sheets
✅ LLM integration readiness
✅ Clear separation of concerns
✅ Easy debugging and testing
✅ Production-ready error handling
