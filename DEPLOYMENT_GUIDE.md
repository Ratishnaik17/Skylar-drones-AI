# Deployment & Hosting Guide

## Overview
This guide covers deploying your Skylark Drones AI agent to production platforms.

## Recommended Platforms

| Platform | Cost | Setup Time | Best For |
|----------|------|-----------|----------|
| **Railway** | $5-20/month | 10 min | 🏆 Recommended |
| **Render** | $0-20/month | 15 min | Good alternative |
| **Heroku** | $7-50/month | 10 min | Legacy option |
| **Vercel** | $20/month | 20 min | Serverless |
| **AWS** | Pay-as-you-go | 30 min | Enterprise |

## Option 1: Deploy to Railway.app (Recommended)

### Step 1: Install Railway CLI
```powershell
npm install -g @railway/cli
```

### Step 2: Login to Railway
```powershell
railway login
```

### Step 3: Initialize Railway Project
```powershell
cd c:\Users\naikr\OneDrive\Desktop\Skylar_ml_model
railway init
```

### Step 4: Set Environment Variables
```powershell
railway variables set GOOGLE_SHEETS_ID=your_sheet_id
railway variables set GOOGLE_SHEETS_CREDENTIALS=@credentials.json
railway variables set OPENAI_API_KEY=sk-xxxx
railway variables set DEBUG=False
```

### Step 5: Create Procfile
Create file: `Procfile`
```
web: python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT
```

### Step 6: Deploy
```powershell
railway up
```

Your app will be available at: `https://your-project-name.up.railway.app`

---

## Option 2: Deploy to Render.com

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/skylark-drones.git
git push -u origin main
```

### Step 2: Connect to Render
1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repo
4. Fill in deployment settings:
   - **Name**: skylark-drones
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn src.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Set Environment Variables
In Render dashboard:
- Environment section → Add each variable from `.env`

### Step 4: Deploy
Click "Deploy" and wait ~5 minutes

---

## Option 3: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Download/train model
# RUN python src/train_model.py data/pilot_roster.csv data/missions.csv

# Start server
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Create docker-compose.yml
```yaml
version: '3.8'

services:
  skylark-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_SHEETS_ID=${GOOGLE_SHEETS_ID}
      - GOOGLE_SHEETS_CREDENTIALS=credentials.json
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEBUG=False
    volumes:
      - ./credentials.json:/app/credentials.json
      - ./models:/app/models
```

### Build and Run
```bash
docker build -t skylark-drones .
docker run -p 8000:8000 skylark-drones
```

---

## Environment Variables for Production

Create `.env.production`:
```
# Google Sheets
GOOGLE_SHEETS_ID=your_spreadsheet_id_here
GOOGLE_SHEETS_CREDENTIALS=path/to/credentials.json

# OpenAI (optional for conversational AI)
OPENAI_API_KEY=sk-xxxx

# FastAPI Settings
DEBUG=False
API_HOST=0.0.0.0
API_PORT=8000

# Security
SECRET_KEY=your-secure-random-key-here
```

---

## Pre-Deployment Checklist

- [ ] All dependencies in `requirements.txt`
- [ ] `credentials.json` secured (not in git)
- [ ] Environment variables configured
- [ ] Model trained and saved
- [ ] API tested locally (`python test_system.py`)
- [ ] Google Sheets credentials working
- [ ] CORS configured if needed
- [ ] Logging set up for production

---

## Post-Deployment Verification

### 1. Health Check
```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "ml_model_loaded": true,
  "sheets_connected": true
}
```

### 2. Root Endpoint
```bash
curl https://your-app.railway.app/
```

### 3. Chat Test
```bash
curl -X POST https://your-app.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "message": "Test message"
  }'
```

### 4. Swagger Docs
Visit: `https://your-app.railway.app/docs`

---

## Monitoring & Maintenance

### Railway Dashboard
- Monitor logs: Railway CLI → Logs tab
- Check metrics: CPU, Memory, Requests
- View deployments: Deployment history

### Health Monitoring
Set up a simple health check:
```python
import requests
import time

while True:
    response = requests.get('https://your-app.railway.app/health')
    if response.status_code != 200:
        # Send alert
        print("⚠️ API is down!")
    time.sleep(300)  # Check every 5 minutes
```

### Logs and Debugging
Check Railway logs for:
```
ERROR: ModuleNotFoundError
ERROR: Google Sheets authentication failed
ERROR: Model not found
```

---

## Scaling & Optimization

### For Higher Traffic (100+ req/min)

1. **Add multiple instances** (Railway auto-scales)
2. **Increase Python memory**: `1GB` (default) → `2GB`
3. **Add caching**: Redis for conversation history
4. **Database**: PostgreSQL instead of in-memory storage

### Production Settings
```python
# In config.py
if not DEBUG:
    # Disable hot reload
    app = FastAPI(debug=False)
    
    # Add CORS for specific domains
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://yourapp.com"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

---

## Security Checklist for Production

- [ ] Never commit `credentials.json` or `.env` files
- [ ] Use GitHub Secrets for sensitive data
- [ ] Enable HTTPS (automatic on Railway/Render)
- [ ] Add API key authentication if public
- [ ] Rate limit `/api/chat` to prevent abuse
- [ ] Log all assignments for audit trail
- [ ] Regular backups of Google Sheets
- [ ] Monitor API response times

---

## Sample Production .env.railway

```
# Railway-specific
RAILWAY_ENVIRONMENT=production

# Google Sheets (base64 encoded credentials.json)
GOOGLE_SHEETS_ID=1a2b3c4d5e6f7g8h9i0j...
GOOGLE_SHEETS_CREDENTIALS_B64=eyJh...

# OpenAI
OPENAI_API_KEY=sk-proj-...

# FastAPI
DEBUG=False
API_HOST=0.0.0.0
API_PORT=${PORT}

# Security
SECRET_KEY=generate-with-openssl-rand-b64-32
```

---

## Troubleshooting Deployments

### App crashes on startup
```
Check logs: railway logs -f
Common issues:
- Missing dependencies (add to requirements.txt)
- Module not found (check imports)
- File path issues (use absolute paths)
```

### Google Sheets not connecting
```
- Verify credentials.json is in project root
- Check GOOGLE_SHEETS_ID environment variable
- Verify service account email is shared with sheet
- Wait 5-10 seconds for permissions to propagate
```

### Model not loading
```
- Ensure models/pilot_match_model.pkl exists
- Or re-train: python src/train_model.py data/pilot_roster.csv data/missions.csv
- Check file permissions
```

### High latency
```
- Check Railway metrics (CPU/Memory)
- Scale up instance size
- Add caching layer
- Optimize Google Sheets queries
```

---

## Rollback Procedure

### Railway Rollback
```bash
railway environment rollback <deployment-id>
```

### Manual Rollback
1. Go to Railway dashboard
2. Click deployment you want to revert to
3. Click "Redeploy"

---

## Performance Targets for Production

| Metric | Target |
|--------|--------|
| API Response | < 500ms |
| Uptime | 99.5% |
| Chat Response | < 1s |
| ML Prediction | < 100ms |
| Sheets Sync | < 2s |

---

## Cost Estimation (Railway)

- **Hobby Tier**: $7/month
  - 500MB RAM, 0.5 CPU
  - Good for development

- **Pro Tier**: $20+/month
  - 2GB RAM, 2 CPU
  - Recommended for production

---

## References

- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs
- FastAPI Production: https://fastapi.tiangolo.com/deployment/
- Python Uvicorn: https://www.uvicorn.org/deployment/

