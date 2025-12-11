@echo off
REM ============================================
REM PDBOT 300-Question Calibration Test Suite
REM Version 3.3.4
REM ============================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo  ========================================
echo   PDBOT 300-Question Calibration Test
echo   Version 3.3.4
echo  ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

REM Check if API is running
echo [1/4] Checking API status...
curl -s http://localhost:5000/health >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo [WARNING] API not running at localhost:5000
    echo.
    echo Starting API server in new window...
    start "PDBOT API" cmd /c "cd /d "%~dp0" && python widget_api.py"
    echo Waiting 30 seconds for API to initialize...
    timeout /t 30 /nobreak >nul
    
    REM Check again
    curl -s http://localhost:5000/health >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to start API. Please start manually.
        pause
        exit /b 1
    )
)
echo [OK] API is running

REM Run the test
echo.
echo [2/4] Running 300-question test suite...
echo      This may take 20-30 minutes...
echo.
python tests\comprehensive_300_test.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Test execution failed
    pause
    exit /b 1
)

REM Generate report
echo.
echo [3/4] Generating detailed report...
python tests\generate_report.py
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Report generation failed
)

REM Find and open the report
echo.
echo [4/4] Opening report...
for /f "delims=" %%i in ('dir /b /o-d tests\reports\TEST_REPORT_*.md 2^>nul') do (
    set "LATEST_REPORT=tests\reports\%%i"
    goto :found_report
)
:found_report
if defined LATEST_REPORT (
    echo Report saved: %LATEST_REPORT%
    start "" "%LATEST_REPORT%"
) else (
    echo No report file found.
)

echo.
echo  ========================================
echo   Test Complete!
echo  ========================================
echo.
echo Results saved to:
echo   - tests\results\test_results_*.json (raw data)
echo   - tests\reports\TEST_REPORT_*.md (formatted report)
echo.
pause
