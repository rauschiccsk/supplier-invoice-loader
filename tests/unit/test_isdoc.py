# -*- coding: utf-8 -*-
"""
Test script for ISDOC XML Generator
"""

import sys
from pathlib import Path

# PRIDAŤ TENTO RIADOK - explicitne pridá aktuálny adresár do PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from src.extractors.ls_extractor import extract_invoice_data
from src.business.isdoc_service import generate_isdoc_xml

# Cesta k testovaciemu PDF
pdf_path = r"C:\NEX_AN\IMPORT\LS\PDF\20250929_232558_32510374_FAK.pdf"

# Cesta pre výstupný XML
xml_path = r"C:\NEX_AN\IMPORT\LS\XML\32510374.xml"

print("=" * 80)
print("ISDOC 6.0.1 XML Generator Test")
print("=" * 80)

# 1. Extrakcia dát z PDF
print("\n[1/3] Extracting data from PDF...")
invoice_data = extract_invoice_data(pdf_path)

if not invoice_data:
    print("❌ Extraction failed!")
    exit(1)

print(f"✅ Extracted invoice: {invoice_data.invoice_number}")
print(f"    Total: {invoice_data.total_amount} {invoice_data.currency}")
print(f"    Items: {len(invoice_data.items)}")

# 2. Generovanie ISDOC XML
print("\n[2/3] Generating ISDOC XML...")
xml_string = generate_isdoc_xml(invoice_data, xml_path)

print(f"✅ XML generated: {len(xml_string)} characters")

# 3. Preview XML
print("\n[3/3] XML Preview (first 1000 chars):")
print("-" * 80)
print(xml_string[:1000])
print("...")
print("-" * 80)

print(f"\n✅ ISDOC XML saved to: {xml_path}")
print("\nValidate XML at: https://isdoc.cz")
print("=" * 80)