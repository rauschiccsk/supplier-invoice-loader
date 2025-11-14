#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Cleanup Diagnostics Script
Analyzuje projekt a vytvori cleanup report.

Usage:
    python cleanup_diagnostics.py

Output:
    cleanup_report.md
"""

import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import json
import re


class CleanupDiagnostics:
    def __init__(self, project_root: str = r"C:\Development\supplier_invoice_loader"):
        self.project_root = Path(project_root)
        self.report_lines = []
        self.issues_found = 0
        self.warnings_found = 0

    def log(self, message: str, level: str = "INFO"):
        """Log spravu do reportu"""
        prefix = {
            "INFO": "[INFO]",
            "ISSUE": "[ISSUE]",
            "WARNING": "[WARN]",
            "SUCCESS": "[OK]"
        }.get(level, "[*]")

        self.report_lines.append(f"{prefix} {message}")

        if level == "ISSUE":
            self.issues_found += 1
        elif level == "WARNING":
            self.warnings_found += 1

    def section(self, title: str):
        """Pridaj sekciu do reportu"""
        self.report_lines.append(f"\n## {title}\n")

    def subsection(self, title: str):
        """Pridaj podsekciu"""
        self.report_lines.append(f"\n### {title}\n")

    def run_powershell(self, command: str) -> tuple:
        """Spusti PowerShell prikaz a vrat output"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            return result.stdout.strip(), result.returncode
        except Exception as e:
            return f"ERROR: {str(e)}", 1

    def check_cloudflared(self):
        """Skontroluj Cloudflared instalaciu"""
        self.section("CLOUDFLARED CLEANUP CHECK")

        # Hladaj na viacerych cestach
        possible_paths = [
            Path(r"C:\cloudflared-magerstav"),
            Path(r"C:\cloudflared"),
            Path(r"C:\Program Files\cloudflared"),
        ]

        cloudflared_dir = None
        for path in possible_paths:
            if path.exists():
                cloudflared_dir = path
                self.log(f"Nasiel sa Cloudflared adresar: {path}", "SUCCESS")
                break

        if not cloudflared_dir:
            self.log("Cloudflared adresar neexistuje na ziadnej z ciest:", "WARNING")
            for p in possible_paths:
                self.log(f"  - {p} (neexistuje)")
            return

        # Subory v adresari
        self.subsection(f"Subory v {cloudflared_dir}")
        files = list(cloudflared_dir.glob("*"))

        if not files:
            self.log("Adresar je prazdny", "WARNING")
        else:
            for f in files:
                size = f.stat().st_size if f.is_file() else 0
                size_str = f"{size:,} bytes" if size > 0 else "directory"
                modified = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                self.log(f"{f.name} - {size_str} - Modified: {modified}")

        # Hladaj duplicitne credentials
        self.subsection("Credentials subory")
        json_files = list(cloudflared_dir.glob("*.json"))

        if len(json_files) == 0:
            self.log("Ziadne .json subory nenajdene", "WARNING")
        elif len(json_files) == 1:
            self.log(f"OK - Len jeden credentials subor: {json_files[0].name}", "SUCCESS")
        else:
            self.log(f"DUPLICITNE credentials subory ({len(json_files)} suborov):", "ISSUE")
            for jf in json_files:
                self.log(f"  - {jf.name} ({jf.stat().st_size} bytes)")

        # Registry check
        self.subsection("Windows Registry Check")
        cmd = 'Get-ChildItem "HKLM:\\SYSTEM\\CurrentControlSet\\Services\\" | Where-Object { $_.Name -like "*cloudflared*" } | Select-Object -ExpandProperty PSChildName'
        output, code = self.run_powershell(cmd)

        if code == 0 and output and "ERROR" not in output:
            services = [s for s in output.split('\n') if s.strip()]
            if len(services) > 1:
                self.log(f"Viacero Cloudflared service entries ({len(services)}):", "WARNING")
                for svc in services:
                    self.log(f"  - {svc.strip()}")
            elif len(services) == 1:
                self.log(f"OK - Jeden service: {services[0]}", "SUCCESS")
            else:
                self.log("Ziadne Cloudflared registry entries", "SUCCESS")
        else:
            self.log("Ziadne Cloudflared registry entries", "SUCCESS")

        # Log subory
        self.subsection("Log subory")
        log_files = list(cloudflared_dir.glob("*.log"))
        total_log_size = sum(f.stat().st_size for f in log_files)

        if total_log_size > 10_000_000:  # 10MB
            self.log(f"Velke log subory: {total_log_size:,} bytes ({len(log_files)} files)", "WARNING")
        else:
            self.log(f"Log size OK: {total_log_size:,} bytes ({len(log_files)} files)", "SUCCESS")

    def check_git_status(self):
        """Skontroluj Git stav"""
        self.section("GIT REPOSITORY CHECK")

        os.chdir(self.project_root)

        # Git status
        self.subsection("Git Status")
        result = subprocess.run(["git", "status", "--short"], capture_output=True, text=True)

        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            self.log(f"Untracked/modified subory ({len(lines)}):", "WARNING")
            for line in lines[:20]:  # Max 20 lines
                self.log(f"  {line}")
            if len(lines) > 20:
                self.log(f"  ... a dalsich {len(lines) - 20} suborov")
        else:
            self.log("Working tree clean", "SUCCESS")

        # .gitignore check
        self.subsection(".gitignore Check")
        gitignore = self.project_root / ".gitignore"

        if not gitignore.exists():
            self.log(".gitignore neexistuje!", "ISSUE")
        else:
            with open(gitignore, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]

            self.log(f".gitignore obsahuje {len(lines)} pravidiel", "SUCCESS")

            # Check for important patterns
            important = {
                '*.pyc': 'Python compiled files',
                '__pycache__/': 'Python cache directory',
                '.env': 'Environment variables',
                'venv/': 'Virtual environment',
                '*.log': 'Log files',
                '.pytest_cache/': 'Pytest cache',
                '*.db': 'SQLite databases (ak nie su v Gite)',
                'cleanup_report.md': 'Diagnostics report (temporary)',
            }

            missing = []
            for pattern, description in important.items():
                # Check if pattern or similar exists
                found = any(pattern.replace('/', '') in line or pattern in line for line in lines)
                if not found:
                    missing.append(f"{pattern} - {description}")

            if missing:
                self.log(f"Mozno chybajuce patterns ({len(missing)}):", "WARNING")
                for m in missing:
                    self.log(f"  - {m}")
            else:
                self.log("Vsetky dolezite patterns pritomne", "SUCCESS")

        # Branches check
        self.subsection("Branches")
        result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True)
        branches = result.stdout.strip().split('\n')
        self.log(f"Celkovo {len(branches)} branches")

        local_branches = [b.strip().replace('* ', '') for b in branches if 'remotes/' not in b]
        if len(local_branches) > 3:
            self.log(f"Vela lokalnych branches ({len(local_branches)}), zvazte cleanup", "WARNING")

    def check_documentation(self):
        """Skontroluj dokumentaciu"""
        self.section("DOCUMENTATION CHECK")

        docs_dir = self.project_root / "docs"

        if not docs_dir.exists():
            self.log("docs/ adresar neexistuje!", "ISSUE")
            return

        # Session notes
        self.subsection("Session Notes")
        sessions_dir = docs_dir / "sessions"

        if not sessions_dir.exists():
            self.log("sessions/ adresar neexistuje", "WARNING")
        else:
            session_files = list(sessions_dir.glob("*.md"))
            self.log(f"Pocet session notes: {len(session_files)}")

            # Podla projektu mame 20+ chatov, mali by byt aspon nejake session notes
            if len(session_files) < 5:
                self.log(f"Malo session notes ({len(session_files)}), projekt ma 20+ chatov", "WARNING")

        # TODO items
        self.subsection("TODO Items v dokumentacii")
        todo_pattern = re.compile(r'(TODO|FIXME|XXX|\[ \])', re.IGNORECASE)

        todo_count = 0
        todo_files = []
        for md_file in docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = todo_pattern.findall(content)
                    if matches:
                        todo_count += len(matches)
                        todo_files.append((md_file, len(matches)))
            except Exception as e:
                self.log(f"Chyba pri citani {md_file.name}: {str(e)}", "WARNING")

        if todo_files:
            self.log(f"Celkovo {todo_count} TODO items v {len(todo_files)} suboroch:")
            for md_file, count in todo_files[:10]:  # Max 10
                self.log(f"  - {md_file.relative_to(docs_dir)}: {count} TODOs")
        else:
            self.log("Ziadne TODO items v dokumentacii", "SUCCESS")

        # URL check (bodka vs pomlcka)
        self.subsection("URL Syntax Check")
        wrong_url = "magerstav.invoices.icc.sk"
        correct_url = "magerstav-invoices.icc.sk"

        wrong_url_files = []
        for md_file in docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if wrong_url in content:
                        wrong_url_files.append(md_file)
            except Exception as e:
                self.log(f"Chyba pri kontrole URL v {md_file.name}: {str(e)}", "WARNING")

        if not wrong_url_files:
            self.log(f"URLs su spravne (pomlcka)", "SUCCESS")
        else:
            self.log(f"Naslo sa {len(wrong_url_files)} suborov so starou URL (bodka):", "ISSUE")
            for md_file in wrong_url_files:
                self.log(f"  - {md_file.relative_to(docs_dir)}")

        # Binarne subory v docs (nepatria tam)
        self.subsection("Binarne subory v docs/")
        binary_files = []
        for file in docs_dir.rglob("*"):
            if file.is_file() and file.suffix not in ['.md', '.txt', '.json', '.yml', '.yaml']:
                binary_files.append(file)

        if binary_files:
            self.log(f"Naslo sa {len(binary_files)} binarnych suborov v docs/:", "WARNING")
            for bf in binary_files[:10]:  # Max 10
                self.log(f"  - {bf.relative_to(docs_dir)} ({bf.stat().st_size:,} bytes)")
        else:
            self.log("Ziadne binarne subory v docs/", "SUCCESS")

    def check_code(self):
        """Skontroluj Python kod"""
        self.section("PYTHON CODE CHECK")

        # Python subory su v roote a v extractors/
        py_files = []

        # Root level Python files
        py_files.extend(self.project_root.glob("*.py"))

        # Extractors directory
        extractors_dir = self.project_root / "extractors"
        if extractors_dir.exists():
            py_files.extend(extractors_dir.rglob("*.py"))

        # Tests directory
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            py_files.extend(tests_dir.rglob("*.py"))
        self.log(f"Celkovo {len(py_files)} Python suborov")

        # Commented code detection
        self.subsection("Commented Code")
        total_comments = 0
        suspicious_comments = 0
        suspicious_files = []

        for py_file in py_files:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            comments = [l for l in lines if l.strip().startswith('#')]
            total_comments += len(comments)

            # Hladaj podezrive commented-out code (obsahuje = alebo def)
            suspicious = [c for c in comments if '=' in c or 'def ' in c or 'import ' in c]
            if suspicious and len(suspicious) > 3:
                suspicious_comments += len(suspicious)
                suspicious_files.append((py_file.name, len(suspicious)))

        self.log(f"Celkovo {total_comments} comment lines, {suspicious_comments} podezrivych")

        if suspicious_files:
            self.log(f"Subory s podozrivym commented-out kodom:", "WARNING")
            for filename, count in suspicious_files:
                self.log(f"  - {filename}: {count} lines")

        # Test data
        self.subsection("Test Data")
        test_data_dir = self.project_root / "tests" / "data"

        if test_data_dir.exists():
            test_files = list(test_data_dir.glob("*"))
            total_size = sum(f.stat().st_size for f in test_files if f.is_file())

            self.log(f"Test data: {len(test_files)} suborov, {total_size:,} bytes")

            if total_size > 50_000_000:  # 50MB
                self.log("Test data su velke, zvazte cleanup", "WARNING")
        else:
            self.log("tests/data adresar neexistuje")

    def generate_summary(self):
        """Vygeneruj summary"""
        self.section("SUMMARY")

        self.log(f"**Issues najdene:** {self.issues_found}")
        self.log(f"**Warnings:** {self.warnings_found}")

        if self.issues_found == 0 and self.warnings_found == 0:
            self.log("Vsetko vyzera v poriadku!", "SUCCESS")
        elif self.issues_found == 0:
            self.log(f"Len mensie warnings ({self.warnings_found}), ziadne kriticke issues", "SUCCESS")
        else:
            self.log(f"Nasli sa issues, odporucame cleanup", "WARNING")

        self.section("RECOMMENDED ACTIONS")

        if self.issues_found > 0 or self.warnings_found > 0:
            self.log("1. Skontroluj vsetky ISSUE items vyssie")
            self.log("2. Oprav WARNING items ak je to potrebne")
            self.log("3. Spusti cleanup akcie (vytvorime cleanup script)")
            self.log("4. Commit zmeny do Git")
        else:
            self.log("Ziadne akcie potrebne, projekt je clean!")

    def run(self) -> str:
        """Spusti vsetky kontroly"""
        print("Spustam diagnostiku...")

        # Header
        self.report_lines.append("# CLEANUP DIAGNOSTICS REPORT")
        self.report_lines.append(f"\n**Datum:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.report_lines.append(f"**Projekt:** {self.project_root}")
        self.report_lines.append("\n---\n")

        try:
            print("  Checking Cloudflared...")
            self.check_cloudflared()

            print("  Checking Git...")
            self.check_git_status()

            print("  Checking Documentation...")
            self.check_documentation()

            print("  Checking Code...")
            self.check_code()

            print("  Generating Summary...")
            self.generate_summary()

        except Exception as e:
            self.section("ERROR")
            self.log(f"Chyba pri diagnostike: {str(e)}", "ISSUE")
            import traceback
            self.report_lines.append(f"\n```\n{traceback.format_exc()}\n```")

        return "\n".join(self.report_lines)

    def save_report(self, filename: str = "cleanup_report.md"):
        """Uloz report do suboru"""
        report_path = self.project_root / filename
        report_content = self.run()

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\nReport ulozeny: {report_path}")
        print(f"Issues: {self.issues_found}, Warnings: {self.warnings_found}")
        return report_path


if __name__ == "__main__":
    print("=" * 60)
    print("Supplier Invoice Loader - Cleanup Diagnostics")
    print("=" * 60)
    print()

    diag = CleanupDiagnostics()
    report_path = diag.save_report()

    print(f"\nOtvor subor: {report_path}")
    print("Posli tento report do chatu s Claude")
    print()
    print("=" * 60)