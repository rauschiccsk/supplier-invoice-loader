# Používateľská Príručka - Supplier Invoice Loader

## Pre Operátorov a Administrátorov

---

## 📖 Obsah

1. [Úvod](#úvod)
2. [Ako Systém Funguje](#ako-systém-funguje)
3. [Denná Prevádzka](#denná-prevádzka)
4. [Riešenie Problémov](#riešenie-problémov)
5. [Často Kladené Otázky](#často-kladené-otázky)
6. [Kontakty](#kontakty)

---

## Úvod

Supplier Invoice Loader je automatizovaný systém na spracovanie faktúr od dodávateľov. Systém automaticky:
- ✅ Prijíma faktúry z emailov
- ✅ Extrahuje dáta z PDF súborov
- ✅ Ukladá faktúry do databázy
- ✅ Generuje XML súbory pre účtovný systém
- ✅ Synchronizuje s NEX Genesis

---

## Ako Systém Funguje

### 🔄 Proces Spracovania

```
1. Operátor dostane faktúru emailom
    ↓
2. Prepošle faktúru na: automation-magerstav@isnex.ai
    ↓
3. n8n workflow automaticky spracuje email
    ↓
4. PDF sa odošle do Invoice Loader API
    ↓
5. Systém extrahuje údaje a uloží faktúru
    ↓
6. Vygeneruje sa XML súbor
    ↓
7. Faktúra sa synchronizuje s NEX Genesis
```

### ⚡ Automatické Funkcie

- **Duplikáty**: Systém automaticky rozpozná a odmietne duplicitné faktúry
- **Chyby**: Pri chybe dostanete email notifikáciu
- **Denný súhrn**: Každý deň o 23:55 príde súhrnný email

---

## Denná Prevádzka

### 📧 Posielanie Faktúr na Spracovanie

**Krok 1: Prijmite faktúru**
- Faktúra musí byť vo formáte PDF
- Môže byť v prílohe emailu

**Krok 2: Prepošlite na automation email**
```
To: automation-magerstav@isnex.ai
Subject: [ľubovoľný - systém ho zachová]
Príloha: faktura.pdf
```

**Krok 3: Počkajte na potvrdenie**
- Do 1-2 minút dostanete potvrdenie o spracovaní
- Pri chybe dostanete email s popisom problému

### ✅ Úspešné Spracovanie

Ak je faktúra spracovaná úspešne:
1. Nedostanete žiadnu chybu
2. Faktúra sa objaví v systéme
3. XML súbor sa vytvorí v: `C:\NEX_INVOICES\XML\`

### ❌ Neúspešné Spracovanie

Dostanete email s informáciou o type chyby:
- **"Duplicate invoice"** - Faktúra už bola spracovaná
- **"Invalid PDF"** - Súbor nie je platné PDF
- **"Extraction failed"** - Nepodarilo sa prečítať údaje
- **"API error"** - Technický problém (kontaktujte IT)

---

## Riešenie Problémov

### 🔍 Kontrola Stavu Systému

**Windows 11 / Windows Server:**

1. **Je služba spustená?**
   ```cmd
   # Otvorte Command Prompt ako Administrator
   sc query SupplierInvoiceLoader
   ```
   
   Mali by ste vidieť: `STATE: 4 RUNNING`

2. **Reštart služby:**
   ```cmd
   net stop SupplierInvoiceLoader
   net start SupplierInvoiceLoader
   ```

3. **Kontrola logov:**
   - Otvorte: `C:\SupplierInvoiceLoader\logs\`
   - Pozrite súbor: `invoice_loader.log`

### ⚠️ Časté Problémy a Riešenia

#### Problem: Faktúra sa nespracovala

**Možné príčiny:**
1. PDF je poškodené
2. Email nebol poslaný na správnu adresu
3. Služba nie je spustená

**Riešenie:**
1. Skúste otvoriť PDF - funguje?
2. Skontrolujte adresu: `automation-magerstav@isnex.ai`
3. Reštartujte službu (viď vyššie)

#### Problem: Dostávam "Duplicate invoice"

**Príčina:** Táto faktúra už bola spracovaná

**Riešenie:** 
- Ak je to naozaj duplicita - ignorujte
- Ak nie - kontaktujte IT support

#### Problem: Systém nefunguje vôbec

**Rýchle kroky:**
1. Reštartujte službu
2. Počkajte 2 minúty
3. Skúste znova
4. Ak stále nefunguje - kontaktujte support

### 📊 Kontrola Spracovania

**Kde nájdem spracované faktúry?**
- PDF súbory: `C:\NEX_INVOICES\PDF\`
- XML súbory: `C:\NEX_INVOICES\XML\`

**Ako zistím koľko faktúr bolo spracovaných?**
- Pozrite denný súhrnný email
- Alebo otvorte: http://localhost:8000/stats

---

## Často Kladené Otázky

### ❓ Musím niečo meniť v predmete emailu?

Nie, predmet môže byť ľubovoľný. Systém ho zachová pre históriu.

### ❓ Môžem poslať viac faktúr naraz?

Áno, ale každá faktúra musí byť v samostatnom emaile (jedna príloha = jeden email).

### ❓ Čo ak omylom pošlem faktúru 2x?

Systém ju automaticky rozpozná ako duplikát a odmietne. Dostanete notifikáciu.

### ❓ Ako dlho trvá spracovanie?

Bežne 30-60 sekúnd od odoslania emailu.

### ❓ Môžem poslať aj iné formáty (Word, Excel)?

Nie, systém podporuje iba PDF formát.

### ❓ Čo ak faktúra nemá všetky údaje?

Systém spracuje čo dokáže prečítať. Chýbajúce údaje budete musieť doplniť manuálne.

### ❓ Kde vidím všetky spracované faktúry?

- V priečinku: `C:\NEX_INVOICES\PDF\`
- V NEX Genesis systéme
- V dennom súhrne emailom

### ❓ Môžem preposlať faktúru z mobilu?

Áno, funguje to rovnako ako z počítača.

---

## Kontakty

### 🆘 Technická Podpora

**Pri problémoch kontaktujte:**

**Primárny kontakt:**
- Email: support@icc.sk
- Telefón: [doplniť]

**Urgentné problémy:**
- Kontakt: [doplniť]

### 📝 Pri Kontaktovaní Supportu Uveďte:

1. **Čas problému** (kedy presne sa to stalo)
2. **Číslo faktúry** (ak je známe)
3. **Chybová správa** (ak nejakú dostanete)
4. **Čo ste robili** keď problém nastal

### 💡 Tipy pre Rýchle Vyriešenie

- Skúste najprv reštartovať službu
- Skontrolujte či je PDF čitateľné
- Overte správnu emailovú adresu
- Pozrite sa do denného súhrnu

---

## Denný Checklist

### 🌅 Ráno
- [ ] Skontrolovať súhrnný email z včera
- [ ] Overiť že služba beží

### 📧 Pri Posielaní Faktúr
- [ ] PDF je v prílohe
- [ ] Adresa: automation-magerstav@isnex.ai
- [ ] Jedna faktúra = jeden email

### 🌙 Koniec Dňa
- [ ] Skontrolovať či všetky faktúry boli spracované
- [ ] Pri problémoch kontaktovať support

---

## Užitočné Príkazy

### Pre Administrátorov

```cmd
# Stav služby
sc query SupplierInvoiceLoader

# Reštart služby
net stop SupplierInvoiceLoader && net start SupplierInvoiceLoader

# Pozrieť posledné záznamy v logu
type C:\SupplierInvoiceLoader\logs\invoice_loader.log | more

# Kontrola zdravia systému
curl http://localhost:8000/health

# Štatistiky
curl http://localhost:8000/stats
```

---

## Verzia a Aktualizácie

- **Verzia systému:** 2.0.0
- **Dátum nasadenia:** [doplniť]
- **Posledná aktualizácia:** [doplniť]

---

**Koniec Používateľskej Príručky**