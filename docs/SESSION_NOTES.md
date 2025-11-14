# Session Notes - Supplier Invoice Loader

**Project:** supplier-invoice-loader  
**Last Updated:** 2025-11-14  
**Status:** ✅ Production Ready - Refactored Structure

---

## 🎯 Project Overview

Automatizované spracovanie dodávateľských faktúr cez email → n8n → Python FastAPI → NEX Genesis.

**Tech Stack:**
- Python 3.10+, FastAPI, SQLite, pdfplumber
- n8n workflows, Cloudflared tunnels
- Windows Service deployment

**Zákazníci:**
- MAGERSTAV, spol. s r.o. (production)
- ANDROS (planned)

**Dodávatelia:**
- L&Š, s.r.o. (IČO: 36555720)

---

## ✅ Completed Work

### STORY 1 - Production Ready (October 2025)
- Multi-customer SaaS architecture
- PDF extraction engine (pdfplumber)
- SQLite database v2 with multi-customer support
- Email notifications & alerting
- Windows Service support
- Cloudflared tunnel setup
- 80+ unit tests
- Complete documentation

### Project Refactoring (November 2025)

**Phase 1 - Project Structure:**
- Created new GitHub repository: supplier-invoice-loader
- Built professional src/ modular architecture
- Organized documentation into subdirectories
- Generated INIT_PROMPT_NEW_CHAT.md and unified docs

**Phase 2 - Code Migration:**
- Migrated 18 Python modules from root to src/
- Updated all imports to use src. prefix
- Moved scripts to scripts/
- Reorganized tests to tests/unit/
- Created minimal main.py entry point
- Clean root directory (6 files only)

**Phase 3 - Documentation:**
- Reorganized docs into guides/, operations/, deployment/
- Updated INIT_PROMPT with new structure
- Professional project organization

---

## 🗂️ Project Structure

```
supplier-invoice-loader/
├── src/                           # Python source code
│   ├── api/                      # FastAPI models
│   ├── business/                 # Business logic (ISDOC)
│   ├── database/                 # SQLite operations
│   ├── extractors/               # PDF extraction
│   └── utils/                    # Config, notifications, monitoring
├── docs/                          # Documentation
│   ├── guides/                   # Development guides
│   ├── operations/               # User & operations manuals
│   ├── deployment/               # Deployment guides
│   ├── architecture/             # Technical docs
│   └── database/                 # DB schemas
├── scripts/                       # Utility scripts
├── config/                        # Configuration files
├── tests/                         # Test suite
├── deploy/                        # Deployment scripts
├── n8n-workflows/                # n8n workflow definitions
├── main.py                       # Application entry point
├── requirements.txt              # Dependencies
└── README.md
```

---

## 🔑 Critical Configuration

### MAGERSTAV
- IČO: 31436871
- PDF Storage: `G:\NEX\IMPORT\LS\PDF`
- XML Storage: `G:\NEX\IMPORT\LS\XML`
- Database: `C:\invoice-loader\invoices.db`

### L&Š Supplier
- IČO: 36555720
- Email: faktury@farby.sk
- Extractor: `src/extractors/ls_extractor.py`

### Cloudflared Tunnel
- URL: https://magerstav-invoices.icc.sk
- Tunnel ID: 0fdfffe9-b348-44b5-adcc-969681ac2786

---

## 🚀 Development Commands

### Setup
```bash
cd C:\Development\supplier-invoice-loader
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### Run Application
```bash
python main.py
# Server: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Testing
```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest --cov=src --cov-report=html
```

### Import Verification
```bash
python -c "from src.database import database; print('✅ OK')"
python -c "from src.extractors.ls_extractor import LSExtractor; print('✅ OK')"
```

---

## 📋 Architecture

### Data Flow
```
Gmail IMAP
  ↓
n8n Workflow (email monitoring)
  ↓
Python FastAPI Server (localhost:8000)
  ↓
PDF Extraction (pdfplumber)
  ↓
SQLite Database (invoices.db)
  ↓
XML Generation (ISDOC format)
  ↓
NEX Genesis API (customer ERP)
```

### Key Components

**src/extractors/ls_extractor.py:**
- L&Š specific PDF parser
- Extracts invoice data (number, date, amount, items)
- Handles multi-page invoices
- 100% success rate on 19 test invoices

**src/database/database.py:**
- SQLite wrapper with multi-customer support
- Duplicate detection (file hash)
- Status tracking (received, processed, error)
- NEX Genesis sync status

**src/business/isdoc_service.py:**
- ISDOC XML generation (Czech standard)
- Invoice data transformation
- XML validation

**src/utils/notifications.py:**
- Email alerts (errors, duplicates, daily summary)
- Gmail SMTP integration
- Template-based notifications

**src/utils/monitoring.py:**
- System health checks
- Disk space monitoring
- Process monitoring
- Heartbeat endpoint

---

## 🔧 Technical Details

### Database Schema (SQLite)
- Table: invoices
- Key fields: file_hash (unique), invoice_number, customer_name
- Indexes: file_hash, invoice_number, status, customer_name
- Status values: received, processed, error, partial
- NEX sync: pending, synced, error

### Import Structure
All imports use `from src.module import`:
```python
from src.database import database
from src.api import models
from src.extractors.ls_extractor import LSExtractor
from src.business import isdoc_service
from src.utils import notifications, monitoring, config
```

### Configuration
- `config/config_customer.py` - customer-specific settings
- `config/config.template.yaml` - YAML config template
- `.env` - environment variables (not in Git)

---

## 📝 Known Issues & Solutions

### Issue: PDF Extraction Failed
**Solution:** Check if PDF is scanned image (needs OCR) or actual text

### Issue: Duplicate Detection
**Solution:** Uses SHA-256 file hash, checks before processing

### Issue: Windows Service Won't Start
**Solution:** Check Python path, port 8000 availability, logs at `C:\invoice-loader\logs\`

### Issue: Email Notifications Not Sending
**Solution:** Verify Gmail App Password in .env, check SMTP settings

---

## 🎯 Next Steps

### Immediate (Testing)
1. Test main.py v novom prostredí
2. Verify všetky importy fungujú
3. Run pytest suite
4. Test v novom Claude chate s INIT_PROMPT

### Short-term (STORY 2)
- Human-in-loop validation UI
- Web interface for operators
- Approve/Reject workflow

### Long-term (STORY 3-6)
- NEX Genesis API direct integration
- OCR support for scanned PDFs
- Advanced monitoring dashboard
- Multi-supplier factory pattern

---

## 💡 Best Practices

1. **Vždy commit pred limitom chatu**
2. **Používaj INIT_PROMPT_NEW_CHAT.md pre nové chaty**
3. **Testuj na reálnych dátach pred deployment**
4. **Aktualizuj SESSION_NOTES.md po dokončení práce**
5. **Review code changes pred commit**
6. **Use src. prefix pre všetky importy**

---

## 📞 Contact

**Developer:** rausch@icc.sk  
**Organization:** ICC Komárno  
**GitHub:** https://github.com/rauschiccsk/supplier-invoice-loader

---

**End of Session Notes**