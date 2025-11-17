# Supplier Invoice Loader - Init Prompt

**Project:** supplier-invoice-loader (refactored structure)  
**Version:** 2.0  
**GitHub:** https://github.com/rauschiccsk/supplier-invoice-loader  
**Last Updated:** 2025-11-17

---

## 🎯 Quick Start

Pre nový chat načítaj tento URL:
```
https://raw.githubusercontent.com/rauschiccsk/supplier-invoice-loader/main/docs/INIT_PROMPT_NEW_CHAT.md
```

Claude odpovie: **"✅ Projekt načítaný. Čo robíme?"**

---

## 📊 Project Overview

**Účel:** Automatizované spracovanie dodávateľských faktúr  
**Flow:** Email → n8n → Python FastAPI → NEX Genesis  
**Stack:** Python 3.11+, FastAPI, SQLite, n8n, Cloudflared

**Status:** Development - All Tests Passing ✅  
**Production:** STORY 1 Complete  
**Refactoring:** ✅ Phase 1 & 2 Complete - Professional src/ structure

---

## 🗂️ Projektová Štruktúra

```
supplier-invoice-loader/
├── .venv/                         # Virtual environment (Python 3.11.9)
├── src/                           # Python source code (modular)
│   ├── api/                      # FastAPI models
│   │   ├── __init__.py
│   │   └── models.py
│   ├── business/                 # Business logic
│   │   ├── __init__.py
│   │   └── isdoc_service.py
│   ├── database/                 # DB operations
│   │   ├── __init__.py
│   │   └── database.py
│   ├── extractors/               # PDF extraction
│   │   ├── __init__.py
│   │   ├── base_extractor.py
│   │   ├── generic_extractor.py
│   │   └── ls_extractor.py
│   └── utils/                    # Utilities
│       ├── __init__.py
│       ├── config.py
│       ├── env_loader.py
│       ├── notifications.py
│       └── monitoring.py
│
├── docs/                          # Documentation
│   ├── INIT_PROMPT_NEW_CHAT.md   # This file
│   ├── SESSION_NOTES.md          # Development history
│   ├── architecture/             # Architecture docs
│   ├── database/                 # DB schemas & docs
│   ├── deployment/               # Deployment guides
│   ├── operations/               # Operations manuals
│   └── guides/                   # Development guides
│
├── scripts/                       # Utility scripts
│   ├── generate_project_access.py  # Manifest generator
│   ├── service_installer.py        # Windows service installer
│   └── verify_installation.py      # Setup verification
│
├── config/                        # Configuration
│   ├── config_customer.py
│   ├── config_template.py
│   ├── config.template.yaml
│   └── .env.example
│
├── tests/                         # Test suite (69 passing ✅)
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── samples/                  # Test data
│   └── conftest.py
│
├── deploy/                        # Deployment scripts
├── n8n-workflows/                 # n8n workflow definitions
├── main.py                       # Application entry point (complete API)
├── requirements.txt              # Production dependencies
├── requirements-dev.txt          # Development dependencies
├── pyproject.toml               # Python project configuration
├── .gitignore
└── README.md
```

---

## 🔑 Kritická Konfigurácia

### Development Environment
- **Python:** 3.11.9 (in `.venv/`)
- **IDE:** PyCharm Community Edition 2024.2.4
- **Install Mode:** Editable (`pip install -e .`)
- **Package:** `supplier-invoice-loader==2.0.0`

### MAGERSTAV Setup
- **IČO:** 31436871
- **PDF Storage:** `G:\NEX\IMPORT\LS\PDF`
- **XML Storage:** `G:\NEX\IMPORT\LS\XML`
- **Database:** `C:\invoice-loader\invoices.db`

### L&Š Dodávateľ
- **IČO:** 36555720
- **Email:** faktury@farby.sk
- **Extractor:** `src/extractors/ls_extractor.py`

### Cloudflared Tunnel
- **URL:** https://magerstav-invoices.icc.sk
- **Tunnel ID:** 0fdfffe9-b348-44b5-adcc-969681ac2786

---

## 🚀 Quick Commands

### Development Setup
```powershell
cd C:\Development\supplier-invoice-loader

# Activate virtual environment (ALWAYS FIRST!)
.\.venv\Scripts\Activate.ps1

# Install dependencies (if needed)
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install project in editable mode
pip install -e .
```

### Run Application
```powershell
# Activate venv first!
.\.venv\Scripts\Activate.ps1

# Start server
python main.py

# Server: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### PyCharm
```
Run Configurations:
  - "Supplier Invoice Loader (FastAPI)" - Start server
  - "pytest - All Tests" - Run all tests
  - "pytest - Unit Tests" - Run unit tests only

External Tools:
  - Black - Format File (code formatter)
  - isort - Sort Imports (import organizer)
```

### Testing
```powershell
# Activate venv
.\.venv\Scripts\Activate.ps1

# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Specific test file
pytest tests/unit/test_api.py -v

# With coverage
pytest --cov=src --cov-report=html

# Current status: 69 passed, 0 failed, 2 skipped ✅
```

### Import Testing
```powershell
python -c "from src.database import database; print('✅ OK')"
python -c "from src.extractors.ls_extractor import LSExtractor; print('✅ OK')"
```

### Verification
```powershell
# Verify complete installation
python scripts/verify_installation.py
```

---

## 📋 Aktuálny Stav

### ✅ Complete API Implementation (2025-11-17)
- ✅ All 8 API endpoints implemented
- ✅ FastAPI request tracking middleware
- ✅ API key authentication (X-API-Key header)
- ✅ Health checks and monitoring endpoints
- ✅ Prometheus metrics support
- ✅ Error handling in all endpoints

### ✅ All Tests Passing (2025-11-17)
- ✅ 69 unit tests passing (100% success rate)
- ✅ 2 tests skipped (integration tests)
- ✅ 0 failing tests
- ✅ Coverage: ~80% overall
- ✅ API endpoint tests: 16/16 passing
- ✅ Config tests: 14/14 passing
- ✅ Monitoring tests: 20/20 passing
- ✅ Notification tests: 14/14 passing

### ✅ Development Environment Setup (2025-11-14)
- ✅ Python 3.11.9 virtual environment (`.venv/`)
- ✅ All dependencies installed (production + dev)
- ✅ Project installed in editable mode (`pip install -e .`)
- ✅ PyCharm configured (run configs, external tools)
- ✅ FastAPI server running (http://localhost:8000)
- ✅ Import fixes completed (src/utils/, tests/)

### ✅ Refactoring Complete (2025-11-14)
- ✅ Phase 1: Project structure & documentation
- ✅ Phase 2: Code migration to src/
- ✅ New GitHub repository: supplier-invoice-loader
- ✅ Professional modular architecture
- ✅ Organized documentation (guides/, operations/, deployment/)
- ✅ All imports updated to src. prefix

### ✅ STORY 1 - Production Ready
- Multi-customer architecture
- PDF extraction engine (pdfplumber)
- SQLite database v2
- Email notifications
- Windows Service support
- Cloudflared tunnel
- 69 unit tests (all passing)
- Complete documentation

### 📝 Planned (STORY 2-6)
- Human-in-loop validation (web UI)
- NEX Genesis API integration
- OCR support for scanned PDFs
- Advanced monitoring dashboard

---

## 📚 Dokumentácia

### Pre Operátorov
- [User Guide](operations/USER_GUIDE.md)
- [Troubleshooting](operations/TROUBLESHOOTING.md)
- [Monitoring](operations/MONITORING.md)
- [Email Alerting](operations/EMAIL_ALERTING.md)

### Pre Vývojárov
- [Development Guide](guides/DEVELOPMENT.md)
- [Testing Guide](guides/TESTING.md)
- [Python Setup](guides/PYTHON_SETUP.md)
- [Security](guides/SECURITY.md)
- [N8N Setup](guides/N8N_WORKFLOW_SETUP.md)
- [Session Notes](SESSION_NOTES.md)

### Deployment
- [Deployment Checklist](deployment/DEPLOYMENT_CHECKLIST.md)
- [Install Customer](deployment/INSTALL_CUSTOMER.md)
- [Windows Service Guide](deployment/WINDOWS_SERVICE_GUIDE.md)
- [Release Notes](deployment/RELEASE_NOTES_v2.0.0.md)

### Architektúra
- [Database Schema](database/TYPE_MAPPINGS.md)
- [Architecture Decisions](decisions/)

---

## 🔗 Rýchly Prístup

**Core Modules:**
- `main.py` - FastAPI application (complete with all endpoints)
- `src/api/models.py` - Pydantic models
- `src/database/database.py` - Database operations
- `src/extractors/ls_extractor.py` - L&Š PDF extractor
- `src/business/isdoc_service.py` - ISDOC XML generation
- `src/utils/notifications.py` - Email notifications (83% coverage)
- `src/utils/monitoring.py` - System monitoring & metrics

**Configuration:**
- `config/config.template.yaml` - Config template
- `config/config_customer.py` - Customer config

**Scripts:**
- `scripts/service_installer.py` - Windows service installer
- `scripts/generate_project_access.py` - Manifest generator
- `scripts/verify_installation.py` - Installation verification

**Testing:**
- `tests/unit/` - Unit tests (69 passing)
- `tests/conftest.py` - Pytest configuration & fixtures

---

## 💡 Best Practices

1. **VŽDY aktivuj venv pred prácou:** `.\.venv\Scripts\Activate.ps1`
2. **Commit pred limitom chatu**
3. **Session notes po každom pracovnom dni**
4. **Testuj na reálnych dátach**
5. **Používaj INIT_PROMPT ako single source of truth**
6. **Review code changes pred commit**
7. **Aktualizuj importy: používaj `from src.module import`**
8. **Regeneruj manifest po každom push:** `python scripts\generate_project_access.py`
9. **Všetky fixe cez .py scripty, nie .ps1**
10. **Run tests before commit:** `pytest tests/unit/ -v`

---

## 📞 Kontakt

**Developer:** rausch@icc.sk  
**Support:** support@icc.sk  
**GitHub:** @rauschiccsk  
**Organization:** ICC Komárno (Innovation & Consulting Center)

---

## 🗝️ Architektúra

### High-Level Flow
```
Email (Gmail) 
  ↓ n8n Workflow (IMAP trigger)
    ↓ Python FastAPI Server (invoice processing)
      ↓ PDF Extraction (pdfplumber)
        ↓ SQLite Database
          ↓ XML Generation (ISDOC)
            ↓ NEX Genesis API (customer ERP)
```

### Tech Stack
- **Backend:** Python 3.11+, FastAPI, Uvicorn
- **PDF Processing:** pdfplumber, PyPDF2
- **Database:** SQLite 3.x
- **Automation:** n8n workflows
- **Tunneling:** Cloudflared
- **Service:** Windows Service (NSSM wrapper)
- **Notifications:** Gmail SMTP
- **Development:** PyCharm, pytest, Black, isort

---

## 📖 Projekt Info

**Zákazníci:**
- MAGERSTAV, spol. s r.o. (production)
- ANDROS (planned)

**Dodávatelia:**
- L&Š, s.r.o. (IČO: 36555720) - farby, laky

**Environment:**
- Development: Windows 11, Python 3.11.9, PyCharm
- Production: Windows Server 2012 R2, Python 3.10+
- Local SQLite database
- Network file storage (PDF/XML)

---

**Pre kompletnú development history pozri:** [SESSION_NOTES.md](SESSION_NOTES.md)

**End of Init Prompt**