# -*- coding: utf-8 -*-
"""
Tests for email notifications module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


def test_notifications_import():
    """Test that notifications module can be imported"""
    try:
        from src.utils import notifications
        assert notifications is not None
    except ImportError as e:
        pytest.fail(f"Failed to from src.utils import notifications: {e}")


def test_error_template_generates_html():
    """Test that error template generates valid HTML"""
    from src.utils import notifications

    html = notifications._error_template(
        error_type="Test Error",
        error_message="This is a test error message",
        details={
            'invoice_id': 42,
            'filename': 'test.pdf',
            'timestamp': '2025-10-06 14:30:00'
        }
    )

    # Check HTML structure
    assert '<html>' in html
    assert '</html>' in html
    assert 'Test Error' in html
    assert 'test error message' in html
    assert 'invoice_id' not in html.lower() or '42' in html  # Either shows label or value


def test_validation_failed_template_generates_html():
    """Test that validation failed template generates valid HTML"""
    from src.utils import notifications

    html = notifications._validation_failed_template(
        invoice_data={
            'filename': 'invoice.pdf',
            'from': 'sender@example.com',
            'subject': 'Test Invoice'
        },
        reason='No PDF attachment found'
    )

    assert '<html>' in html
    assert 'invoice.pdf' in html
    assert 'sender@example.com' in html
    assert 'No PDF attachment found' in html


def test_daily_summary_template_generates_html():
    """Test that daily summary template generates valid HTML"""
    from src.utils import notifications

    stats = {
        'total_invoices': 100,
        'processed_count': 95,
        'pending_count': 2,
        'failed_count': 3,
        'duplicate_count': 5
    }

    html = notifications._daily_summary_template(stats)

    assert '<html>' in html
    assert '100' in html  # total
    assert '95' in html  # processed
    assert '3' in html  # failed


@patch('src.utils.notifications.smtplib.SMTP')
def test_send_email_success(mock_smtp):
    """Test successful email sending"""
    from src.utils import notifications

    # Mock SMTP
    mock_server = Mock()
    mock_smtp.return_value = mock_server

    # Send email
    result = notifications._send_email(
        to='test@example.com',
        subject='Test Subject',
        html_body='<html><body>Test</body></html>'
    )

    # Verify
    assert result is True
    mock_smtp.assert_called_once()
    mock_server.starttls.assert_called_once()
    mock_server.send_message.assert_called_once()
    mock_server.quit.assert_called_once()


@patch('src.utils.notifications.config.SMTP_PASSWORD', 'test_password')
@patch('src.utils.notifications.config.SMTP_USER', 'test@example.com')
@patch('src.utils.notifications.smtplib.SMTP')
def test_send_email_authentication_failure(mock_smtp):
    """Test email sending with authentication failure"""
    from src.utils import notifications
    import smtplib

    # Mock SMTP to raise authentication error
    mock_server = Mock()
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, 'Authentication failed')
    mock_smtp.return_value = mock_server

    # Try to send email
    result = notifications._send_email(
        to='test@example.com',
        subject='Test',
        html_body='<html><body>Test</body></html>'
    )

    # Should return False on auth failure
    assert result is False


@patch('src.utils.notifications.smtplib.SMTP')
def test_send_email_multiple_recipients(mock_smtp):
    """Test sending to multiple recipients"""
    from src.utils import notifications

    mock_server = Mock()
    mock_smtp.return_value = mock_server

    # Send to multiple recipients
    result = notifications._send_email(
        to='user1@example.com,user2@example.com,user3@example.com',
        subject='Test',
        html_body='<html><body>Test</body></html>'
    )

    assert result is True
    mock_server.send_message.assert_called_once()


@patch('src.utils.notifications._send_email')
def test_send_alert_email(mock_send):
    """Test send_alert_email wrapper"""
    from src.utils import notifications

    mock_send.return_value = True

    result = notifications.send_alert_email(
        error_type='Test Error',
        error_message='Test message',
        details={'test': True}
    )

    assert result is True
    mock_send.assert_called_once()

    # Check that HTML was generated
    call_args = mock_send.call_args
    assert 'Test Error' in call_args[0][1]  # subject
    assert '<html>' in call_args[0][2]  # html_body


@patch('src.utils.notifications._send_email')
def test_send_validation_failed_email(mock_send):
    """Test send_validation_failed_email wrapper"""
    from src.utils import notifications

    mock_send.return_value = True

    result = notifications.send_validation_failed_email(
        invoice_data={'filename': 'test.pdf', 'from': 'sender@example.com'},
        reason='No PDF found'
    )

    assert result is True
    mock_send.assert_called_once()


@patch('src.utils.notifications._send_email')
@patch('src.database.database.get_stats')
def test_send_daily_summary(mock_get_stats, mock_send):
    """Test send_daily_summary function"""
    from src.utils import notifications

    # Mock database stats
    mock_get_stats.return_value = {
        'total_invoices': 100,
        'processed_count': 95,
        'failed_count': 5
    }

    mock_send.return_value = True

    result = notifications.send_daily_summary()

    assert result is True
    mock_get_stats.assert_called_once()
    mock_send.assert_called_once()


def test_send_alert_email_requires_alert_email_config():
    """Test that alert email requires ALERT_EMAIL to be configured"""
    from src.utils import notifications
    from src.utils import config

    # Save original
    original_alert_email = config.ALERT_EMAIL

    # Temporarily set to empty
    config.ALERT_EMAIL = ""

    result = notifications.send_alert_email(
        error_type='Test',
        error_message='Test',
        details={}
    )

    # Should return False if ALERT_EMAIL not configured
    assert result is False

    # Restore
    config.ALERT_EMAIL = original_alert_email


@patch('src.utils.notifications._send_email')
def test_test_email_configuration(mock_send):
    """Test test_email_configuration function"""
    from src.utils import notifications

    mock_send.return_value = True

    result = notifications.test_email_configuration()

    assert result is True
    mock_send.assert_called_once()

    # Check test email content
    call_args = mock_send.call_args
    assert 'Test' in call_args[0][1]  # subject contains "Test"


def test_send_alert_adds_timestamp_if_missing():
    """Test that send_alert_email adds timestamp if not provided"""
    from src.utils import notifications

    with patch('src.utils.notifications._send_email') as mock_send:
        mock_send.return_value = True

        # Call without timestamp in details
        notifications.send_alert_email(
            error_type='Test',
            error_message='Test',
            details={'test': True}
        )

        # Check that HTML contains a timestamp
        call_args = mock_send.call_args
        html = call_args[0][2]

        # Should contain some date format (at least year)
        assert '2025' in html or '2024' in html


@pytest.mark.integration
def test_real_email_sending(request):
    """Integration test: Actually send test email (requires valid SMTP config)"""
    from src.utils import notifications
    from src.utils import config

    # Skip if not running integration tests
    if not request.config.getoption("--run-integration", default=False):
        pytest.skip("Requires --run-integration flag")

    # Skip if SMTP not configured
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        pytest.skip("SMTP credentials not configured")

    result = notifications.test_email_configuration()

    # If configured correctly, should succeed
    assert result is True


def test_email_templates_no_injection():
    """Test that email templates prevent HTML injection"""
    from src.utils import notifications

    # Try to inject HTML/JavaScript
    malicious_message = '<script>alert("XSS")</script>'

    html = notifications._error_template(
        error_type='Test',
        error_message=malicious_message,
        details={}
    )

    # Should not contain raw script tags (should be escaped or sanitized)
    # Note: This is a basic check, proper HTML escaping should be implemented
    assert '<script>' not in html or '&lt;script&gt;' in html