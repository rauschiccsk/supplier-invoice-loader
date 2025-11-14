# Customer Testing Checklist

## 🎯 Testovanie u zákazníka po nasadení

Tento checklist sa používa **PO nasadení** aplikácie u zákazníka na ich serveri.

---

## Základné informácie

- **Zákazník:** _________________
- **Dátum nasadenia:** _________________
- **Verzia:** 2.0.0
- **Server:** _________________
- **Tester:** _________________

---

## 1️⃣ Post-Installation Checks

### ✅ Inštalácia

- [ ] Aplikácia je nainštalovaná v: `C:\SupplierInvoiceLoader\`
- [ ] Python venv je vytvorený a aktivovaný
- [ ] Všetky dependencies sú nainštalované
- [ ] `config_customer.py` je vytvorený a nakonfigurovaný
- [ ] `.env` súbor obsahuje všetky credentials
- [ ] Windows Service je nainštalovaný
- [ ] Service sa automaticky spúšťa pri štarte Windows

### ✅ Databáza

- [ ] Databáza `invoices.db` je vytvorená
- [ ] Migrácia na v2 schema úspešná
- [ ] Databáza má správne permissions

### ✅ Adresáre a Paths

- [ ] Storage path existuje: `config_customer.STORAGE_PATH`
- [ ] Processed path existuje: `config_customer.PROCESSED_PATH`
- [ ] Error path existuje: `config_customer.ERROR_PATH`
- [ ] ISDOC output path existuje: `config_customer.ISDOC_OUTPUT_PATH`
- [ ] Všetky adresáre majú write permissions

---

## 2️⃣ Configuration Tests

### ✅ NEX Genesis API

**Test pripojenia:**
```python
python -c "from config_customer import NEX_GENESIS_API_URL, NEX_GENESIS_API_KEY; import requests; r=requests.get(NEX_GENESIS_API_URL, headers={'Authorization': f'Bearer {NEX_GENESIS_API_KEY}'}); print(f'Status: {r.status_code}')"
```

- [ ] API URL je správna
- [ ] API Key funguje
- [ ] Connection test vrátil status 200
- [ ] Testovací import faktúry úspešný

**Poznámky:**
```
_________________________________________________________________
_________________________________________________________________
```

### ✅ Email Configuration

**Test SMTP:**
```python
python -c "from notifications import EmailNotifier; n = EmailNotifier(); n.send_test_email('test@example.com')"
```

- [ ] SMTP server je dostupný
- [ ] SMTP credentials sú správne
- [ ] Test email bol odoslaný
- [ ] Test email bol prijatý
- [ ] Email má správny formát

**Poznámky:**
```
_________________________________________________________________
_________________________________________________________________
```

### ✅ Operator Settings

- [ ] `OPERATOR_EMAIL` je správny
- [ ] `OPERATOR_NAME` je správny
- [ ] `COMPANY_NAME` je správny
- [ ] `COMPANY_ICO` je správne

---

## 3️⃣ Functional Tests

### ✅ Test 1: API Endpoints

**Spustite aplikáciu:**
```batch
python main.py
```

**Otvorte v prehliadači:**
- http://localhost:8000/docs

Checklist:
- [ ] API dokumentácia sa načíta
- [ ] `/health` endpoint vracia OK
- [ ] `/api/invoices/upload` endpoint je dostupný
- [ ] `/api/invoices/` endpoint vracia zoznam (môže byť prázdny)
- [ ] API vyžaduje autentifikáciu

**Screenshot:** _________________

### ✅ Test 2: PDF Extraction

**Pripravte testovaciu faktúru (PDF):**

```batch
# Umiestnite test.pdf do storage adresára
python test_extraction.py test.pdf
```

Checklist:
- [ ] PDF sa načíta bez chýb
- [ ] Text sa extrahuje správne
- [ ] Dodávateľ je rozpoznaný
- [ ] Číslo faktúry je extrahovane
- [ ] Dátum je extrahovaný
- [ ] Suma je extrahovaná
- [ ] Extrakcia trvá < 10 sekúnd

**Výsledok extrakcie:**
```
Dodávateľ: _______________________
Číslo FV: _______________________
Dátum: _______________________
Suma: _______________________
```

### ✅ Test 3: ISDOC Generation

```python
python test_isdoc.py
```

Checklist:
- [ ] ISDOC XML sa vygeneruje
- [ ] XML má správnu štruktúru
- [ ] XML validácia OK
- [ ] Súbor sa uloží do ISDOC output path
- [ ] Názov súboru je správny formát

**ISDOC súbor:**
```
Path: _______________________
Veľkosť: _______________________
```

### ✅ Test 4: NEX Genesis Import

**Použite skutočnú faktúru zákazníka:**

1. Upload PDF cez API
2. Počkajte na spracovanie
3. Skontrolujte NEX Genesis

Checklist:
- [ ] PDF sa nahrá úspešne
- [ ] Extrakcia prebehne automaticky
- [ ] ISDOC sa vygeneruje
- [ ] Import do NEX Genesis úspešný
- [ ] Faktúra je viditeľná v NEX Genesis
- [ ] Všetky údaje sú správne
- [ ] Príloha (PDF) je v NEX Genesis

**NEX Genesis:**
```
Faktúra ID: _______________________
Stav: _______________________
```

### ✅ Test 5: Email Notifications

**Trigger email notifikáciu:**

```python
# Test úspešnej notifikácie
python -c "from notifications import EmailNotifier; n = EmailNotifier(); n.notify_success('TEST-001', 'Test supplier')"

# Test error notifikácie
python -c "from notifications import EmailNotifier; n = EmailNotifier(); n.notify_error('TEST-002', 'Test error message')"
```

Checklist:
- [ ] Success email bol odoslaný
- [ ] Success email bol prijatý operátorom
- [ ] Error email bol odoslaný
- [ ] Error email bol prijatý operátorom
- [ ] Emaily majú správny subject
- [ ] Emaily majú správne info
- [ ] Emaily sú čitateľné

**Email samples:** _(uložte screenshot)_

---

## 4️⃣ Integration Tests

### ✅ N8N Workflow

**Workflow setup:**
- [ ] N8N workflow je naimportovaný
- [ ] Email trigger je nakonfigurovaný na automation email
- [ ] Webhook URL je správna (API endpoint)
- [ ] Credentials sú nastavené
- [ ] Workflow je aktivovaný

**Test workflow:**
1. Pošlite test email s PDF prílohou na automation email
2. Počkajte 1-2 minúty
3. Skontrolujte N8N execution log
4. Skontrolujte NEX Genesis

Checklist:
- [ ] Email bol prijatý N8N
- [ ] PDF príloha bola extrahovaná
- [ ] API call na supplier_invoice_loader úspešný
- [ ] Faktúra sa spracovala
- [ ] Faktúra sa importovala do NEX Genesis
- [ ] Success notifikácia bola odoslaná

**N8N Execution:**
```
Execution ID: _______________________
Status: _______________________
Duration: _______________________
```

### ✅ End-to-End Test

**Kompletný proces:**

1. **Dodávateľ** pošle faktúru emailom
2. **N8N** zachytí email a PDF
3. **Supplier Invoice Loader** spracuje PDF
4. **NEX Genesis** prijme faktúru
5. **Operátor** dostane notifikáciu

Checklist:
- [ ] E2E test s reálnym emailom úspešný
- [ ] Celý proces trval < 5 minút
- [ ] Faktúra je v NEX Genesis
- [ ] Údaje sú správne
- [ ] PDF príloha je pripojená
- [ ] Notifikácia bola odoslaná

**Čas spracovania:**
```
Email prijatý: _______________________
Faktúra v NEX: _______________________
Celkový čas: _______________________
```

---

## 5️⃣ Error Handling Tests

### ✅ Test chybných scenárov

**Test 1: Nečitateľný PDF**
- [ ] Upload poškodeného PDF
- [ ] Aplikácia zachytí chybu
- [ ] PDF sa presunie do ERROR_PATH
- [ ] Error email bol odoslaný
- [ ] Chyba je zalogovaná

**Test 2: Chybné NEX API credentials**
- [ ] Dočasne zmeňte API key na nesprávny
- [ ] Spracujte faktúru
- [ ] Import zlyhá gracefully
- [ ] Error notifikácia odoslaná
- [ ] Aplikácia neprestala bežať

**Test 3: Email server nedostupný**
- [ ] Dočasne zmeňte SMTP settings
- [ ] Trigger notifikáciu
- [ ] Chyba je zalogovaná
- [ ] Aplikácia neprestala bežať

---

## 6️⃣ Performance & Monitoring

### ✅ Performance

**Spracovanie jednej faktúry:**
- [ ] PDF parsing < 5 sekúnd
- [ ] ISDOC generovanie < 2 sekundy
- [ ] NEX Genesis import < 3 sekundy
- [ ] Celkový čas < 15 sekúnd

**Batch spracovanie (5 faktúr):**
- [ ] Všetky sa spracujú úspešne
- [ ] Žiadne memory leaks
- [ ] CPU usage < 50%
- [ ] Celkový čas < 1 minúta

### ✅ Monitoring

```batch
python monitoring.py status
```

Checklist:
- [ ] Application status: RUNNING
- [ ] Database accessible: YES
- [ ] Disk space available: > 1GB
- [ ] Memory usage: < 500MB
- [ ] CPU usage: < 30%
- [ ] API response time: < 1s

**System info:**
```
CPU: _______________________
Memory: _______________________
Disk: _______________________
```

---

## 7️⃣ Security & Backup

### ✅ Security

- [ ] `.env` súbor má obmedzené permissions
- [ ] `config_customer.py` má obmedzené permissions
- [ ] Database má obmedzené permissions
- [ ] API používa authentication
- [ ] HTTPS (ak je nakonfigurované)
- [ ] Firewall pravidlá sú nastavené

### ✅ Backup

- [ ] Backup stratégia je definovaná
- [ ] Databáza sa pravidelne zálohuje
- [ ] Config súbory sú zazálohované
- [ ] Restore procedúra je otestovaná

---

## 8️⃣ Documentation & Training

### ✅ Dokumentácia

- [ ] Operátor dostal dokumentáciu
- [ ] Operátor vie kde nájsť logy
- [ ] Operátor vie reštartovať service
- [ ] Operátor vie riešiť základné problémy
- [ ] Support kontakty sú známe

### ✅ Training

- [ ] Operátor vie spracovať faktúru manuálne
- [ ] Operátor vie skontrolovať status v NEX
- [ ] Operátor vie odpovedať dodávateľovi
- [ ] Operátor vie eskalovať problém

---

## ✅ FINAL APPROVAL

### Sign-off

- [ ] Všetky testy PASSED
- [ ] Zákazník je spokojný
- [ ] Operátor je vyškolený
- [ ] Dokumentácia odovzdaná
- [ ] Support je aktivovaný

**Schválenie:**

```
Tester:        _________________ Dátum: _________
Zákazník:      _________________ Dátum: _________
ICC Support:   _________________ Dátum: _________
```

---

## 📝 Poznámky a Problémy

### Problémy počas testovania:

```
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
```

### Riešenia:

```
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
```

### Follow-up úlohy:

```
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
___________________________________________________________________
```

---

## 📞 Support

- **Email:** support@icc.sk
- **Tel:** +421 XXX XXX XXX
- **Dokumentácia:** TROUBLESHOOTING.md

---

**Verzia:** 1.0  
**Dátum:** 2024-10-09  
**Projekt:** Supplier Invoice Loader v2.0