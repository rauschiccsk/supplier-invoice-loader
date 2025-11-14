#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Automated Cleanup Script
Automaticky opravi issues najdene v cleanup reporte.

Usage:
    python cleanup_script.py [--dry-run]

Options:
    --dry-run    Ukaze co by sa spravilo, ale neupravi subory
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import argparse


class CleanupScript:
    def __init__(self, project_root: str = r"C:\Development\supplier_invoice_loader", dry_run: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.backup_dir = self.project_root / ".cleanup_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fixes_applied = 0
        self.errors_found = 0

    def log(self, message: str, level: str = "INFO"):
        """Vypis spravu"""
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "ERROR": "[ERROR]",
            "DRY_RUN": "[DRY-RUN]"
        }.get(level, "[*]")
        print(f"{prefix} {message}")

    def create_backup(self, file_path: Path):
        """Vytvor backup suboru"""
        if self.dry_run:
            self.log(f"Backup: {file_path.name}", "DRY_RUN")
            return

        # Vytvor backup adresar ak neexistuje
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Relativna cesta od project root
        rel_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / rel_path

        # Vytvor parent directories
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Skopiruj subor
        shutil.copy2(file_path, backup_path)
        self.log(f"Backup created: {rel_path}")

    def fix_url_syntax(self):
        """Opravi URL syntax (bodka -> pomlcka) v dokumentacii"""
        self.log("\n=== FIX 1: URL Syntax ===")

        wrong_url = "magerstav.invoices.icc.sk"
        correct_url = "magerstav-invoices.icc.sk"

        # Subory ktore treba opravit (z diagnostiky)
        files_to_fix = [
            "docs/MASTER_CONTEXT.md",
            "docs/architecture/cloudflared-setup.md",
            "docs/architecture/n8n-workflows.md",
            "docs/troubleshooting/common-issues.md"
        ]

        for file_rel in files_to_fix:
            file_path = self.project_root / file_rel

            if not file_path.exists():
                self.log(f"File not found: {file_rel}", "ERROR")
                self.errors_found += 1
                continue

            # Citaj obsah
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                self.log(f"Error reading {file_rel}: {e}", "ERROR")
                self.errors_found += 1
                continue

            # Skontroluj ci obsahuje wrong URL
            if wrong_url not in content:
                self.log(f"No changes needed: {file_rel}")
                continue

            # Spocitaj vyskyty
            count = content.count(wrong_url)

            if self.dry_run:
                self.log(f"Would fix {count} URL(s) in: {file_rel}", "DRY_RUN")
                continue

            # Vytvor backup
            self.create_backup(file_path)

            # Opravi URL
            new_content = content.replace(wrong_url, correct_url)

            # Uloz
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.log(f"Fixed {count} URL(s) in: {file_rel}", "SUCCESS")
                self.fixes_applied += 1
            except Exception as e:
                self.log(f"Error writing {file_rel}: {e}", "ERROR")
                self.errors_found += 1

    def update_diagnostics(self):
        """Aktualizuj cleanup_diagnostics.py aby hladal Python subory v roote"""
        self.log("\n=== FIX 2: Update Diagnostics Script ===")

        diag_file = self.project_root / "cleanup_diagnostics.py"

        if not diag_file.exists():
            self.log("cleanup_diagnostics.py not found", "ERROR")
            self.errors_found += 1
            return

        # Citaj obsah
        with open(diag_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Najdi metodu check_code
        old_code = '''    def check_code(self):
        """Skontroluj Python kod"""
        self.section("PYTHON CODE CHECK")

        src_dir = self.project_root / "src"

        if not src_dir.exists():
            self.log("src/ adresar neexistuje!", "ISSUE")
            return

        # Python subory
        py_files = list(src_dir.rglob("*.py"))'''

        new_code = '''    def check_code(self):
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
            py_files.extend(tests_dir.rglob("*.py"))'''

        if old_code not in content:
            self.log("Diagnostics script already updated or structure changed", "INFO")
            return

        if self.dry_run:
            self.log("Would update check_code() method in diagnostics script", "DRY_RUN")
            return

        # Vytvor backup
        self.create_backup(diag_file)

        # Opravi
        new_content = content.replace(old_code, new_code)

        # Uloz
        with open(diag_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        self.log("Updated cleanup_diagnostics.py to check root Python files", "SUCCESS")
        self.fixes_applied += 1

    def update_gitignore(self):
        """Pridaj cleanup backup do .gitignore"""
        self.log("\n=== FIX 3: Update .gitignore ===")

        gitignore_file = self.project_root / ".gitignore"

        if not gitignore_file.exists():
            self.log(".gitignore not found", "ERROR")
            self.errors_found += 1
            return

        # Citaj obsah
        with open(gitignore_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Skontroluj ci uz obsahuje .cleanup_backup
        if '.cleanup_backup/' in content or '.cleanup/' in content:
            self.log(".gitignore already has cleanup backup rule")
            return

        if self.dry_run:
            self.log("Would add .cleanup_backup/ to .gitignore", "DRY_RUN")
            return

        # Vytvor backup
        self.create_backup(gitignore_file)

        # Pridaj na koniec Cleanup sekcie
        cleanup_section = "# Cleanup scripts output\ncleanup_backup/\ncleanup_temp/\n.cleanup/"

        if cleanup_section in content:
            # Pridaj za existujucu sekciu
            new_rule = ".cleanup_backup/  # Automatic backups from cleanup script"
            new_content = content.replace(".cleanup/", f".cleanup/\n{new_rule}")
        else:
            # Pridaj novu sekciu
            new_content = content + f"\n\n# Cleanup script backups\n.cleanup_backup/\n"

        # Uloz
        with open(gitignore_file, 'w', encoding='utf-8') as f:
            f.write(new_content)

        self.log("Added .cleanup_backup/ to .gitignore", "SUCCESS")
        self.fixes_applied += 1

    def generate_summary_report(self):
        """Vygeneruj summary report"""
        self.log("\n" + "=" * 60)
        self.log("CLEANUP SUMMARY")
        self.log("=" * 60)

        self.log(f"Fixes applied: {self.fixes_applied}")
        self.log(f"Errors found: {self.errors_found}")

        if self.backup_dir.exists() and not self.dry_run:
            self.log(f"Backups saved to: {self.backup_dir}")

        if self.dry_run:
            self.log("\nDRY RUN MODE - No files were modified", "INFO")
            self.log("Run without --dry-run to apply changes")
        elif self.fixes_applied > 0:
            self.log(f"\nSuccessfully applied {self.fixes_applied} fixes!", "SUCCESS")
            self.log("\nNext steps:")
            self.log("1. Review changes: git diff")
            self.log("2. Run diagnostics again: python cleanup_diagnostics.py")
            self.log("3. If OK, commit: git add . && git commit -m 'chore: Cleanup - Fix URLs and update diagnostics'")
        else:
            self.log("\nNo fixes needed - project is clean!", "SUCCESS")

    def run(self):
        """Spusti cleanup"""
        self.log("=" * 60)
        self.log("SUPPLIER INVOICE LOADER - AUTOMATED CLEANUP")
        self.log("=" * 60)

        if self.dry_run:
            self.log("DRY RUN MODE - No files will be modified", "INFO")

        self.log(f"Project: {self.project_root}")
        self.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            # Fix 1: URL syntax
            self.fix_url_syntax()

            # Fix 2: Update diagnostics
            self.update_diagnostics()

            # Fix 3: Update gitignore
            self.update_gitignore()

            # Summary
            self.generate_summary_report()

        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return 1

        return 0 if self.errors_found == 0 else 1


def main():
    parser = argparse.ArgumentParser(description='Automated cleanup for Supplier Invoice Loader')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without modifying files')
    args = parser.parse_args()

    cleanup = CleanupScript(dry_run=args.dry_run)
    exit_code = cleanup.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()