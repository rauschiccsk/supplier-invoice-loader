# Monitoring & Health Checks

Complete guide for monitoring the Supplier Invoice Loader application.

---

## Overview

The application provides comprehensive monitoring capabilities through multiple endpoints:

- **`/health`** - Basic health check (no authentication)
- **`/status`** - Detailed system status (requires API key)
- **`/metrics`** - Metrics in JSON format (no authentication)
- **`/metrics/prometheus`** - Metrics in Prometheus format (no authentication)
- **`/stats`** - Database statistics (no authentication)

---

## Monitoring Endpoints

### 1. Health Check - `/health`

**Purpose:** Basic health status for uptime monitoring  
**Authentication:** None required  
**Use case:** External monitoring (Uptime Robot, Pingdom, StatusCake)

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-06T14:30:00",
  "uptime": "2 days, 3:45:12",
  "storage_ok": true,
  "database_ok": true
}
```

**Status values:**
- `healthy` - All systems operational
- `degraded` - Some components not working
- `unhealthy` - Critical components down

**Monitoring setup:**

**Uptime Robot:**
1. Add new monitor → HTTP(s)
2. URL: `http://your-server:8000/health`
3. Monitoring Interval: 5 minutes
4. Monitor Type: Keyword (look for "healthy")
5. Alert Contacts: Your email/SMS

**Pingdom:**
1. Add new uptime check
2. URL: `http://your-server:8000/health`
3. Check interval: 1 minute
4. Response should contain: "healthy"

---

### 2. Detailed Status - `/status`

**Purpose:** Comprehensive system information  
**Authentication:** Required (X-API-Key header)  
**Use case:** Admin dashboards, troubleshooting

**Request:**
```bash
curl http://localhost:8000/status \
  -H "X-API-Key: your-api-key"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-06T14:30:00",
  "customer": "MAGERSTAV",
  "version": "2.0.0",
  
  "uptime": {
    "started_at": "2025-10-04T10:00:00",
    "uptime_seconds": 189612,
    "uptime_formatted": "2 days, 4:40:12"
  },
  
  "components": {
    "storage": {
      "pdf_dir_exists": true,
      "pdf_dir_writable": true,
      "pdf_dir_path": "C:\\NEX_INVOICES\\PDF",
      "xml_dir_exists": true,
      "xml_dir_writable": true,
      "xml_dir_path": "C:\\NEX_INVOICES\\XML",
      "disk_free_gb": 150.25,
      "disk_used_percent": 45.2,
      "storage_healthy": true
    },
    "database": {
      "db_exists": true,
      "db_accessible": true,
      "db_path": "C:\\SupplierInvoiceLoader\\invoices.db",
      "db_size_mb": 2.34,
      "database_healthy": true
    },
    "smtp": {
      "smtp_configured": true,
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_user": "automation@customer.sk...",
      "alert_email": "it@customer.sk",
      "daily_summary_enabled": true
    }
  },
  
  "system": {
    "cpu_percent": 5.2,
    "memory_total_gb": 16.0,
    "memory_used_gb": 8.5,
    "memory_percent": 53.1,
    "memory_available_gb": 7.5
  },
  
  "statistics": {
    "since_startup": {
      "processed": 45,
      "failed": 2,
      "duplicates": 3,
      "extraction_errors": 1,
      "xml_errors": 0,
      "api_requests": 152,
      "auth_failures": 0
    },
    "last_activity": {
      "last_invoice": "2025-10-06T14:25:00",
      "last_error": "2025-10-06T12:30:00"
    },
    "all_time": {
      "total_invoices": 150,
      "processed_count": 145,
      "pending_count": 2,
      "failed_count": 3
    }
  },
  
  "configuration": {
    "operator_email": "operator@customer.sk",
    "alert_email": "it@customer.sk",
    "daily_summary_enabled": true,
    "heartbeat_enabled": true,
    "nex_api_configured": true
  }
}
```

---

### 3. Metrics (JSON) - `/metrics`

**Purpose:** Monitoring system integration  
**Authentication:** None required  
**Use case:** Custom dashboards, data collection, Grafana

**Request:**
```bash
curl http://localhost:8000/metrics
```

**Response:**
```json
{
  "timestamp": "2025-10-06T14:30:00",
  "uptime_seconds": 189612,
  
  "app_invoices_processed_total": 45,
  "app_invoices_failed_total": 2,
  "app_invoices_duplicates_total": 3,
  "app_extraction_errors_total": 1,
  "app_xml_errors_total": 0,
  "app_api_requests_total": 152,
  "app_auth_failures_total": 0,
  
  "db_invoices_total": 150,
  "db_invoices_processed": 145,
  "db_invoices_pending": 2,
  "db_invoices_failed": 3,
  "db_size_mb": 2.34,
  
  "storage_disk_free_gb": 150.25,
  "storage_disk_used_percent": 45.2,
  "storage_pdf_writable": 1,
  "storage_xml_writable": 1,
  
  "system_cpu_percent": 5.2,
  "system_memory_used_gb": 8.5,
  "system_memory_percent": 53.1,
  "system_memory_available_gb": 7.5,
  
  "health_storage": 1,
  "health_database": 1,
  "health_overall": 1
}
```

---

### 4. Metrics (Prometheus) - `/metrics/prometheus`

**Purpose:** Prometheus monitoring integration  
**Authentication:** None required  
**Use case:** Prometheus scraping

**Request:**
```bash
curl http://localhost:8000/metrics/prometheus
```

**Response:**
```
# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds 189612

# HELP app_invoices_processed_total Total invoices processed successfully since startup
# TYPE app_invoices_processed_total counter
app_invoices_processed_total 45

# HELP app_invoices_failed_total Total invoices failed processing since startup
# TYPE app_invoices_failed_total counter
app_invoices_failed_total 2

# HELP system_cpu_percent CPU usage percentage
# TYPE system_cpu_percent gauge
system_cpu_percent 5.2

# HELP health_overall Overall health status (1=healthy, 0=unhealthy)
# TYPE health_overall gauge
health_overall 1
```

**Prometheus configuration:**

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'supplier-invoice-loader'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/prometheus'
```

---

### 5. Database Statistics - `/stats`

**Purpose:** Invoice processing statistics  
**Authentication:** None required  
**Use case:** Quick status check, reports

**Request:**
```bash
curl http://localhost:8000/stats
```

**Response:**
```json
{
  "total_invoices": 150,
  "processed_count": 145,
  "pending_count": 2,
  "failed_count": 3,
  "duplicate_count": 5,
  "oldest_invoice": "2025-01-01T10:00:00",
  "newest_invoice": "2025-10-06T14:25:00"
}
```

---

## Metrics Tracking

### Application Metrics (Since Startup)

Tracked in memory, reset on application restart:

- **`invoices_processed`** - Successfully processed invoices
- **`invoices_failed`** - Failed processing attempts
- **`invoices_duplicates`** - Duplicate invoices detected
- **`extraction_errors`** - PDF extraction failures
- **`xml_generation_errors`** - ISDOC XML generation failures
- **`api_requests`** - Total API requests received
- **`auth_failures`** - Failed authentication attempts

### Database Metrics (All-Time)

Persistent, stored in database:

- **`total_invoices`** - Total invoices in database
- **`processed_count`** - Successfully processed invoices (all-time)
- **`pending_count`** - Pending invoices
- **`failed_count`** - Failed invoices (all-time)
- **`duplicate_count`** - Duplicates prevented (all-time)

### System Metrics (Real-Time)

- **`cpu_percent`** - CPU usage percentage
- **`memory_used_gb`** - Memory usage in GB
- **`memory_percent`** - Memory usage percentage
- **`disk_free_gb`** - Free disk space in GB
- **`disk_used_percent`** - Disk usage percentage

---

## Setting Up Monitoring

### 1. Uptime Monitoring (Recommended)

**Using Uptime Robot (Free):**

1. Sign up at https://uptimerobot.com/
2. Add New Monitor:
   - Monitor Type: HTTP(s)
   - Friendly Name: "Invoice Loader - MAGERSTAV"
   - URL: `http://your-server-ip:8000/health`
   - Monitoring Interval: 5 minutes
   - Monitor Timeout: 30 seconds

3. Create Alert Contacts:
   - Email: it@customer.sk
   - SMS (optional)
   - Slack/Discord webhook (optional)

4. Test:
   ```bash
   # Stop service temporarily
   Stop-Service SupplierInvoiceLoader
   
   # Wait 5 minutes - should receive alert
   # Start service
   Start-Service SupplierInvoiceLoader
   ```

### 2. Prometheus + Grafana (Advanced)

**Install Prometheus:**

Download from https://prometheus.io/download/

**Configure:**
```yaml
# prometheus.yml
global:
  scrape_interval: 30s

scrape_configs:
  - job_name: 'invoice-loader'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics/prometheus'
```

**Install Grafana:**

Download from https://grafana.com/grafana/download

**Create Dashboard:**

1. Add Prometheus data source
2. Create new dashboard
3. Add panels:
   - Invoices Processed Rate
   - Error Rate
   - CPU/Memory Usage
   - Disk Space
   - Uptime

**Example Grafana queries:**
```promql
# Invoices processed per hour
rate(app_invoices_processed_total[1h])

# Error rate
rate(app_invoices_failed_total[5m])

# Memory usage
system_memory_percent
```

### 3. Custom Monitoring Script

**Simple Python script:**
```python
import requests
import time

def check_health():
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        data = response.json()
        
        if data['status'] != 'healthy':
            send_alert(f"Service unhealthy: {data}")
        
        print(f"✓ Healthy - Uptime: {data['uptime']}")
    except Exception as e:
        send_alert(f"Health check failed: {e}")

def send_alert(message):
    # Implement: email, SMS, Slack, etc.
    print(f"ALERT: {message}")

# Run every 5 minutes
while True:
    check_health()
    time.sleep(300)
```

**Schedule with cron:**
```cron
*/5 * * * * /usr/bin/python3 /path/to/monitoring_script.py
```

---

## Command Line Monitoring

### Quick Health Check

```bash
# Basic check
python monitoring.py health

# Detailed status
python monitoring.py status

# Metrics (JSON)
python monitoring.py metrics

# Metrics (Prometheus format)
python monitoring.py prometheus
```

### Watch Mode

**Linux:**
```bash
# Continuous monitoring (updates every 10 seconds)
watch -n 10 'curl -s http://localhost:8000/health | jq'
```

**PowerShell:**
```powershell
# Continuous monitoring
while ($true) {
    Clear-Host
    curl http://localhost:8000/health | ConvertFrom-Json | ConvertTo-Json
    Start-Sleep -Seconds 10
}
```

---

## Alerting Rules

### Recommended Alerts

**Critical (Immediate Action):**
- Service down (health endpoint unreachable)
- Status = "unhealthy"
- Disk space < 10 GB
- Memory usage > 90%
- Database not accessible

**Warning (Review Soon):**
- Status = "degraded"
- Disk space < 50 GB
- Memory usage > 80%
- Error rate > 10% (last hour)
- No invoices processed in 24 hours

**Info (Monitor):**
- Service restarted
- High processing volume
- Authentication failures

### Email Alert Integration

Already built-in via `notifications.py`:
- Automatic alerts on errors
- Daily summary emails
- Can be customized in code

---

## Dashboard Examples

### Simple HTML Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Invoice Loader Status</title>
    <script>
        async function updateStatus() {
            const response = await fetch('http://localhost:8000/health');
            const data = await response.json();
            
            document.getElementById('status').textContent = data.status;
            document.getElementById('uptime').textContent = data.uptime;
            document.getElementById('status').className = data.status;
        }
        
        setInterval(updateStatus, 10000);  // Update every 10 seconds
        updateStatus();
    </script>
    <style>
        .healthy { color: green; }
        .degraded { color: orange; }
        .unhealthy { color: red; }
    </style>
</head>
<body>
    <h1>Invoice Loader Status</h1>
    <p>Status: <span id="status">...</span></p>
    <p>Uptime: <span id="uptime">...</span></p>
</body>
</html>
```

### Python Dashboard (Rich library)

```python
import requests
from rich.console import Console
from rich.table import Table

console = Console()

def show_status():
    response = requests.get('http://localhost:8000/status', 
                          headers={'X-API-Key': 'your-key'})
    data = response.json()
    
    table = Table(title="Invoice Loader Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    
    table.add_row("Overall", data['status'])
    table.add_row("Uptime", data['uptime']['uptime_formatted'])
    table.add_row("Processed", str(data['statistics']['since_startup']['processed']))
    table.add_row("Failed", str(data['statistics']['since_startup']['failed']))
    table.add_row("CPU", f"{data['system']['cpu_percent']}%")
    table.add_row("Memory", f"{data['system']['memory_percent']}%")
    
    console.print(table)

show_status()
```

---

## Troubleshooting

### Endpoints Not Responding

**Check service is running:**
```bash
# Windows
Get-Service SupplierInvoiceLoader

# Linux
systemctl status supplier-invoice-loader
```

**Check port 8000:**
```bash
netstat -ano | findstr :8000  # Windows
netstat -tlnp | grep 8000     # Linux
```

**Check logs:**
```bash
tail -f invoice_loader.log | grep "Starting server"
```

### High Memory Usage

**Check metrics:**
```bash
curl http://localhost:8000/metrics | jq '.system_memory_percent'
```

**If > 80%:**
- Restart service (clears memory leaks)
- Increase server RAM
- Check for PDF processing issues (large files)

### Metrics Not Updating

**Counters reset on restart** - this is normal for in-memory metrics.

**Database metrics not updating:**
- Check database connectivity
- Check database.py `get_stats()` function
- Check database file permissions

---

## Best Practices

1. **Set up external monitoring** (Uptime Robot, Pingdom)
2. **Monitor metrics daily** (check /status dashboard)
3. **Alert on critical issues** (service down, disk full)
4. **Review logs weekly** for patterns
5. **Test monitoring** (stop service, verify alerts)
6. **Document response procedures** (who to call, what to do)
7. **Keep historical metrics** (trend analysis)
8. **Set up backup monitoring** (secondary service)

---

## Integration Examples

### Slack Webhook

```python
import requests

def send_to_slack(message):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    response = requests.get('http://localhost:8000/health')
    health = response.json()
    
    if health['status'] != 'healthy':
        payload = {
            "text": f"⚠️ Invoice Loader Alert",
            "attachments": [{
                "color": "danger",
                "fields": [
                    {"title": "Status", "value": health['status'], "short": True},
                    {"title": "Uptime", "value": health['uptime'], "short": True}
                ]
            }]
        }
        requests.post(webhook_url, json=payload)
```

### Discord Webhook

```python
import requests

def send_to_discord(message, status):
    webhook_url = "https://discord.com/api/webhooks/YOUR/WEBHOOK"
    
    color = 3066993 if status == 'healthy' else 15158332  # Green or Red
    
    payload = {
        "embeds": [{
            "title": "Invoice Loader Status",
            "description": message,
            "color": color,
            "timestamp": datetime.now().isoformat()
        }]
    }
    
    requests.post(webhook_url, json=payload)
```

---

## FAQ

**Q: How often should I check health?**  
A: Every 5 minutes for uptime monitoring. More frequent checks (30s-1min) for critical systems.

**Q: Do metrics persist after restart?**  
A: In-memory metrics (since_startup) reset. Database metrics (all_time) persist.

**Q: Can I reset counters?**  
A: Yes, but not via API. Would need to add endpoint if needed.

**Q: What's the difference between /health and /status?**  
A: `/health` is lightweight for uptime checks. `/status` requires auth and provides detailed info.

**Q: Why use Prometheus format?**  
A: Industry standard, works with Grafana, many tools support it.

---

## Support

For monitoring issues:
- Check logs: `tail -f invoice_loader.log`
- Test endpoints: `curl http://localhost:8000/health`
- Contact: support@icc.sk

---

**END OF MONITORING GUIDE**