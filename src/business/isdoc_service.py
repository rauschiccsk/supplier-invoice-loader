# -*- coding: utf-8 -*-
"""
L&Š Invoice Loader - ISDOC 6.0.1 XML Generator
Generates ISDOC XML from extracted invoice data
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

from src.extractors.ls_extractor import InvoiceData

logger = logging.getLogger(__name__)

# ISDOC namespace
ISDOC_NS = "http://isdoc.cz/namespace/2013"


class ISDOCGenerator:
    """Generator pre ISDOC 6.0.1 XML faktúry"""

    def __init__(self):
        self.ns = ISDOC_NS

    def generate_from_invoice_data(self, data: InvoiceData, output_path: Optional[str] = None) -> str:
        """
        Hlavná metóda - vytvorí ISDOC XML z InvoiceData

        Args:
            data: InvoiceData objekt z ls_extractor.py
            output_path: Cesta kam uložiť XML (optional)

        Returns:
            XML ako string
        """
        logger.info(f"Generating ISDOC XML for invoice: {data.invoice_number}")

        # Root element
        root = Element("Invoice", {
            "xmlns": self.ns,
            "version": "6.0.1"
        })

        # 1. Document Type
        SubElement(root, "DocumentType").text = "1"  # 1 = Faktúra (daňový doklad)

        # 2. ID (číslo faktúry)
        SubElement(root, "ID").text = str(data.invoice_number)

        # 3. UUID - vygenerujeme z čísla faktúry a IČO
        uuid = f"INV-{data.supplier_ico}-{data.invoice_number}"
        SubElement(root, "UUID").text = uuid

        # 4. Issuing System
        SubElement(root, "IssuingSystem").text = "L&Š Invoice Loader v1.0"

        # 5. Issue Date
        SubElement(root, "IssueDate").text = self._format_date(data.issue_date)

        # 6. Tax Point Date (dátum daňovej povinnosti)
        SubElement(root, "TaxPointDate").text = self._format_date(data.tax_point_date or data.issue_date)

        # 7. VAT Applicable
        SubElement(root, "VATApplicable").text = "true"

        # 8. Electronic Possibility Agreement Reference
        SubElement(root, "ElectronicPossibilityAgreementReference").text = "Elektronická fakturácia"

        # 9. Note (voliteľné)
        if data.invoice_number:
            SubElement(root, "Note").text = f"Faktúra č. {data.invoice_number}"

        # 10. Local Currency Code
        SubElement(root, "LocalCurrencyCode").text = data.currency

        # 11. Currency Code
        SubElement(root, "CurrencyCode").text = data.currency

        # 12. Accounting Supplier Party (dodávateľ)
        self._add_supplier_party(root, data)

        # 13. Accounting Customer Party (odberateľ)
        self._add_customer_party(root, data)

        # 14. Delivery (dodanie tovaru)
        self._add_delivery(root, data)

        # 15. Payment Means (platobné údaje)
        self._add_payment_means(root, data)

        # 16. Tax Total (DPH súhrn)
        self._add_tax_total(root, data)

        # 17. Legal Monetary Total (celkové sumy)
        self._add_legal_monetary_total(root, data)

        # 18. Invoice Lines (položky faktúry)
        self._add_invoice_lines(root, data)

        # Konvert na string
        xml_string = self._prettify_xml(root)

        # Uložiť ak je zadaná cesta
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_string)
            logger.info(f"ISDOC XML saved to: {output_path}")

        return xml_string

    def _add_supplier_party(self, root: Element, data: InvoiceData):
        """Pridá dodávateľa (L&Š)"""
        party = SubElement(root, "AccountingSupplierParty")

        # Party
        party_elem = SubElement(party, "Party")

        # Party Identification (IČO)
        party_id = SubElement(party_elem, "PartyIdentification")
        party_id_id = SubElement(party_id, "ID")
        party_id_id.text = data.supplier_ico

        # Party Name
        party_name = SubElement(party_elem, "PartyName")
        SubElement(party_name, "Name").text = data.supplier_name

        # Postal Address
        if data.supplier_address:
            address = SubElement(party_elem, "PostalAddress")
            # Rozdeliť adresu na časti (zjednodušene)
            addr_parts = data.supplier_address.split(",")
            if len(addr_parts) > 0:
                SubElement(address, "StreetName").text = addr_parts[0].strip()
            if len(addr_parts) > 1:
                SubElement(address, "CityName").text = addr_parts[1].strip()

            # Krajina
            country = SubElement(address, "Country")
            SubElement(country, "IdentificationCode").text = "SK"
            SubElement(country, "Name").text = "Slovenská republika"

        # Party Tax Scheme (DIČ)
        if data.supplier_dic:
            tax_scheme = SubElement(party_elem, "PartyTaxScheme")
            SubElement(tax_scheme, "CompanyID").text = data.supplier_dic
            SubElement(tax_scheme, "TaxScheme").text = "DIČ"

        # Party Tax Scheme (IČ DPH)
        if data.supplier_icdph:
            tax_scheme = SubElement(party_elem, "PartyTaxScheme")
            SubElement(tax_scheme, "CompanyID").text = data.supplier_icdph
            SubElement(tax_scheme, "TaxScheme").text = "VAT"

    def _add_customer_party(self, root: Element, data: InvoiceData):
        """Pridá odberateľa"""
        party = SubElement(root, "AccountingCustomerParty")

        # Party
        party_elem = SubElement(party, "Party")

        # Party Identification (IČO)
        party_id = SubElement(party_elem, "PartyIdentification")
        party_id_id = SubElement(party_id, "ID")
        party_id_id.text = data.customer_ico

        # Party Name
        party_name = SubElement(party_elem, "PartyName")
        SubElement(party_name, "Name").text = data.customer_name

        # Postal Address
        if data.customer_address:
            address = SubElement(party_elem, "PostalAddress")
            addr_parts = data.customer_address.split(",")
            if len(addr_parts) > 0:
                SubElement(address, "StreetName").text = addr_parts[0].strip()
            if len(addr_parts) > 1:
                SubElement(address, "CityName").text = addr_parts[1].strip()

            country = SubElement(address, "Country")
            SubElement(country, "IdentificationCode").text = "SK"
            SubElement(country, "Name").text = "Slovenská republika"

        # Party Tax Scheme (DIČ)
        if data.customer_dic:
            tax_scheme = SubElement(party_elem, "PartyTaxScheme")
            SubElement(tax_scheme, "CompanyID").text = data.customer_dic
            SubElement(tax_scheme, "TaxScheme").text = "DIČ"

        # Party Tax Scheme (IČ DPH)
        if data.customer_icdph:
            tax_scheme = SubElement(party_elem, "PartyTaxScheme")
            SubElement(tax_scheme, "CompanyID").text = data.customer_icdph
            SubElement(tax_scheme, "TaxScheme").text = "VAT"

    def _add_delivery(self, root: Element, data: InvoiceData):
        """Pridá informácie o dodaní"""
        delivery = SubElement(root, "Delivery")

        # Delivery Party (dodacie miesto = odberateľ)
        party = SubElement(delivery, "DeliveryParty")
        party_name = SubElement(party, "PartyName")
        SubElement(party_name, "Name").text = data.customer_name

    def _add_payment_means(self, root: Element, data: InvoiceData):
        """Pridá platobné údaje"""
        payment = SubElement(root, "PaymentMeans")

        # Payment
        payment_elem = SubElement(payment, "Payment")

        # Payment Means Code (42 = SEPA transfer)
        SubElement(payment_elem, "PaidAmount").text = self._format_amount(data.total_amount)

        # Payment Due Date
        if data.due_date:
            SubElement(payment_elem, "PaymentDueDate").text = self._format_date(data.due_date)

        # Bank Account
        if data.iban:
            details = SubElement(payment, "PayeeFinancialAccount")
            SubElement(details, "ID").text = data.iban
            if data.bank_name:
                SubElement(details, "Name").text = data.bank_name
            if data.bic:
                bank = SubElement(details, "FinancialInstitutionBranch")
                SubElement(bank, "ID").text = data.bic

        # Variable Symbol
        if data.variable_symbol:
            vs_elem = SubElement(payment, "VariableSymbol")
            vs_elem.text = data.variable_symbol

        # Constant Symbol
        if data.constant_symbol:
            cs_elem = SubElement(payment, "ConstantSymbol")
            cs_elem.text = data.constant_symbol

    def _add_tax_total(self, root: Element, data: InvoiceData):
        """Pridá DPH súhrn"""
        tax_total = SubElement(root, "TaxTotal")

        # Tax Amount
        SubElement(tax_total, "TaxAmount").text = self._format_amount(data.tax_amount)

        # Tax Sub Total (rozdelenie podľa sadzieb DPH)
        tax_subtotal = SubElement(tax_total, "TaxSubTotal")

        # Taxable Amount (základ DPH)
        SubElement(tax_subtotal, "TaxableAmount").text = self._format_amount(data.net_amount)

        # Tax Amount
        SubElement(tax_subtotal, "TaxAmount").text = self._format_amount(data.tax_amount)

        # Tax Category
        category = SubElement(tax_subtotal, "TaxCategory")
        SubElement(category, "Percent").text = "23.00"  # Štandardná sadzba 23%
        SubElement(category, "VATCalculationMethod").text = "0"  # Bežný výpočet

    def _add_legal_monetary_total(self, root: Element, data: InvoiceData):
        """Pridá celkové sumy"""
        monetary_total = SubElement(root, "LegalMonetaryTotal")

        # Tax Exclusive Amount (suma bez DPH)
        SubElement(monetary_total, "TaxExclusiveAmount").text = self._format_amount(data.net_amount)

        # Tax Inclusive Amount (suma s DPH)
        SubElement(monetary_total, "TaxInclusiveAmount").text = self._format_amount(data.total_amount)

        # Already Claimed Tax Exclusive Amount
        SubElement(monetary_total, "AlreadyClaimedTaxExclusiveAmount").text = "0.00"

        # Already Claimed Tax Inclusive Amount
        SubElement(monetary_total, "AlreadyClaimedTaxInclusiveAmount").text = "0.00"

        # Difference Tax Exclusive Amount
        SubElement(monetary_total, "DifferenceTaxExclusiveAmount").text = self._format_amount(data.net_amount)

        # Difference Tax Inclusive Amount
        SubElement(monetary_total, "DifferenceTaxInclusiveAmount").text = self._format_amount(data.total_amount)

        # Payable Amount (suma na úhradu)
        SubElement(monetary_total, "PayableAmount").text = self._format_amount(data.total_amount)

    def _add_invoice_lines(self, root: Element, data: InvoiceData):
        """Pridá položky faktúry"""
        for item in data.items:
            line = SubElement(root, "InvoiceLine")

            # ID (poradové číslo)
            SubElement(line, "ID").text = str(item.line_number)

            # Invoiced Quantity
            quantity = SubElement(line, "InvoicedQuantity")
            quantity.text = self._format_amount(item.quantity)
            quantity.set("unitCode", item.unit)

            # Line Extension Amount (celková suma bez DPH)
            line_total_no_vat = item.quantity * item.unit_price_no_vat if item.quantity and item.unit_price_no_vat else Decimal(0)
            SubElement(line, "LineExtensionAmount").text = self._format_amount(line_total_no_vat)

            # Line Extension Amount Tax Inclusive (celková suma s DPH)
            SubElement(line, "LineExtensionAmountTaxInclusive").text = self._format_amount(item.total_with_vat)

            # Unit Price
            SubElement(line, "UnitPrice").text = self._format_amount(item.unit_price_no_vat)

            # Unit Price Tax Inclusive
            SubElement(line, "UnitPriceTaxInclusive").text = self._format_amount(item.unit_price_with_vat)

            # Classified Tax Category (DPH sadzba)
            tax_category = SubElement(line, "ClassifiedTaxCategory")
            SubElement(tax_category, "Percent").text = self._format_amount(item.vat_rate)
            SubElement(tax_category, "VATCalculationMethod").text = "0"

            # Item (produkt)
            item_elem = SubElement(line, "Item")
            SubElement(item_elem, "Description").text = item.description or ""

            # Sellers Item Identification (kód tovaru)
            if item.item_code:
                sellers_id = SubElement(item_elem, "SellersItemIdentification")
                SubElement(sellers_id, "ID").text = item.item_code

            # Standard Item Identification (EAN)
            if item.ean_code:
                std_id = SubElement(item_elem, "StandardItemIdentification")
                SubElement(std_id, "ID").text = item.ean_code

    def _format_date(self, date_str: str) -> str:
        """
        Konvertuje dátum na ISDOC formát YYYY-MM-DD

        Args:
            date_str: Dátum v rôznych formátoch (napr. "16.09.2025")

        Returns:
            Dátum v ISO formáte
        """
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # Očakávaný formát: DD.MM.YYYY
        try:
            if "." in date_str:
                parts = date_str.split(".")
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass

        # Fallback
        return datetime.now().strftime("%Y-%m-%d")

    def _format_amount(self, amount: Optional[Decimal]) -> str:
        """
        Konvertuje Decimal na string vo formáte ISDOC

        Args:
            amount: Decimal číslo

        Returns:
            String s 2 desatinnými miestami
        """
        if amount is None:
            return "0.00"
        return f"{amount:.2f}"

    def _prettify_xml(self, elem: Element) -> str:
        """
        Naformátuje XML pre lepšiu čitateľnosť

        Args:
            elem: Root element

        Returns:
            Formatted XML string
        """
        rough_string = tostring(elem, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")


# Pomocná funkcia pre použitie v main.py
def generate_isdoc_xml(invoice_data: InvoiceData, output_path: Optional[str] = None) -> str:
    """
    Wrapper funkcia pre generovanie ISDOC XML

    Args:
        invoice_data: InvoiceData objekt z ls_extractor.py
        output_path: Cesta kam uložiť XML (optional)

    Returns:
        XML ako string

    Usage:
        from src.business.isdoc_service import generate_isdoc_xml
        xml = generate_isdoc_xml(invoice_data, "/path/to/output.xml")
    """
    generator = ISDOCGenerator()
    return generator.generate_from_invoice_data(invoice_data, output_path)