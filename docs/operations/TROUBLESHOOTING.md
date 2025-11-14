# Supplier Invoice Loader - Troubleshooting Guide

Quick reference for diagnosing and fixing common issues.

---

## Table of Contents

1. [Installation & Setup Issues](#installation--setup-issues)
2. [Configuration Problems](#configuration-problems)
3. [Service & Startup Issues](#service--startup-issues)
4. [API & Network Issues](#api--network-issues)
5. [PDF Processing Issues](#pdf-processing-issues)
6. [Database Issues](#database-issues)
7. [Email & SMTP Issues](#email--smtp-issues)
8. [NEX Genesis Integration Issues](#nex-genesis-integration-issues)
9. [Performance Issues](#performance-issues)
10. [Log Analysis](#log-analysis)

---

## Installation & Setup Issues

### Python Version Mismatch

**Symptom:**
```
ERROR: This package requires Python 3.10 or later
```

**Solution:**
```bash
# Check Python version
python --version

# If < 3.10, install newer version
# Windows: Download from python.org
# Linux: sudo apt install python3.11
```

**Verification:**
```bash
python --version
# Should show: Python 3.10.x or later
```

---

### pip Install Failures

**Symptom:**
```
ERROR: Could not find a version that satisfies the requirement...
```

**Causes & Solutions:**

**A) No internet connection:**
```bash
# Test connectivity
ping pypi.org

# If behind proxy, configure pip
pip config set global.proxy http://proxy.company.com:8080
```

**B) Outdated pip:**
```bash
python -m pip install --upgrade pip
pip --version
# Should be 23.x or later
```

**C) Missing Visual C++ (Windows):**
- Download and install: [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Restart PowerShell
- Retry: `pip install -r requirements.txt`

**D) SSL Certificate errors:**
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

### Virtual Environment Not Activating

**Symptom (Windows):**
```
.\venv\Scripts\activate : cannot be loaded because running scripts is disabled
```

**Solution:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate again
.\venv\Scripts\activate
```

**Symptom (Linux):**
```
bash: venv/bin/activate: No such file or directory
```

**Solution:**
```bash
# Recreate virtual environment
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
```

---

### Module Import Errors After Installation

**Symptom:**
```python
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
```bash
# Ensure virtual environment is activated
which python  # Linux/Mac
where python  # Windows
# Should point to venv/bin/python or venv\Scripts\python.exe

# Reinstall in correct environment
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

---

## Configuration Problems

### config_customer.py Not Found

**Symptom:**
```
WARNING: config_customer.py not found, using template
```

**Solution:**
```bash
# Copy template
cp config_template.py config_customer.py

# Edit with your values
nano config_customer.py  # Linux
notepad config_customer.py  # Windows
```

**Verify:**
```bash
ls -l config_customer.py  # Linux
dir config_customer.py  # Windows
```

---

### Environment Variables Not Loading

**Symptom:**
API key shows default value or SMTP credentials missing.

**Windows Solution:**
```powershell
# Check if variables are set
[System.Environment]::GetEnvironmentVariable("LS_API_KEY", "Machine")

# If null, set it
[System.Environment]::SetEnvironmentVariable("LS_API_KEY", "your-key-here", "Machine")

# IMPORTANT: Restart service/application after setting
Restart-Service SupplierInvoiceLoader
```

**Linux Solution:**
```bash
# Check variables
echo $LS_API_KEY

# If empty, add to /etc/environment
sudo nano /etc/environment

# Add line:
LS_API_KEY="your-key-here"

# Load and restart service
source /etc/environment
sudo systemctl restart supplier-invoice-loader
```

---

### Storage Directory Permission Denied

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'C:\\NEX_INVOICES\\PDF\\...'
```

**Windows Solution:**
```powershell
# Grant permissions to service account
icacls C:\NEX_INVOICES /grant "NETWORK SERVICE:(OI)(CI)F" /T

# Or for specific user
icacls C:\NEX_INVOICES /grant "DOMAIN\username:(OI)(CI)F" /T

# Verify
icacls C:\NEX_INVOICES
```

**Linux Solution:**
```bash
# Check current permissions
ls -la /var/nex_invoices

# Fix ownership
sudo chown -R your-username:your-username /var/nex_invoices

# Fix permissions
sudo chmod -R 755 /var/nex_invoices

# Verify
ls -la /var/nex_invoices
```

---

## Service & Startup Issues

### Service Won't Start (Windows)

**Symptom:**
```
Start-Service : Service 'SupplierInvoiceLoader' cannot be started
```

**Diagnostic Steps:**

**1. Check service status:**
```powershell
Get-Service SupplierInvoiceLoader
nssm status SupplierInvoiceLoader
```

**2. Check service logs:**
```powershell
Get-Content C:\SupplierInvoiceLoader\service_stderr.log -Tail 50
Get-Content C:\SupplierInvoiceLoader\invoice_loader.log -Tail 50
```

**3. Try manual start:**
```powershell
cd C:\SupplierInvoiceLoader
.\venv\Scripts\activate
python main.py
# Watch for errors
```

**Common Causes:**

**A) Wrong Python path in NSSM:**
```powershell
# Check NSSM configuration
nssm dump SupplierInvoiceLoader

# Fix path
nssm set SupplierInvoiceLoader Application "C:\SupplierInvoiceLoader\venv\Scripts\python.exe"
nssm set SupplierInvoiceLoader AppDirectory "C:\SupplierInvoiceLoader"
```

**B) Port 8000 already in use:**
```powershell
# Check what's using port 8000
netstat -ano | findstr :8000

# Kill process (use PID from above)
taskkill /PID <PID> /F

# Or change port in config
```

**C) Missing dependencies:**
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

### Service Won't Start (Linux)

**Symptom:**
```
Failed to start supplier-invoice-loader.service
```

**Diagnostic Steps:**

**1. Check status:**
```bash
sudo systemctl status supplier-invoice-loader
```

**2. Check logs:**
```bash
sudo journalctl -u supplier-invoice-loader -n 50
tail -f /opt/supplier_invoice_loader/invoice_loader.log
```

**3. Try manual start:**
```bash
cd /opt/supplier_invoice_loader
source venv/bin/activate
python main.py
```

**Common Causes:**

**A) Wrong paths in service file:**
```bash
# Edit service file
sudo nano /etc/systemd/system/supplier-invoice-loader.service

# Verify paths:
# WorkingDirectory=/opt/supplier_invoice_loader
# ExecStart=/opt/supplier_invoice_loader/venv/bin/python main.py

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart supplier-invoice-loader
```

**B) Permission issues:**
```bash
# Check user in service file
grep User /etc/systemd/system/supplier-invoice-loader.service

# Ensure that user owns the directory
sudo chown -R username:username /opt/supplier_invoice_loader
```

---

### Application Crashes on Startup

**Symptom:**
Service starts but immediately stops.

**Check logs for these errors:**

**A) Import errors:**
```
ModuleNotFoundError: No module named 'pdfplumber'
```
**Solution:** `pip install -r requirements.txt`

**B) Config errors:**
```
AttributeError: module 'config' has no attribute 'API_KEY'
```
**Solution:** Ensure config_customer.py has all required fields

**C) Database errors:**
```
sqlite3.OperationalError: unable to open database file
```
**Solution:** Check DB_FILE path and permissions

**D) Port binding error:**
```
OSError: [Errno 98] Address already in use
```
**Solution:** Change port or kill process using port 8000

---

## API & Network Issues

### 401 Unauthorized Error

**Symptom:**
```
{"detail": "Invalid API key"}
```

**Diagnostic:**
```bash
# Check API key in config
python -c "import config; print(config.API_KEY[:10] + '...')"

# Test with correct key
curl -X GET http://localhost:8000/invoices \
  -H "X-API-Key: your-actual-key-here"
```

**Solution:**
- Verify X-API-Key header in n8n matches config.API_KEY
- Check environment variable LS_API_KEY is set correctly
- Restart service after changing API key

---

### Connection Refused / Timeout

**Symptom:**
```
curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**Diagnostic Steps:**

**1. Check if service is running:**
```powershell
# Windows
Get-Service SupplierInvoiceLoader
netstat -ano | findstr :8000

# Linux
sudo systemctl status supplier-invoice-loader
sudo netstat -tlnp | grep 8000
```

**2. Check firewall:**
```powershell
# Windows
Get-NetFirewallRule -DisplayName "*Supplier*"

# Linux
sudo ufw status
```

**3. Test from localhost first:**
```bash
curl http://localhost:8000/health
# If this works, it's a network/firewall issue
```

**Solutions:**

**A) Service not running:** Start service

**B) Firewall blocking:**
```powershell
# Windows
New-NetFirewallRule -DisplayName "Supplier Invoice Loader" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow

# Linux
sudo ufw allow 8000/tcp
```

**C) Listening on wrong interface:**
Check main.py: `uvicorn.run(..., host="0.0.0.0", port=8000)`
- `0.0.0.0` = all interfaces (correct)
- `127.0.0.1` = localhost only (wrong for network access)

---

### Slow API Response

**Symptom:**
Requests take > 5 seconds to complete.

**Diagnostic:**
```bash
# Time a request
time curl http://localhost:8000/health
```

**Common Causes:**

**A) Large PDF processing:**
- Check PDF file size in logs
- PDFs > 10 MB are slow
- Solution: Optimize PDFs before sending, or increase server resources

**B) Database locked:**
```
sqlite3.OperationalError: database is locked
```
- Multiple processes accessing DB simultaneously
- Solution: Ensure only one service instance running

**C) Network latency to NEX Genesis:**
```bash
# Test NEX connectivity
ping nex-server-ip
curl http://nex-server-ip:8080/api/health
```

---

## PDF Processing Issues

### No Text Extracted from PDF

**Symptom:**
```
ERROR: No text extracted from PDF
```

**Causes & Solutions:**

**A) PDF is scanned image (no text layer):**
- Check manually: Open PDF, try to select text
- If can't select text → it's an image
- Solution: Implement OCR (future feature) or ask customer to use text-based PDFs

**B) PDF is encrypted:**
```
pdfplumber.pdf.PDFSyntaxError: PDF is encrypted
```
- Solution: Ask customer to remove password protection

**C) Corrupted PDF:**
- Try opening PDF in reader
- Solution: Re-generate PDF from source system

---

### Invoice Data Not Extracted Correctly

**Symptom:**
Invoice number, dates, or amounts are null/wrong.

**Diagnostic:**

**1. Check PDF text extraction:**
```python
import pdfplumber

with pdfplumber.open('problem_invoice.pdf') as pdf:
    text = pdf.pages[0].extract_text()
    print(text)
```

**2. Check if pattern matches:**
```python
import re
text = "... PDF text here ..."
pattern = r'FAKTÚRA[^\d]*?(\d+)'
match = re.search(pattern, text)
print(match)  # Should not be None
```

**Solutions:**

**A) Supplier changed invoice format:**
- Update regex patterns in `ls_extractor.py`
- Or create new extractor for this supplier

**B) Encoding issues (Slovak characters):**
- Check text encoding in PDF
- May need to adjust pdfplumber settings

**C) Extra spaces in numbers:**
```
# "1 2 3 4 5 6" instead of "123456"
```
- Already handled in ls_extractor.py with `re.sub(r'\s+', '', value)`
- If still issues, adjust regex patterns

---

### Items Not Extracted from Table

**Symptom:**
`invoice_data.items` is empty list.

**Diagnostic:**
```python
# Check table detection
import re
text = "... PDF text ..."
table_start = re.search(r'Č\.\s+Názov.*?Spolu s DPH', text)
print(f"Table found: {table_start is not None}")
```

**Solutions:**

**A) Table format changed:**
- Update `_extract_items()` method in ls_extractor.py
- Adjust regex patterns for new format

**B) Table split across pages:**
- Current implementation only processes first page
- Enhancement needed: process all pages

---

## Database Issues

### Database Locked Error

**Symptom:**
```
sqlite3.OperationalError: database is locked
```

**Causes:**
- Multiple processes trying to write simultaneously
- Previous process didn't close connection properly
- Database file on network drive (not supported)

**Solutions:**

**A) Check for multiple instances:**
```powershell
# Windows
tasklist | findstr python
Get-Service SupplierInvoiceLoader

# Linux
ps aux | grep python
```
**Kill duplicate processes**

**B) Restart service:**
```powershell
Restart-Service SupplierInvoiceLoader
```

**C) Close hung connections:**
```python
# Emergency fix - connect and close all
import sqlite3
conn = sqlite3.connect('invoices.db', timeout=30)
conn.execute("PRAGMA busy_timeout = 30000")
conn.close()
```

**D) Move DB to local disk:**
- SQLite doesn't work well on network drives
- Ensure DB_FILE is on local disk (C:\, /opt/, etc.)

---

### Database Corruption

**Symptom:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Recovery Steps:**

**1. Stop service immediately**
```powershell
Stop-Service SupplierInvoiceLoader
```

**2. Backup corrupted database:**
```bash
copy invoices.db invoices.db.corrupted
```

**3. Try SQLite recovery:**
```bash
sqlite3 invoices.db

.mode insert
.output recovery.sql
.dump
.exit

# Create new DB from dump
sqlite3 invoices_new.db < recovery.sql
```

**4. If recovery fails, restore from backup:**
```bash
copy C:\NEX_INVOICES\Backups\invoices_20251006.db invoices.db
```

**5. Restart service:**
```powershell
Start-Service SupplierInvoiceLoader
```

**Prevention:**
- Regular backups (daily)
- Graceful service shutdown
- Keep database on reliable local disk
- Monitor disk space

---

### Duplicate Invoice Detection Not Working

**Symptom:**
Same invoice processed multiple times.

**Diagnostic:**
```sql
sqlite3 invoices.db

-- Check for duplicates
SELECT file_hash, COUNT(*) 
FROM invoices 
GROUP BY file_hash 
HAVING COUNT(*) > 1;

-- Check message_id uniqueness
SELECT message_id, COUNT(*) 
FROM invoices 
GROUP BY message_id 
HAVING COUNT(*) > 1;
```

**Solutions:**

**A) Different email message_id each time:**
- n8n might be re-downloading email with new message_id
- Solution: Configure n8n to mark emails as read

**B) Hash calculation changed:**
- Check database.py `calculate_file_hash()` function
- Ensure consistent hash algorithm

---

## Email & SMTP Issues

### SMTP Authentication Failed

**Symptom:**
```
SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted')
```

**Gmail-specific solutions:**

**1. Use App Password (not regular password):**
- Go to: https://myaccount.google.com/apppasswords
- Enable 2-Step Verification first
- Generate app password for "Mail"
- Use that password in SMTP_PASSWORD

**2. Enable "Less secure app access":**
- Not recommended, use App Passwords instead

**3. Check credentials:**
```bash
echo $SMTP_USER
echo $SMTP_PASSWORD
# Should not be empty
```

---

### SMTP Connection Timeout

**Symptom:**
```
TimeoutError: [Errno 110] Connection timed out
```

**Diagnostic:**
```bash
# Test SMTP connectivity
telnet smtp.gmail.com 587
# Should connect

# Or use openssl
openssl s_client -connect smtp.gmail.com:587 -starttls smtp
```

**Solutions:**

**A) Firewall blocking outbound SMTP:**
```powershell
# Windows - allow outbound on 587
New-NetFirewallRule -DisplayName "SMTP Outbound" -Direction Outbound -Protocol TCP -RemotePort 587 -Action Allow
```

**B) Wrong SMTP port:**
```python
SMTP_PORT = 587  # TLS (correct)
# NOT 465 (SSL) or 25 (unencrypted)
```

**C) Corporate proxy:**
- SMTP doesn't work through HTTP proxy
- May need direct internet access or SMTP relay server

---

### Emails Not Sending (No Error)

**Symptom:**
No exception thrown, but emails never arrive.

**Diagnostic:**
```python
# Test email sending
python
>>> import smtplib
>>> from email.mime.text import MIMEText
>>> 
>>> msg = MIMEText("Test")
>>> msg['Subject'] = "Test"
>>> msg['From'] = "noreply@icc.sk"
>>> msg['To'] = "your-email@example.com"
>>> 
>>> server = smtplib.SMTP('smtp.gmail.com', 587)
>>> server.starttls()
>>> server.login('your-smtp-user', 'your-app-password')
>>> server.send_message(msg)
>>> server.quit()
```

**Solutions:**

**A) Email in spam folder:**
- Check recipient's spam/junk folder
- Add sender to safe senders list

**B) Wrong recipient email:**
- Verify ALERT_EMAIL in config_customer.py
- Check for typos

**C) Rate limiting:**
- Gmail limits: 500 emails/day, 100 recipients/email
- If exceeded, wait 24 hours

---

## NEX Genesis Integration Issues

### Cannot Connect to NEX Genesis API

**Symptom:**
```
ConnectionError: Failed to connect to NEX Genesis API
```

**Diagnostic Steps:**

**1. Test basic connectivity:**
```bash
ping nex-server-ip

# Test HTTP
curl http://nex-server-ip:8080/api/health
# or
curl http://nex-server-ip:8080/api/version
```

**2. Check from application server:**
```bash
# SSH into application server
# Then test from there (not from your laptop!)
curl http://nex-server-ip:8080/api
```

**3. Check firewall rules:**
- NEX server firewall must allow incoming from application server
- Application server firewall must allow outgoing to NEX server

**Solutions:**

**A) Wrong URL in config:**
```python
# config_customer.py
NEX_GENESIS_API_URL = "http://192.168.1.50:8080/api"
# Common mistakes:
# - Trailing slash: "http://192.168.1.50:8080/api/" ❌
# - Wrong port: 8000 instead of 8080
# - Missing /api: "http://192.168.1.50:8080" ❌
```

**B) VPN required:**
- If NEX server on private network, application server may need VPN
- Configure site-to-site VPN or client VPN

**C) Network routing issue:**
```bash
# Trace route to NEX server
tracert nex-server-ip  # Windows
traceroute nex-server-ip  # Linux
```

---

### NEX Genesis API Returns 401/403

**Symptom:**
```
HTTPError: 401 Unauthorized / 403 Forbidden
```

**Solutions:**

**A) Wrong API key:**
```python
# Check API key in config
python -c "import config; print(config.NEX_GENESIS_API_KEY)"

# Get correct key from NEX Genesis admin panel
# Update in config_customer.py
NEX_GENESIS_API_KEY = "correct-key-here"
```

**B) API key expired:**
- Contact NEX Genesis administrator
- Generate new API key
- Update config

**C) IP whitelist:**
- NEX Genesis may restrict API access by IP
- Add application server IP to whitelist

---

### NEX Genesis API Timeout

**Symptom:**
```
ReadTimeout: HTTPSConnectionPool(host='nex', port=8080): Read timed out
```

**Solutions:**

**A) Slow NEX Genesis response:**
- Check NEX Genesis server load
- Optimize invoice data size
- Increase timeout in HTTP request (future enhancement)

**B) Network latency:**
```bash
# Test latency
ping nex-server-ip
# Should be < 50ms

# If > 200ms, investigate network issues
```

---

## Performance Issues

### High Memory Usage

**Symptom:**
Service using > 2 GB RAM.

**Diagnostic:**
```powershell
# Windows
Get-Process python | Select-Object ProcessName, @{Name="Memory(MB)"; Expression={[math]::Round($_.WorkingSet / 1MB, 2)}}

# Linux
ps aux | grep python
```

**Causes:**

**A) Large PDF files:**
- pdfplumber loads entire PDF into memory
- 100 MB PDF → 500+ MB RAM usage
- Solution: Process smaller batches, restart service periodically

**B) Memory leak:**
- Check for unclosed file handles
- Update to latest pdfplumber version

**Solution:**
```powershell
# Scheduled task to restart service daily at 3 AM
# Clears memory leaks
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
$action = New-ScheduledTaskAction -Execute 'Restart-Service' -Argument 'SupplierInvoiceLoader'
Register-ScheduledTask -TaskName "Restart Invoice Loader" -Trigger $trigger -Action $action
```

---

### High CPU Usage

**Symptom:**
Python process using 100% CPU constantly.

**Diagnostic:**
```bash
# Check what Python is doing
# Windows: Use Process Explorer
# Linux: 
top -p $(pgrep python)
```

**Causes:**

**A) Infinite loop in code:**
- Check recent code changes
- Review logs for repeated error messages

**B) Processing very large PDF:**
- OCR or complex extraction
- Solution: Optimize extraction code or limit PDF size

**C) Multiple instances running:**
```bash
# Check for duplicate processes
ps aux | grep "main.py"  # Linux
tasklist | findstr python  # Windows

# Kill extras
```

---

### Slow PDF Processing

**Symptom:**
Each invoice takes > 30 seconds to process.

**Optimization tips:**

**A) Use pdfplumber efficiently:**
```python
# Good: Extract text once
with pdfplumber.open(pdf_path) as pdf:
    text = "\n".join(page.extract_text() for page in pdf.pages)
    # Then parse text multiple times

# Bad: Open PDF multiple times
def get_invoice_number(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:  # ❌ Slow
        ...
```

**B) Lazy import:**
```python
# Import pdfplumber only when needed
def extract_from_pdf(pdf_path):
    import pdfplumber  # Good - lazy import
    ...
```

**C) Upgrade server:**
- Add more RAM (8 GB → 16 GB)
- Faster CPU helps with PDF parsing
- SSD instead of HDD for storage

---

## Log Analysis

### Understanding Log Levels

```
DEBUG: Detailed diagnostic information
INFO: General informational messages (default)
WARNING: Something unexpected but not critical
ERROR: Serious problem, functionality impaired
CRITICAL: System failure, service may crash
```

**Change log level:**
```bash
# Windows
$env:LOG_LEVEL = "DEBUG"
Restart-Service SupplierInvoiceLoader

# Linux
export LOG_LEVEL=DEBUG
sudo systemctl restart supplier-invoice-loader
```

---

### Common Log Patterns

**Normal operation:**
```
[INFO] L&Š Invoice Loader Starting...
[INFO] Processing invoice: faktura_123.pdf
[INFO] Extracted: 2025001, 5 items, total: 1234.56 EUR
[INFO] ISDOC XML generated: 2143 chars
[INFO] Invoice processed successfully: ID=42
```

**Duplicate detection (expected):**
```
[WARNING] Duplicate invoice: abc12345...
```

**Partial success (needs review):**
```
[ERROR] PDF extraction failed
[INFO] PDF saved but extraction failed
```

**Critical errors:**
```
[ERROR] Error processing invoice: database is locked
[CRITICAL] Failed to start: Port 8000 already in use
```

---

### Log Rotation

**Problem:** Log file grows > 1 GB and slows down system.

**Solution (Windows):**
```powershell
# PowerShell script: rotate_logs.ps1
$logFile = "C:\SupplierInvoiceLoader\invoice_loader.log"
$maxSize = 100MB

if ((Get-Item $logFile).Length -gt $maxSize) {
    $date = Get-Date -Format "yyyyMMdd"
    Move-Item $logFile "C:\SupplierInvoiceLoader\logs\invoice_loader_$date.log"
    New-Item $logFile -ItemType File
}

# Schedule to run daily
```

**Solution (Linux):**
```bash
# Use logrotate
sudo nano /etc/logrotate.d/supplier-invoice-loader

# Add:
/opt/supplier_invoice_loader/invoice_loader.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 username username
}
```

---

## Emergency Recovery Procedures

### Complete Service Failure

**When everything is broken:**

**1. Stop service:**
```powershell
Stop-Service SupplierInvoiceLoader
```

**2. Backup current state:**
```powershell
$date = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item C:\SupplierInvoiceLoader C:\Backups\SupplierInvoiceLoader_$date -Recurse
```

**3. Restore from known good backup:**
```powershell
# Or restore from Git
cd C:\SupplierInvoiceLoader
git stash
git pull origin v2.0-multi-customer
```

**4. Reinstall dependencies:**
```powershell
.\venv\Scripts\activate
pip install --force-reinstall -r requirements.txt
```

**5. Test manually:**
```powershell
python main.py
# Fix any errors before restarting service
```

**6. Restart service:**
```powershell
Start-Service SupplierInvoiceLoader
```

---

### Data Loss - Database Gone

**If invoices.db is deleted or corrupted beyond recovery:**

**1. Stop service**

**2. Restore from backup:**
```bash
copy C:\NEX_INVOICES\Backups\invoices_20251006.db C:\SupplierInvoiceLoader\invoices.db
```

**3. If no backup exists:**
```python
# Reinitialize empty database
python
>>> import database
>>> database.init_database()
>>> exit()
```

**4. Rebuild from PDFs:**
```python
# Create script to reprocess all PDFs in storage
import os
from extractors.ls_extractor import extract_invoice_data
import database

pdf_dir = "C:\\NEX_INVOICES\\PDF"
for pdf_file in os.listdir(pdf_dir):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(pdf_dir, pdf_file)
        data = extract_invoice_data(pdf_path)
        if data:
            database.insert_invoice(...)
```

---

## Getting Help

### Before Contacting Support

Collect this information:

1. **System info:**
   - OS version: `ver` (Windows) or `uname -a` (Linux)
   - Python version: `python --version`
   - Service status: `Get-Service` or `systemctl status`

2. **Logs (last 100 lines):**
   ```bash
   tail -100 invoice_loader.log > problem_log.txt
   ```

3. **Config (redacted):**
   ```python
   # Remove sensitive data before sharing
   CUSTOMER_NAME = "MAGERSTAV"
   NEX_GENESIS_API_URL = "http://192.168.x.x:8080/api"  # Hide IP
   API_KEY = "REDACTED"
   ```

4. **Problem description:**
   - What were you doing?
   - What did you expect?
   - What actually happened?
   - When did it start?
   - Can you reproduce it?

### Contact Information

- **Email:** support@icc.sk
- **GitHub Issues:** https://github.com/rauschiccsk/supplier_invoice_loader/issues
- **Emergency Hotline:** +421 XXX XXX XXX (business hours)

### Remote Support

If needed, provide secure remote access:

**Windows:**
- TeamViewer, AnyDesk, or Windows Remote Desktop
- Ensure firewall allows RDP (port 3389)

**Linux:**
- SSH access: `ssh username@server-ip`
- Or VNC/X11 forwarding

**IMPORTANT:** Never share passwords or API keys via email or chat. Use secure methods like encrypted files or password managers.

---

**END OF TROUBLESHOOTING GUIDE**