# -*- coding: utf-8 -*-
"""
Text Utilities - String sanitization functions
"""

from typing import Any, Optional


def clean_string(value: Any) -> Optional[str]:
    """
    Sanitizácia string hodnôt pre PostgreSQL UTF8 encoding.

    Odstraňuje:
    - Null bytes (\x00) - z NEX Genesis Btrieve fixed-width fields
    - Control characters (okrem newline, tab)
    - Prebytočné whitespace

    Args:
        value: Vstupná hodnota (string, int, float, None, atď.)

    Returns:
        Vyčistený string alebo None ak vstup je None/prázdny
    """
    if value is None:
        return None

    # Convert to string if needed
    if not isinstance(value, str):
        value = str(value)

    # Remove null bytes (NEX Genesis Btrieve padding)
    cleaned = value.replace('\x00', '')

    # Remove control characters (except newline \n, tab \t)
    cleaned = ''.join(
        char for char in cleaned
        if ord(char) >= 32 or char in '\n\t'
    )

    # Strip excess whitespace from both ends
    cleaned = cleaned.strip()

    # Return None if result is empty string
    return cleaned if cleaned else None
