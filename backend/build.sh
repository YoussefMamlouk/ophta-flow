#!/bin/bash
# Build script for Render
# This ensures Python 3.11 is used

# Check Python version
python3 --version

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

