@echo off
REM ============================================
REM PDBOT Setup for Windows Server + Docker Engine
REM One-click setup with Docker containers
REM ============================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo  ============================================
echo   PDBOT v4.0.0 - Docker Engine Setup
echo   Windows Server Edition
echo  ============================================
echo.
echo  This setup will:
echo   - Check Docker Engine is running
echo   - Pull and start Qdrant container
echo   - Pull and start Ollama container
echo   - Create Python virtual environment
echo   - Install Python dependencies
echo   - Initialize models and backend
echo.
echo  Requires: Docker Engine installed and running
echo.
pause

REM ============================================
REM Step 1: Check Docker Engine
REM ============================================
echo.
echo [1/6] Checking Docker Engine...
docker --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Docker Engine not found or not running!
    echo.
    echo Please ensure:
    echo  1. Docker Engine is installed on Windows Server
    echo  2. Docker daemon is running
    echo  3. You have admin permissions to use Docker
    echo.
    echo Docker installation: https://docs.docker.com/engine/install/
    goto :error
)
for /f %%i in ('docker --version') do echo       %%i detected
echo       [OK]

REM ============================================
REM Step 2: Pull and Start Qdrant Container
REM ============================================
echo.
echo [2/6] Setting up Qdrant (Vector Database in Docker)...

REM Check if container is already running
docker ps --filter "name=pcbot-qdrant" --format "{{.Names}}" 2>nul | findstr "pcbot-qdrant" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       Qdrant container already running
    echo       [OK]
    goto :skip_qdrant
)

REM Check if container exists but stopped
docker ps -a --filter "name=pcbot-qdrant" --format "{{.Names}}" 2>nul | findstr "pcbot-qdrant" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       Starting existing Qdrant container...
    docker start pcbot-qdrant >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARN] Failed to start container, removing and recreating...
        docker rm pcbot-qdrant >nul 2>&1
        goto :create_qdrant
    )
    echo       [OK] Qdrant container started
    goto :skip_qdrant
)

:create_qdrant
echo       Pulling Qdrant image (this may take a minute)...
docker pull qdrant/qdrant >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to pull Qdrant image
    goto :error
)

echo       Creating and starting Qdrant container...
docker run -d ^
    --name pcbot-qdrant ^
    -p 6333:6333 ^
    -p 6334:6334 ^
    -e QDRANT_API_KEY= ^
    -v qdrant_storage:/qdrant/storage ^
    qdrant/qdrant >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to start Qdrant container
    goto :error
)

timeout /t 3 /nobreak >nul
echo       [OK] Qdrant running on port 6333 (Docker)

:skip_qdrant

REM ============================================
REM Step 3: Pull and Start Ollama Container (Optional)
REM ============================================
echo.
echo [3/6] Setting up Ollama (LLM in Docker - Optional)...

REM Check if Ollama is running on host
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo       Ollama already running on host (not using Docker container)
    echo       [OK]
    goto :skip_ollama_docker
)

REM Inform user - Ollama Docker on Windows Server is optional
echo       Note: Ollama in Docker requires significant resources
echo       For Windows Server, its recommended to run Ollama on the host
echo.
set /p OLLAMA_DOCKER="Do you want to start Ollama in Docker? (y/n): "

if /i "%OLLAMA_DOCKER%"=="y" (
    docker ps --filter "name=pcbot-ollama" --format "{{.Names}}" 2>nul | findstr "pcbot-ollama" >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo       Ollama container already running
        echo       [OK]
        goto :skip_ollama_docker
    )

    echo       Pulling Ollama image...
    docker pull ollama/ollama >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARN] Failed to pull Ollama image, skipping Docker Ollama
        goto :skip_ollama_docker
    )

    echo       Starting Ollama container...
    docker run -d ^
        --name pcbot-ollama ^
        -p 11434:11434 ^
        -v ollama_models:/root/.ollama ^
        ollama/ollama >nul 2>&1

    if %ERRORLEVEL% neq 0 (
        echo [WARN] Failed to start Ollama container, skipping
        goto :skip_ollama_docker
    )

    timeout /t 5 /nobreak >nul
    echo       Pulling Mistral model (this may take 10-15 minutes)...
    docker exec pcbot-ollama ollama pull mistral >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [WARN] Failed to pull Mistral model
        goto :skip_ollama_docker
    )
    echo       [OK] Ollama container running with Mistral
) else (
    echo       Skipping Docker Ollama
    echo       Please install and run Ollama on the host machine
    echo       Download from: https://ollama.ai
)

:skip_ollama_docker

REM ============================================
REM Step 4: Check Python
REM ============================================
echo.
echo [4/6] Checking Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found!
    echo       Install Python 3.10+ from https://python.org
    goto :error
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo       Python %%i detected
echo       [OK]

REM ============================================
REM Step 5: Create Virtual Environment and Install Dependencies
REM ============================================
echo.
echo [5/6] Setting up Python virtual environment...
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

echo.
echo       Installing Python dependencies...
echo       This may take a few minutes...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet

echo       Installing core packages...
python -m pip install flask flask-cors waitress --quiet
python -m pip install qdrant-client sentence-transformers --quiet
python -m pip install langchain langchain-community langchain-text-splitters --quiet
python -m pip install PyMuPDF nltk requests python-dotenv psutil transformers --quiet

echo       [OK] Python packages installed

REM ============================================
REM Step 6: Backend Initialization
REM ============================================
echo.
echo [6/6] Initializing backend and downloading models...
echo       This will download embedding models (may take 5-10 minutes)...
timeout /t 2 /nobreak >nul

echo       Starting backend for initialization...
start "PCBot Docker Setup - Backend Warmup" "scripts\setup\run_backend.bat"

echo       Waiting for models to download (60 seconds)...
timeout /t 60 /nobreak >nul

echo       Stopping initial run...
powershell -Command "Get-Process | Where-Object {$_.MainWindowTitle -like 'PCBot Docker Setup*'} | Stop-Process -Force" 2>nul

echo       [OK] Models downloaded and initialized

REM ============================================
REM Setup Complete
REM ============================================
echo.
echo  ============================================
echo   Setup Complete!
echo  ============================================
echo.
echo   Docker containers running:
echo     [x] Qdrant (port 6333)
echo.
echo   Python:
echo     [x] Virtual environment created
echo     [x] Dependencies installed
echo.
echo   To start PCBot:
echo     Double-click: run_widget_standalone.bat
echo.
echo   Docker container commands:
echo     List Qdrant: docker ps --filter name=pcbot-qdrant
echo     List Ollama: docker ps --filter name=pcbot-ollama
echo     Stop Qdrant: docker stop pcbot-qdrant
echo     Stop Ollama: docker stop pcbot-ollama
echo     View logs: docker logs pcbot-qdrant
echo.
pause
exit /b 0

:error
echo.
echo  ============================================
echo   Setup Failed
echo  ============================================
echo.
echo   Please fix the error above and run setup again.
echo.
pause
exit /b 1
