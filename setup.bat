@echo off
REM ============================================
REM PDBOT Complete Setup Script v3.3.4
REM Developer: M. Hassan Arif Afridi
REM One-time setup for all dependencies
REM ============================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo  ========================================
echo   PDBOT v3.3.4 - Complete Setup
echo   Developer: M. Hassan Arif Afridi
echo  ========================================
echo.
echo  This will install all required components:
echo  - Python dependencies (Flask, Qdrant, etc.)
echo  - Node.js dependencies (React Widget)
echo  - Docker container (Qdrant vector DB)
echo.
pause

REM ============================================
REM Step 1: Check Python
REM ============================================
echo.
echo [1/7] Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://python.org
    goto :error
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo       Python %%i detected
echo       [OK]

REM ============================================
REM Step 2: Create Virtual Environment
REM ============================================
echo.
echo [2/7] Setting up virtual environment...
if exist ".venv\" (
    echo       Virtual environment already exists
) else (
    echo       Creating virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        goto :error
    )
)
call .venv\Scripts\activate.bat
echo       Virtual environment activated
echo       [OK]

REM ============================================
REM Step 3: Install Python Dependencies
REM ============================================
echo.
echo [3/7] Installing Python dependencies...
echo       This may take a few minutes...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [WARN] Some packages may have failed. Trying essential ones...
)

REM Install essential packages individually to ensure they're installed
echo       Installing core packages...
python -m pip install flask flask-cors waitress --quiet
python -m pip install qdrant-client sentence-transformers --quiet
python -m pip install langchain langchain-community langchain-text-splitters --quiet
python -m pip install PyMuPDF nltk requests python-dotenv psutil transformers torch --quiet

echo       [OK] Python packages installed

REM ============================================
REM Step 4: Check Node.js
REM ============================================
echo.
echo [4/7] Checking Node.js...
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Node.js not found!
    echo       Install from https://nodejs.org for React Widget
    echo       Skipping frontend setup...
    goto :skip_node
)
for /f %%i in ('node --version') do echo       Node.js %%i detected
echo       [OK]

REM ============================================
REM Step 5: Install Node.js Dependencies
REM ============================================
echo.
echo [5/7] Installing React Widget dependencies...
cd frontend-widget
call npm install --silent 2>nul
if %ERRORLEVEL% neq 0 (
    echo [WARN] npm install had issues, trying again...
    call npm install
)
cd ..
echo       [OK] React dependencies installed

:skip_node

REM ============================================
REM Step 6: Check Docker & Start Qdrant
REM ============================================
echo.
echo [6/7] Setting up Qdrant (Vector Database)...
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Docker not found!
    echo       Install Docker Desktop from https://docker.com
    echo       Qdrant is required for semantic search.
    goto :skip_docker
)
echo       Docker detected

REM Check if container exists
docker ps -a --filter "name=pndbot-qdrant" --format "{{.Names}}" | findstr "pndbot-qdrant" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       Qdrant container exists, starting...
    docker start pndbot-qdrant >nul 2>&1
) else (
    echo       Creating Qdrant container...
    docker run -d -p 6338:6333 -p 6334:6334 --name pndbot-qdrant qdrant/qdrant >nul 2>&1
)
timeout /t 3 /nobreak >nul
echo       [OK] Qdrant running on port 6338

:skip_docker

REM ============================================
REM Step 7: Check Ollama & Download Model
REM ============================================
echo.
echo [7/7] Checking Ollama (LLM Backend)...
where ollama >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Ollama not found!
    echo       Install from https://ollama.ai
    echo       Then run: ollama pull mistral
    goto :skip_ollama
)

echo       Ollama found, checking if running...
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo       Starting Ollama...
    start "Ollama Server" cmd /c "ollama serve"
    timeout /t 3 /nobreak >nul
)

echo       Checking for Mistral model...
ollama list | findstr "mistral" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo       Downloading Mistral model (this may take 10-15 minutes)...
    ollama pull mistral
)
echo       [OK] Ollama ready with Mistral model

:skip_ollama

REM ============================================
REM Step 8: Initial Run & Model Warmup
REM ============================================
echo.
echo [8/8] Running initial setup and model warmup...
echo       This will download embedding models on first run...
timeout /t 2 /nobreak >nul

echo       Starting backend for initialization...
REM Use backend wrapper for consistent startup and logging during initial setup
start "PCBot Initial Setup" "scripts\setup\run_backend.bat"

echo       Waiting for models to download and warm up (30 seconds)...
timeout /t 30 /nobreak >nul

echo       Stopping initial run...
taskkill /FI "WINDOWTITLE eq PCBot Initial Setup*" /F >nul 2>&1

echo       [OK] Models downloaded and warmed up

REM ============================================
REM Setup Complete
REM ============================================
echo.
echo  ========================================
echo   Setup Complete!
echo  ========================================
echo.
echo   All components installed and initialized:
echo     [x] Python virtual environment (.venv)
echo     [x] All Python packages (including sentence-transformers)
echo     [x] Qdrant vector database
echo     [x] Ollama with Mistral model
echo     [x] Embedding models downloaded
echo.
echo   To start PCBot:
echo     1. Quick Launch:   run_pcbot.bat
echo     2. Widget Only:    run_widget_standalone.bat
echo.
echo   First-time users: run_widget_standalone.bat
echo.
echo  ========================================
echo.
pause
goto :end

:error
echo.
echo  ========================================
echo   Setup Failed - Please check errors above
echo  ========================================
echo.
pause

:end
endlocal
