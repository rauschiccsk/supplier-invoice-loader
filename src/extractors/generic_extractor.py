# -*- coding: utf-8 -*-
"""
Generic Extractor - For standard invoice formats
"""

import logging
from typing import Optional
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)


class GenericExtractor(BaseExtractor):
    """
    Generic extractor for standard invoice formats
    Works with most common accounting software outputs
    """

    def __init__(self):
        super().__init__()
        self.supplier_name = "Generic"

    def extract_from_pdf(self, pdf_path: str):
        """
        Extract invoice data from standard PDF format

        TODO: Implement generic extraction logic
        - Detect common patterns (Invoice Number:, Date:, Total:)
        - Extract using flexible regex patterns
        - Handle multiple date formats
        - Parse simple item tables

        Args:
            pdf_path: Path to PDF file

        Returns:
            InvoiceData object or None
        """
        if not self.validate_pdf(pdf_path):
            return None

        logger.warning(f"Generic extractor not yet implemented for: {pdf_path}")

        # TODO: Implement extraction
        return None


# Helper function for compatibility
def extract_invoice_data(pdf_path: str):
    """Wrapper function for generic extraction"""
    extractor = GenericExtractor()
    return extractor.extract_from_pdf(pdf_path)