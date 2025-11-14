# Email Alerting System

Complete guide for configuring and using the email alerting system.

---

## Overview

The Supplier Invoice Loader includes a comprehensive email alerting system that sends notifications for:

- **Error Alerts** - Critical errors during invoice processing
- **Validation Failures** - Invoices that couldn't be processed automatically
- **Daily Summary** - End-of-day statistics and status report
- **Unhandled Exceptions** - Any unexpected errors caught by global handler

---

## Configuration

### 1. SMTP Settings

Configure in `config_customer.py` or `.env`:

```python
# config_customer.py
ALERT_EMAIL = "it@customer.sk"  # Where to send alerts
SEND_DAILY_SUMMARY = True  # Enable daily summary

# SMTP Configuration (or set in .env)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "automation@customer.sk"
SMTP_PASSWORD = "app-password-here"  # Use Gmail App Password!
SMTP_FROM = "noreply@icc.sk"
```

**Or use environment variables:**

```bash
# .env file
SMTP_USER=automation@customer.sk
SMTP_PASSWORD=your-gmail-app-password
```

### 2. Gmail App Password Setup

**Required for Gmail accounts:**

1. Enable 2-Step Verification:
   - https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. Generate App Password:
   - https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy 16-character password (e.g., `abcd efgh ijkl mnop`)

3. Use in config:
   ```bash
   SMTP_PASSWORD=abcdefghijklmnop  # No spaces in .env
   ```

**⚠️ NEVER use your regular Gmail password!**

---

## Testing Email Configuration

### Quick Test

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Test email configuration
python notifications.py test
```

**Expected output:**
```
Sending test email to: it@customer.sk
SMTP Server: smtp.gmail.com:587
SMTP User: automation@customer.sk
✓ Test email sent successfully!
Check inbox: it@customer.sk
```

### Via API Endpoint

```bash
# Start application
python main.py

# In another terminal:
curl -X POST http://localhost:8000/admin/test-email \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "success": true,
  "message": "Test email sent",
  "recipient": "it@customer.sk"
}
```

---

## Email Types

### 1. Error Alert

**Triggered when:**
- PDF extraction fails
- ISDOC XML generation fails
- Database errors
- API connection errors
- Any unhandled exception

**Email content:**
- Error type and message
- Invoice details (ID, filename)
- Timestamp
- Stack trace (for debugging)

**Example alert:**
```
Subject: [MAGERSTAV] Alert: PDF Extraction Failed

⚠️ Supplier Invoice Loader - Error Alert

Customer: MAGERSTAV
Error Type: PDF Extraction Failed
Time: 2025-10-06 14:30:00
Invoice ID: 42
Filename: invoice_123.pdf

Error Message:
pdfplumber.pdf.PDFSyntaxError: Invalid PDF structure

Stack Trace:
[Full stack trace here]

Action Required:
Please investigate this error and take appropriate action.
```

### 2. Validation Failure

**Triggered when:**
- No PDF attachment in email
- PDF is corrupted or unreadable
- Required fields missing from extracted data

**Email content:**
- Invoice details (filename, sender, subject)
- Reason for validation failure
- Timestamp

**Example:**
```
Subject: [MAGERSTAV] Invoice Validation Failed

⚠️ Invoice Validation Failed

Customer: MAGERSTAV
Time: 2025-10-06 14:30:00
Filename: invoice_123.pdf
From: operator@customer.sk
Subject: Faktúra 2025001

Validation Failure Reason:
No PDF attachment found in email

Action Required:
This invoice could not be processed automatically.
Please review and process manually.
```

### 3. Daily Summary

**Triggered:**
- Manually via API: `POST /admin/send-summary`
- Scheduled task (cron/Task Scheduler)

**Email content:**
- Today's activity (processed, failed)
- All-time statistics
- System status
- Action items if failures detected

**Example:**
```
Subject: [MAGERSTAV] Daily Summary - 2025-10-06

📊 Daily Summary - 2025-10-06

Status: All systems operational

Today's Activity:
  Processed: 15
  Failed: 0

All-Time Statistics:
  Total Invoices: 150
  Successfully Processed: 145
  Pending: 2
  Failed: 3
  Duplicates Prevented: 5
```

---

## Manual Testing

### Send Test Alert

```bash
python notifications.py alert
```

### Send Daily Summary

```bash
python notifications.py summary
```

### From Python Code

```python
from notifications import send_alert_email, send_daily_summary

# Send test alert
send_alert_email(
    "Test Alert",
    "This is a test alert",
    {'test': True}
)

# Send daily summary
send_daily_summary()
```

---

## Automated Daily Summary

### Option 1: Windows Task Scheduler

**Create scheduled task:**

1. Open Task Scheduler
2. Create Task → General:
   - Name: "Invoice Loader Daily Summary"
   - Run whether user is logged on or not
   - Run with highest privileges

3. Triggers:
   - Daily at 23:55 (before midnight)
   - Enabled

4. Actions:
   - Program: `C:\SupplierInvoiceLoader\venv\Scripts\python.exe`
   - Arguments: `notifications.py summary`
   - Start in: `C:\SupplierInvoiceLoader`

5. Conditions:
   - Start only if computer is on AC power: ✗ (unchecked)
   - Wake computer to run: ✓ (checked)

**PowerShell script (alternative):**

```powershell
# send_daily_summary.ps1
cd C:\SupplierInvoiceLoader
.\venv\Scripts\activate
python notifications.py summary
```

**Schedule PowerShell:**
```powershell
$trigger = New-ScheduledTaskTrigger -Daily -At "23:55"
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File C:\SupplierInvoiceLoader\send_daily_summary.ps1"
Register-ScheduledTask -TaskName "Invoice Daily Summary" -Trigger $trigger -Action $action -User "SYSTEM"
```

### Option 2: Linux Cron

**Edit crontab:**
```bash
crontab -e
```

**Add line:**
```cron
# Daily summary at 23:55
55 23 * * * /opt/supplier_invoice_loader/venv/bin/python /opt/supplier_invoice_loader/notifications.py summary >> /var/log/invoice_summary.log 2>&1
```

**Or via systemd timer:**

Create `/etc/systemd/system/invoice-summary.service`:
```ini
[Unit]
Description=Invoice Loader Daily Summary

[Service]
Type=oneshot
User=invoice_loader
WorkingDirectory=/opt/supplier_invoice_loader
ExecStart=/opt/supplier_invoice_loader/venv/bin/python notifications.py summary
```

Create `/etc/systemd/system/invoice-summary.timer`:
```ini
[Unit]
Description=Invoice Loader Daily Summary Timer

[Timer]
OnCalendar=daily
OnCalendar=23:55
Persistent=true

[Install]
WantedBy=timers.target
```

Enable timer:
```bash
sudo systemctl enable invoice-summary.timer
sudo systemctl start invoice-summary.timer
sudo systemctl status invoice-summary.timer
```

### Option 3: Via API Endpoint

**Setup external cron service** (cron-job.org, EasyCron):

```
URL: http://your-server:8000/admin/send-summary
Method: POST
Headers: X-API-Key: your-api-key
Schedule: Daily at 23:55
```

---

## Troubleshooting

### No Emails Received

**Check 1: SMTP Configuration**
```bash
python notifications.py test
```

**Check 2: Environment Variables**
```bash
echo $SMTP_USER
echo $SMTP_PASSWORD
```

**Check 3: Logs**
```bash
tail -f invoice_loader.log | grep SMTP
```

**Common issues:**
- Using regular password instead of App Password
- Wrong SMTP host/port
- Firewall blocking port 587
- Incorrect email address

### Authentication Failed

**Error:**
```
SMTPAuthenticationError: (535, '5.7.8 Username and Password not accepted')
```

**Solutions:**
1. Use Gmail App Password (not regular password)
2. Enable "Less secure app access" (not recommended)
3. Check SMTP_USER and SMTP_PASSWORD are correct
4. Verify 2FA is enabled on Gmail account

### Emails in Spam

**Solutions:**
1. Add sender to safe senders list
2. Use proper SPF/DKIM records (advanced)
3. Use reputable SMTP service
4. Check email content for spam triggers

### Timeout Errors

**Error:**
```
TimeoutError: [Errno 110] Connection timed out
```

**Solutions:**
1. Check internet connectivity
2. Check firewall allows outbound port 587
3. Try different SMTP server
4. Check proxy settings

---

## Email Templates Customization

### Modify Templates

Edit `notifications.py` functions:

```python
def _error_template(error_type: str, error_message: str, details: Dict[str, Any]) -> str:
    # Customize HTML template here
    html = f"""
    <html>
    <body>
        <!-- Your custom template -->
    </body>
    </html>
    """
    return html
```

### Add New Email Type

```python
def send_custom_notification(subject: str, message: str) -> bool:
    """Send custom notification"""
    html = f"""
    <html>
    <body>
        <h2>{subject}</h2>
        <p>{message}</p>
    </body>
    </html>
    """
    
    return _send_email(config.ALERT_EMAIL, subject, html)
```

---

## Integration with Main Application

### Error Alert in Code

```python
from notifications import send_alert_email
import traceback

try:
    # Some operation
    process_invoice()
except Exception as e:
    send_alert_email(
        error_type="Invoice Processing Failed",
        error_message=str(e),
        details={
            'invoice_id': 42,
            'filename': 'invoice.pdf',
            'stack_trace': traceback.format_exc()
        }
    )
```

### Validation Failure

```python
from notifications import send_validation_failed_email

if not pdf_has_text:
    send_validation_failed_email(
        invoice_data={'filename': 'invoice.pdf', 'from': 'sender@example.com'},
        reason='PDF contains no extractable text (scanned image?)'
    )
```

### Global Exception Handler

Already integrated in `main.py`:

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Send email alert
    notifications.send_alert_email(
        error_type=f"Unhandled Exception: {type(exc).__name__}",
        error_message=str(exc),
        details={
            'endpoint': str(request.url.path),
            'stack_trace': traceback.format_exc()
        }
    )
    # Return error response
    ...
```

---

## Security Considerations

### SMTP Credentials

- **NEVER commit** SMTP_PASSWORD to Git
- Use `.env` file or environment variables
- Rotate credentials quarterly
- Use App Passwords (not regular passwords)
- Monitor email account for suspicious activity

### Email Content

- Don't include sensitive customer data in emails
- Redact credit card numbers, passwords, etc.
- Be cautious with PII (personally identifiable information)
- Consider encryption for highly sensitive alerts

### Rate Limiting

Gmail limits:
- 500 emails per day
- 100 recipients per email

Monitor usage to avoid hitting limits.

---

## Monitoring

### Check Email Sending

```bash
# Search logs for email activity
grep "Email sent" invoice_loader.log
grep "SMTP" invoice_loader.log
```

### Track Failures

```bash
# Count email failures
grep "Failed to send email" invoice_loader.log | wc -l
```

### Dashboard (Future Enhancement)

Consider adding metrics:
- Emails sent today
- Failed email attempts
- Average email delivery time
- Alert types distribution

---

## Best Practices

1. **Test thoroughly** before production deployment
2. **Monitor inbox** for first 24 hours after setup
3. **Set up email filters** to organize alerts
4. **Review alerts weekly** - don't ignore them
5. **Update recipients** when team members change
6. **Use multiple recipients** for critical alerts (comma-separated)
7. **Adjust frequency** if too many emails
8. **Document email handling** procedures for team

---

## FAQ

**Q: Can I use Outlook/Office365 instead of Gmail?**  
A: Yes, change SMTP settings:
```python
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "your-email@company.com"
SMTP_PASSWORD = "your-password"
```

**Q: Can I send to multiple recipients?**  
A: Yes, use comma-separated list:
```python
ALERT_EMAIL = "it@customer.sk,manager@customer.sk,support@icc.sk"
```

**Q: Can I disable specific alerts?**  
A: Edit main.py and comment out `notifications.send_alert_email()` calls you don't want.

**Q: How do I change email templates?**  
A: Edit functions in `notifications.py`: `_error_template()`, `_validation_failed_template()`, etc.

**Q: Can I test without sending real emails?**  
A: Set `ALERT_EMAIL = ""` in config to disable all emails. Check logs instead.

---

## Support

If you encounter issues:

1. Check logs: `tail -f invoice_loader.log`
2. Test configuration: `python notifications.py test`
3. Review troubleshooting section above
4. Contact: support@icc.sk

---

**END OF EMAIL ALERTING GUIDE**