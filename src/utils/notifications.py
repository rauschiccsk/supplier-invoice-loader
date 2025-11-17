# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Email Notifications
Handles all email alerts and notifications
"""

import smtplib
import logging
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List, Dict, Any

from src.utils import config
from src.database import database

logger = logging.getLogger(__name__)


# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

def _error_template(error_type: str, error_message: str, details: Dict[str, Any]) -> str:
    """
    Template for error alert emails

    Args:
        error_type: Type of error (e.g., "PDF Processing Failed", "Database Error")
        error_message: Error message
        details: Additional details (invoice_id, filename, stack trace, etc.)

    Returns:
        HTML email body
    """
    invoice_id = details.get('invoice_id', 'N/A')
    filename = details.get('filename', 'N/A')
    timestamp = details.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    stack_trace = details.get('stack_trace', '')

    
    # Escape HTML to prevent XSS
    escaped_error_message = html.escape(error_message)
    escaped_stack_trace = html.escape(stack_trace) if stack_trace else ''

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #d32f2f; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f5f5f5; padding: 20px; border: 1px solid #ddd; }}
            .details {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #d32f2f; }}
            .error-box {{ background-color: #ffebee; padding: 10px; margin: 10px 0; border-radius: 3px; font-family: monospace; font-size: 12px; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; }}
            h2 {{ margin: 0 0 10px 0; }}
            .label {{ font-weight: bold; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>⚠️ Supplier Invoice Loader - Error Alert</h2>
            </div>

            <div class="content">
                <div class="details">
                    <p><span class="label">Customer:</span> {config.CUSTOMER_NAME}</p>
                    <p><span class="label">Error Type:</span> {error_type}</p>
                    <p><span class="label">Time:</span> {timestamp}</p>
                    <p><span class="label">Invoice ID:</span> {invoice_id}</p>
                    <p><span class="label">Filename:</span> {filename}</p>
                </div>

                <h3>Error Message:</h3>
                <div class="error-box">
                    {escaped_error_message}
                </div>

                {f'<h3>Stack Trace:</h3><div class="error-box">{escaped_stack_trace}</div>' if stack_trace else ''}

                <p style="margin-top: 20px;">
                    <strong>Action Required:</strong><br>
                    Please investigate this error and take appropriate action. 
                    Check application logs for more details.
                </p>
            </div>

            <div class="footer">
                <p>Supplier Invoice Loader v2.0 - {config.CUSTOMER_FULL_NAME}</p>
                <p>This is an automated message. Do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_content


def _validation_failed_template(invoice_data: Dict[str, Any], reason: str) -> str:
    """
    Template for validation failure emails

    Args:
        invoice_data: Invoice data that failed validation
        reason: Reason for validation failure

    Returns:
        HTML email body
    """
    filename = invoice_data.get('filename', 'N/A')
    from_email = invoice_data.get('from', 'N/A')
    subject = invoice_data.get('subject', 'N/A')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    
    # Escape HTML to prevent XSS
    escaped_reason = html.escape(reason)

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #ff9800; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f5f5f5; padding: 20px; border: 1px solid #ddd; }}
            .details {{ background-color: white; padding: 15px; margin: 10px 0; border-left: 4px solid #ff9800; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; }}
            h2 {{ margin: 0 0 10px 0; }}
            .label {{ font-weight: bold; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>⚠️ Invoice Validation Failed</h2>
            </div>

            <div class="content">
                <div class="details">
                    <p><span class="label">Customer:</span> {config.CUSTOMER_NAME}</p>
                    <p><span class="label">Time:</span> {timestamp}</p>
                    <p><span class="label">Filename:</span> {filename}</p>
                    <p><span class="label">From:</span> {from_email}</p>
                    <p><span class="label">Subject:</span> {subject}</p>
                </div>

                <h3>Validation Failure Reason:</h3>
                <p style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff9800;">
                    {escaped_reason}
                </p>

                <p style="margin-top: 20px;">
                    <strong>Action Required:</strong><br>
                    This invoice could not be processed automatically. Please review and process manually.
                </p>
            </div>

            <div class="footer">
                <p>Supplier Invoice Loader v2.0 - {config.CUSTOMER_FULL_NAME}</p>
                <p>This is an automated message. Do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_content


def _daily_summary_template(stats: Dict[str, Any]) -> str:
    """
    Template for daily summary emails

    Args:
        stats: Statistics dictionary from database.get_stats()

    Returns:
        HTML email body
    """
    today = datetime.now().strftime('%Y-%m-%d')

    # Extract stats
    total = stats.get('total_invoices', 0)
    processed = stats.get('processed_count', 0)
    pending = stats.get('pending_count', 0)
    failed = stats.get('failed_count', 0)
    duplicates = stats.get('duplicate_count', 0)

    # Calculate today's stats (would need date filtering in database.py)
    # For now, showing all-time stats
    today_processed = processed  # TODO: Filter by today
    today_failed = failed  # TODO: Filter by today

    # Status color
    if failed == 0:
        status_color = "#4caf50"  # Green
        status_text = "All systems operational"
    elif failed < 5:
        status_color = "#ff9800"  # Orange
        status_text = "Some issues detected"
    else:
        status_color = "#d32f2f"  # Red
        status_text = "Multiple failures detected"

    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #1976d2; color: white; padding: 15px; border-radius: 5px 5px 0 0; }}
            .status {{ background-color: {status_color}; color: white; padding: 10px; text-align: center; font-weight: bold; }}
            .content {{ background-color: #f5f5f5; padding: 20px; border: 1px solid #ddd; }}
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 20px 0; }}
            .stat-box {{ background-color: white; padding: 15px; border-radius: 5px; text-align: center; border-left: 4px solid #1976d2; }}
            .stat-number {{ font-size: 32px; font-weight: bold; color: #1976d2; margin: 10px 0; }}
            .stat-label {{ font-size: 14px; color: #666; }}
            .footer {{ background-color: #f5f5f5; padding: 10px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 5px 5px; }}
            h2 {{ margin: 0 0 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>📊 Daily Summary - {today}</h2>
            </div>

            <div class="status">
                {status_text}
            </div>

            <div class="content">
                <h3>Today's Activity</h3>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">Processed</div>
                        <div class="stat-number" style="color: #4caf50;">{today_processed}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Failed</div>
                        <div class="stat-number" style="color: #d32f2f;">{today_failed}</div>
                    </div>
                </div>

                <h3>All-Time Statistics</h3>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">Total Invoices</div>
                        <div class="stat-number">{total}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Successfully Processed</div>
                        <div class="stat-number" style="color: #4caf50;">{processed}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Pending</div>
                        <div class="stat-number" style="color: #ff9800;">{pending}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Failed</div>
                        <div class="stat-number" style="color: #d32f2f;">{failed}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Duplicates Prevented</div>
                        <div class="stat-number" style="color: #9e9e9e;">{duplicates}</div>
                    </div>
                </div>

                {f'<p style="background-color: #ffebee; padding: 15px; border-left: 4px solid #d32f2f; margin-top: 20px;"><strong>Action Required:</strong> {failed} invoices failed processing. Please review logs and take corrective action.</p>' if failed > 0 else ''}
            </div>

            <div class="footer">
                <p>Supplier Invoice Loader v2.0 - {config.CUSTOMER_FULL_NAME}</p>
                <p>Customer: {config.CUSTOMER_NAME}</p>
                <p>This is an automated daily summary. Do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    return html_content


# ============================================================================
# SMTP CONNECTION
# ============================================================================

def _send_email(
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
) -> bool:
    """
    Send email via SMTP

    Args:
        to: Recipient email address (comma-separated for multiple)
        subject: Email subject
        html_body: HTML email body
        text_body: Plain text body (optional, falls back to HTML stripped)

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Parse recipients (support comma-separated list)
        recipients = [r.strip() for r in to.split(',')]

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config.SMTP_FROM
        msg['To'] = to

        # Add text and HTML parts
        if text_body:
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            msg.attach(part1)

        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part2)

        # Connect to SMTP server
        logger.info(f"Connecting to SMTP server: {config.SMTP_HOST}:{config.SMTP_PORT}")

        server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=30)
        server.starttls()  # Enable TLS

        # Login if credentials provided
        if config.SMTP_USER and config.SMTP_PASSWORD:
            logger.info(f"Authenticating as: {config.SMTP_USER}")
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)

        # Send email
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to: {to}")
        logger.info(f"Subject: {subject}")

        return True

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        logger.error("Check SMTP_USER and SMTP_PASSWORD in config/environment")
        return False

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        return False

    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        return False


# ============================================================================
# PUBLIC API
# ============================================================================

def send_alert_email(
        error_type: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send error alert email

    Args:
        error_type: Type of error (e.g., "PDF Processing Failed")
        error_message: Error message
        details: Additional details (invoice_id, filename, stack_trace, etc.)

    Returns:
        True if sent successfully, False otherwise

    Example:
        send_alert_email(
            "PDF Extraction Failed",
            "Could not extract text from PDF",
            {
                'invoice_id': 42,
                'filename': 'invoice.pdf',
                'stack_trace': traceback.format_exc()
            }
        )
    """
    if not config.ALERT_EMAIL:
        logger.warning("ALERT_EMAIL not configured, skipping alert")
        return False

    if details is None:
        details = {}

    # Add timestamp if not present
    if 'timestamp' not in details:
        details['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    subject = f"[{config.CUSTOMER_NAME}] Alert: {error_type}"
    html_body = _error_template(error_type, error_message, details)

    logger.info(f"Sending alert email: {error_type}")
    return _send_email(config.ALERT_EMAIL, subject, html_body)


def send_validation_failed_email(
        invoice_data: Dict[str, Any],
        reason: str
) -> bool:
    """
    Send validation failure notification

    Args:
        invoice_data: Invoice data that failed validation
        reason: Reason for validation failure

    Returns:
        True if sent successfully, False otherwise

    Example:
        send_validation_failed_email(
            {'filename': 'invoice.pdf', 'from': 'sender@example.com'},
            'No PDF attachment found in email'
        )
    """
    if not config.ALERT_EMAIL:
        logger.warning("ALERT_EMAIL not configured, skipping notification")
        return False

    subject = f"[{config.CUSTOMER_NAME}] Invoice Validation Failed"
    html_body = _validation_failed_template(invoice_data, reason)

    logger.info("Sending validation failure notification")
    return _send_email(config.ALERT_EMAIL, subject, html_body)


def send_daily_summary() -> bool:
    """
    Send daily summary email with processing statistics

    Typically called by cron job or scheduled task at end of day

    Returns:
        True if sent successfully, False otherwise

    Example:
        # In cron: 0 23 * * * /path/to/python -c "from src.utils from src.utils import notifications; notifications.send_daily_summary()"
        send_daily_summary()
    """
    if not config.SEND_DAILY_SUMMARY:
        logger.info("Daily summary disabled in config")
        return False

    if not config.ALERT_EMAIL:
        logger.warning("ALERT_EMAIL not configured, skipping summary")
        return False

    # Get statistics
    stats = database.get_stats()

    subject = f"[{config.CUSTOMER_NAME}] Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
    html_body = _daily_summary_template(stats)

    logger.info("Sending daily summary email")
    return _send_email(config.ALERT_EMAIL, subject, html_body)


def test_email_configuration() -> bool:
    """
    Test email configuration by sending a test email

    Returns:
        True if test email sent successfully, False otherwise

    Example:
        python -c "from src.utils from src.utils import notifications; notifications.test_email_configuration()"
    """
    if not config.ALERT_EMAIL:
        logger.error("ALERT_EMAIL not configured")
        print("ERROR: ALERT_EMAIL not set in config")
        return False

    test_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2 style="color: #4caf50;">✓ Email Configuration Test</h2>
        <p>This is a test email from Supplier Invoice Loader.</p>
        <p><strong>Customer:</strong> {config.CUSTOMER_NAME}</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>If you received this email, your SMTP configuration is working correctly!</p>
        <hr>
        <p style="font-size: 12px; color: #666;">
            SMTP Server: {config.SMTP_HOST}:{config.SMTP_PORT}<br>
            SMTP User: {config.SMTP_USER}<br>
            From Address: {config.SMTP_FROM}
        </p>
    </body>
    </html>
    """

    subject = f"[{config.CUSTOMER_NAME}] Email Configuration Test"

    print(f"Sending test email to: {config.ALERT_EMAIL}")
    print(f"SMTP Server: {config.SMTP_HOST}:{config.SMTP_PORT}")
    print(f"SMTP User: {config.SMTP_USER}")

    success = _send_email(config.ALERT_EMAIL, subject, test_html)

    if success:
        print("✓ Test email sent successfully!")
        print(f"Check inbox: {config.ALERT_EMAIL}")
    else:
        print("✗ Failed to send test email")
        print("Check logs for details")

    return success


def send_test_email() -> bool:
    """
    Alias for test_email_configuration() for backward compatibility

    Returns:
        True if test email sent successfully, False otherwise
    """
    return test_email_configuration()


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

if __name__ == "__main__":
    import sys

    # Simple CLI for testing
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            # Test email configuration
            test_email_configuration()

        elif command == "summary":
            # Send daily summary
            send_daily_summary()

        elif command == "alert":
            # Send test alert
            send_alert_email(
                "Test Alert",
                "This is a test alert from command line",
                {'test': True}
            )

        else:
            print("Unknown command")
            print("Usage:")
            print("  python notifications.py test     - Test email configuration")
            print("  python notifications.py summary  - Send daily summary")
            print("  python notifications.py alert    - Send test alert")
    else:
        print("Supplier Invoice Loader - Email Notifications Module")
        print()
        print("Usage:")
        print("  python notifications.py test     - Test email configuration")
        print("  python notifications.py summary  - Send daily summary")
        print("  python notifications.py alert    - Send test alert")
        print()
        print("Or import as module:")
        print("  from src.utils.notifications import send_alert_email, send_daily_summary")