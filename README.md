# Supplier Invoice Loader

Automatické spracovanie faktúr od viacerých dodávateľov pre NEX Genesis.

## Version 2.0 - Multi-Supplier Support

Systém podporuje automatické spracovanie faktúr od viacerých dodávateľov s:
- Human-in-loop validácia (operátor prepošle faktúry)
- Špecifické extraction engines pre každého dodávateľa
- Jednotný ISDOC XML výstup
- Integrácia s NEX Genesis API

## History
- v1.1.0 - IMAP trigger, základný workflow pre L&Š
- v2.0.0 - Multi-supplier architecture (in development)

---

## 🔒 Security & Configuration

### ⚠️ IMPORTANT: Before First Use

**NEVER commit sensitive data to Git!**

1. **Create customer configuration:**
   ```bash
   cp config_template.py config_customer.py
   # Edit config_customer.py with your values
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   # Edit .env with your secrets (API keys, SMTP passwords)
   ```

3. **Verify .gitignore:**
   - `config_customer.py` should NOT be committed
   - `.env` should NOT be committed
   - `*.log` files should NOT be committed
   - Check before every commit!

### Security Best Practices

- 📖 **Read [SECURITY.md](docs/guides/SECURITY.md)** for complete security guidelines
- 🔑 Use strong random API keys (32+ characters)
- 🔐 Use Gmail App Passwords (not regular passwords)
- 🔄 Rotate API keys quarterly
- 🚫 Never commit secrets to Git
- 🔒 Restrict file permissions on production servers
- 📊 Monitor logs regularly for security issues

### Environment Variables

The application supports configuration via environment variables:

**Required:**
- `LS_API_KEY` - API key for FastAPI endpoints
- `SMTP_USER` - SMTP username for email alerts
- `SMTP_PASSWORD` - SMTP password (use App Password for Gmail)

**Optional:**
- `LS_STORAGE_PATH` - Override storage location
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `NEX_API_KEY` - NEX Genesis API key

**Setup:**
```bash
# Development: Use .env file
cp .env.example .env
# Edit .env with your values

# Production: Use system environment variables (recommended)
# Windows:
$env:LS_API_KEY = "your-secure-key"
# Linux:
export LS_API_KEY="your-secure-key"
```

---

## 📦 Installation

### Prerequisites

- Python 3.10 or later
- pip (Python package manager)
- Virtual environment (recommended)

### Quick Start

```bash
# Clone repository
git clone https://github.com/rauschiccsk/supplier_invoice_loader.git
cd supplier_invoice_loader
git checkout v2.0-multi-customer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configuration
cp config_template.py config_customer.py
cp .env.example .env
# Edit both files with your values!

# Run application
python main.py
```

### Development Setup

```bash
# Install development dependencies (testing, linting, etc.)
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .

# Check code quality
flake8 .
mypy .

# Security checks
safety check
bandit -r .
```

---

## 📚 Documentation

### Deployment & Configuration

- **[DEPLOYMENT_CHECKLIST.md](docs/deployment/DEPLOYMENT_CHECKLIST.md)** - Step-by-step deployment guide
- **[config_template.py](config_template.py)** - Configuration parameters explained
- **[SECURITY.md](docs/guides/SECURITY.md)** - Security guidelines and best practices
- **[TROUBLESHOOTING.md](docs/operations/TROUBLESHOOTING.md)** - Common issues and solutions

### N8N Workflow

- **[N8N_WORKFLOW_SETUP.md](docs/guides/N8N_WORKFLOW_SETUP.md)** - n8n workflow setup guide
- **[n8n_workflow_template.json](n8n_workflow_template.json)** - Workflow template

### API Documentation

FastAPI provides interactive API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Monitoring Endpoints

- `GET /health` - Basic health check (no auth)
- `GET /status` - Detailed system status (requires API key)
- `GET /metrics` - Metrics in JSON format (no auth)
- `GET /metrics/prometheus` - Prometheus format metrics (no auth)
- `GET /stats` - Database statistics (no auth)

See [MONITORING.md](docs/operations/MONITORING.md) for complete monitoring setup guide.

---

## 🚀 Usage

### Running as Service

**Windows (NSSM):**
```powershell
# See DEPLOYMENT_CHECKLIST.md for complete instructions
nssm install SupplierInvoiceLoader "C:\path\to\venv\Scripts\python.exe" "C:\path\to\main.py"
nssm start SupplierInvoiceLoader
```

**Linux (systemd):**
```bash
# See DEPLOYMENT_CHECKLIST.md for complete instructions
sudo systemctl enable supplier-invoice-loader
sudo systemctl start supplier-invoice-loader
```

### API Endpoints

- `GET /` - Service info
- `GET /health` - Health check (no auth)
- `POST /invoice` - Process invoice (requires API key)
- `GET /invoices` - List invoices (requires API key)
- `GET /stats` - Statistics (no auth)

**Example API call:**
```bash
curl -X POST http://localhost:8000/invoice \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "file_b64": "...",
    "filename": "invoice.pdf",
    "from": "operator@customer.sk",
    "subject": "Faktúra",
    "message_id": "..."
  }'
```

---

## 🔧 Configuration

### Customer-Specific Settings

Edit `config_customer.py`:

```python
# Customer identification
CUSTOMER_NAME = "MAGERSTAV"
CUSTOMER_FULL_NAME = "MÁGERSTAV, spol. s r.o."

# NEX Genesis API
NEX_GENESIS_API_URL = "http://192.168.1.50:8080/api"
NEX_GENESIS_API_KEY = "your-nex-api-key"

# Email addresses
OPERATOR_EMAIL = "operator@customer.sk"
AUTOMATION_EMAIL = "automation-customer@isnex.ai"
ALERT_EMAIL = "it@customer.sk"

# Monitoring
SEND_DAILY_SUMMARY = True
HEARTBEAT_ENABLED = True
```

See [config_template.py](config_template.py) for all parameters.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_extraction.py

# Test health endpoint
curl http://localhost:8000/health
```

---

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](docs/operations/TROUBLESHOOTING.md) for solutions to common issues.

**Quick checks:**
- Is Python 3.10+ installed? `python --version`
- Is virtual environment activated? `which python` / `where python`
- Are dependencies installed? `pip list | grep fastapi`
- Is service running? `Get-Service` / `systemctl status`
- Can you reach health endpoint? `curl http://localhost:8000/health`

---

## 🤝 Contributing

This is an internal project for ICC customers. For issues or improvements:

1. Create GitHub issue with details
2. Contact: support@icc.sk
3. For security issues: security@icc.sk (see [SECURITY.md](docs/guides/SECURITY.md))

---

## 📄 License

Proprietary - Internal use only for ICC customers.

---

## 📞 Support

- **Documentation:** This README and linked docs
- **Email:** support@icc.sk
- **Emergency:** +421 XXX XXX XXX
- **GitHub Issues:** https://github.com/rauschiccsk/supplier_invoice_loader/issues

---

## ⚠️ Important Notes

### Before Deployment

- [ ] Read [SECURITY.md](docs/guides/SECURITY.md) completely
- [ ] Generate strong API key (32+ characters)
- [ ] Configure `config_customer.py` with real values
- [ ] Set up `.env` with secrets (or use system environment variables)
- [ ] Test on development environment first
- [ ] Verify firewall rules
- [ ] Set up backups
- [ ] Configure monitoring

### Regular Maintenance

- **Weekly:** Review logs for errors
- **Monthly:** Check for dependency updates
- **Quarterly:** Rotate API keys, review security
- **Yearly:** Full security audit

---

*Last updated: October 2025*