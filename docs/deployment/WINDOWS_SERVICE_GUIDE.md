# Windows Service Installation Guide

## Overview

This guide covers Windows service installation for Supplier Invoice Loader on:
- ✅ Windows 11
- ✅ Windows Server 2012 R2
- ✅ Windows Server 2016/2019/2022
- ✅ Windows 10

---

## ⚡ Quick Installation

### Administrator Mode Required!

```cmd
# Run as Administrator
cd C:\SupplierInvoiceLoader
python service_installer.py install
net start SupplierInvoiceLoader
```

---

## 📋 Installation Methods

### Method 1: Using service_installer.py (Recommended)

**Interactive Mode:**
```cmd
# Run as Administrator
python service_installer.py
# Select option 1 to install
```

**Command Line Mode:**
```cmd
# Install
python service_installer.py install

# Start
python service_installer.py start

# Check status
python service_installer.py status
```

### Method 2: Using deploy.bat

```cmd
# Full deployment with service
cd deploy
deploy.bat new CUSTOMER_NAME
# Answer 'y' when asked about service installation
```

### Method 3: Manual Installation with NSSM

1. **Download NSSM:**
   - Download from https://nssm.cc/download
   - Extract to `tools\nssm\`

2. **Install Service:**
```cmd
# For 64-bit Windows
tools\nssm\win64\nssm.exe install SupplierInvoiceLoader "C:\SupplierInvoiceLoader\venv\Scripts\python.exe"

# Configure
tools\nssm\win64\nssm.exe set SupplierInvoiceLoader AppParameters "C:\SupplierInvoiceLoader\main.py"
tools\nssm\win64\nssm.exe set SupplierInvoiceLoader AppDirectory "C:\SupplierInvoiceLoader"
tools\nssm\win64\nssm.exe set SupplierInvoiceLoader DisplayName "Supplier Invoice Loader"
```

---

## 🔧 Service Configuration

### Basic Properties

| Property | Value |
|----------|-------|
| Service Name | SupplierInvoiceLoader |
| Display Name | Supplier Invoice Loader |
| Description | Automated invoice processing system |
| Startup Type | Automatic |
| Account | Local System |

### Advanced Configuration

#### Log Files
```
Location: C:\SupplierInvoiceLoader\logs\
- service.log         # Main service output
- service_error.log   # Error messages
- invoice_loader.log  # Application log
```

#### Recovery Settings
- First failure: Restart after 1 minute
- Second failure: Restart after 1 minute
- Subsequent failures: Restart after 1 minute
- Reset fail count after: 24 hours

#### Environment Variables
```cmd
# Set via service_installer.py
python service_installer.py configure
# Select option 4
```

---

## 📊 Service Management

### Starting the Service

**Method 1: Command Line**
```cmd
net start SupplierInvoiceLoader
```

**Method 2: Services GUI**
1. Press `Win + R`, type `services.msc`
2. Find "Supplier Invoice Loader"
3. Right-click → Start

**Method 3: PowerShell**
```powershell
Start-Service SupplierInvoiceLoader
```

### Stopping the Service

```cmd
net stop SupplierInvoiceLoader
```

### Restarting the Service

```cmd
python service_installer.py restart
# Or
net stop SupplierInvoiceLoader && net start SupplierInvoiceLoader
```

### Checking Status

```cmd
sc query SupplierInvoiceLoader
```

**Output interpretation:**
```
STATE : 4  RUNNING       # Service is running
STATE : 1  STOPPED       # Service is stopped
STATE : 2  START_PENDING # Service is starting
STATE : 3  STOP_PENDING  # Service is stopping
```

---

## 🛠️ Troubleshooting

### Service Won't Start

**1. Check Python Path**
```cmd
# Verify Python is accessible
C:\SupplierInvoiceLoader\venv\Scripts\python.exe --version
```

**2. Check Logs**
```cmd
# Check error log
type logs\service_error.log

# Check Windows Event Log
eventvwr.msc
# Navigate to Windows Logs → Application
```

**3. Test Manually**
```cmd
cd C:\SupplierInvoiceLoader
venv\Scripts\activate
python main.py
```

### Permission Issues

**Error: "Access Denied"**
- Run as Administrator
- Check service account permissions
- Ensure write access to logs directory

```cmd
# Grant permissions
icacls C:\SupplierInvoiceLoader /grant "NT SERVICE\SupplierInvoiceLoader":F /T
```

### Port Already in Use

**Error: "Port 8000 already in use"**
```cmd
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /F /PID 1234
```

### Service Crashes Immediately

1. Check if virtual environment exists
2. Verify all dependencies installed
3. Check config_customer.py exists
4. Review service_error.log

---

## 🔄 Auto-Restart Configuration

### Configure via service_installer.py

```cmd
python service_installer.py configure
# Select option 2 (Recovery actions)
```

### Configure via SC command

```cmd
sc failure SupplierInvoiceLoader reset=86400 actions=restart/60000/restart/60000/restart/60000
```

### Configure via GUI

1. Open `services.msc`
2. Right-click service → Properties
3. Recovery tab → Configure restart options

---

## 📝 Uninstallation

### Method 1: Using service_installer.py

```cmd
# Run as Administrator
python service_installer.py remove
```

### Method 2: Using Batch Script

```cmd
# Run as Administrator
service_uninstaller.bat
```

### Method 3: Manual Removal

```cmd
# Stop service
net stop SupplierInvoiceLoader

# Delete service
sc delete SupplierInvoiceLoader

# Clean up (optional)
del service_info.json
rmdir /s /q logs
```

---

## 🔐 Security Considerations

### Service Account

**Default:** Local System Account
- Full system privileges
- No network credentials

**Alternative:** Dedicated Service Account
```cmd
# Create service account
net user SvcInvoiceLoader P@ssw0rd123 /add

# Grant "Log on as service" right
secpol.msc → Local Policies → User Rights Assignment

# Configure service
sc config SupplierInvoiceLoader obj=.\SvcInvoiceLoader password=P@ssw0rd123
```

### Firewall Rules

```cmd
# Allow inbound on port 8000
netsh advfirewall firewall add rule name="Invoice Loader API" dir=in action=allow protocol=TCP localport=8000
```

---

## 📊 Monitoring

### Service Health Check

```powershell
# PowerShell script for monitoring
$service = Get-Service SupplierInvoiceLoader
if ($service.Status -ne 'Running') {
    Send-MailMessage -To "admin@company.com" -Subject "Service Down" -Body "Invoice Loader service is not running"
}
```

### Performance Counters

Monitor in Performance Monitor (perfmon.exe):
- Process\% Processor Time (python.exe)
- Process\Private Bytes (python.exe)
- Process\Handle Count (python.exe)

---

## 🎯 Windows 11 Specific Notes

### Windows 11 Requirements
- .NET Framework 3.5 (for NSSM)
- Windows Defender exclusion recommended

```powershell
# Add Defender exclusion
Add-MpPreference -ExclusionPath "C:\SupplierInvoiceLoader"
```

### Windows 11 Service Installation

1. **Enable Developer Mode (Optional)**
   - Settings → Privacy & Security → For developers
   - Enable Developer Mode

2. **Install Service**
   - Must run as Administrator
   - May require approval in Windows Security

---

## 🖥️ Windows Server 2012 R2 Specific Notes

### Prerequisites
- .NET Framework 4.5+ 
- Visual C++ Redistributable 2015-2022
- PowerShell 4.0+

### Server Manager Configuration

1. Add Features:
   - .NET Framework 3.5
   - .NET Framework 4.5

2. Configure Windows Firewall:
```powershell
New-NetFirewallRule -DisplayName "Invoice Loader" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Group Policy Considerations

If in domain environment:
1. Check Group Policy restrictions
2. May need to add service to allowed list
3. Verify service account permissions

---

## 📝 Service Information File

After installation, `service_info.json` contains:

```json
{
  "service_name": "SupplierInvoiceLoader",
  "display_name": "Supplier Invoice Loader",
  "installed_date": "2025-01-15 10:30:00",
  "python_path": "C:\\SupplierInvoiceLoader\\venv\\Scripts\\python.exe",
  "main_script": "C:\\SupplierInvoiceLoader\\main.py",
  "project_root": "C:\\SupplierInvoiceLoader",
  "using_nssm": true,
  "windows_version": "Windows 11 Pro (Build 22000)"
}
```

---

## 🚀 Best Practices

1. **Always test manually first:**
   ```cmd
   python main.py
   ```

2. **Use NSSM for production:**
   - Better logging
   - Rotation support
   - Environment variables
   - I/O redirection

3. **Monitor regularly:**
   - Check service status daily
   - Review logs weekly
   - Set up alerts

4. **Backup before changes:**
   ```cmd
   python migrate_v2.py --backup
   ```

5. **Document configuration:**
   - Service account used
   - Firewall rules added
   - Custom settings

---

## 📞 Support

If service issues persist:

1. Collect information:
   - `service_info.json`
   - `logs\service_error.log`
   - Windows Event Log entries
   - Output of `sc query SupplierInvoiceLoader`

2. Contact support:
   - Email: support@icc.sk
   - Include collected information

---

**End of Windows Service Guide**