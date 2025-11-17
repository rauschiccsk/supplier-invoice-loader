# -*- coding: utf-8 -*-
"""
Tests for configuration loading
"""

import os
import pytest
from pathlib import Path


def test_config_imports():
    """Test that config module can be imported"""
    try:
        from src.utils import config
        assert config is not None
    except ImportError as e:
        pytest.fail(f"Failed to from src.utils import config: {e}")


def test_config_has_required_attributes():
    """Test that config has all required attributes"""
    from src.utils import config

    # Customer specific
    assert hasattr(config, 'CUSTOMER_NAME')
    assert hasattr(config, 'CUSTOMER_FULL_NAME')

    # API
    assert hasattr(config, 'API_KEY')
    assert hasattr(config, 'NEX_GENESIS_API_URL')
    assert hasattr(config, 'NEX_GENESIS_API_KEY')

    # Email
    assert hasattr(config, 'OPERATOR_EMAIL')
    assert hasattr(config, 'AUTOMATION_EMAIL')
    assert hasattr(config, 'ALERT_EMAIL')

    # Monitoring
    assert hasattr(config, 'SEND_DAILY_SUMMARY')
    assert hasattr(config, 'HEARTBEAT_ENABLED')

    # SMTP
    assert hasattr(config, 'SMTP_HOST')
    assert hasattr(config, 'SMTP_PORT')
    assert hasattr(config, 'SMTP_USER')
    assert hasattr(config, 'SMTP_PASSWORD')

    # Paths
    assert hasattr(config, 'BASE_DIR')
    assert hasattr(config, 'PDF_DIR')
    assert hasattr(config, 'XML_DIR')
    assert hasattr(config, 'DB_FILE')
    assert hasattr(config, 'LOG_FILE')


def test_config_customer_name_type():
    """Test that CUSTOMER_NAME is a string"""
    from src.utils import config
    assert isinstance(config.CUSTOMER_NAME, str)
    assert len(config.CUSTOMER_NAME) > 0


def test_config_paths_are_pathlib():
    """Test that path configs are Path objects"""
    from src.utils import config

    assert isinstance(config.BASE_DIR, Path)
    assert isinstance(config.PDF_DIR, Path)
    assert isinstance(config.XML_DIR, Path)
    assert isinstance(config.DB_FILE, Path)
    assert isinstance(config.LOG_FILE, Path)


def test_config_storage_directories_exist():
    """Test that storage directories are created"""
    from src.utils import config

    # Directories should be created by config module
    assert config.PDF_DIR.exists()
    assert config.PDF_DIR.is_dir()

    assert config.XML_DIR.exists()
    assert config.XML_DIR.is_dir()


def test_config_smtp_port_is_int():
    """Test that SMTP_PORT is an integer"""
    from src.utils import config
    assert isinstance(config.SMTP_PORT, int)
    assert config.SMTP_PORT > 0
    assert config.SMTP_PORT <= 65535


def test_config_boolean_flags():
    """Test that boolean flags are actually boolean"""
    from src.utils import config

    assert isinstance(config.SEND_DAILY_SUMMARY, bool)
    assert isinstance(config.HEARTBEAT_ENABLED, bool)


def test_config_api_key_not_default():
    """Test that API key has been changed from default (in production)"""
    from src.utils import config

    # This test will fail in production if default key is used
    # Skip in development
    if 'dev' in config.API_KEY.lower() or 'test' in config.API_KEY.lower():
        pytest.skip("Development/test environment detected")

    assert 'change' not in config.API_KEY.lower()
    assert 'default' not in config.API_KEY.lower()
    assert len(config.API_KEY) >= 16  # Minimum secure length


def test_config_environment_variable_override():
    """Test that environment variables override config values"""
    import sys

    # Save original value
    original_value = os.environ.get('LS_API_KEY')

    # Set test environment variable
    test_key = "test_override_key_12345"
    os.environ['LS_API_KEY'] = test_key

    # Remove ALL related modules from cache
    modules_to_remove = [
        'config.config_template',
        'config.config_customer', 
        'config',
        'src.utils.config',
        'src.utils'
    ]

    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]

    # Fresh import with new environment variable
    from src.utils import config as reloaded_config

    # Check if override worked
    assert reloaded_config.API_KEY == test_key, f"Expected {test_key}, got {reloaded_config.API_KEY}"

    # Cleanup - restore original state
    if original_value is not None:
        os.environ['LS_API_KEY'] = original_value
    else:
        if 'LS_API_KEY' in os.environ:
            del os.environ['LS_API_KEY']

    # Remove from cache again for clean state
    for module_name in modules_to_remove:
        if module_name in sys.modules:
            del sys.modules[module_name]


def test_config_log_level_valid():
    """Test that LOG_LEVEL is a valid logging level"""
    from src.utils import config
    import logging

    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    assert config.LOG_LEVEL.upper() in valid_levels


def test_config_storage_base_exists():
    """Test that STORAGE_BASE directory exists"""
    from src.utils import config

    # STORAGE_BASE might not be directly exposed, but PDF_DIR/XML_DIR should exist
    assert config.PDF_DIR.parent.exists()


@pytest.mark.skipif(
    os.getenv('CI') == 'true',
    reason="Skipping in CI environment"
)
def test_config_customer_specific_file_exists():
    """Test that config_customer.py exists (production check)"""
    from src.utils import config

    config_customer_path = config.BASE_DIR / 'config_customer.py'

    # In production, config_customer.py should exist
    # In development, it might not (using template)
    if not config_customer_path.exists():
        pytest.skip("config_customer.py not found (development mode)")

    assert config_customer_path.exists()
    assert config_customer_path.is_file()


def test_config_nex_genesis_url_format():
    """Test that NEX_GENESIS_API_URL has valid format"""
    from src.utils import config

    url = config.NEX_GENESIS_API_URL

    # Should start with http:// or https://
    assert url.startswith('http://') or url.startswith('https://')

    # Should not end with trailing slash (convention)
    assert not url.endswith('/'), "NEX_GENESIS_API_URL should not have trailing slash"


def test_config_email_addresses_format():
    """Test that email addresses have valid format (basic check)"""
    from src.utils import config

    emails = [
        config.OPERATOR_EMAIL,
        config.AUTOMATION_EMAIL,
        config.ALERT_EMAIL
    ]

    for email in emails:
        if email:  # Some might be optional
            assert '@' in email, f"Invalid email format: {email}"
            assert '.' in email.split('@')[1], f"Invalid domain in email: {email}"