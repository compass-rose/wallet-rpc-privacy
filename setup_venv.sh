#!/bin/bash
# Setup Python 3.10 virtual environment for the project

set -e

echo "=== Setting up Python 3.10 virtual environment ==="

# Check if Python 3.10 is available
if ! command -v python3.10 &> /dev/null; then
    echo "❌ Python 3.10 not found. Installing via Homebrew..."
    brew install python@3.10

    if ! command -v python3.10 &> /dev/null; then
        echo "❌ Failed to install Python 3.10 via Homebrew."
        echo "Please install manually:"
        echo "  Option 1: Download from https://www.python.org/ftp/python/3.10.14/"
        echo "  Option 2: Use pyenv: brew install pyenv && pyenv install 3.10.14"
        exit 1
    fi
fi

echo "✓ Found Python 3.10"

# Check if virtual environment already exists
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment 'venv' already exists."
    read -p "Do you want to recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv
    else
        echo "Using existing virtual environment."
        source venv/bin/activate
        python --version
        exit 0
    fi
fi

# Create virtual environment
echo "Creating virtual environment..."
python3.10 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install project dependencies
echo "Installing project dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Virtual environment setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate the virtual environment, run:"
echo "  deactivate"
echo ""
echo "Current Python version:"
python --version
