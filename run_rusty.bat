@echo off
REM === Activate virtual environment ===
IF NOT EXIST venv (
    echo [!] Virtual environment not found. Creating one...
    python -m venv venv
)

call venv\Scripts\activate

REM === Install dependencies ===
echo [*] Installing required packages...
pip install -r requirements.txt

REM === Check for .env file ===
IF NOT EXIST .env (
    echo [!] .env file is missing! Please add your API keys to a .env file.
    pause
    exit /b
)

REM === Launch Rusty ===
echo [*] Starting Rusty...
python main.py
