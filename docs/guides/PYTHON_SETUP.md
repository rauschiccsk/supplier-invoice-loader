# Python Environment Setup Guide

Complete guide for setting up Python environment for Supplier Invoice Loader.

---

## Requirements

### Python Version

**Required:** Python 3.10 or later  
**Recommended:** Python 3.11 or 3.12  
**Not supported:** Python 3.9 or earlier, Python 2.x

**Why Python 3.10+?**
- Modern type hints (PEP 604 - Union types with `|`)
- Structural pattern matching
- Better performance
- Active security support

---

## Installation

### Windows

**Option A: Official Python Installer (Recommended)**

1. Download Python from https://www.python.org/downloads/
   - Get latest 3.11.x or 3.12.x version
   - Choose "Windows installer (64-bit)"

2. Run installer:
   - ✅ **CHECK** "Add Python to PATH" (IMPORTANT!)
   - ✅ **CHECK** "Install pip"
   - Click "Install Now" or "Customize Installation"
   
3. Verify installation:
   ```powershell
   python --version
   # Should show: Python 3.11.x or 3.12.x
   
   pip --version
   # Should show: pip 23.x.x or later
   ```

**Option B: Windows Store**

1. Open Microsoft Store
2. Search "Python 3.11" or "Python 3.12"
3. Click "Get" / "Install"
4. Automatically adds to PATH

**Option C: Chocolatey (Package Manager)**

```powershell
# Install Chocolatey first (if not installed):
# https://chocolatey.org/install

# Install Python
choco install python --version=3.11.6

# Verify
python --version
```

**Troubleshooting Windows:**

**Problem: `python` command not found**
```powershell
# Check if Python is installed
where python

# If not found, add to PATH manually:
# 1. Open System Properties → Environment Variables
# 2. Edit "Path" under System variables
# 3. Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311
# 4. Add: C:\Users\YourName\AppData\Local\Programs\Python\Python311\Scripts
# 5. Restart PowerShell
```

**Problem: `pip` not found**
```powershell
# Reinstall pip
python -m ensurepip --upgrade

# Or download get-pip.py
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

---

### Linux (Ubuntu/Debian)

**Install Python 3.11:**

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Install pip
sudo apt install python3-pip -y

# Verify
python3.11 --version
pip3 --version
```

**Set as default (optional):**

```bash
# Create alias
echo 'alias python=python3.11' >> ~/.bashrc
source ~/.bashrc

# Or use update-alternatives
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1
```

**Ubuntu 22.04+ has Python 3.10 by default:**
```bash
# Check version
python3 --version

# If 3.10+, you're good!
# Just use python3 instead of python3.11
```

**Install from deadsnakes PPA (for older Ubuntu):**

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev
```

---

### Linux (CentOS/RHEL/Fedora)

**RHEL 8 / CentOS 8:**

```bash
# Enable PowerTools repository
sudo dnf config-manager --set-enabled powertools

# Install Python 3.11
sudo dnf install python3.11 python3.11-devel -y

# Verify
python3.11 --version
```

**Fedora:**

```bash
# Python 3.11+ should be available
sudo dnf install python3 python3-pip python3-devel -y
```

---

### macOS

**Option A: Homebrew (Recommended)**

```bash
# Install Homebrew first (if not installed):
# https://brew.sh/

# Install Python
brew install python@3.11

# Verify
python3 --version
pip3 --version
```

**Option B: Official Installer**

1. Download from https://www.python.org/downloads/macos/
2. Run .pkg installer
3. Follow installation wizard

---

## Virtual Environment Setup

### Why Virtual Environments?

- **Isolation:** Each project has its own dependencies
- **Version control:** Different projects can use different package versions
- **Clean:** Easy to delete and recreate
- **Best practice:** Avoid polluting system Python

### Create Virtual Environment

**Windows:**

```powershell
# Navigate to project directory
cd C:\SupplierInvoiceLoader

# Create virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Verify (prompt should show (venv))
(venv) PS C:\SupplierInvoiceLoader>
```

**Linux/macOS:**

```bash
# Navigate to project directory
cd /opt/supplier_invoice_loader

# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Verify (prompt should show (venv))
(venv) user@server:/opt/supplier_invoice_loader$
```

### Deactivate Virtual Environment

```bash
deactivate
```

### Delete Virtual Environment

```bash
# Simply delete the directory
# Windows:
Remove-Item -Recurse -Force venv

# Linux/Mac:
rm -rf venv
```

---

## Installing Dependencies

### Production Dependencies

```bash
# Activate virtual environment first!
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install production dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages:**
```
fastapi        0.104.1
uvicorn        0.24.0.post1
pydantic       2.5.0
pdfplumber     0.10.3
lxml           4.9.3
python-dotenv  1.0.0
psutil         5.9.6
...
```

### Development Dependencies

```bash
# Install development + production dependencies
pip install -r requirements-dev.txt

# This installs:
# - All production dependencies (from requirements.txt)
# - Testing tools (pytest, pytest-cov)
# - Code quality tools (black, flake8, mypy)
# - Security scanners (safety, bandit)
# - Debugging tools (ipython, ipdb)
```

---

## Dependency Management

### Check Installed Packages

```bash
# List all installed packages
pip list

# Show specific package
pip show fastapi

# Check outdated packages
pip list --outdated
```

### Update Dependencies

**Update single package:**
```bash
pip install --upgrade fastapi
```

**Update all packages (CAREFULLY!):**
```bash
# First, test in development!
pip install --upgrade -r requirements.txt

# Check if application still works
python main.py
```

**Best practice:**
1. Update one package at a time
2. Test thoroughly after each update
3. Commit to Git after successful update
4. Monitor logs for issues

### Security Scanning

```bash
# Install safety (if not installed)
pip install safety

# Check for known vulnerabilities
safety check

# Check specific requirements file
safety check -r requirements.txt

# Check with detailed output
safety check --full-report
```

**Example output:**
```
+==============================================================================+
|                                                                              |
|                               /$$$$$$            /$$                         |
|                              /$$__  $$          | $$                         |
|           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           |
|          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           |
|         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           |
|          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           |
|          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           |
|         |_______/  \_______/|__/     \_______/   \___/   \____  $$           |
|                                                          /$$  | $$           |
|                                                         |  $$$$$$/           |
|  by pyup.io                                              \______/            |
|                                                                              |
+==============================================================================+
|                                                                              |
|  REPORT                                                                      |
|  No known security vulnerabilities found.                                   |
|                                                                              |
+==============================================================================+
```

### Freeze Dependencies

```bash
# Save exact versions of all installed packages
pip freeze > requirements-frozen.txt

# Useful for:
# - Exact reproduction of environment
# - Troubleshooting dependency issues
# - Rollback if update causes problems
```

---

## Version Pinning Strategy

### Current Strategy

**Critical packages (exact version):**
- `fastapi==0.104.1` - Core framework
- `pydantic==2.5.0` - Data validation
- `lxml==4.9.3` - ISDOC XML generation
- `pdfplumber==0.10.3` - PDF extraction

**Why exact versions?**
- Stability and reproducibility
- Avoid breaking changes
- Known good versions

**Non-critical packages (minimum version):**
- `uvicorn>=0.24.0` - Allow minor updates
- `psutil>=5.9.0` - Bug fixes welcomed

### Update Checklist

Before updating dependencies:

- [ ] Read changelog for breaking changes
- [ ] Update in development environment first
- [ ] Run full test suite
- [ ] Test invoice processing end-to-end
- [ ] Check logs for warnings/errors
- [ ] Monitor for 24-48 hours
- [ ] Update in production if stable
- [ ] Update requirements.txt version
- [ ] Commit changes to Git

---

## Python Version Upgrade

### Upgrading Python (e.g., 3.10 → 3.11)

**Procedure:**

1. **Install new Python version:**
   ```bash
   # Windows: Download new installer
   # Linux: sudo apt install python3.11
   ```

2. **Create new virtual environment:**
   ```bash
   # Don't delete old venv yet!
   python3.11 -m venv venv-new
   ```

3. **Activate new environment:**
   ```bash
   source venv-new/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Test thoroughly:**
   ```bash
   python main.py
   # Test all functionality
   ```

6. **If successful, replace old venv:**
   ```bash
   deactivate
   rm -rf venv
   mv venv-new venv
   ```

7. **Update documentation:**
   - Update PYTHON_SETUP.md
   - Update README.md
   - Update deployment guides

---

## Common Issues

### Issue: `ModuleNotFoundError`

**Symptom:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**

1. **Ensure virtual environment is activated:**
   ```bash
   # Check prompt for (venv)
   # If not, activate:
   source venv/bin/activate  # Linux/Mac
   .\venv\Scripts\activate   # Windows
   ```

2. **Check Python path:**
   ```bash
   which python  # Linux/Mac
   where python  # Windows
   
   # Should point to venv/bin/python or venv\Scripts\python.exe
   ```

3. **Reinstall dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

### Issue: `pip` SSL Certificate Error

**Symptom:**
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions:**

1. **Update certificates:**
   ```bash
   pip install --upgrade certifi
   ```

2. **Temporary bypass (NOT recommended for production):**
   ```bash
   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

3. **Corporate proxy:**
   ```bash
   # Set proxy
   set HTTP_PROXY=http://proxy.company.com:8080
   set HTTPS_PROXY=http://proxy.company.com:8080
   
   pip install -r requirements.txt
   ```

---

### Issue: Permission Denied (Linux)

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Don't use sudo with pip inside venv:**
   ```bash
   # WRONG:
   sudo pip install -r requirements.txt
   
   # CORRECT:
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Fix venv ownership:**
   ```bash
   sudo chown -R $USER:$USER venv/
   ```

---

### Issue: Long Path Error (Windows)

**Symptom:**
```
FileNotFoundError: [WinError 206] The filename or extension is too long
```

**Solutions:**

1. **Enable long paths:**
   ```powershell
   # Run as Administrator
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

2. **Use shorter project path:**
   ```
   C:\SupplierInvoiceLoader  # Good
   C:\Users\VeryLongUsername\Documents\Projects\SupplierInvoiceLoader  # Too long
   ```

---

## Best Practices

### 1. Always Use Virtual Environments

```bash
# NEVER install packages globally
pip install fastapi  # ❌ Wrong

# ALWAYS use virtual environment
python -m venv venv
source venv/bin/activate
pip install fastapi  # ✅ Correct
```

### 2. Keep requirements.txt Updated

```bash
# After installing new package:
pip freeze > requirements.txt

# Better: Only add what you need manually
echo "new-package==1.0.0" >> requirements.txt
```

### 3. Separate Dev and Prod Dependencies

```
requirements.txt        # Production only
requirements-dev.txt    # Development tools (includes requirements.txt)
```

### 4. Document Python Version

```python
# In setup.py or pyproject.toml
python_requires='>=3.10'
```

### 5. Regular Security Audits

```bash
# Weekly check
safety check

# Monthly full scan
safety check --full-report
bandit -r .
```

---

## IDE Configuration

### PyCharm

1. **Set Python Interpreter:**
   - File → Settings → Project → Python Interpreter
   - Click gear icon → Add
   - Select "Existing environment"
   - Browse to `venv/bin/python` or `venv\Scripts\python.exe`

2. **Enable Code Quality Tools:**
   - Settings → Tools → Black
   - Settings → Tools → External Tools → Add flake8, mypy

### VS Code

1. **Select Python Interpreter:**
   - Ctrl+Shift+P → "Python: Select Interpreter"
   - Choose `./venv/bin/python`

2. **Install Python extension:**
   - Microsoft Python extension
   - Pylance for type checking

3. **Configure settings.json:**
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true,
     "python.formatting.provider": "black",
     "python.linting.mypyEnabled": true
   }
   ```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Python Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest
    
    - name: Security check
      run: safety check
```

---

## Resources

### Documentation
- Python Official: https://docs.python.org/3/
- pip Documentation: https://pip.pypa.io/
- Virtual Environments: https://docs.python.org/3/tutorial/venv.html
- PyPI (Python Package Index): https://pypi.org/

### Tools
- Python Version Manager (pyenv): https://github.com/pyenv/pyenv
- Poetry (Alternative to pip): https://python-poetry.org/
- pipx (Install CLI tools): https://pypa.github.io/pipx/

### Learning
- Real Python: https://realpython.com/
- Python Tutorial: https://docs.python.org/3/tutorial/
- PEP 8 Style Guide: https://pep8.org/

---

## Support

For Python environment issues:

1. Check this guide first
2. Search error message on Stack Overflow
3. Check project logs: `invoice_loader.log`
4. Contact: support@icc.sk

---

**END OF PYTHON SETUP GUIDE**