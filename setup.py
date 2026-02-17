#!/usr/bin/env python
"""
Setup script for AI Operations Brain
Configures environment and trains initial model
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_python_version():
    """Verify Python 3.9+"""
    if sys.version_info < (3, 9):
        print(f"❌ Python 3.9+ required. You have {sys.version_info.major}.{sys.version_info.minor}")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def create_virtual_env():
    """Create virtual environment"""
    print_header("Creating Virtual Environment")
    
    if Path("venv").exists():
        print("⚠️  venv already exists")
        return
    
    print("Creating venv...")
    subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    print("✅ Virtual environment created")


def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    # Determine pip command based on OS
    pip_cmd = "venv\\Scripts\\pip" if sys.platform == "win32" else "venv/bin/pip"
    
    print("Installing packages from requirements.txt...")
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
    print("✅ Dependencies installed")


def setup_env_file():
    """Create .env file from example"""
    print_header("Setting Up Environment Configuration")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("⚠️  .env already exists - skipping")
        return
    
    if env_example.exists():
        with open(env_example) as f:
            content = f.read()
        with open(env_file, "w") as f:
            f.write(content)
        print("✅ Created .env from .env.example")
        print("\n⚠️  Please edit .env with your settings:")
        print("   - GOOGLE_SHEETS_ID")
        print("   - GOOGLE_SHEETS_CREDENTIALS")
        print("   - OPENAI_API_KEY")
    else:
        print("❌ .env.example not found")


def create_directories():
    """Create required directories"""
    print_header("Setting Up Directories")
    
    dirs = ["models", "logs", "data", "src", "tests"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ {dir_name}/")


def train_initial_model():
    """Train initial ML model"""
    print_header("Training Initial ML Model")
    
    data_dir = Path("data")
    pilots_file = data_dir / "pilot_roster.csv"
    missions_file = data_dir / "missions.csv"
    
    if not pilots_file.exists() or not missions_file.exists():
        print("⚠️  Sample data files not found - skipping training")
        print("   Run: python src/train_model.py data/pilot_roster.csv data/missions.csv")
        return
    
    print("Training model...")
    try:
        # Determine python command based on OS
        python_cmd = "venv\\Scripts\\python" if sys.platform == "win32" else "venv/bin/python"
        
        subprocess.run(
            [python_cmd, "src/train_model.py", str(pilots_file), str(missions_file)],
            check=True,
            cwd=Path(__file__).parent
        )
        print("✅ Model trained successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Training failed: {e}")
        print("   Run manually: python src/train_model.py data/pilot_roster.csv data/missions.csv")


def main():
    """Run setup process"""
    print("\n" + "=" * 70)
    print("  🚀 AI OPERATIONS BRAIN - SETUP")
    print("=" * 70)
    
    try:
        # Change to script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Setup steps
        check_python_version()
        create_directories()
        create_virtual_env()
        install_dependencies()
        setup_env_file()
        train_initial_model()
        
        # Summary
        print_header("Setup Complete!")
        print("""
✅ Your AI Operations Brain is ready!

Next steps:
1. Edit .env with your configuration:
   - Set GOOGLE_SHEETS_ID for your spreadsheet
   - Set GOOGLE_SHEETS_CREDENTIALS path or content
   - Set OPENAI_API_KEY for LLM integration

2. Start the API server:
   Windows: venv\\Scripts\\python src/main.py
   Linux/Mac: venv/bin/python src/main.py

3. Visit http://localhost:8000/docs for interactive API docs

4. Read DECISION_LOG.md for architecture details

5. Run tests:
   pytest tests/

Questions? See README.md for detailed documentation.
""")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
