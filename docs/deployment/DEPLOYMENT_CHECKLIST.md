# 📋 Supplier Invoice Loader - Deployment Checklist

## Customer Information

- **Customer Name:** _______________________
- **Deployment Date:** _______________________
- **Deployed By:** _______________________
- **Server OS:** [ ] Windows Server [ ] Linux [ ] Other: _______
- **Python Version:** _______________________
- **Contact Person:** _______________________
- **Support Email:** _______________________

---

## 📦 Phase 1: Pre-Deployment Preparation

### 1.1 Infrastructure Requirements

- [ ] **Server Access**
  - [ ] SSH/RDP access confirmed
  - [ ] Admin/sudo privileges available
  - [ ] Server IP: _______________________
  - [ ] Server hostname: _______________________

- [ ] **System Requirements**
  - [ ] CPU: Minimum 2 cores
  - [ ] RAM: Minimum 4 GB
  - [ ] Disk space: Minimum 10 GB free
  - [ ] Network: Internet access for API calls

- [ ] **Software Prerequisites**
  - [ ] Python 3.8+ installed
  - [ ] pip package manager available
  - [ ] Git installed (optional but recommended)
  - [ ] SQLite3 available
  - [ ] Text editor available (nano/vim/notepad++)

### 1.2 Customer Information Gathering

- [ ] **NEX Genesis API Details**
  - [ ] API URL: _______________________
  - [ ] API Key: _______________________
  - [ ] API documentation received
  - [ ] Test endpoint verified

- [ ] **Email Configuration**
  - [ ] Operator email address: _______________________
  - [ ] Automation email created: _______________________
  - [ ] SMTP server details obtained
  - [ ] SMTP credentials secured

- [ ] **Business Information**
  - [ ] Company full legal name: _______________________
  - [ ] Company IČO: _______________________
  - [ ] Company DIČ: _______________________
  - [ ] Company IČ DPH: _______________________

### 1.3 Package Preparation

- [ ] **Download/Clone Repository**
  ```bash
  git clone https://github.com/rauschiccsk/supplier_invoice_loader.git
  cd supplier_invoice_loader
  git checkout v2.0-multi-customer
  ```

- [ ] **Or Extract Package**
  - [ ] Package extracted to target directory
  - [ ] All files verified present
  - [ ] Permissions checked

---

## 🔧 Phase 2: Installation

### 2.1 Environment Setup

- [ ] **Create Virtual Environment**
  ```bash
  # Linux/Mac
  python3 -m venv venv
  source venv/bin/activate
  
  # Windows
  python -m venv venv
  venv\Scripts\activate
  ```

- [ ] **Install Dependencies**
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] **Verify Installation**
  ```bash
  python -c "import fastapi, pydantic, sqlite3; print('Core packages OK')"
  ```

### 2.2 Configuration

- [ ] **Create Customer Configuration**
  ```bash
  cp config_template.py config_customer.py
  ```

- [ ] **Edit config_customer.py**
  - [ ] CUSTOMER_NAME = "_______"
  - [ ] CUSTOMER_FULL_NAME = "_______"
  - [ ] NEX_GENESIS_API_URL = "_______"
  - [ ] NEX_GENESIS_API_KEY = "_______"
  - [ ] OPERATOR_EMAIL = "_______"
  - [ ] AUTOMATION_EMAIL = "_______"
  - [ ] ALERT_EMAIL = "_______"
  - [ ] Storage paths configured

- [ ] **Create Environment File**
  ```bash
  cp .env.example .env
  ```

- [ ] **Edit .env**
  - [ ] LS_API_KEY generated (use strong random key)
  - [ ] SMTP_USER configured
  - [ ] SMTP_PASSWORD configured
  - [ ] LOG_LEVEL set (INFO for production)

- [ ] **Secure Configuration Files**
  ```bash
  # Linux/Mac
  chmod 600 .env
  chmod 644 config_customer.py
  
  # Windows
  # Right-click → Properties → Security → Edit permissions
  ```

### 2.3 Database Setup

- [ ] **Initialize Database**
  ```bash
  python -c "import database; database.init_database()"
  ```

- [ ] **Run Migration (if upgrading)**
  ```bash
  python migrate_v2.py --check
  python migrate_v2.py
  ```

- [ ] **Verify Database**
  ```bash
  sqlite3 invoices.db "SELECT COUNT(*) FROM invoices;"
  ```

### 2.4 Storage Setup

- [ ] **Create Storage Directories**
  ```bash
  # Default: C:\NEX_INVOICES or /opt/nex_invoices
  mkdir -p /path/to/storage/PDF
  mkdir -p /path/to/storage/XML
  ```

- [ ] **Set Permissions**
  ```bash
  # Linux
  chmod 755 /path/to/storage
  chown appuser:appgroup /path/to/storage
  
  # Windows
  # Right-click → Properties → Security → Edit
  ```

---

## 🧪 Phase 3: Testing

### 3.1 Component Testing

- [ ] **Test Configuration Loading**
  ```bash
  python -c "from config import *; print(f'Customer: {CUSTOMER_NAME}')"
  ```

- [ ] **Test Database Connection**
  ```bash
  python -c "import database; print(database.get_stats())"
  ```

- [ ] **Test Email Configuration**
  ```bash
  python notifications.py test
  ```

### 3.2 API Testing

- [ ] **Start Test Server**
  ```bash
  python main.py
  ```

- [ ] **Test Endpoints**
  - [ ] Health check: http://localhost:8000/health
  - [ ] API docs: http://localhost:8000/docs
  - [ ] Stats: http://localhost:8000/stats

- [ ] **Test with curl**
  ```bash
  curl http://localhost:8000/health
  curl -H "X-API-Key: YOUR_API_KEY" http://localhost:8000/invoices
  ```

### 3.3 Integration Testing

- [ ] **Test PDF Processing**
  - [ ] Place test PDF in watched folder
  - [ ] Verify extraction works
  - [ ] Check database entry created
  - [ ] Confirm XML generated

- [ ] **Test NEX Genesis Integration**
  - [ ] Send test request to NEX API
  - [ ] Verify authentication works
  - [ ] Test data sync

---

## 🚀 Phase 4: n8n Workflow Setup

### 4.1 n8n Configuration

- [ ] **Access n8n Instance**
  - [ ] URL: _______________________
  - [ ] Credentials obtained

- [ ] **Import Workflow Template**
  - [ ] Import n8n_workflow_template.json
  - [ ] Or create new workflow

### 4.2 Workflow Nodes Configuration

- [ ] **Email Trigger Node**
  - [ ] IMAP/Gmail credentials configured
  - [ ] Filter for AUTOMATION_EMAIL
  - [ ] Attachment handling enabled

- [ ] **HTTP Request Node**
  - [ ] URL: http://YOUR_SERVER:8000/invoice
  - [ ] Method: POST
  - [ ] Headers: X-API-Key configured
  - [ ] Body mapping configured

- [ ] **Error Handling**
  - [ ] Error notification node added
  - [ ] Retry logic configured
  - [ ] Logging enabled

### 4.3 Workflow Testing

- [ ] **Test Email Processing**
  - [ ] Send test email with PDF
  - [ ] Verify workflow triggers
  - [ ] Check API call succeeds
  - [ ] Confirm database entry

- [ ] **Test Error Scenarios**
  - [ ] Invalid PDF format
  - [ ] API unavailable
  - [ ] Duplicate detection

---

## 🎯 Phase 5: Production Deployment

### 5.1 Service Installation

#### Windows Service

- [ ] **Install NSSM (if not available)**
  - [ ] Download from https://nssm.cc
  - [ ] Extract to system PATH

- [ ] **Create Service**
  ```cmd
  cd deploy
  deploy.bat new %CUSTOMER_NAME%
  # Choose to install as service when prompted
  ```

- [ ] **Configure Service**
  - [ ] Startup type: Automatic
  - [ ] Recovery actions configured
  - [ ] Log rotation setup

#### Linux Service

- [ ] **Create systemd Service**
  ```bash
  cd deploy
  sudo ./deploy.sh new $CUSTOMER_NAME
  # Choose to install as service when prompted
  ```

- [ ] **Enable Service**
  ```bash
  sudo systemctl enable supplier-invoice-loader
  sudo systemctl start supplier-invoice-loader
  ```

### 5.2 Monitoring Setup

- [ ] **Internal Monitoring**
  - [ ] Health endpoint accessible
  - [ ] Metrics endpoint configured
  - [ ] Log files rotating properly

- [ ] **External Monitoring (Optional)**
  - [ ] Uptime monitoring configured
  - [ ] Alert thresholds set
  - [ ] Contact list updated

### 5.3 Backup Configuration

- [ ] **Database Backup**
  ```bash
  # Add to crontab (Linux)
  0 2 * * * sqlite3 /path/to/invoices.db ".backup /backups/invoices_$(date +\%Y\%m\%d).db"
  
  # Or Task Scheduler (Windows)
  ```

- [ ] **Configuration Backup**
  - [ ] config_customer.py backed up
  - [ ] .env backed up securely
  - [ ] Backup location: _______________________

---

## ✅ Phase 6: Validation & Handover

### 6.1 Final Validation

- [ ] **System Health Checks**
  - [ ] Service running and stable
  - [ ] No errors in logs
  - [ ] API responding correctly
  - [ ] Database accessible

- [ ] **Process Validation**
  - [ ] End-to-end test with real invoice
  - [ ] Email → n8n → API → Database → XML
  - [ ] NEX Genesis sync verified

- [ ] **Performance Check**
  - [ ] Response times acceptable
  - [ ] Resource usage normal
  - [ ] No memory leaks detected

### 6.2 Documentation

- [ ] **System Documentation**
  - [ ] Server details documented
  - [ ] Network topology documented
  - [ ] Firewall rules documented

- [ ] **Operational Documentation**
  - [ ] Runbook created/updated
  - [ ] Troubleshooting guide provided
  - [ ] Contact information updated

- [ ] **Customer Documentation**
  - [ ] User guide provided
  - [ ] Admin guide provided
  - [ ] API documentation shared

### 6.3 Training & Handover

- [ ] **Operator Training**
  - [ ] Email forwarding process explained
  - [ ] Error handling procedures covered
  - [ ] Escalation path defined

- [ ] **Admin Training**
  - [ ] Service management explained
  - [ ] Log review demonstrated
  - [ ] Backup/restore procedures shown

- [ ] **Support Handover**
  - [ ] Support contact provided
  - [ ] SLA explained
  - [ ] Escalation matrix shared

---

## 📝 Post-Deployment Tasks

### Immediate (Day 1)

- [ ] Monitor system for 24 hours
- [ ] Review first batch of invoices
- [ ] Verify all alerts working
- [ ] Document any issues found

### Week 1

- [ ] Daily log reviews
- [ ] Performance baseline established
- [ ] Any configuration adjustments
- [ ] User feedback collected

### Month 1

- [ ] Monthly statistics review
- [ ] Database maintenance
- [ ] Update documentation
- [ ] Security patches applied

---

## 🚨 Emergency Procedures

### If Service Fails

1. Check logs: `tail -f invoice_loader.log`
2. Restart service: `systemctl restart supplier-invoice-loader`
3. Check database: `sqlite3 invoices.db "PRAGMA integrity_check;"`
4. Contact support if issues persist

### If API Unavailable

1. Check network connectivity
2. Verify API key is valid
3. Test NEX Genesis endpoint directly
4. Check firewall rules

### Support Contacts

- **Primary Support:** support@icc.sk
- **Emergency:** _______________________
- **Customer Contact:** _______________________

---

## 📊 Sign-Off

### Deployment Completed

- [ ] All phases completed successfully
- [ ] No critical issues remaining
- [ ] Customer acceptance received

**Customer Representative:**
- Name: _______________________
- Signature: _______________________
- Date: _______________________

**Deployment Engineer:**
- Name: _______________________  
- Signature: _______________________
- Date: _______________________

---

## 📎 Appendices

### A. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Python not found | Install Python 3.8+ from python.org |
| Permission denied | Run as administrator/sudo |
| Port 8000 in use | Change port in main.py |
| SMTP authentication failed | Generate app password for Gmail |
| Database locked | Only one process should access DB |

### B. Important File Locations

- **Configuration:** `config_customer.py`
- **Environment:** `.env`
- **Database:** `invoices.db`
- **Logs:** `invoice_loader.log`
- **PDF Storage:** Configured in config
- **XML Storage:** Configured in config

### C. Useful Commands

```bash
# Check service status
systemctl status supplier-invoice-loader  # Linux
sc query SupplierInvoiceLoader           # Windows

# View logs
tail -f invoice_loader.log               # Linux
type invoice_loader.log | more           # Windows

# Database queries
sqlite3 invoices.db "SELECT COUNT(*) FROM invoices;"
sqlite3 invoices.db "SELECT * FROM invoices ORDER BY created_at DESC LIMIT 10;"

# Test API
curl -H "X-API-Key: YOUR_KEY" http://localhost:8000/health
```

### D. Version Information

- **Application Version:** 2.0.0
- **Database Version:** v2 (multi-customer)
- **Python Required:** 3.8+
- **Deployment Date:** _______________________

---

**End of Deployment Checklist**