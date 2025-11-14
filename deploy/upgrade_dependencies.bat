@echo off
REM ============================================================================
REM Upgrade Dependencies for Python 3.13
REM ============================================================================

echo ============================================================================
echo Upgrading Dependencies for Python 3.13
echo ============================================================================
echo.

echo This will upgrade all dependencies to versions compatible with Python 3.13
echo.
pause

echo.
echo [1/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [2/4] Uninstalling problematic old versions...
pip uninstall -y lxml Pillow 2>nul

echo.
echo [3/4] Installing core dependencies...
pip install fastapi==0.115.0
pip install uvicorn[standard]==0.32.0
pip install pydantic==2.9.0
pip install python-multipart==0.0.12
pip install pdfplumber==0.11.4
pip install PyPDF2==3.0.1
pip install "Pillow>=10.4.0"
pip install "lxml>=5.0.0"
pip install python-dotenv==1.0.1
pip install psutil==6.0.0
pip install "requests>=2.31.0"

echo.
echo [4/4] Verifying installation...
python -c "import fastapi; print('✓ FastAPI:', fastapi.__version__)"
python -c "import uvicorn; print('✓ Uvicorn:', uvicorn.__version__)"
python -c "import pydantic; print('✓ Pydantic:', pydantic.__version__)"
python -c "import pdfplumber; print('✓ pdfplumber:', pdfplumber.__version__)"
python -c "import PIL; print('✓ Pillow:', PIL.__version__)"
python -c "import lxml; print('✓ lxml:', lxml.__version__)"
python -c "import dotenv; print('✓ python-dotenv')"
python -c "import psutil; print('✓ psutil:', psutil.__version__)"
python -c "import requests; print('✓ requests:', requests.__version__)"

echo.
echo ============================================================================
echo Upgrade Complete!
echo ============================================================================
echo.
echo You can now run: run_smoke_tests.bat
echo.
pause
