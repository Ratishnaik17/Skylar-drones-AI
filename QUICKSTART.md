# Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Clone/download the project
cd Skylar_ml_model

# 2. Run setup (installs dependencies, creates venv)
python setup.py

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Edit configuration
cp .env.example .env
# Open .env and set your values
```

## Configuration

### Google Sheets Setup (Optional but Recommended)

1. Create a Google Cloud project
2. Enable Google Sheets API
3. Create Service Account with Sheets & Drive scopes
4. Download credentials.json
5. Create a Google Sheet with these worksheets:
   - `Pilots` (columns: ID, Name, Skills, Certifications, Experience, Location, Cost/Day, Days Available, Status)
   - `Missions` (columns: ID, Name, Required Skills, Cert, Location, Days, Budget, Priority, Start, End, Status)
   - `Drones` (columns: ID, Name, Location, Status, Weather Rating, Range, Payload, Battery)
   - `Assignments` (columns: ID, Mission ID, Pilot Name, Status, Created At, Notes)

6. Set environment variables:
```bash
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_SHEETS_CREDENTIALS=/path/to/credentials.json
```

### OpenAI API (Optional for LLM Agent)

1. Get API key from https://platform.openai.com
2. Set environment variable:
```bash
OPENAI_API_KEY=sk-your-key-here
```

## Running the System

### 1. Train the ML Model

```bash
python src/train_model.py data/pilot_roster.csv data/missions.csv
```

Output:
```
✅ Model trained successfully
✅ Model saved to models/pilot_match_model.pkl

Feature Importance:
  skill_match: 0.3521
  experience: 0.2843
  cost_fit: 0.1876
  ...
```

### 2. Start the API Server

```bash
python src/main.py
```

Server runs at `http://localhost:8000`

### 3. Access API Documentation

Open browser to: `http://localhost:8000/docs`

Interactive documentation with try-it-out functionality!

## Testing

### Unit Tests

```bash
cd tests
python -m pytest test_core.py -v
```

### Demo Workflow

```bash
cd tests
python demo.py
```

Shows complete workflow:
- Model training
- Feature importance
- Pilot ranking
- Conflict detection
- Drone matching
- Urgent reassignment

## Example API Calls

### Using Python

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Rank pilots for a mission
response = requests.post(
    "http://localhost:8000/api/rank-pilots",
    json={
        "pilots": [...],
        "mission": {...}
    }
)
ranked = response.json()["ranked_pilots"]
```

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get API summary
curl http://localhost:8000/

# Get available functions for LLM
curl http://localhost:8000/api/functions
```

## Troubleshooting

### Model Not Loading

```
Error: Could not load ML model
```

**Solution**: Train the model first
```bash
python src/train_model.py data/pilot_roster.csv data/missions.csv
```

### Google Sheets Connection Failed

```
Error: Authentication failed
```

**Solution**: 
1. Check credentials.json path in .env
2. Verify service account has Sheets API access
3. Verify spreadsheet ID is correct
4. Check credentials file exists and is valid JSON

### Port Already in Use

```bash
ERROR: Uvicorn failed to start. Port 8000 is in use
```

**Solution**: 
- Change port in .env: `API_PORT=8001`
- Or kill existing process using port 8000

### Import Errors

```
ModuleNotFoundError: No module named 'sklearn'
```

**Solution**:
```bash
pip install -r requirements.txt
```

## Deployment

### Local Production

```bash
# Set production mode
DEBUG=False python src/main.py
```

### Railway.app Deployment

1. Push to GitHub
2. Connect Railway to GitHub repo
3. Set environment variables in Railway dashboard
4. Deploy!

### AWS/GCP/Azure

See [DECISION_LOG.md](DECISION_LOG.md) deployment section for detailed instructions.

## Next Steps

1. **Read Architecture**: Check [DECISION_LOG.md](DECISION_LOG.md)
2. **Understand Models**: Review [src/train_model.py](src/train_model.py)
3. **Customize**: Adjust `SUITABILITY_THRESHOLD` in config.py
4. **Scale**: Set up PostgreSQL for >100 pilots
5. **Monitor**: Add logging and metrics tracking

## API Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/train-model` | POST | Train ML model |
| `/api/rank-pilots` | POST | Rank pilots for mission |
| `/api/assign-pilot` | POST | Assign with conflict check |
| `/api/detect-conflicts` | POST | Find all conflicts |
| `/api/match-drone` | POST | Check drone compatibility |
| `/api/urgent-reassign` | POST | Emergency reassignment |
| `/api/sync/pilots` | GET | Read from Google Sheets |

## Support

- 📖 See [README.md](README.md) for full documentation
- 🏗️ See [DECISION_LOG.md](DECISION_LOG.md) for architecture details
- 💬 Check source code comments in `src/`

---

**Ready to assign pilots like a boss?** 🚀
