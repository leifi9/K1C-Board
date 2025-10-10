@echo off
REM Set up the environment
echo Setting up the environment...
call venv\Scripts\activate.bat

REM Run the main application
echo Starting the 3D model generation agent...
python src\app.py

REM Deactivate the environment after execution
call venv\Scripts\deactivate.bat
echo Agent execution completed.
