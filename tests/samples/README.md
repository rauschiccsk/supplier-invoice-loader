# Test Sample Files

This directory contains sample PDF files for testing invoice extraction.

---

## Usage

Place sanitized/anonymized sample PDFs here for testing:

- `sample_ls_invoice.pdf` - L&Š invoice format
- `sample_generic_invoice.pdf` - Generic invoice format
- `invalid.pdf` - Corrupted PDF for error handling tests
- `large.pdf` - Large file for performance testing
- `empty.pdf` - Empty PDF
- `scanned.pdf` - Scanned image PDF (no text layer)

---

## IMPORTANT Security Guidelines

### ❌ DO NOT commit:
- Real customer invoices
- Invoices with real company names
- Invoices with real addresses
- Invoices with real bank account numbers
- Invoices with real personal data
- Any confidential information

### ✅ DO commit:
- Anonymized test invoices
- Sample invoices with fake data:
  - Company name: "Test Company s.r.o."
  - IČO: 12345678 (fictional)
  - Address: "Test Street 1, Test City"
  - Bank account: SK0000000000000000000000
  - Amounts: Round numbers like 1000.00 EUR
  
---

## Creating Test Samples

### Option 1: Manually Create

Use LibreOffice/Word to create invoice template:
1. Create invoice in document editor
2. Fill with fake/test data
3. Export as PDF
4. Save in this directory

### Option 2: Anonymize Real Invoice

If you have a real invoice to test with:
1. Make a copy
2. Replace all sensitive data:
   - Company names → "Test Company"
   - Addresses → "Test Address 123"
   - IČO → 12345678
   - IBAN → SK0000000000000000000000
   - Amounts → 1000.00, 2000.00, etc.
3. Save as test sample

### Option 3: Generate Programmatically

Use library like ReportLab to generate test PDFs:

```python
from reportlab.pdfgen import canvas

def create_test_invoice():
    c = canvas.Canvas("sample_test_invoice.pdf")
    c.drawString(100, 750, "FAKTÚRA")
    c.drawString(100, 700, "Číslo faktúry: 2025001")
    c.drawString(100, 680, "Dátum vystavenia: 01.10.2025")
    # ... more fields
    c.save()
```

---

## Test Coverage

Different sample types for testing:

### Valid Invoices
- Standard format (L&Š style)
- Alternative format
- Multiple items (10+ items)
- Single item
- Various VAT rates (20%, 10%, 0%)

### Edge Cases
- Very long invoice numbers
- Special characters in descriptions
- Large amounts (millions)
- Zero amounts
- Negative amounts (credit notes)

### Error Cases
- Missing required fields
- Corrupted PDF
- Password-protected PDF
- Scanned image (no text layer)
- Empty PDF
- Non-PDF file renamed to .pdf

---

## Sample Naming Convention

Use descriptive names:

```
sample_[supplier]_[type]_[scenario].pdf

Examples:
- sample_ls_standard_valid.pdf
- sample_ls_multi_item_valid.pdf
- sample_generic_valid.pdf
- sample_ls_corrupted_invalid.pdf
- sample_ls_scanned_notext.pdf
```

---

## .gitignore

This directory is included in .gitignore by default to prevent accidental commits of real invoices.

If you want to commit test samples:
1. Create sample with fake data
2. Add to Git: `git add -f tests/samples/sample_test.pdf`
3. Commit: `git commit -m "Add test sample PDF"`

---

## Sample Checklist

Before committing any PDF:

- [ ] Contains NO real company names
- [ ] Contains NO real addresses
- [ ] Contains NO real bank accounts
- [ ] Contains NO real IČO/DIČ numbers
- [ ] Contains NO real personal names
- [ ] Contains NO confidential data
- [ ] Filename indicates it's a test sample
- [ ] Added with `git add -f` (if committing)

---

## Current Samples

List of available samples in this directory:

(Add your samples here with description)

- None yet - Add test samples as needed

---

**Remember: Never commit real customer data!**