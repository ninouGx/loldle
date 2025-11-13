#!/bin/bash
# Setup script for virtual environment

set -e

echo "🔧 Setting up Loldle Solver development environment..."

# Check if uv is available (modern fast pip alternative)
if command -v uv &> /dev/null; then
    echo "✓ Using uv (fast!)"
    UV_CMD="uv"
else
    echo "ℹ uv not found, using standard venv"
    UV_CMD=""
fi

# Create virtual environment
if [ -n "$UV_CMD" ]; then
    echo "📦 Creating virtual environment with uv..."
    uv venv
else
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
if [ -n "$UV_CMD" ]; then
    uv pip install --upgrade pip
else
    pip install --upgrade pip
fi

# Install dependencies
echo "📥 Installing core dependencies..."
if [ -n "$UV_CMD" ]; then
    uv pip install -r requirements.txt
else
    pip install -r requirements.txt
fi

# Install package in editable mode
echo "📦 Installing loldle in editable mode..."
if [ -n "$UV_CMD" ]; then
    uv pip install -e .
else
    pip install -e .
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate    (Linux/Mac)"
echo "  venv\\Scripts\\activate      (Windows)"
echo ""
echo "Optional extras:"
echo "  pip install -r requirements-dev.txt      # Development tools"
echo "  pip install -r requirements-scraper.txt  # Web scraping (Selenium)"
echo ""
echo "Try it:"
echo "  loldle --help"
echo "  loldle play"
echo "  loldle solve"
echo ""
