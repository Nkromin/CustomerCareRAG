#!/bin/bash
# Quick start script for Enterprise Policy Assistant

echo "=============================================="
echo "Enterprise Policy Assistant - Quick Start"
echo "=============================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv .venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file..."
    echo "grok_api_key=YOUR_API_KEY_HERE" > .env
    echo "Please edit .env and add your Groq API key"
    exit 1
fi

echo "✓ Environment checks passed"
echo ""
echo "Starting Streamlit app..."
echo "=============================================="
echo ""

# Run streamlit
.venv/bin/streamlit run app.py

