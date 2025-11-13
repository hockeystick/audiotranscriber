#!/bin/bash

# MP3 Audio Transcriber - Mac Launcher Script
# This script starts the Flask transcription app

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    # Try to load from .env file
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
fi

# If still not set, prompt user
if [ -z "$OPENAI_API_KEY" ]; then
    echo "=================================="
    echo "OpenAI API Key Required"
    echo "=================================="
    echo ""
    echo "Please enter your OpenAI API key:"
    read -s OPENAI_API_KEY
    export OPENAI_API_KEY

    # Optionally save to .env for future use
    echo ""
    echo "Would you like to save this key for future sessions? (y/n)"
    read -r REPLY
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" > .env
        echo "API key saved to .env file"
    fi
fi

# Start the Flask app
echo ""
echo "=================================="
echo "Starting MP3 Audio Transcriber"
echo "=================================="
echo ""
echo "The app will open in your browser at:"
echo "http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser after a short delay
sleep 2 && open "http://localhost:8000" &

# Start Flask app
python app.py
