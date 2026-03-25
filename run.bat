@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_CMD=python"
if exist ".venv\Scripts\python.exe" set "PYTHON_CMD=.venv\Scripts\python.exe"
echo Starting Flask app with dynamic port...
"%PYTHON_CMD%" app.py
endlocal
