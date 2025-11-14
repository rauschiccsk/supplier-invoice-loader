# N8N Workflow Setup Guide

Complete guide for importing and configuring the Supplier Invoice Loader n8n workflow.

---

## Overview

**Workflow Name:** SupplierInvoiceEmailLoader  
**Purpose:** Automatically processes supplier invoices from email  
**Trigger:** IMAP Email monitoring  
**Output:** Posts invoice data to Python API for processing

### Workflow Architecture

```
┌─────────────────────┐
│ IMAP Email Trigger  │ ← Monitors operator's email
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Split PDF        │ ← JavaScript: Extract PDF attachments
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Check PDF Present   │ ← Switch: Is PDF attached?
└──────┬──────────────┘
       │
       ├─YES──────────────────────┐
       │                          │
       ▼                          ▼
┌──────────────────┐    ┌─────────────────┐
│ HTTP POST to     │    │ Send Alert      │
│ Python API       │    │ Email (no PDF)  │
└──────────────────┘    └─────────────────┘
```

---

## Before You Begin

Ensure you have:

1. **n8n instance running** (self-hosted or cloud)
2. **IMAP email account** for operator
   - Gmail, Outlook, or custom IMAP server
   - IMAP access enabled
3. **Gmail account** for sending alerts (can be same as IMAP)
   - OAuth2 configured in n8n
4. **Python API running** and accessible
5. **API Key** from Python config (config.API_KEY)

---

## Step 1: Import Workflow Template

### 1.1 Download Template

Download `n8n_workflow_template.json` from the repository:
```
https://github.com/rauschiccsk/supplier_invoice_loader/blob/v2.0-multi-customer/n8n_workflow_template.json
```

### 1.2 Import into n8n

1. Open n8n UI (usually http://localhost:5678)
2. Click **"+"** (Create New Workflow)
3. Click **menu** (3 dots) → **Import from File**
4. Select `n8n_workflow_template.json`
5. Click **Import**

Workflow will appear with placeholder values that need configuration.

---

## Step 2: Configure Credentials

### 2.1 IMAP Credentials (Email Trigger)

**Node:** "Email Trigger (IMAP)"

1. Click on **Email Trigger (IMAP)** node
2. Click **Credential to connect with** dropdown
3. Click **"+ Create New Credential"**

**For Gmail:**
```
Host: imap.gmail.com
Port: 993
User: operator@customer.com
Password: <app-password>  ← Use App Password, not regular password!
SSL/TLS: Enabled
```

**Gmail App Password Setup:**
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Select "Mail" and generate
4. Use that password in n8n (not your regular password)

**For Outlook/Office365:**
```
Host: outlook.office365.com
Port: 993
User: operator@company.com
Password: <password>
SSL/TLS: Enabled
```

**For Custom IMAP:**
```
Host: mail.yourserver.com
Port: 993 (or 143 for non-SSL)
User: username
Password: password
SSL/TLS: Enabled (recommended)
```

4. Click **Save**
5. Test connection (n8n will try to connect)

### 2.2 Gmail OAuth2 Credentials (Alert Email)

**Node:** "Send Alert Email"

1. Click on **Send Alert Email** node
2. Click **Credential to connect with** dropdown
3. Click **"+ Create New Credential"**
4. Select **Gmail OAuth2**

**Setup Gmail OAuth2:**

n8n requires OAuth2 app setup in Google Cloud Console:

1. Go to: https://console.cloud.google.com/
2. Create new project (or use existing)
3. Enable Gmail API
4. Create OAuth2 credentials (Web application)
5. Add redirect URI: `https://your-n8n-instance.com/rest/oauth2-credential/callback`
6. Copy Client ID and Client Secret
7. In n8n credential:
   - Paste Client ID
   - Paste Client Secret
   - Click **Connect my account**
   - Authorize with Google

**Alternative: SMTP instead of Gmail**

If Gmail OAuth2 is too complex, you can replace "Send Alert Email" node with "Send Email" (SMTP) node:
- Node type: Email Send (SMTP)
- SMTP settings from config_customer.py
- Simpler but less reliable

---

## Step 3: Configure Nodes

### 3.1 Email Trigger (IMAP) - Advanced Settings

Click on **Email Trigger (IMAP)** node:

**Basic Settings:**
- **Mailbox Name:** `INBOX` (default)
- **Action:** `Mark as read` (prevents reprocessing)

**Email Filters (Options → Add Option → Custom Email Config):**

Example filter for L&Š invoices:
```javascript
// In "Simple" mode, filter by:
Subject Contains: "Faktúra"
From Contains: "ls.sk" or specific supplier domain

// OR use "Custom Email Config" for advanced filtering:
{
  "search": ["UNSEEN", ["FROM", "operator@customer.sk"]]
}
```

**Recommended Settings:**
- **Options → Download Attachments:** ✓ Enabled
- **Options → Mark as Read:** ✓ Enabled (prevents duplicates)
- **Execute Once:** ✗ Disabled (continuous monitoring)

### 3.2 Split PDF Node (JavaScript Code)

**No changes needed** - this node is generic and works for all customers.

What it does:
- Extracts all PDF attachments from email
- Converts to base64
- Creates JSON objects for each PDF
- Handles missing PDFs gracefully

### 3.3 Check PDF Present Node (Switch)

**No changes needed** - logic is universal.

Routes to:
- **Output 1:** If PDF exists → send to Python API
- **Output 2:** If no PDF → send alert email

### 3.4 HTTP -> Python /invoice Node ⚠️ IMPORTANT

Click on **HTTP -> Python /invoice** node:

**Replace Placeholders:**

1. **URL:** 
   ```
   PLACEHOLDER_PYTHON_API_URL
   ↓ Replace with:
   http://SERVER-IP:8000/invoice
   
   Examples:
   - Local: http://127.0.0.1:8000/invoice
   - Same network: http://192.168.1.100:8000/invoice
   - VPN/Cloud: http://10.0.1.50:8000/invoice
   ```

2. **X-API-Key Header:**
   ```
   PLACEHOLDER_API_KEY
   ↓ Replace with:
   Your actual API key from config.API_KEY
   
   Example: ls-prod-key-XyZ123AbC456DeF789
   
   ⚠️ Must match exactly with Python config!
   ```

**Timeout:**
- Keep at 120000 ms (2 minutes)
- Large PDFs may take time to process

**Body Parameters:**
- Leave as is - these map to Python API request model
- DO NOT change parameter names

### 3.5 Send Alert Email Node

Click on **Send Alert Email** node:

**Replace Placeholders:**

1. **Send To:**
   ```
   PLACEHOLDER_ALERT_EMAIL
   ↓ Replace with:
   it@customer.sk
   
   Or multiple recipients (comma-separated):
   it@customer.sk,operator@customer.sk
   ```

2. **Subject (Optional):**
   - Keep default or customize
   - Current: "⚠️ Nerozpoznaná faktúra - {{ subject }}"

3. **Message (Optional):**
   - Keep default or customize
   - Shows: From, Subject, Date

---

## Step 4: Configuration Summary

### Quick Reference Table

| Node | Parameter | Placeholder | Replace With | Example |
|------|-----------|-------------|--------------|---------|
| Email Trigger (IMAP) | Credentials | CONFIGURE | IMAP account details | operator@customer.sk |
| HTTP -> Python | URL | PLACEHOLDER_PYTHON_API_URL | Python API endpoint | http://192.168.1.50:8000/invoice |
| HTTP -> Python | X-API-Key | PLACEHOLDER_API_KEY | API key from config | ls-prod-key-abc123 |
| Send Alert Email | Credentials | CONFIGURE | Gmail OAuth2 | automation@customer.sk |
| Send Alert Email | Send To | PLACEHOLDER_ALERT_EMAIL | Alert recipient | it@customer.sk |

---

## Step 5: Test Workflow

### 5.1 Manual Test Execution

1. **Activate workflow:** Click **Active** toggle in top right
2. **Send test email** to operator email:
   - From: operator@customer.sk (or configured sender)
   - Subject: "Test Faktúra"
   - Attach: Sample PDF invoice
3. **Watch execution:**
   - Click **Executions** tab
   - Wait 30-60 seconds (IMAP polling interval)
   - Should see new execution

### 5.2 Verify Each Node

Click on execution to see data flow:

**✓ Email Trigger:** Should show email details
```json
{
  "from": "operator@customer.sk",
  "subject": "Test Faktúra",
  "date": "2025-10-06...",
  "attachments": [...],
  ...
}
```

**✓ Split PDF:** Should show extracted PDF
```json
{
  "file_b64": "JVBERi0xLjQK...",
  "filename": "invoice.pdf",
  "message_id": "...",
  "from": "operator@customer.sk",
  ...
}
```

**✓ Check PDF Present:** Should route to Output 1 (HTTP node)

**✓ HTTP -> Python:** Should return success
```json
{
  "status": "success",
  "message": "Invoice processed: 2025001",
  "invoice_id": 42,
  "duplicate": false,
  ...
}
```

### 5.3 Test Error Path

Send email **without** PDF attachment:

1. Send email with just text (no attachment)
2. **Check PDF Present** should route to Output 2
3. **Send Alert Email** should execute
4. Check alert email inbox - should receive notification

---

## Step 6: Production Deployment

### 6.1 Pre-Production Checklist

- [ ] All credentials configured and tested
- [ ] Python API URL points to production server (not localhost)
- [ ] API key matches production config (not dev key)
- [ ] Alert email recipient correct
- [ ] IMAP filters configured correctly
- [ ] Test execution successful with real invoice
- [ ] Error path tested (email without PDF)

### 6.2 Activate Workflow

1. Click **Active** toggle → ON
2. Workflow will now run continuously
3. Monitor first 24 hours closely

### 6.3 Monitoring

**Check Execution History:**
- Executions tab shows all runs
- Filter by: Success, Error, Waiting

**Common Execution States:**
- ✅ **Success:** Invoice processed successfully
- ⚠️ **Warning:** No PDF attached (alert sent)
- ❌ **Error:** API connection failed, timeout, etc.

**Set up Alerts (Optional):**
- n8n can send webhook on workflow error
- Configure in: Workflow Settings → Error Workflow

---

## Troubleshooting

### Workflow Not Triggering

**Symptom:** No executions appearing

**Solutions:**
1. Check workflow is **Active** (toggle in top right)
2. Check IMAP credentials are valid
3. Test IMAP connection:
   - Click "Email Trigger" node
   - Click "Test Step"
4. Check IMAP mailbox has new emails matching filter
5. Check n8n logs: `docker logs n8n` or n8n UI logs

---

### HTTP Request Fails (Connection Refused)

**Symptom:**
```
Error: connect ECONNREFUSED 127.0.0.1:8000
```

**Solutions:**
1. Check Python API is running:
   ```bash
   curl http://SERVER-IP:8000/health
   ```
2. Check URL in HTTP node (should be server IP, not 127.0.0.1)
3. Check firewall allows connection from n8n server to Python server
4. Try from n8n server:
   ```bash
   curl http://PYTHON-SERVER-IP:8000/health
   ```

---

### HTTP Request Fails (401 Unauthorized)

**Symptom:**
```
{"detail": "Invalid API key"}
```

**Solutions:**
1. Check X-API-Key header value in HTTP node
2. Check Python config.API_KEY value:
   ```bash
   python -c "import config; print(config.API_KEY)"
   ```
3. Ensure they match exactly (case-sensitive)
4. Restart Python service after changing API key

---

### Alert Email Not Sending

**Symptom:** Gmail node fails or no email received

**Solutions:**
1. Check Gmail OAuth2 credential is connected
2. Re-authorize if expired (click "Reconnect")
3. Check recipient email address is valid
4. Check Gmail sending limits not exceeded (500/day)
5. Check spam folder of recipient

**Alternative:** Replace Gmail node with SMTP node (simpler but less reliable)

---

### PDF Not Extracted

**Symptom:** "No PDF attachment found" error even when PDF attached

**Solutions:**
1. Check "Download Attachments" is enabled in IMAP node
2. Check email actually contains PDF (not just link)
3. Check PDF size < 25 MB (IMAP limitations)
4. Try different PDF (some are corrupted)
5. Check Split PDF node in executions - does $binary have attachment_0?

---

### Duplicate Invoices

**Symptom:** Same invoice processed multiple times

**Solutions:**
1. Enable "Mark as Read" in IMAP node options
2. Check if email client is moving emails back to INBOX
3. Python API has duplicate detection (file_hash) - should reject duplicates
4. Check database for duplicates:
   ```sql
   SELECT file_hash, COUNT(*) FROM invoices GROUP BY file_hash HAVING COUNT(*) > 1;
   ```

---

## Advanced Configuration

### Custom Email Filters

**Filter only from specific sender:**
```javascript
// In IMAP node → Options → Custom Email Config
{
  "search": ["UNSEEN", ["FROM", "operator@customer.sk"]]
}
```

**Filter by subject:**
```javascript
{
  "search": ["UNSEEN", ["SUBJECT", "Faktúra"], ["FROM", "operator@customer.sk"]]
}
```

**Multiple suppliers:**
```javascript
{
  "search": ["UNSEEN", ["OR", ["FROM", "supplier1@example.com"], ["FROM", "supplier2@example.com"]]]
}
```

---

### Multiple Workflows per Customer

If customer has multiple suppliers with different formats:

**Option A: Single workflow with supplier detection**
- Add Switch node after Split PDF
- Route to different HTTP endpoints based on sender
- Python API has different extractors per supplier

**Option B: Separate workflows**
- Clone this workflow
- Configure different IMAP filters (by sender/subject)
- Point to different Python extractors
- Easier to manage, more isolated

---

### Retry Logic

**Add retry on HTTP failure:**

1. Click **HTTP -> Python** node
2. Settings → **Retry On Fail:** Enable
3. **Maximum Retries:** 3
4. **Wait Between Tries:** 5000 ms

This helps with temporary network issues or API overload.

---

### Workflow Scheduling

**Option: Process emails only during business hours**

1. Add **Schedule** node before IMAP trigger
2. Configure: Weekdays, 8 AM - 6 PM
3. Or use Cron: `0 8-18 * * 1-5` (8 AM-6 PM, Mon-Fri)

**Benefit:** Reduces server load, aligns with operator working hours

---

## Backup & Version Control

### Export Workflow

1. Click menu (3 dots) → **Download**
2. Save as: `SupplierInvoiceEmailLoader_CUSTOMER_v1.json`
3. Store in safe location (NOT in Git - contains credentials)

**Recommended:**
- Export monthly backups
- Export before major changes
- Document version in filename

### Restore Workflow

1. Import JSON file (same as Step 1)
2. Reconfigure credentials (not exported)
3. Test thoroughly before activating

---

## Multi-Customer Deployment

### Approach 1: Separate n8n Instances

- Each customer has own n8n instance
- Complete isolation
- Higher resource usage

### Approach 2: Shared n8n with Separate Workflows

- One n8n instance
- Multiple workflows (one per customer)
- Use naming: `InvoiceLoader_MAGERSTAV`, `InvoiceLoader_ANDROS`
- Each points to different Python API endpoint
- Easier management, lower costs

### Approach 3: Single Workflow with Router

- One workflow for all customers
- Switch node routes by sender email
- More complex logic
- Not recommended (harder to debug)

**Recommendation:** Use Approach 2 for most cases.

---

## Security Best Practices

1. **Credentials:**
   - Never commit n8n credentials to Git
   - Use n8n's credential encryption
   - Rotate passwords quarterly

2. **API Keys:**
   - Use strong random keys (32+ chars)
   - Different key per customer
   - Store securely in n8n credentials (not hardcoded)

3. **Network:**
   - Use HTTPS for n8n if internet-exposed
   - Firewall n8n → Python API communication
   - Use VPN for cross-site deployments

4. **Email:**
   - Use app passwords, not account passwords
   - Enable 2FA on email accounts
   - Monitor for unauthorized access

5. **Monitoring:**
   - Review execution history weekly
   - Set up alerts for workflow failures
   - Monitor for unusual activity (high volume, errors)

---

## Maintenance

### Weekly Tasks
- Review execution history for errors
- Check alert email for unprocessed invoices
- Verify Python API health endpoint

### Monthly Tasks
- Export workflow backup
- Review and clean execution history (n8n database)
- Update n8n if new version available
- Check credential expiration (OAuth2)

### Quarterly Tasks
- Rotate API keys
- Review email account security
- Performance review (execution times)
- Customer feedback session

---

## Support

### Documentation
- n8n Docs: https://docs.n8n.io/
- Python API: See DEPLOYMENT.md
- This workflow: See GitHub repository

### Contact
- **Technical Support:** support@icc.sk
- **GitHub Issues:** https://github.com/rauschiccsk/supplier_invoice_loader/issues
- **Emergency:** +421 XXX XXX XXX

---

**END OF N8N WORKFLOW SETUP GUIDE**