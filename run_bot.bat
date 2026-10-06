@echo off
echo ===================================================
echo     Starting BotKubera Dashboard...
echo ===================================================

:: Deactivate virtual environment if it is currently active in the console
if defined VIRTUAL_ENV (
    echo [INFO] Active virtual environment detected. Deactivating...
    call deactivate 2>nul
)

:: 1. Verify and install requirements inside venv
echo [INFO] Checking/Installing dependencies...
venv\Scripts\python.exe -m pip install -q -r requirements.txt

:: 2. Prompt about Ollama and open the web dashboard in default browser
echo ===================================================
echo [IMPORTANT] Please ensure Ollama is running in another terminal.
echo Command: ollama run llama3:8b
echo ===================================================
echo.
echo [INFO] Launching Web Dashboard in browser...
start http://127.0.0.1:5050

echo [INFO] Starting Flask Server backend...
venv\Scripts\python.exe app.py

pause
