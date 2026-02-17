# Google Sheets Integration Setup Guide

## Overview
This guide helps you set up 2-way Google Sheets sync for your Skylark Drones system.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project"
3. Name it: `Skylark Drones Operations`
4. Click Create

## Step 2: Enable Google Sheets & Drive APIs

1. In the Cloud Console, search for "Google Sheets API"
2. Click "Google Sheets API" → Click Enable
3. Search for "Google Drive API"
4. Click "Google Drive API" → Click Enable

## Step 3: Create Service Account

1. In Cloud Console, go to "Credentials"
2. Click "Create Credentials" → Service Account
3. Fill in details:
   - Service account name: `skylark-drones-api`
   - Click Create and Continue
4. Grant roles:
   - Select "Editor" role (for full access)
   - Click Continue
5. Click "Create Key"
   - Select JSON format
   - Click Create
   - **Save this file as `credentials.json` in your project root**

## Step 4: Create Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet: `Skylark Drones Operations`
3. Rename sheets as follows (right-click tab → Rename):
   
   **Sheet 1 - Pilots**
   ```
   Headers: pilot_id | name | skills | certifications | experience_years | 
            location | cost_per_day | days_available | status | current_assignment
   
   Sample Row:
   PLT001 | Arjun | Thermal_Imaging,Photogrammetry | PPL,ATPL | 5 | 
   Bangalore | 500 | 30 | available | None
   ```

   **Sheet 2 - Missions**
   ```
   Headers: project_id | client | location | required_skills | required_cert | 
            start_date | end_date | priority | mission_budget_inr | weather_forecast
   
   Sample Row:
   PRJ001 | TechCorp | Mumbai | Thermal_Imaging | PPL | 2024-02-20 | 2024-02-25 | 
   HIGH | 15000 | Rainy
   ```

   **Sheet 3 - Drones**
   ```
   Headers: drone_id | name | location | status | weather_rating | 
            flight_range_km | payload_capacity_kg | battery_endurance_minutes
   
   Sample Row:
   DJI001 | DJI M300 | Bangalore | available | IP54 | 50 | 6 | 45
   ```

   **Sheet 4 - Assignments**
   ```
   Headers: id | mission_id | pilot_name | status | created_at | notes
   
   (This will be auto-populated by the system)
   ```

## Step 5: Share Sheet with Service Account

1. Open your new Google Sheet
2. Click Share button
3. Copy the service account email from the JSON (something like `xyz@xxx.iam.gserviceaccount.com`)
4. Paste in the share dialog and select Editor role
5. Click Share

## Step 6: Get Sheet ID

1. In the sheet URL, copy the ID: 
   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
                                          ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
   ```

## Step 7: Configure Environment

1. Create `.env` file in project root:
   ```
   GOOGLE_SHEETS_ID=your_sheet_id_here
   GOOGLE_SHEETS_CREDENTIALS=credentials.json
   OPENAI_API_KEY=your_openai_key_here (optional for conversational AI)
   DEBUG=False
   ```

2. Place `credentials.json` in project root (from Step 3)

## Step 8: Restart Server

```bash
# Kill existing server and restart
C:/Users/naikr/OneDrive/Desktop/Skylar_ml_model/.venv/Scripts/uvicorn.exe src.main:app --host 127.0.0.1 --port 8000 --reload
```

Server logs should show:
```
✅ Authenticated with Google Sheets: Skylark Drones Operations
✅ Google Sheets integration ready
```

## Step 9: Test Sync

Run the system test:
```bash
python test_system.py
```

You should see:
- ✅ Sync Pilots: Loaded X pilots
- ✅ Sync Missions: Loaded X missions
- ✅ Sync Drones: Loaded X drones

## Troubleshooting

### "Credentials file not found"
- Place `credentials.json` in project root
- Update GOOGLE_SHEETS_CREDENTIALS path in `.env`

### "Sheet not found"
- Verify sheet names exactly match (case-sensitive): "Pilots", "Missions", "Drones", "Assignments"
- Check service account has access (shared with Editor role)

### "Permission denied"
- Re-share sheet with service account email
- Wait 5-10 seconds for permissions to propagate

### API quota exceeded
- Sheets API has monthly quotas
- Check Cloud Console > Quotas

## Features After Setup

Once configured, your system will:
✅ Read pilot roster from Google Sheets
✅ Read missions from Google Sheets
✅ Read drone inventory from Google Sheets
✅ Write new assignments to Assignments sheet
✅ Update pilot status and availability
✅ Log all activities to Activity Log sheet
✅ Sync all changes bidirectionally

## Sample Test Flow

1. **Add a pilot to Google Sheets**
   - Enter new row in Pilots sheet

2. **Make a conversational request**
   ```
   POST /api/chat
   {
     "session_id": "user1",
     "message": "Who is available for a mapping mission in Bangalore?"
   }
   ```

3. **System will**:
   - Read from Google Sheets
   - Analyze pilot availability
   - Return AI response with recommendations

## Next Steps

- Monitor `/health` endpoint for sync status
- Check API logs for any sync errors
- Test assignment creation to verify write access
- Set up automated backups of your Google Sheet

---

**Questions?** Check README.md and DECISION_LOG.md for more details.

