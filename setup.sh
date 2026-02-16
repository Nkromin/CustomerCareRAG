#!/bin/bash
# Complete setup script for Enterprise Policy Assistant

set -e  # Exit on error

echo "=============================================="
echo "Enterprise Policy Assistant - Complete Setup"
echo "=============================================="
echo ""

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

# Step 2: Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo ""
    echo "Step 2: Creating virtual environment..."
    python3 -m venv .venv
    echo "   ✓ Virtual environment created"
else
    echo ""
    echo "Step 2: Virtual environment exists"
fi

# Step 3: Activate and install dependencies
echo ""
echo "Step 3: Installing dependencies..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q

echo "   ✓ Dependencies installed"

# Step 4: Check .env file
echo ""
echo "Step 4: Checking configuration..."
if [ ! -f ".env" ]; then
    echo "   ⚠️  .env file not found!"
    echo "   Creating template .env file..."
    cat > .env << 'EOF'
# Groq API Key (get from https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here
grok_api_key=your_groq_api_key_here
EOF
    echo ""
    echo "   ❌ Please edit .env and add your Groq API key!"
    echo "   Then run this script again."
    exit 1
else
    echo "   ✓ .env file exists"
fi

# Step 5: Create docs folder
echo ""
echo "Step 5: Setting up document folder..."
if [ ! -d "docs" ]; then
    mkdir -p docs
    echo "   ✓ Created docs/ folder"
else
    echo "   ✓ docs/ folder exists"
fi

# Step 6: Test imports
echo ""
echo "Step 6: Testing system components..."
.venv/bin/python -c "
import config
from rag.loader import load_documents
from rag.vector_store import initialize_vector_store
from agent.graph import create_agent
print('   ✓ All components loaded successfully')
" 2>&1

if [ $? -ne 0 ]; then
    echo "   ❌ Component test failed"
    exit 1
fi

# Success
echo ""
echo "=============================================="
echo "✓ Setup completed successfully!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Add your PDF policy documents to docs/ folder (optional)"
echo "  2. Run: ./start.sh"
echo "  or: .venv/bin/streamlit run app.py"
echo ""
echo "The app will automatically create sample documents if none exist."
echo "=============================================="

