# Security Guidelines

**Version:** 2.0  
**Last Updated:** October 2025

This document outlines security best practices for deploying and maintaining the Supplier Invoice Loader system.

---

## 🔴 CRITICAL: What NEVER to Commit to Git

**NEVER commit these files or data to Git:**

1. **config_customer.py** - Contains customer-specific API keys, URLs, emails
2. **.env** - Environment variables with secrets
3. ***.log** - May contain sensitive data from invoices
4. **invoices.db** - Customer database with invoice data
5. **PDF/XML files** - Customer invoice documents
6. **n8n workflows with real credentials** - Only commit templates
7. **Backup files** - May contain sensitive data
8. **SSL certificates** - Private keys, certificates

**All of these are already in .gitignore** - verify before committing!

---

## API Key Security

### 1. Generate Strong API Keys

**DO NOT use default keys in production!**

```bash
# Generate secure random key (32+ characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Example output:
# vK3mP9xL2wQ7nR8tY4uA1zB5cD6eF0gH1iJ2kL3mN4oP
```

### 2. Store API Keys Securely

**Priority (best to worst):**

1. **System Environment Variables** (Production - BEST)
   ```powershell
   # Windows - persistent
   [System.Environment]::SetEnvironmentVariable("LS_API_KEY", "your-key", "Machine")
   
   # Linux - add to /etc/environment
   sudo nano /etc/environment
   LS_API_KEY="your-key"
   ```

2. **.env File** (Development - GOOD)
   ```bash
   # Create .env from template
   cp .env.example .env
   nano .env
   
   # Set values
   LS_API_KEY=your-secure-key-here
   ```

3. **config_customer.py** (Acceptable if protected)
   - Only if file has restricted permissions
   - Never commit to Git
   - Use only for hardcoded deployments

**NEVER:**
- Hardcode in config_template.py
- Include in README examples
- Share via email or chat
- Commit to Git
- Store in plaintext documentation

### 3. API Key Rotation

**Rotate API keys quarterly (every 3 months)**

**Rotation procedure:**
1. Generate new key
2. Update in .env or system variables
3. Update in n8n workflow (X-API-Key header)
4. Restart Python service
5. Test workflow
6. Deactivate old key
7. Document rotation date

**Emergency rotation** (if compromised):
- Immediate - within 1 hour
- Follow same steps
- Investigate breach

---

## SMTP Credentials Security

### Gmail App Passwords

**NEVER use your regular Gmail password!**

**Setup App Password:**

1. Enable 2-Step Verification:
   - https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. Generate App Password:
   - https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy 16-character password

3. Store in .env:
   ```bash
   SMTP_USER=automation@customer.sk
   SMTP_PASSWORD=abcd efgh ijkl mnop  # App password
   ```

**Security notes:**
- App passwords bypass 2FA - keep secure
- Revoke if compromised
- One app password per application
- Monitor account activity

### Other Email Providers

**Office365/Outlook:**
- Use OAuth2 if possible
- Or app-specific password
- Enable MFA on account

**Custom SMTP:**
- Use TLS/SSL (port 587 or 465)
- Avoid port 25 (unencrypted)
- Strong password (16+ characters)
- Consider IP whitelisting

---

## NEX Genesis API Security

### 1. API Key Management

```python
# config_customer.py
NEX_GENESIS_API_KEY = os.getenv("NEX_API_KEY", "fallback-only-for-dev")
```

**Best practices:**
- Different key per customer
- Rotate every 6 months
- Monitor API usage in NEX
- Revoke on employee departure

### 2. Network Security

**Restrict API access:**

1. **IP Whitelist** (NEX Genesis side)
   - Only allow Python server IP
   - Block all other IPs
   - Update when IP changes

2. **Firewall Rules** (Python server side)
   ```powershell
   # Windows - allow only to NEX server
   New-NetFirewallRule -DisplayName "NEX Genesis API" `
     -Direction Outbound `
     -Protocol TCP `
     -RemoteAddress 192.168.1.50 `
     -RemotePort 8080 `
     -Action Allow
   ```

3. **Use HTTPS** in production
   ```python
   NEX_GENESIS_API_URL = "https://nex.customer.com/api"  # HTTPS!
   ```

### 3. API Rate Limiting

**Implement in Python** (future enhancement):
```python
# Limit: 100 requests per hour to NEX
# Prevents abuse if API key leaked
```

---

## File System Security

### 1. Storage Directory Permissions

**Windows:**
```powershell
# Restrict to service account only
icacls C:\NEX_INVOICES /inheritance:r
icacls C:\NEX_INVOICES /grant "NETWORK SERVICE:(OI)(CI)F"
icacls C:\NEX_INVOICES /remove "Users"
```

**Linux:**
```bash
# Restrict to app user only
sudo chown -R appuser:appuser /var/nex_invoices
sudo chmod 700 /var/nex_invoices
```

### 2. Database Security

**Protect invoices.db:**
```bash
# Windows
icacls invoices.db /grant "NETWORK SERVICE:RW"
icacls invoices.db /remove "Users"

# Linux
chmod 600 invoices.db
chown appuser:appuser invoices.db
```

**Backup encryption** (recommended):
```bash
# Encrypt database backups
gpg --encrypt --recipient admin@company.com invoices_backup.db
```

### 3. Log File Security

**Logs may contain:**
- Email addresses
- Invoice numbers
- Supplier names
- Error details with data

**Protection:**
1. Restrict read access
2. Rotate regularly
3. Purge old logs (> 90 days)
4. Do not commit to Git
5. Redact sensitive data if sharing for debugging

```python
# In logger configuration - redact sensitive data
import logging
import re

class RedactingFormatter(logging.Formatter):
    def format(self, record):
        msg = super().format(record)
        # Redact email addresses
        msg = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     'EMAIL_REDACTED', msg)
        return msg
```

---

## Network Security

### 1. Firewall Configuration

**Python API Server:**

Inbound rules (allow):
- Port 8000 from n8n server IP only
- Port 3389 (RDP) from admin IPs only (Windows)
- Port 22 (SSH) from admin IPs only (Linux)

Outbound rules (allow):
- Port 8080 to NEX Genesis server only
- Port 587/465 to SMTP server only
- Port 443 for system updates

**Block all other traffic by default**

### 2. Use Private Networks

**Recommended network topology:**

```
[Internet]
    |
    v
[n8n Server] --private--> [Python API Server] --private--> [NEX Genesis Server]
  Public                   Internal                         Internal
  10.0.1.10               192.168.1.50                     192.168.1.100
```

**Benefits:**
- Python API not exposed to internet
- NEX Genesis not exposed to internet
- Only n8n has public access (if needed)

### 3. VPN for Remote Access

**For admin access:**
- Use VPN (not direct RDP/SSH)
- Strong VPN passwords
- MFA on VPN
- Monitor VPN logs

---

## Application Security

### 1. Input Validation

**Already implemented in main.py:**
- Base64 validation on PDF upload
- API key validation on all endpoints
- Pydantic models for request validation

**Additional recommendations:**
- Limit PDF file size (max 25 MB)
- Validate email addresses format
- Sanitize filenames (prevent path traversal)

### 2. Error Handling

**DO NOT expose sensitive data in errors:**

```python
# BAD - exposes internal paths
raise HTTPException(500, detail=f"Failed to save to {pdf_path}")

# GOOD - generic message
raise HTTPException(500, detail="Failed to process invoice")
logger.error(f"Failed to save to {pdf_path}")  # Log internally
```

### 3. Dependency Security

**Keep dependencies updated:**
```bash
# Check for vulnerabilities
pip install safety
safety check -r requirements.txt

# Update dependencies quarterly
pip list --outdated
pip install --upgrade package-name
```

**Pin versions in requirements.txt:**
```
fastapi==0.104.0  # Specific version
uvicorn>=0.24.0   # Minimum version
```

---

## Access Control

### 1. Principle of Least Privilege

**Service account (Windows):**
- Use NETWORK SERVICE or dedicated user
- Grant only necessary permissions
- No admin rights

**Linux user:**
```bash
# Create dedicated user
sudo useradd -r -s /bin/false invoice_loader
sudo chown -R invoice_loader:invoice_loader /opt/supplier_invoice_loader
```

### 2. Human Access

**Who needs access?**
- **Developers:** Code repository (GitHub)
- **Operators:** n8n workflow (view/edit)
- **IT Admin:** Server access (RDP/SSH)
- **Support:** Logs (read-only)

**Who does NOT need access:**
- End users
- External vendors
- Unrelated IT staff

### 3. Password Policy

**All accounts:**
- Minimum 16 characters
- Mix of letters, numbers, symbols
- No dictionary words
- Change quarterly
- Use password manager (1Password, LastPass, KeePass)

**For service accounts:**
- 32+ character random passwords
- Store in secure vault
- Document location

---

## Monitoring & Auditing

### 1. Enable Logging

**Already implemented:**
- API requests logged
- Invoice processing logged
- Errors logged

**Add (future enhancement):**
```python
# Log failed authentication attempts
@app.middleware("http")
async def log_failed_auth(request, call_next):
    response = await call_next(request)
    if response.status_code == 401:
        logger.warning(f"Failed auth from {request.client.host}")
    return response
```

### 2. Monitor Logs

**Weekly review:**
- Failed authentication attempts
- Unusual API activity
- Error patterns
- Performance issues

**Set up alerts for:**
- Multiple failed auth attempts (5+ in 1 hour)
- Service crashes
- Disk space low
- Unusual traffic volume

### 3. Audit Trail

**Track:**
- Who deployed what (Git commits)
- Who accessed server (RDP/SSH logs)
- Who modified n8n workflows
- Who changed API keys

**Tools:**
- Windows Event Viewer
- Linux auditd
- Git commit history
- n8n execution history

---

## Incident Response

### Security Breach Procedure

**If API key is compromised:**

1. **Immediate (< 1 hour):**
   - Rotate API key
   - Check logs for unauthorized access
   - Update n8n workflow with new key
   - Restart service

2. **Within 24 hours:**
   - Review all recent activity
   - Check for data exfiltration
   - Identify breach source
   - Document incident

3. **Within 1 week:**
   - Implement additional controls
   - Review access logs
   - Update security procedures
   - Report to stakeholders

**If server is compromised:**

1. **Immediate:**
   - Isolate server (disconnect network)
   - Preserve logs
   - Contact security team/vendor

2. **Do NOT:**
   - Turn off server (destroys evidence)
   - Delete anything
   - Investigate alone (get expert help)

### Contact Information

**Security incidents:**
- Email: security@icc.sk
- Phone: +421 XXX XXX XXX (24/7)
- Escalation: CTO, CEO

---

## Compliance & Privacy

### GDPR Considerations

Invoice data may contain personal data:
- Names
- Addresses
- Email addresses
- Company registration numbers

**Requirements:**
1. **Data minimization** - store only necessary data
2. **Purpose limitation** - use only for invoicing
3. **Retention** - delete after retention period (7 years for accounting)
4. **Security** - implement appropriate safeguards (this document)
5. **Breach notification** - report breaches within 72 hours

**Data processing agreement:**
- Required between you (processor) and customer (controller)
- Document what data you process and how
- Customer owns the data, you just process it

### Accounting Regulations

**Slovakia:**
- Invoice retention: 10 years
- Secure storage required
- Audit trail required
- Paper or electronic storage allowed (ISDOC XML is valid)

**Compliance:**
- Backups for disaster recovery
- Access logs for audits
- Ensure data integrity (checksums, hashes)

---

## Security Checklist

### Initial Deployment
- [ ] Strong API key generated (32+ characters)
- [ ] API key stored in .env or system variables (not hardcoded)
- [ ] SMTP credentials use app passwords (not regular passwords)
- [ ] config_customer.py not committed to Git
- [ ] .env not committed to Git
- [ ] Firewall configured (allow only necessary ports)
- [ ] File permissions restricted (storage, database, logs)
- [ ] HTTPS used for NEX Genesis API (if possible)
- [ ] Service runs with least privilege account
- [ ] Backups configured with encryption

### Monthly Review
- [ ] Review access logs for anomalies
- [ ] Check for failed authentication attempts
- [ ] Verify backups are working
- [ ] Update dependencies (pip list --outdated)
- [ ] Check disk space
- [ ] Review error logs

### Quarterly Tasks
- [ ] Rotate API keys
- [ ] Review and update firewall rules
- [ ] Test backup restoration
- [ ] Security awareness training for operators
- [ ] Review access permissions (who has access?)
- [ ] Update documentation

### Annual Tasks
- [ ] Full security audit
- [ ] Penetration testing (if required)
- [ ] Review and update security policies
- [ ] Compliance review (GDPR, accounting)
- [ ] Disaster recovery drill

---

## Resources

### Security Tools
- **Password managers:** 1Password, LastPass, KeePass
- **Vulnerability scanning:** `safety check`, `bandit`
- **Encryption:** GPG, OpenSSL
- **Monitoring:** Uptime Robot, Datadog, Prometheus

### Learning Resources
- OWASP Top 10: https://owasp.org/www-project-top-ten/
- Python Security: https://python.readthedocs.io/en/latest/library/security_warnings.html
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

### Compliance
- GDPR: https://gdpr.eu/
- Slovak DPA: https://dataprotection.gov.sk/

---

## Reporting Security Issues

**Found a security vulnerability?**

**DO NOT:**
- Post as GitHub issue (public)
- Discuss on social media
- Share details publicly

**DO:**
- Email: security@icc.sk
- Encrypt with PGP if possible
- Include: description, steps to reproduce, impact
- Allow time for fix before disclosure (90 days)

**We will:**
- Acknowledge within 48 hours
- Investigate and fix
- Credit you (if desired)
- Notify affected customers

---

**END OF SECURITY GUIDELINES**