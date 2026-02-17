"""
Verification script to ensure all components are working
"""

import sys
import os
from pathlib import Path


def check_directories():
    """Verify all required directories exist"""
    print("\n📁 Checking directories...")
    
    required_dirs = ["src", "data", "models", "tests", "examples"]
    all_ok = True
    
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"  ✅ {dir_name}/")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
            all_ok = False
    
    return all_ok


def check_files():
    """Verify all required source files exist"""
    print("\n📄 Checking source files...")
    
    required_files = {
        "src/main.py": "FastAPI backend",
        "src/config.py": "Configuration",
        "src/train_model.py": "ML training",
        "src/features.py": "Feature engineering",
        "src/conflict_detector.py": "Conflict detection",
        "src/drone_matcher.py": "Drone matching",
        "src/urgent_reassignment.py": "Urgent reassignment",
        "src/sheets_integration.py": "Google Sheets sync",
        "src/__init__.py": "Package initialization",
        "requirements.txt": "Dependencies",
        "README.md": "Documentation",
        "DECISION_LOG.md": "Architecture decisions",
        "ARCHITECTURE.md": "System architecture",
        "QUICKSTART.md": "Quick start guide",
    }
    
    all_ok = True
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            size = Path(file_path).stat().st_size
            print(f"  ✅ {file_path:35s} ({size:,} bytes) - {description}")
        else:
            print(f"  ❌ {file_path:35s} (missing) - {description}")
            all_ok = False
    
    return all_ok


def check_sample_data():
    """Verify sample data files"""
    print("\n📊 Checking sample data...")
    
    data_files = {
        "data/pilot_roster.csv": "Pilot data",
        "data/missions.csv": "Mission data",
        "data/drones.csv": "Drone data"
    }
    
    all_ok = True
    for file_path, description in data_files.items():
        if Path(file_path).exists():
            # Count lines
            with open(file_path) as f:
                lines = len(f.readlines())
            print(f"  ✅ {file_path:30s} ({lines} lines) - {description}")
        else:
            print(f"  ❌ {file_path:30s} (missing) - {description}")
            all_ok = False
    
    return all_ok


def check_python_imports():
    """Verify Python dependencies can be imported"""
    print("\n🐍 Checking Python imports...")
    
    modules = {
        "fastapi": "FastAPI web framework",
        "pydantic": "Data validation",
        "pandas": "Data manipulation",
        "sklearn": "Machine learning",
        "joblib": "Model persistence",
        "gspread": "Google Sheets API",
        "google.auth": "Google authentication"
    }
    
    all_ok = True
    for module, description in modules.items():
        try:
            __import__(module.replace(".", "/"))
            print(f"  ✅ {module:20s} - {description}")
        except ImportError as e:
            print(f"  ❌ {module:20s} - {description} (not installed)")
            all_ok = False
    
    return all_ok


def check_code_structure():
    """Verify core code structure"""
    print("\n🔍 Checking code structure...")
    
    checks = [
        {
            "file": "src/features.py",
            "classes": ["FeatureEngineer"],
            "methods": ["calculate_skill_match", "create_training_dataset"]
        },
        {
            "file": "src/conflict_detector.py",
            "classes": ["ConflictDetector"],
            "methods": ["detect_all_conflicts", "check_double_booking"]
        },
        {
            "file": "src/drone_matcher.py",
            "classes": ["DroneMatcher"],
            "methods": ["match_drone_to_mission", "rank_drones_for_mission"]
        },
        {
            "file": "src/train_model.py",
            "classes": ["PilotMatchModel"],
            "methods": ["train", "predict", "batch_predict"]
        },
        {
            "file": "src/urgent_reassignment.py",
            "classes": ["UrgentReassignmentEngine"],
            "methods": ["should_trigger_reassignment", "rank_pilot_candidates"]
        }
    ]
    
    all_ok = True
    for check in checks:
        file_path = check["file"]
        if Path(file_path).exists():
            with open(file_path) as f:
                content = f.read()
            
            # Check classes
            found_classes = all(f"class {cls}" in content for cls in check["classes"])
            found_methods = all(f"def {method}" in content for method in check["methods"])
            
            if found_classes and found_methods:
                print(f"  ✅ {file_path:30s} - Structure OK")
            else:
                print(f"  ⚠️  {file_path:30s} - Missing some classes/methods")
                all_ok = False
        else:
            print(f"  ❌ {file_path:30s} - File not found")
            all_ok = False
    
    return all_ok


def check_api_routes():
    """Verify API routes are defined"""
    print("\n🛣️  Checking API routes...")
    
    routes = [
        "/",
        "/health",
        "/api/train-model",
        "/api/rank-pilots",
        "/api/match-pilot",
        "/api/assign-pilot",
        "/api/detect-conflicts",
        "/api/match-drone",
        "/api/rank-drones",
        "/api/urgent-reassign",
        "/api/sync/pilots",
        "/api/sync/missions",
        "/api/sync/drones",
        "/api/functions"
    ]
    
    main_file = Path("src/main.py")
    if not main_file.exists():
        print("  ❌ src/main.py not found")
        return False
    
    with open(main_file) as f:
        content = f.read()
    
    all_ok = True
    for route in routes:
        # Check for route creation with @app decorator
        escaped_route = route.replace("{", "\\{").replace("}", "\\}")
        if f'"{route}"' in content or f"'{route}'" in content:
            print(f"  ✅ {route:30s}")
        else:
            print(f"  ⚠️  {route:30s} (might not be implemented)")
            all_ok = False
    
    return all_ok


def check_models_directory():
    """Check if trained model exists"""
    print("\n🧠 Checking ML model...")
    
    model_file = Path("models/pilot_match_model.pkl")
    if model_file.exists():
        size = model_file.stat().st_size
        print(f"  ✅ Model file exists ({size:,} bytes)")
        return True
    else:
        print(f"  ℹ️  Model file not found")
        print(f"     Run: python src/train_model.py data/pilot_roster.csv data/missions.csv")
        return False


def run_all_checks():
    """Run all verification checks"""
    print("\n" + "=" * 70)
    print("  AI OPERATIONS BRAIN - VERIFICATION REPORT")
    print("=" * 70)
    
    results = {
        "Directories": check_directories(),
        "Source Files": check_files(),
        "Sample Data": check_sample_data(),
        "Code Structure": check_code_structure(),
        "API Routes": check_api_routes(),
        "Python Imports": check_python_imports(),
        "ML Model": check_models_directory()
    }
    
    print("\n" + "=" * 70)
    print("  VERIFICATION SUMMARY")
    print("=" * 70)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "⚠️  PARTIAL"
        print(f"  {check_name:25s} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 70)
    if all_passed:
        print("  🎉 ALL CHECKS PASSED!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. python src/train_model.py data/pilot_roster.csv data/missions.csv")
        print("  2. python src/main.py")
        print("  3. Visit http://localhost:8000/docs")
    else:
        print("  ⚠️  SOME CHECKS FAILED")
        print("=" * 70)
        print("\nFix issues and run verification again:")
        print("  python verify.py")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_checks()
    sys.exit(0 if success else 1)
