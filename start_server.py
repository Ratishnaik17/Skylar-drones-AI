#!/usr/bin/env python
"""
Quick Start Script for Skylark Drones AI Operations Brain
Starts the API server and shows access information
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def check_model():
    """Check if ML model is trained"""
    model_path = Path("models/pilot_match_model.pkl")
    if model_path.exists():
        print("✅ ML Model: Ready")
        return True
    else:
        print("❌ ML Model: Not trained")
        print("   Run: python -m src.train_model data/pilot_roster.csv data/missions.csv")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    
    required = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'pandas',
        'sklearn',
        'numpy',
        'joblib'
    ]

    missing = []

    # Check standard packages
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    # Special check for python-dotenv
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing.append("python-dotenv")

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        return False
    else:
        print("✅ All dependencies: Installed")
        return True


def main():
    print_header("🚀 Skylark Drones - Quick Start")
    
    # Check prerequisites
    print("Checking prerequisites...\n")
    
    deps_ok = check_dependencies()
    model_ok = check_model()
    
    if not (deps_ok and model_ok):
        print("\n⚠️  Fix issues above before starting server")
        sys.exit(1)
    
    print("\n✅ All checks passed!\n")
    
    # Start server
    print_header("Starting API Server")
    
    print("Starting FastAPI server on http://127.0.0.1:8000...\n")
    
    try:
        # Use the venv Python and uvicorn
        
        venv_dir = ".venv" if Path(".venv").exists() else "venv"

        venv_python = (
            Path(f"{venv_dir}/Scripts/python.exe")
            if sys.platform == "win32"
            else Path(f"{venv_dir}/bin/python")
        )


        
        subprocess.run([
            str(venv_python),
            "-m", "uvicorn",
            "src.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
