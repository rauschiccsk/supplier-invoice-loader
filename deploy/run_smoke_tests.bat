@echo off
REM ============================================================================
REM Supplier Invoice Loader - Smoke Tests
REM Quick tests before creating deployment package
REM ============================================================================

echo ============================================================================
echo Supplier Invoice Loader - Smoke Tests
echo ============================================================================
echo.
echo These are QUICK tests to verify basic functionality before deployment.
echo Detailed testing will be done at customer site.
echo.

set ERRORS=0

REM ============================================================================
echo [1/4] Testing Python imports...
echo ============================================================================
echo.

python -c "import main; print('[OK] main.py')" 2>nul
if errorlevel 1 (
    echo [FAIL] main.py import error
    set /a ERRORS+=1
) else (
    echo [OK] main.py imported successfully
)

python -c "import config; print('[OK] config.py')" 2>nul
if errorlevel 1 (
    echo [FAIL] config.py import error
    set /a ERRORS+=1
) else (
    echo [OK] config.py imported successfully
)

python -c "import database; print('[OK] database.py')" 2>nul
if errorlevel 1 (
    echo [FAIL] database.py import error
    set /a ERRORS+=1
) else (
    echo [OK] database.py imported successfully
)

python -c "import isdoc; print('[OK] isdoc.py')" 2>nul
if errorlevel 1 (
    echo [FAIL] isdoc.py import error
    set /a ERRORS+=1
) else (
    echo [OK] isdoc.py imported successfully
)

python -c "import notifications; print('[OK] notifications.py')" 2>nul
if errorlevel 1 (
    echo [FAIL] notifications.py import error
    set /a ERRORS+=1
) else (
    echo [OK] notifications.py imported successfully
)

python -c "import monitoring; print('[OK] monitoring.py')" 2>nul
if errorlevel 1 (
    echo [FAIL] monitoring.py import error
    set /a ERRORS+=1
) else (
    echo [OK] monitoring.py imported successfully
)

python -c "from extractors import GenericExtractor; print('[OK] extractors')" 2>nul
if errorlevel 1 (
    echo [FAIL] extractors import error
    set /a ERRORS+=1
) else (
    echo [OK] extractors imported successfully
)

echo.

REM ============================================================================
echo [2/4] Testing dependencies...
echo ============================================================================
echo.

python -c "import fastapi; print('[OK] FastAPI')" 2>nul
if errorlevel 1 (
    echo [FAIL] FastAPI not installed
    set /a ERRORS+=1
) else (
    echo [OK] FastAPI installed
)

python -c "import pdfplumber; print('[OK] pdfplumber')" 2>nul
if errorlevel 1 (
    echo [FAIL] pdfplumber not installed
    set /a ERRORS+=1
) else (
    echo [OK] pdfplumber installed
)

python -c "import lxml; print('[OK] lxml')" 2>nul
if errorlevel 1 (
    echo [FAIL] lxml not installed
    set /a ERRORS+=1
) else (
    echo [OK] lxml installed
)

python -c "import uvicorn; print('[OK] uvicorn')" 2>nul
if errorlevel 1 (
    echo [FAIL] uvicorn not installed
    set /a ERRORS+=1
) else (
    echo [OK] uvicorn installed
)

echo.

REM ============================================================================
echo [3/4] Testing configuration files...
echo ============================================================================
echo.

if exist config.py (
    echo [OK] config.py exists
) else (
    echo [FAIL] config.py missing
    set /a ERRORS+=1
)

if exist config_template.py (
    echo [OK] config_template.py exists
) else (
    echo [FAIL] config_template.py missing
    set /a ERRORS+=1
)

if exist requirements.txt (
    echo [OK] requirements.txt exists
) else (
    echo [FAIL] requirements.txt missing
    set /a ERRORS+=1
)

if exist .env.example (
    echo [OK] .env.example exists
) else (
    echo [FAIL] .env.example missing
    set /a ERRORS+=1
)

if exist extractors\generic_extractor.py (
    echo [OK] extractors directory OK
) else (
    echo [FAIL] extractors missing
    set /a ERRORS+=1
)

echo.

REM ============================================================================
echo [4/4] Testing application startup...
echo ============================================================================
echo.
echo Starting application for 5 seconds...
echo (This will test if the API starts without errors)
echo.

REM Start the application in background
start /B python main.py >test_startup.log 2>&1
set PID=%ERRORLEVEL%

REM Wait 5 seconds
timeout /t 5 /nobreak >nul

REM Try to access the API docs
echo Testing API endpoint...
curl -s http://localhost:8000/docs >nul 2>&1
if errorlevel 1 (
    echo [FAIL] API not responding
    set /a ERRORS+=1
) else (
    echo [OK] API is responding
)

REM Kill the application
taskkill /F /IM python.exe >nul 2>&1

REM Check startup log for errors
findstr /I "ERROR Exception Traceback" test_startup.log >nul 2>&1
if not errorlevel 1 (
    echo [WARN] Errors found in startup log
    echo Check test_startup.log for details
    set /a ERRORS+=1
) else (
    echo [OK] No critical errors in startup log
)

echo.

REM ============================================================================
echo ============================================================================
echo SMOKE TESTS SUMMARY
echo ============================================================================
echo.

if %ERRORS% EQU 0 (
    echo ============================================
    echo SUCCESS - ALL TESTS PASSED
    echo ============================================
    echo.
    echo The application is ready for deployment.
    echo You can now create the deployment package.
    echo.
    echo Next step: create_deployment_package.bat
    echo.
    goto END
)

echo ============================================
echo FAILED - %ERRORS% TEST(S) FAILED
echo ============================================
echo.
echo Please fix the errors before creating deployment package.
echo.
echo Common issues:
echo - Missing dependencies: pip install -r requirements.txt
echo - Import errors: Check if all files are present
echo - API startup errors: Check test_startup.log
echo.

:END

REM Cleanup
if exist test_startup.log del test_startup.log

echo ============================================================================
pause
exit /b %ERRORS%
