"""
Configuration module for Drone Operations AI System
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for directory in [DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True)

# Model configuration
MODEL_PATH = MODELS_DIR / "pilot_match_model.pkl"
MODEL_VERSION = "1.0"
TEST_SIZE = 0.2
RANDOM_STATE = 42

# Google Sheets configuration
GOOGLE_SHEETS_CREDENTIALS = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "credentials.json")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")

# Sheet names
PILOTS_SHEET = "Pilots"
MISSIONS_SHEET = "Missions"
ASSIGNMENTS_SHEET = "Assignments"
DRONES_SHEET = "Drones"

# FastAPI configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4"

# Conflict detection configuration
MAX_CONCURRENT_ASSIGNMENTS = 3
MAX_TRAVEL_DISTANCE_KM = 500

# ML thresholds
SUITABILITY_THRESHOLD = 0.6  # Minimum confidence score
HIGH_PRIORITY_THRESHOLD = 0.8  # Threshold for urgent reassignment

# Cost configuration
COST_MARGIN_BUFFER = 0.1  # 10% buffer for budget calculations

# Features for ML model
FEATURE_COLUMNS = [
    "skill_match",
    "cert_match",
    "location_match",
    "cost_fit",
    "experience"
]

TARGET_COLUMN = "label"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "drone_operations.log"

print(f"Configuration loaded from: {__file__}")
print(f"Data directory: {DATA_DIR}")
print(f"Models directory: {MODELS_DIR}")
