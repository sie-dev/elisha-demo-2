#!/bin/bash

# Chabad Search Interface Launcher
# Runs the Flask server for searching Sichos and Maamarim

echo "🔵 Starting Chabad Search Interface..."
echo "📚 Loading Sichos and Maamarim from תשל״ה..."
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if required files exist
SICHOS_FILE="/Users/elishapearl/Downloads/sichos_structured (4).json"
MAAMARIM_FILE="/Users/elishapearl/Downloads/maamarim_structured (2).json"

if [ ! -f "$SICHOS_FILE" ]; then
    echo "❌ Sichos file not found: $SICHOS_FILE"
    exit 1
fi

if [ ! -f "$MAAMARIM_FILE" ]; then
    echo "❌ Maamarim file not found: $MAAMARIM_FILE"
    exit 1
fi

echo "✅ Data files found"
echo ""

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -q flask flask-cors anthropic

echo ""
echo "🚀 Starting server on http://localhost:8080"
echo ""
echo "📖 Open your browser to: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
python3 server.py