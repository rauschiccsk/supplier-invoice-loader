# -*- coding: utf-8 -*-
from src.extractors.ls_extractor import extract_invoice_data

pdf_path = r"C:\NEX_AN\IMPORT\LS\PDF\20250929_232558_32510374_FAK.pdf"

print("=" * 80)
print("L&Š Invoice Data Extraction Test")
print("=" * 80)

data = extract_invoice_data(pdf_path)

if not data:
    print("\n❌ EXTRACTION FAILED")
    exit(1)

print("\n✅ EXTRACTION SUCCESSFUL\n")

# Hlavička
print("=" * 80)
print("HLAVIČKA")
print("=" * 80)
print(f"Číslo faktúry:        {data.invoice_number}")
print(f"Dátum vystavenia:     {data.issue_date}")
print(f"Dátum splatnosti:     {data.due_date}")
print(f"Dátum daň. povinnosti: {data.tax_point_date}")
print(f"\nCelkom k úhrade:      {data.total_amount} {data.currency}")
print(f"Základ DPH:           {data.net_amount} {data.currency}")
print(f"DPH:                  {data.tax_amount} {data.currency}")

# Dodávateľ
print("\n" + "=" * 80)
print("DODÁVATEĽ")
print("=" * 80)
print(f"Názov:    {data.supplier_name}")
print(f"IČO:      {data.supplier_ico}")
print(f"DIČ:      {data.supplier_dic}")
print(f"IČ DPH:   {data.supplier_icdph}")

# Odberateľ
print("\n" + "=" * 80)
print("ODBERATEĽ")
print("=" * 80)
print(f"Názov:    {data.customer_name}")
print(f"IČO:      {data.customer_ico}")
print(f"DIČ:      {data.customer_dic}")
print(f"IČ DPH:   {data.customer_icdph}")

# Bankové údaje
print("\n" + "=" * 80)
print("BANKOVÉ ÚDAJE")
print("=" * 80)
print(f"IBAN:              {data.iban}")
print(f"BIC:               {data.bic}")
print(f"Variabilný symbol: {data.variable_symbol}")

# Položky
print("\n" + "=" * 80)
print(f"POLOŽKY ({len(data.items)} ks)")
print("=" * 80)

for item in data.items[:5]:
    print(f"\n{item.line_number}. {item.description}")
    print(f"   Kód: {item.item_code} | EAN: {item.ean_code or 'N/A'}")
    print(f"   {item.quantity} {item.unit} × {item.unit_price_with_vat} EUR = {item.total_with_vat} EUR")
    print(f"   DPH: {item.vat_rate}%")

if len(data.items) > 5:
    print(f"\n... a ďalších {len(data.items) - 5} položiek")

print("\n" + "=" * 80)