# Customer Installation Checklist

Quick reference checklist for deploying to new customer.

## Pre-Installation

- [ ] Customer server ready (Windows Server, Python 3.10+)
- [ ] NEX Genesis installed and running
- [ ] NEX Genesis API endpoints ready
- [ ] API key from customer obtained
- [ ] Automation email created (automation-customer@isnex.ai)
- [ ] Gmail/IMAP credentials ready

## Installation Steps

### 1. Copy Project Files
- [ ] Copy supplier_invoice_loader to `C:\NEX_INVOICES\`
- [ ] Verify all files present

### 2. Python Environment
- [ ] Create venv: `python -m venv venv`
- [ ] Activate venv: `venv\Scripts\activate`
- [ ] Install requirements: `pip install -r requirements.txt`

### 3. Configuration
- [ ] Copy `config_template.py` → `config_customer.py`
- [ ] Set `CUSTOMER_NAME`
- [ ] Set `NEX_GENESIS_API_URL`
- [ ] Set `NEX_GENESIS_API_KEY`
- [ ] Set `OPERATOR_EMAIL`
- [ ] Set `AUTOMATION_EMAIL`
- [ ] Set `ALERT_EMAIL`
- [ ] Set `SMTP_USER` and `SMTP_PASSWORD` (for alerts)

### 4. Test Run
- [ ] Run `python main.py`
- [ ] Verify server starts on port 8000
- [ ] Test `/health` endpoint
- [ ] Check logs for errors

### 5. Windows Service
- [ ] Run service installer
- [ ] Verify service auto-starts
- [ ] Test service restart

### 6. N8N Workflow
- [ ] Import template JSON
- [ ] Configure IMAP credentials
- [ ] Set customer server URL
- [ ] Set API key
- [ ] Activate workflow
- [ ] Test with sample email

### 7. End-to-End Test
- [ ] Operator sends test invoice
- [ ] Verify PDF saved
- [ ] Verify XML generated
- [ ] Verify NEX Genesis received data
- [ ] Check alert emails work

## Post-Installation

- [ ] Document customer-specific settings
- [ ] Train operator on process
- [ ] Setup monitoring alerts
- [ ] Schedule follow-up check (1 week)

## Rollback Plan

If installation fails:
1. Stop Python service
2. Restore previous configuration
3. Contact support@icc.sk

---

**Installation Time Estimate:** 2-3 hours
**Tested By:** ________________
**Date:** ________________