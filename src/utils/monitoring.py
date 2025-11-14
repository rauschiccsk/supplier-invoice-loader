# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Monitoring & Metrics
Tracks application health, uptime, and processing statistics
"""

import time
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path

from src.utils from src.utils import config
import database

logger = logging.getLogger(__name__)


# ============================================================================
# GLOBAL STATE
# ============================================================================

class ApplicationMetrics:
    """
    In-memory metrics tracking
    Persists for the lifetime of the application process
    """

    def __init__(self):
        self.start_time = time.time()
        self.start_datetime = datetime.now()

        # Processing counters (since startup)
        self.invoices_processed = 0
        self.invoices_failed = 0
        self.invoices_duplicates = 0
        self.extraction_errors = 0
        self.xml_generation_errors = 0

        # Request counters
        self.api_requests = 0
        self.auth_failures = 0

        # Last activity
        self.last_invoice_time: Optional[datetime] = None
        self.last_error_time: Optional[datetime] = None

    def increment_processed(self):
        """Increment successful invoice counter"""
        self.invoices_processed += 1
        self.last_invoice_time = datetime.now()

    def increment_failed(self):
        """Increment failed invoice counter"""
        self.invoices_failed += 1
        self.last_error_time = datetime.now()

    def increment_duplicate(self):
        """Increment duplicate counter"""
        self.invoices_duplicates += 1

    def increment_extraction_error(self):
        """Increment extraction error counter"""
        self.extraction_errors += 1
        self.last_error_time = datetime.now()

    def increment_xml_error(self):
        """Increment XML generation error counter"""
        self.xml_generation_errors += 1
        self.last_error_time = datetime.now()

    def increment_api_request(self):
        """Increment API request counter"""
        self.api_requests += 1

    def increment_auth_failure(self):
        """Increment authentication failure counter"""
        self.auth_failures += 1

    def get_uptime_seconds(self) -> float:
        """Get uptime in seconds"""
        return time.time() - self.start_time

    def get_uptime_formatted(self) -> str:
        """Get uptime as formatted string (e.g., '2 days, 3:45:12')"""
        uptime_seconds = self.get_uptime_seconds()
        return str(timedelta(seconds=int(uptime_seconds)))

    def reset_counters(self):
        """Reset all counters (keep start_time)"""
        logger.info("Resetting application metrics counters")
        self.invoices_processed = 0
        self.invoices_failed = 0
        self.invoices_duplicates = 0
        self.extraction_errors = 0
        self.xml_generation_errors = 0
        self.api_requests = 0
        self.auth_failures = 0
        self.last_invoice_time = None
        self.last_error_time = None


# Global metrics instance
metrics = ApplicationMetrics()


# ============================================================================
# HEALTH CHECK
# ============================================================================

def check_storage_health() -> Dict[str, Any]:
    """
    Check storage directories health

    Returns:
        Dict with storage status and details
    """
    pdf_dir_ok = config.PDF_DIR.exists() and config.PDF_DIR.is_dir()
    xml_dir_ok = config.XML_DIR.exists() and config.XML_DIR.is_dir()

    # Check if writable
    pdf_writable = False
    xml_writable = False

    if pdf_dir_ok:
        try:
            test_file = config.PDF_DIR / '.write_test'
            test_file.touch()
            test_file.unlink()
            pdf_writable = True
        except Exception:
            pass

    if xml_dir_ok:
        try:
            test_file = config.XML_DIR / '.write_test'
            test_file.touch()
            test_file.unlink()
            xml_writable = True
        except Exception:
            pass

    # Get disk usage
    try:
        usage = psutil.disk_usage(str(config.STORAGE_BASE))
        disk_free_gb = usage.free / (1024 ** 3)
        disk_used_percent = usage.percent
    except Exception:
        disk_free_gb = None
        disk_used_percent = None

    return {
        'pdf_dir_exists': pdf_dir_ok,
        'pdf_dir_writable': pdf_writable,
        'pdf_dir_path': str(config.PDF_DIR),
        'xml_dir_exists': xml_dir_ok,
        'xml_dir_writable': xml_writable,
        'xml_dir_path': str(config.XML_DIR),
        'disk_free_gb': round(disk_free_gb, 2) if disk_free_gb else None,
        'disk_used_percent': disk_used_percent,
        'storage_healthy': pdf_dir_ok and pdf_writable and xml_dir_ok and xml_writable
    }


def check_database_health() -> Dict[str, Any]:
    """
    Check database health

    Returns:
        Dict with database status and details
    """
    db_exists = config.DB_FILE.exists()
    db_accessible = False
    db_size_mb = None

    if db_exists:
        try:
            # Try to query database
            stats = database.get_stats()
            db_accessible = True

            # Get database file size
            db_size_mb = config.DB_FILE.stat().st_size / (1024 ** 2)
        except Exception as e:
            logger.error(f"Database health check failed: {e}")

    return {
        'db_exists': db_exists,
        'db_accessible': db_accessible,
        'db_path': str(config.DB_FILE),
        'db_size_mb': round(db_size_mb, 2) if db_size_mb else None,
        'database_healthy': db_exists and db_accessible
    }


def check_smtp_config() -> Dict[str, Any]:
    """
    Check SMTP configuration (doesn't test connection)

    Returns:
        Dict with SMTP configuration status
    """
    smtp_configured = bool(
        config.SMTP_HOST and
        config.SMTP_PORT and
        config.SMTP_USER and
        config.SMTP_PASSWORD
    )

    alert_email_configured = bool(config.ALERT_EMAIL)

    return {
        'smtp_configured': smtp_configured,
        'smtp_host': config.SMTP_HOST,
        'smtp_port': config.SMTP_PORT,
        'smtp_user': config.SMTP_USER[:20] + '...' if config.SMTP_USER else None,
        'alert_email': config.ALERT_EMAIL if alert_email_configured else None,
        'daily_summary_enabled': config.SEND_DAILY_SUMMARY
    }


def get_system_info() -> Dict[str, Any]:
    """
    Get system resource information

    Returns:
        Dict with CPU, memory, and disk usage
    """
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()

        return {
            'cpu_percent': round(cpu_percent, 1),
            'memory_total_gb': round(memory.total / (1024 ** 3), 2),
            'memory_used_gb': round(memory.used / (1024 ** 3), 2),
            'memory_percent': round(memory.percent, 1),
            'memory_available_gb': round(memory.available / (1024 ** 3), 2)
        }
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {
            'cpu_percent': None,
            'memory_total_gb': None,
            'memory_used_gb': None,
            'memory_percent': None,
            'memory_available_gb': None
        }


# ============================================================================
# HEALTH STATUS
# ============================================================================

def get_health_status() -> Dict[str, Any]:
    """
    Get overall health status (for /health endpoint)

    Returns:
        Dict with basic health status
    """
    storage = check_storage_health()
    database = check_database_health()

    # Determine overall status
    if storage['storage_healthy'] and database['database_healthy']:
        status = 'healthy'
    elif storage['storage_healthy'] or database['database_healthy']:
        status = 'degraded'
    else:
        status = 'unhealthy'

    return {
        'status': status,
        'timestamp': datetime.now().isoformat(),
        'uptime': metrics.get_uptime_formatted(),
        'storage_ok': storage['storage_healthy'],
        'database_ok': database['database_healthy']
    }


def get_detailed_status() -> Dict[str, Any]:
    """
    Get detailed status (for /status endpoint)

    Returns:
        Dict with comprehensive status information
    """
    storage = check_storage_health()
    database = check_database_health()
    smtp = check_smtp_config()
    system = get_system_info()

    # Get database stats
    try:
        db_stats = database.get_stats()
    except Exception:
        db_stats = {}

    # Overall status
    components_ok = [
        storage['storage_healthy'],
        database['database_healthy'],
        smtp['smtp_configured']
    ]

    if all(components_ok):
        overall_status = 'healthy'
    elif any(components_ok):
        overall_status = 'degraded'
    else:
        overall_status = 'unhealthy'

    return {
        'status': overall_status,
        'timestamp': datetime.now().isoformat(),
        'customer': config.CUSTOMER_NAME,
        'version': '2.0.0',

        # Uptime
        'uptime': {
            'started_at': metrics.start_datetime.isoformat(),
            'uptime_seconds': int(metrics.get_uptime_seconds()),
            'uptime_formatted': metrics.get_uptime_formatted()
        },

        # Component health
        'components': {
            'storage': storage,
            'database': database,
            'smtp': smtp
        },

        # System resources
        'system': system,

        # Processing statistics (since startup)
        'statistics': {
            'since_startup': {
                'processed': metrics.invoices_processed,
                'failed': metrics.invoices_failed,
                'duplicates': metrics.invoices_duplicates,
                'extraction_errors': metrics.extraction_errors,
                'xml_errors': metrics.xml_generation_errors,
                'api_requests': metrics.api_requests,
                'auth_failures': metrics.auth_failures
            },
            'last_activity': {
                'last_invoice': metrics.last_invoice_time.isoformat() if metrics.last_invoice_time else None,
                'last_error': metrics.last_error_time.isoformat() if metrics.last_error_time else None
            },
            'all_time': db_stats
        },

        # Configuration (safe subset)
        'configuration': {
            'operator_email': config.OPERATOR_EMAIL,
            'alert_email': config.ALERT_EMAIL,
            'daily_summary_enabled': config.SEND_DAILY_SUMMARY,
            'heartbeat_enabled': config.HEARTBEAT_ENABLED,
            'nex_api_configured': bool(config.NEX_GENESIS_API_URL and config.NEX_GENESIS_API_KEY)
        }
    }


def get_metrics() -> Dict[str, Any]:
    """
    Get metrics in Prometheus-like format (for /metrics endpoint)

    Returns:
        Dict with metrics suitable for monitoring systems
    """
    storage = check_storage_health()
    database = check_database_health()
    system = get_system_info()

    try:
        db_stats = database.get_stats()
    except Exception:
        db_stats = {}

    return {
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': int(metrics.get_uptime_seconds()),

        # Application metrics
        'app_invoices_processed_total': metrics.invoices_processed,
        'app_invoices_failed_total': metrics.invoices_failed,
        'app_invoices_duplicates_total': metrics.invoices_duplicates,
        'app_extraction_errors_total': metrics.extraction_errors,
        'app_xml_errors_total': metrics.xml_generation_errors,
        'app_api_requests_total': metrics.api_requests,
        'app_auth_failures_total': metrics.auth_failures,

        # Database metrics (all-time)
        'db_invoices_total': db_stats.get('total_invoices', 0),
        'db_invoices_processed': db_stats.get('processed_count', 0),
        'db_invoices_pending': db_stats.get('pending_count', 0),
        'db_invoices_failed': db_stats.get('failed_count', 0),
        'db_size_mb': database['db_size_mb'],

        # Storage metrics
        'storage_disk_free_gb': storage['disk_free_gb'],
        'storage_disk_used_percent': storage['disk_used_percent'],
        'storage_pdf_writable': 1 if storage['pdf_dir_writable'] else 0,
        'storage_xml_writable': 1 if storage['xml_dir_writable'] else 0,

        # System metrics
        'system_cpu_percent': system['cpu_percent'],
        'system_memory_used_gb': system['memory_used_gb'],
        'system_memory_percent': system['memory_percent'],
        'system_memory_available_gb': system['memory_available_gb'],

        # Health flags (1 = healthy, 0 = unhealthy)
        'health_storage': 1 if storage['storage_healthy'] else 0,
        'health_database': 1 if database['database_healthy'] else 0,
        'health_overall': 1 if (storage['storage_healthy'] and database['database_healthy']) else 0
    }


# ============================================================================
# PROMETHEUS FORMAT (Optional)
# ============================================================================

def get_metrics_prometheus() -> str:
    """
    Get metrics in Prometheus text format

    Returns:
        String in Prometheus exposition format
    """
    metrics_dict = get_metrics()

    lines = [
        '# HELP app_uptime_seconds Application uptime in seconds',
        '# TYPE app_uptime_seconds gauge',
        f'app_uptime_seconds {metrics_dict["uptime_seconds"]}',
        '',
        '# HELP app_invoices_processed_total Total invoices processed successfully since startup',
        '# TYPE app_invoices_processed_total counter',
        f'app_invoices_processed_total {metrics_dict["app_invoices_processed_total"]}',
        '',
        '# HELP app_invoices_failed_total Total invoices failed processing since startup',
        '# TYPE app_invoices_failed_total counter',
        f'app_invoices_failed_total {metrics_dict["app_invoices_failed_total"]}',
        '',
        '# HELP app_invoices_duplicates_total Total duplicate invoices detected since startup',
        '# TYPE app_invoices_duplicates_total counter',
        f'app_invoices_duplicates_total {metrics_dict["app_invoices_duplicates_total"]}',
        '',
        '# HELP db_invoices_total Total invoices in database (all-time)',
        '# TYPE db_invoices_total gauge',
        f'db_invoices_total {metrics_dict["db_invoices_total"]}',
        '',
        '# HELP system_cpu_percent CPU usage percentage',
        '# TYPE system_cpu_percent gauge',
        f'system_cpu_percent {metrics_dict["system_cpu_percent"] or 0}',
        '',
        '# HELP system_memory_percent Memory usage percentage',
        '# TYPE system_memory_percent gauge',
        f'system_memory_percent {metrics_dict["system_memory_percent"] or 0}',
        '',
        '# HELP health_overall Overall health status (1=healthy, 0=unhealthy)',
        '# TYPE health_overall gauge',
        f'health_overall {metrics_dict["health_overall"]}',
        ''
    ]

    return '\n'.join(lines)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_recent_errors(limit: int = 10) -> list:
    """
    Get recent error logs from log file

    Args:
        limit: Maximum number of errors to return

    Returns:
        List of recent error log entries
    """
    try:
        errors = []
        with open(config.LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if '[ERROR]' in line or '[CRITICAL]' in line:
                    errors.append(line.strip())

        return errors[-limit:]  # Return last N errors
    except Exception as e:
        logger.error(f"Failed to read log file: {e}")
        return []


def get_log_summary() -> Dict[str, int]:
    """
    Get summary of log levels from log file

    Returns:
        Dict with counts per log level
    """
    try:
        counts = {
            'DEBUG': 0,
            'INFO': 0,
            'WARNING': 0,
            'ERROR': 0,
            'CRITICAL': 0
        }

        with open(config.LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                for level in counts.keys():
                    if f'[{level}]' in line:
                        counts[level] += 1
                        break

        return counts
    except Exception as e:
        logger.error(f"Failed to analyze log file: {e}")
        return {}


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "health":
            status = get_health_status()
            print(json.dumps(status, indent=2))

        elif command == "status":
            status = get_detailed_status()
            print(json.dumps(status, indent=2))

        elif command == "metrics":
            metrics_data = get_metrics()
            print(json.dumps(metrics_data, indent=2))

        elif command == "prometheus":
            print(get_metrics_prometheus())

        else:
            print("Unknown command")
            print("Usage:")
            print("  python monitoring.py health      - Basic health check")
            print("  python monitoring.py status      - Detailed status")
            print("  python monitoring.py metrics     - Metrics (JSON)")
            print("  python monitoring.py prometheus  - Metrics (Prometheus)")
    else:
        print("Supplier Invoice Loader - Monitoring Module")
        print()
        print("Usage:")
        print("  python monitoring.py health      - Basic health check")
        print("  python monitoring.py status      - Detailed status")
        print("  python monitoring.py metrics     - Metrics (JSON)")
        print("  python monitoring.py prometheus  - Metrics (Prometheus format)")