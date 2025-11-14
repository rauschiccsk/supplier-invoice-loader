# Release Notes - Version 2.0.0

**Release Date:** January 2025  
**Codename:** Multi-Customer Edition

---

## 🎉 Major Release Highlights

### Multi-Customer Support
Complete transformation from single-customer to multi-tenant architecture, enabling deployment for multiple customers from single codebase.

### Production Readiness
Enterprise-grade features including Windows service support, comprehensive monitoring, and automated deployment tools.

### Enhanced Reliability
Robust error handling, automatic recovery, and failover mechanisms for 24/7 operation.

---

## ✨ New Features

### 1. Multi-Customer Architecture
- **Customer Isolation**: Complete data separation per customer
- **Template System**: Single codebase, multiple configurations
- **Dynamic Configuration**: Customer-specific settings without code changes
- **Database Migration**: Automated migration to v2 schema with multi-customer fields

### 2. Windows Service Support
- **Native Windows Service**: Full integration with Windows Service Manager
- **NSSM Integration**: Advanced service management capabilities
- **Auto-Recovery**: Automatic restart on failures
- **Service Installer**: One-click service installation script
- **Windows 11 & Server 2012 R2+**: Full compatibility

### 3. Deployment Automation
- **Deployment Scripts**: Automated installation for Windows/Linux/Mac
- **Package Builder**: ZIP package generation for distribution
- **Environment Detection**: Automatic OS and dependency detection
- **One-Command Deploy**: `deploy.bat new CUSTOMER_NAME`

### 4. Enhanced Monitoring
- **Health Endpoints**: `/health`, `/status`, `/metrics`
- **Email Alerts**: Automatic error notifications
- **Daily Summaries**: Automated daily processing reports
- **Metrics Tracking**: Performance and usage statistics
- **Prometheus Support**: Metrics in Prometheus format

### 5. NEX Genesis Integration
- **API Integration**: Direct synchronization with NEX Genesis
- **Status Tracking**: Sync status per invoice
- **Error Recovery**: Automatic retry on failures
- **Bulk Operations**: Batch processing support

### 6. Professional Documentation
- **Deployment Guide**: Step-by-step deployment instructions
- **User Guide**: Operator manual in Slovak
- **API Documentation**: Complete API reference
- **Troubleshooting Guide**: Common issues and solutions
- **Migration Guide**: Database migration procedures

### 7. Testing Infrastructure
- **80+ Unit Tests**: Comprehensive test coverage
- **End-to-End Testing**: Complete system validation
- **Load Testing**: Performance validation
- **Failover Testing**: Resilience verification

### 8. Email System
- **SMTP Integration**: Configurable email notifications
- **Alert Templates**: Professional HTML email templates
- **Daily Summaries**: Automated reporting
- **Error Notifications**: Immediate problem alerts
- **Test Mode**: Email configuration testing

---

## 🔧 Technical Improvements

### Performance
- **Optimized Database Queries**: Indexed columns for fast lookups
- **Async Processing**: Non-blocking API operations
- **Connection Pooling**: Efficient resource management
- **Memory Management**: Reduced memory footprint

### Security
- **API Key Authentication**: Secure API access
- **Environment Variables**: Sensitive data protection
- **SQL Injection Prevention**: Parameterized queries
- **File System Security**: Restricted file access
- **Service Account Support**: Least privilege principle

### Reliability
- **Transaction Support**: ACID compliance for database operations
- **Duplicate Detection**: SHA-256 hash-based deduplication
- **Error Recovery**: Automatic retry mechanisms
- **Graceful Shutdown**: Clean service termination
- **Data Validation**: Input sanitization and validation

### Maintainability
- **Modular Architecture**: Clear separation of concerns
- **Factory Pattern**: Extractor plugin system
- **Configuration Templates**: Easy customer onboarding
- **Comprehensive Logging**: Detailed operation logs
- **Code Documentation**: Inline documentation and docstrings

---

## 📦 Components

### Core Modules
- `main.py` - FastAPI application
- `database.py` - Database operations (v2 with multi-customer)
- `config.py` - Configuration management
- `models.py` - Pydantic data models
- `notifications.py` - Email notification system
- `monitoring.py` - Health and metrics
- `isdoc.py` - ISDOC XML generation

### Extractors
- `extractors/base_extractor.py` - Abstract base class
- `extractors/ls_extractor.py` - L&Š specific extraction
- `extractors/generic_extractor.py` - Template for new extractors

### Deployment Tools
- `deploy/deploy.sh` - Linux/Mac deployment
- `deploy/deploy.bat` - Windows deployment
- `deploy/build_package.py` - Package builder
- `service_installer.py` - Windows service installer
- `migrate_v2.py` - Database migration tool

### Testing
- `test_e2e.py` - End-to-end testing
- `tests/` - Unit test suite
- `conftest.py` - Test fixtures
- Test coverage: 80%+

---

## 📊 Statistics

- **Total Lines of Code:** 15,000+
- **Files Created:** 50+
- **Tests Written:** 80+
- **Documentation Pages:** 20+
- **Deployment Time:** < 10 minutes
- **Processing Speed:** 30-60 seconds per invoice

---

## 🔄 Migration from v1.x

### Database Migration
```bash
# Check if migration needed
python migrate_v2.py --check

# Run migration (creates automatic backup)
python migrate_v2.py

# Verify migration
sqlite3 invoices.db "SELECT COUNT(DISTINCT customer_name) FROM invoices;"
```

### Configuration Migration
1. Copy `config_customer.py` from v1
2. Add new required fields:
   - `CUSTOMER_NAME`
   - `NEX_GENESIS_API_URL`
   - `NEX_GENESIS_API_KEY`

### Service Update
```bash
# Stop old service
net stop InvoiceLoader

# Install new service
python service_installer.py install

# Start new service
net start SupplierInvoiceLoader
```

---

## 🐛 Bug Fixes

- Fixed duplicate detection edge cases
- Resolved memory leak in PDF processing
- Fixed timezone handling in timestamps
- Corrected UTF-8 encoding issues
- Fixed service shutdown race condition
- Resolved database locking issues
- Fixed email template rendering
- Corrected API error responses

---

## ⚠️ Breaking Changes

### Database Schema
- New required field: `customer_name`
- New tracking fields for NEX Genesis
- Migration required from v1.x

### Configuration
- Config split into template and customer files
- Environment variables now required for sensitive data
- New mandatory configuration fields

### API
- API key now required for all endpoints except `/health`
- Changed response format for error messages
- New required fields in invoice submission

---

## 📋 Known Issues

1. **Large PDF Processing**: PDFs over 10MB may timeout
   - Workaround: Increase timeout in config
   
2. **Special Characters**: Some Unicode characters in PDFs may not extract correctly
   - Workaround: Manual entry for affected fields

3. **Concurrent Access**: Database may lock under heavy concurrent load
   - Workaround: Use API rate limiting

---

## 🚀 Deployment Requirements

### Minimum Requirements
- **OS**: Windows 11, Windows Server 2012 R2+, Linux, macOS
- **Python**: 3.8+
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 10GB free space
- **Network**: Internet access for email and API

### Dependencies
- FastAPI 0.104.1+
- SQLite 3.x
- Python packages (see requirements.txt)
- NSSM (optional, for Windows service)

---

## 📝 Documentation

### For Administrators
- [Deployment Guide](DEPLOYMENT.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Windows Service Guide](WINDOWS_SERVICE_GUIDE.md)
- [Monitoring Guide](../operations/MONITORING.md)

### For Operators
- [User Guide](../operations/USER_GUIDE.md) (Slovak)
- [Troubleshooting Guide](../operations/TROUBLESHOOTING.md)
- [FAQ](../operations/USER_GUIDE.md#často-kladené-otázky)

### For Developers
- [Development Guide](../guides/DEVELOPMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [Testing Guide](../guides/TESTING.md)

---

## 🙏 Acknowledgments

- **MAGERSTAV** - First customer and beta tester
- **Development Team** - Design and implementation
- **Open Source Community** - Libraries and tools

---

## 📞 Support

**Email**: support@icc.sk  
**Documentation**: https://github.com/rauschiccsk/supplier_invoice_loader  
**Issues**: GitHub Issues

---

## 🔮 Future Plans (v2.1)

- [ ] Web UI for invoice management
- [ ] Multiple PDF attachments support
- [ ] OCR for scanned invoices
- [ ] Machine learning for extraction improvement
- [ ] REST API v2 with GraphQL
- [ ] Docker containerization
- [ ] Kubernetes deployment manifests
- [ ] Multi-language support

---

## 📜 License

Proprietary - All rights reserved

---

## 🎯 Upgrade Checklist

Before upgrading to v2.0.0:

- [ ] Backup database
- [ ] Backup configuration
- [ ] Test in development environment
- [ ] Read breaking changes section
- [ ] Plan maintenance window
- [ ] Prepare rollback plan
- [ ] Update documentation
- [ ] Train operators
- [ ] Monitor after deployment

---

**Thank you for using Supplier Invoice Loader v2.0.0!**

*"Making invoice processing simple, reliable, and scalable."*

---

**End of Release Notes v2.0.0**