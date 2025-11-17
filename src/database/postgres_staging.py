# -*- coding: utf-8 -*-
"""
PostgreSQL Staging Database Client
Zaevidovanie faktúr do staging databázy pre invoice-editor aplikáciu
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from decimal import Decimal

try:
    import pg8000
except ImportError:
    pg8000 = None

logger = logging.getLogger(__name__)


class PostgresStagingClient:
    """
    PostgreSQL client pre staging databázu invoice-editor aplikácie.
    Používa pg8000 (Pure Python driver, 32-bit compatible).
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Inicializácia PostgreSQL klienta.

        Args:
            config: Dict s kľúčmi: host, port, database, user, password
        """
        if pg8000 is None:
            raise ImportError(
                "pg8000 package not installed. "
                "Install with: pip install pg8000"
            )

        self.config = config
        self.conn = None

        logger.info(
            f"PostgresStagingClient initialized: "
            f"{config['host']}:{config['port']}/{config['database']}"
        )

    def connect(self) -> None:
        """Vytvorenie spojenia s databázou."""
        try:
            self.conn = pg8000.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
            logger.info("PostgreSQL connection established")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def disconnect(self) -> None:
        """Zatvorenie spojenia s databázou."""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("PostgreSQL connection closed")

    def __enter__(self):
        """Context manager enter."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is not None:
            if self.conn:
                self.conn.rollback()
                logger.warning("Transaction rolled back due to exception")
        self.disconnect()

    def insert_invoice_with_items(
        self,
        invoice_data: Dict[str, Any],
        items_data: List[Dict[str, Any]],
        isdoc_xml: Optional[str] = None
    ) -> Optional[int]:
        """
        Zaevidovanie faktúry s položkami do staging databázy.

        Args:
            invoice_data: Dict s údajmi faktúry (supplier_ico, supplier_name,
                         invoice_number, invoice_date, due_date, total_amount, currency)
            items_data: List Dict s položkami faktúry (line_number, name, quantity,
                       unit, price_per_unit, ean, vat_rate)
            isdoc_xml: Voliteľne kompletný ISDOC XML string

        Returns:
            invoice_id ak úspešné, None ak zlyhalo
        """
        if not self.conn:
            logger.error("Not connected to database")
            return None

        cursor = None
        try:
            cursor = self.conn.cursor()

            # Insert invoice header
            cursor.execute("""
                INSERT INTO invoices_pending (
                    supplier_ico, supplier_name, supplier_dic,
                    invoice_number, invoice_date, due_date,
                    total_amount, total_vat, total_without_vat,
                    currency, status, isdoc_xml
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """, (
                self._clean_string(invoice_data.get('supplier_ico')),
                self._clean_string(invoice_data.get('supplier_name')),
                self._clean_string(invoice_data.get('supplier_dic')),
                self._clean_string(invoice_data.get('invoice_number')),
                invoice_data.get('invoice_date'),
                invoice_data.get('due_date'),
                invoice_data.get('total_amount'),
                invoice_data.get('total_vat'),
                invoice_data.get('total_without_vat'),
                invoice_data.get('currency', 'EUR'),
                'pending',
                isdoc_xml
            ))

            result = cursor.fetchone()
            invoice_id = result[0]

            logger.info(
                f"Invoice inserted: ID={invoice_id}, "
                f"Number={invoice_data.get('invoice_number')}"
            )

            # Insert invoice items
            for item in items_data:
                cursor.execute("""
                    INSERT INTO invoice_items_pending (
                        invoice_id, line_number,
                        original_name, original_quantity, original_unit,
                        original_price_per_unit, original_ean, original_vat_rate,
                        edited_name, edited_price_buy, final_price_buy
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    invoice_id,
                    item.get('line_number'),
                    self._clean_string(item.get('name')),
                    item.get('quantity'),
                    self._clean_string(item.get('unit')),
                    item.get('price_per_unit'),
                    self._clean_string(item.get('ean')),
                    item.get('vat_rate'),
                    # Fallback hodnoty pre editáciu
                    self._clean_string(item.get('name')),  # edited_name
                    item.get('price_per_unit'),  # edited_price_buy
                    item.get('price_per_unit')   # final_price_buy (bez rabatu)
                ))

            logger.info(f"Inserted {len(items_data)} invoice items")

            # Commit transaction
            self.conn.commit()

            logger.info(
                f"Invoice successfully saved to staging database: "
                f"invoice_id={invoice_id}"
            )

            return invoice_id

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Failed to insert invoice: {e}", exc_info=True)
            return None

        finally:
            if cursor:
                cursor.close()

    def check_duplicate_invoice(
        self,
        supplier_ico: str,
        invoice_number: str
    ) -> bool:
        """
        Kontrola či faktúra už existuje v staging databáze.

        Args:
            supplier_ico: IČO dodávateľa
            invoice_number: Číslo faktúry

        Returns:
            True ak faktúra už existuje, False inak
        """
        if not self.conn:
            logger.error("Not connected to database")
            return False

        cursor = None
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM invoices_pending
                WHERE supplier_ico = %s AND invoice_number = %s
            """, (
                self._clean_string(supplier_ico),
                self._clean_string(invoice_number)
            ))

            result = cursor.fetchone()
            count = result[0]

            return count > 0

        except Exception as e:
            logger.error(f"Failed to check duplicate: {e}", exc_info=True)
            return False

        finally:
            if cursor:
                cursor.close()

    @staticmethod
    def _clean_string(value: Any) -> Optional[str]:
        """
        Sanitizácia string hodnôt pre PostgreSQL UTF8 encoding.
        Odstraňuje null bytes a control characters.

        Args:
            value: Vstupná hodnota (string alebo iné)

        Returns:
            Vyčistený string alebo None
        """
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        # Remove null bytes (NEX Genesis Btrieve padding)
        cleaned = value.replace('\x00', '')

        # Remove control characters (except newline, tab)
        cleaned = ''.join(
            char for char in cleaned
            if ord(char) >= 32 or char in '\n\t'
        )

        # Strip excess whitespace
        cleaned = cleaned.strip()

        return cleaned if cleaned else None

    def test_connection(self) -> bool:
        """
        Test pripojenia k databáze.

        Returns:
            True ak pripojenie funguje, False inak
        """
        cursor = None
        try:
            if not self.conn:
                self.connect()

            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            if result and result[0] == 1:
                logger.info("PostgreSQL connection test: OK")
                return True
            else:
                logger.error("PostgreSQL connection test: FAILED")
                return False

        except Exception as e:
            logger.error(f"PostgreSQL connection test failed: {e}")
            return False

        finally:
            if cursor:
                cursor.close()
