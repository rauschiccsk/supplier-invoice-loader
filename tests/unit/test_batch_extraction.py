# -*- coding: utf-8 -*-
"""
Batch Test - Test extraction na všetkých PDF v priečinku
"""

from pathlib import Path
from src.extractors.ls_extractor import extract_invoice_data

# Priečinok s PDF faktúrami
PDF_DIR = Path(r"C:\NEX_AN\IMPORT\LS\PDF")

print("=" * 80)
print("L&Š Invoice Extraction - Batch Test")
print("=" * 80)

# Nájdi všetky PDF súbory
pdf_files = list(PDF_DIR.glob("*.pdf"))

if not pdf_files:
    print(f"\n❌ Žiadne PDF súbory v {PDF_DIR}")
    exit(1)

print(f"\nNájdených {len(pdf_files)} PDF súborov\n")

# Štatistiky
success = 0
failed = 0
results = []

# Testuj každý súbor
for pdf_path in pdf_files:
    print("-" * 80)
    print(f"Testujem: {pdf_path.name}")

    try:
        data = extract_invoice_data(str(pdf_path))

        if not data:
            print(f"  ❌ FAILED - extraction returned None")
            failed += 1
            results.append((pdf_path.name, "FAILED", "No data extracted"))
            continue

        # Validácia kľúčových polí
        issues = []
        if not data.invoice_number:
            issues.append("Missing invoice_number")
        if not data.total_amount:
            issues.append("Missing total_amount")
        if not data.customer_ico:
            issues.append("Missing customer_ico")
        if len(data.items) == 0:
            issues.append("No items extracted")

        if issues:
            print(f"  ⚠️  PARTIAL - {', '.join(issues)}")
            results.append((pdf_path.name, "PARTIAL", issues))
        else:
            print(f"  ✅ SUCCESS")
            print(f"     Invoice: {data.invoice_number}")
            print(f"     Total: {data.total_amount} {data.currency}")
            print(f"     Customer: {data.customer_name}")
            print(f"     Items: {len(data.items)}")
            success += 1
            results.append((pdf_path.name, "SUCCESS", None))

    except Exception as e:
        print(f"  ❌ ERROR - {str(e)}")
        failed += 1
        results.append((pdf_path.name, "ERROR", str(e)))

# Výsledky
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total files:  {len(pdf_files)}")
print(f"Success:      {success} ({success / len(pdf_files) * 100:.1f}%)")
print(f"Failed:       {failed}")

if failed > 0 or any(r[1] == "PARTIAL" for r in results):
    print("\n" + "=" * 80)
    print("PROBLEMS")
    print("=" * 80)
    for filename, status, detail in results:
        if status != "SUCCESS":
            print(f"\n{filename}: {status}")
            if detail:
                if isinstance(detail, list):
                    for issue in detail:
                        print(f"  - {issue}")
                else:
                    print(f"  {detail}")

print("\n" + "=" * 80)