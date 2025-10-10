#!/bin/bash

# Set up the environment
echo "Setting up the environment..."
source venv/bin/activate

# Run the main application
echo "Starting the 3D model generation agent..."
python src/app.py

# Deactivate the environment after execution
deactivate
echo "Agent execution completed."