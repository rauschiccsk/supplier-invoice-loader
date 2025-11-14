# -*- coding: utf-8 -*-
"""
Base Extractor - Abstract class for all invoice extractors
"""

from abc import ABC, abstractmethod
from typing import Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseExtractor(ABC):
    """
    Abstract base class for invoice extractors
    All supplier-specific extractors must inherit from this
    """

    def __init__(self):
        self.supplier_name = "Unknown"

    @abstractmethod
    def extract_from_pdf(self, pdf_path: str):
        """
        Extract invoice data from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            InvoiceData object or None if extraction failed
        """
        pass

    def validate_pdf(self, pdf_path: str) -> bool:
        """
        Validate that PDF file exists and is readable
        """
        path = Path(pdf_path)
        if not path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return False

        if not path.suffix.lower() == '.pdf':
            logger.error(f"File is not PDF: {pdf_path}")
            return False

        return True