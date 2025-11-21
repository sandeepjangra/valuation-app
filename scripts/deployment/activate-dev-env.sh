#!/bin/bash

# ValuationApp Development Environment Activation Script
# This script activates the Python virtual environment and sets up the development environment

echo "🚀 Activating ValuationApp Development Environment..."
echo "📍 Project: Property Valuation Application"
echo "🐍 Python: 3.11.14"
echo "📦 Virtual Environment: valuation_env"
echo ""

# Check if virtual environment exists
if [ ! -d "valuation_env" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.11 -m venv valuation_env"
    exit 1
fi

# Activate virtual environment
source valuation_env/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated successfully!"
    echo "📁 Virtual environment path: $VIRTUAL_ENV"
    echo ""
    echo "💡 Available commands:"
    echo "   pip list                 - Show installed packages"
    echo "   python --version         - Check Python version"
    echo "   jupyter lab             - Start Jupyter Lab"
    echo "   black .                 - Format Python code"
    echo "   pytest                  - Run tests"
    echo "   deactivate              - Exit virtual environment"
    echo ""
    echo "🔧 To install dependencies: pip install -r requirements.txt"
    echo "📚 For setup guide: cat SETUP.md"
    echo ""
else
    echo "❌ Failed to activate virtual environment!"
    exit 1
fi

# Optional: Set environment variables if .env file exists
if [ -f ".env" ]; then
    echo "🔐 Loading environment variables from .env..."
    set -a
    source .env
    set +a
else
    echo "💡 Tip: Copy .env.example to .env and configure your settings"
fi

echo "🎯 Ready for development! Happy coding! 🚀"