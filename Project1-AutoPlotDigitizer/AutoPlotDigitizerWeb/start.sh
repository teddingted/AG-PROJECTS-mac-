#!/bin/bash

# AutoPlotDigitizer Web Launcher
# Cross-platform launcher script

cd "$(dirname "$0")"

LOG_FILE="launcher_debug.log"

echo "🚀 Starting AutoPlotDigitizer Web..." | tee -a "$LOG_FILE"
echo "📅 Date: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Ensure python3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Error: Python is not installed or not in PATH." | tee -a "$LOG_FILE"
    exit 1
fi

echo "Using Python: $($PYTHON_CMD --version)" | tee -a "$LOG_FILE"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Setting up virtual environment..." | tee -a "$LOG_FILE"
    $PYTHON_CMD -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install/Update dependencies
echo "📦 Checking dependencies..." | tee -a "$LOG_FILE"
pip install -r requirements.txt | tee -a "$LOG_FILE"

echo "✅ Setup complete! Running app..." | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Run the app and capture output
python app.py 2>&1 | tee -a "$LOG_FILE"

