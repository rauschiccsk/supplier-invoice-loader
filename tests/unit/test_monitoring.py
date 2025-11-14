# -*- coding: utf-8 -*-
"""
Tests for monitoring and metrics functionality
"""

import pytest
import time


def test_monitoring_module_imports():
    """Test that monitoring module can be imported"""
    try:
        from src.utils import monitoring
        assert monitoring is not None
    except ImportError as e:
        pytest.fail(f"Failed to from src.utils import monitoring: {e}")


def test_application_metrics_class_exists():
    """Test that ApplicationMetrics class exists"""
    from src.utils.monitoring import ApplicationMetrics

    assert ApplicationMetrics is not None


def test_create_application_metrics():
    """Test creating ApplicationMetrics instance"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    assert metrics.start_time > 0
    assert metrics.invoices_processed == 0
    assert metrics.invoices_failed == 0
    assert metrics.invoices_duplicates == 0


def test_increment_processed():
    """Test incrementing processed counter"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    initial = metrics.invoices_processed
    metrics.increment_processed()

    assert metrics.invoices_processed == initial + 1
    assert metrics.last_invoice_time is not None


def test_increment_failed():
    """Test incrementing failed counter"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    initial = metrics.invoices_failed
    metrics.increment_failed()

    assert metrics.invoices_failed == initial + 1
    assert metrics.last_error_time is not None


def test_increment_duplicate():
    """Test incrementing duplicate counter"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    initial = metrics.invoices_duplicates
    metrics.increment_duplicate()

    assert metrics.invoices_duplicates == initial + 1


def test_uptime_calculation():
    """Test uptime calculation"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    # Wait a tiny bit
    time.sleep(0.1)

    uptime = metrics.get_uptime_seconds()
    assert uptime > 0
    assert uptime >= 0.1


def test_uptime_formatted():
    """Test formatted uptime string"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    uptime_str = metrics.get_uptime_formatted()

    assert isinstance(uptime_str, str)
    assert ':' in uptime_str  # Should contain time separator


def test_reset_counters():
    """Test resetting metrics counters"""
    from src.utils.monitoring import ApplicationMetrics

    metrics = ApplicationMetrics()

    # Increment some counters
    metrics.increment_processed()
    metrics.increment_failed()
    metrics.increment_duplicate()

    # Verify they're not zero
    assert metrics.invoices_processed > 0
    assert metrics.invoices_failed > 0

    # Reset
    metrics.reset_counters()

    # Should be zero again
    assert metrics.invoices_processed == 0
    assert metrics.invoices_failed == 0
    assert metrics.invoices_duplicates == 0


def test_check_storage_health():
    """Test storage health check"""
    from src.utils import monitoring

    result = monitoring.check_storage_health()

    assert isinstance(result, dict)
    assert 'pdf_dir_exists' in result
    assert 'xml_dir_exists' in result
    assert 'storage_healthy' in result

    # Should be boolean values
    assert isinstance(result['storage_healthy'], bool)


def test_check_database_health():
    """Test database health check"""
    from src.utils import monitoring

    result = monitoring.check_database_health()

    assert isinstance(result, dict)
    assert 'db_exists' in result
    assert 'db_accessible' in result
    assert 'database_healthy' in result


def test_check_smtp_config():
    """Test SMTP configuration check"""
    from src.utils import monitoring

    result = monitoring.check_smtp_config()

    assert isinstance(result, dict)
    assert 'smtp_configured' in result
    assert 'alert_email' in result
    assert 'daily_summary_enabled' in result


def test_get_system_info():
    """Test system information retrieval"""
    from src.utils import monitoring

    result = monitoring.get_system_info()

    assert isinstance(result, dict)

    # Should have CPU and memory info
    # Values might be None if psutil fails
    assert 'cpu_percent' in result
    assert 'memory_percent' in result


def test_get_health_status():
    """Test health status endpoint data"""
    from src.utils import monitoring

    result = monitoring.get_health_status()

    assert isinstance(result, dict)
    assert 'status' in result
    assert 'timestamp' in result
    assert 'uptime' in result
    assert 'storage_ok' in result
    assert 'database_ok' in result

    # Status should be one of expected values
    assert result['status'] in ['healthy', 'degraded', 'unhealthy']


def test_get_detailed_status():
    """Test detailed status endpoint data"""
    from src.utils import monitoring

    result = monitoring.get_detailed_status()

    assert isinstance(result, dict)
    assert 'status' in result
    assert 'timestamp' in result
    assert 'customer' in result
    assert 'uptime' in result
    assert 'components' in result
    assert 'statistics' in result

    # Check nested structure
    assert 'storage' in result['components']
    assert 'database' in result['components']
    assert 'smtp' in result['components']


def test_get_metrics():
    """Test metrics endpoint data"""
    from src.utils import monitoring

    result = monitoring.get_metrics()

    assert isinstance(result, dict)
    assert 'timestamp' in result
    assert 'uptime_seconds' in result
    assert 'app_invoices_processed_total' in result
    assert 'app_invoices_failed_total' in result

    # All counters should be integers
    assert isinstance(result['uptime_seconds'], int)


def test_get_metrics_prometheus():
    """Test Prometheus format metrics"""
    from src.utils import monitoring

    result = monitoring.get_metrics_prometheus()

    assert isinstance(result, str)

    # Should contain Prometheus format elements
    assert '# HELP' in result
    assert '# TYPE' in result
    assert 'app_uptime_seconds' in result


def test_global_metrics_instance():
    """Test that global metrics instance exists"""
    from src.utils import monitoring

    # Should have global metrics instance
    assert hasattr(monitoring, 'metrics')
    assert monitoring.metrics is not None


def test_metrics_persistence():
    """Test that metrics persist across function calls"""
    from src.utils import monitoring

    # Get current value
    initial = monitoring.metrics.invoices_processed

    # Increment
    monitoring.metrics.increment_processed()

    # Should persist
    assert monitoring.metrics.invoices_processed == initial + 1

    # Call metrics function - should still have same value
    result = monitoring.get_metrics()
    assert result['app_invoices_processed_total'] == initial + 1


def test_health_status_values():
    """Test that health status returns correct values"""
    from src.utils import monitoring

    status = monitoring.get_health_status()

    # If storage and DB are healthy, overall should be healthy
    if status['storage_ok'] and status['database_ok']:
        assert status['status'] == 'healthy'

    # If neither is healthy, should be unhealthy
    if not status['storage_ok'] and not status['database_ok']:
        assert status['status'] == 'unhealthy'


def test_system_info_types():
    """Test that system info returns correct types"""
    from src.utils import monitoring

    info = monitoring.get_system_info()

    # CPU and memory should be numbers or None
    if info['cpu_percent'] is not None:
        assert isinstance(info['cpu_percent'], (int, float))
        assert 0 <= info['cpu_percent'] <= 100

    if info['memory_percent'] is not None:
        assert isinstance(info['memory_percent'], (int, float))
        assert 0 <= info['memory_percent'] <= 100


@pytest.mark.integration
def test_end_to_end_monitoring():
    """Integration test for full monitoring workflow"""
    from src.utils import monitoring

    # Simulate some activity
    monitoring.metrics.increment_processed()
    monitoring.metrics.increment_processed()
    monitoring.metrics.increment_failed()

    # Get metrics
    metrics = monitoring.get_metrics()

    # Should reflect our activity
    assert metrics['app_invoices_processed_total'] >= 2
    assert metrics['app_invoices_failed_total'] >= 1