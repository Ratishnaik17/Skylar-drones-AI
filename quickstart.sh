#!/bin/bash
# Quick start script for Linux/Mac users

echo "================================================"
echo "  AI OPERATIONS BRAIN - QUICK START"
echo "================================================"
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python $python_version detected"
echo

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"
echo

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"
echo

# Create directories
mkdir -p data models logs
echo "✅ Directories created"
echo

# Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env (please edit with your settings)"
fi
echo

# Train model
if [ -f "data/pilot_roster.csv" ] && [ -f "data/missions.csv" ]; then
    echo "🧠 Training ML model..."
    python src/train_model.py data/pilot_roster.csv data/missions.csv
    echo
fi

echo "================================================"
echo "  ✅ SETUP COMPLETE!"
echo "================================================"
echo
echo "Next commands:"
echo "1. Start API server:"
echo "   python src/main.py"
echo
echo "2. In another terminal, test:"
echo "   curl http://localhost:8000/health"
echo
echo "3. Visit documentation:"
echo "   http://localhost:8000/docs"
echo
