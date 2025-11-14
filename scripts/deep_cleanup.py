#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Deep Cleanup Script
Odstrani dead code, obsolete subory a Docker artifacts.

Usage:
    python deep_cleanup.py [--dry-run] [--keep-tests]

Options:
    --dry-run      Ukaze co by sa spravilo bez zmien
    --keep-tests   Necha test subory v roote (default: presunie do tests/)
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
import argparse


class DeepCleanup:
    def __init__(self, project_root: str = r"C:\Development\supplier_invoice_loader",
                 dry_run: bool = False, keep_tests: bool = False):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.keep_tests = keep_tests
        self.archive_dir = self.project_root / ".cleanup_archive"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.removed_count = 0
        self.moved_count = 0
        self.errors = 0

    def log(self, message: str, level: str = "INFO"):
        """Vypis spravu"""
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[OK]",
            "ERROR": "[ERROR]",
            "WARNING": "[WARN]",
            "DRY_RUN": "[DRY-RUN]"
        }.get(level, "[*]")
        print(f"{prefix} {message}")

    def create_archive(self, files_to_archive: list, category: str):
        """Vytvor ZIP archive pred odstranenim"""
        if self.dry_run or not files_to_archive:
            return

        self.archive_dir.mkdir(exist_ok=True)
        archive_name = f"{category}_{self.timestamp}.zip"
        archive_path = self.archive_dir / archive_name

        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in files_to_archive:
                if file_path.exists():
                    arcname = file_path.relative_to(self.project_root)
                    zipf.write(file_path, arcname)

        self.log(f"Archive created: {archive_name} ({len(files_to_archive)} files)")

    def safe_remove(self, path: Path, category: str = ""):
        """Bezpecne odstran subor/adresar"""
        if not path.exists():
            return

        if self.dry_run:
            kind = "dir" if path.is_dir() else "file"
            self.log(f"Would remove {kind}: {path.name}", "DRY_RUN")
            return

        try:
            if path.is_dir():
                shutil.rmtree(path)
                self.log(f"Removed directory: {path.name}", "SUCCESS")
            else:
                path.unlink()
                self.log(f"Removed file: {path.name}", "SUCCESS")
            self.removed_count += 1
        except Exception as e:
            self.log(f"Error removing {path.name}: {e}", "ERROR")
            self.errors += 1

    def cleanup_docker(self):
        """Odstran Docker-related subory"""
        self.log("\n=== CATEGORY 1: Docker Files ===")

        docker_files = [
            ".dockerignore",
            "docker-compose.yml",
            "Dockerfile",
            "DOCKER_DEPLOYMENT.md",
            "nginx.conf",
            "deploy.sh",
            "SECURITY_SETUP.md"
        ]

        files_to_remove = []
        for filename in docker_files:
            file_path = self.project_root / filename
            if file_path.exists():
                files_to_remove.append(file_path)

        if not files_to_remove:
            self.log("No Docker files found")
            return

        self.log(f"Found {len(files_to_remove)} Docker files to remove")

        # Create archive
        self.create_archive(files_to_remove, "docker_files")

        # Remove files
        for file_path in files_to_remove:
            self.safe_remove(file_path, "Docker")

    def cleanup_obsolete_scripts(self):
        """Odstran obsolete/duplicitne skripty"""
        self.log("\n=== CATEGORY 2: Obsolete Scripts ===")

        obsolete_files = [
            # Nahradene verzie
            "generate_access.py",  # -> split_project_access.py
            "database.py",  # -> database_v2.py
            "CLAUDE_CONTEXT.md",  # -> FULL_PROJECT_CONTEXT.md
            "project_file_access.json",  # -> split versions

            # Migration files (uz hotove)
            "migrate_v2.py",
            "rollback_v2.py",
            "migration_v2.sql",
            "MIGRATION_GUIDE.md",

            # Duplicitne/stare docs
            "DEPLOYMENT.md",  # duplicitny s INSTALL_CUSTOMER.md
            "POJECT_PLAIN.md",  # typo v nazve, pravdepodobne stary
        ]

        files_to_remove = []
        for filename in obsolete_files:
            file_path = self.project_root / filename
            if file_path.exists():
                files_to_remove.append(file_path)

        if not files_to_remove:
            self.log("No obsolete scripts found")
            return

        self.log(f"Found {len(files_to_remove)} obsolete files to remove")

        # Create archive
        self.create_archive(files_to_remove, "obsolete_scripts")

        # Remove files
        for file_path in files_to_remove:
            self.safe_remove(file_path, "Obsolete")

    def cleanup_old_databases_logs(self):
        """Odstran stare dev databazy a logy"""
        self.log("\n=== CATEGORY 3: Old Databases & Logs ===")

        old_files = [
            "ls_invoices.db",  # stara dev databaza
            "invoices.db",  # stara dev databaza
            "ls_loader.log",  # 1.4 MB stary log
            "invoice_loader.log",  # stary log
        ]

        files_to_remove = []
        for filename in old_files:
            file_path = self.project_root / filename
            if file_path.exists():
                size = file_path.stat().st_size
                files_to_remove.append(file_path)
                self.log(f"  - {filename} ({size:,} bytes)")

        if not files_to_remove:
            self.log("No old databases/logs found")
            return

        total_size = sum(f.stat().st_size for f in files_to_remove)
        self.log(f"Total size to free: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")

        # Create archive
        self.create_archive(files_to_remove, "old_databases_logs")

        # Remove files
        for file_path in files_to_remove:
            self.safe_remove(file_path, "Old data")

    def cleanup_test_files(self):
        """Presun test subory z rootu do tests/"""
        if self.keep_tests:
            self.log("\n=== CATEGORY 4: Test Files (SKIPPED - keep-tests flag) ===")
            return

        self.log("\n=== CATEGORY 4: Test Files ===")

        test_files = [
            "test_batch_extraction.py",
            "test_extraction.py",
            "test_import.py",
            "test_isdoc.py",
            # test_e2e.py nechat v roote - pouziva sa
        ]

        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            tests_dir.mkdir()

        for filename in test_files:
            src = self.project_root / filename
            if not src.exists():
                continue

            dst = tests_dir / filename

            if self.dry_run:
                self.log(f"Would move: {filename} -> tests/", "DRY_RUN")
                continue

            try:
                shutil.move(str(src), str(dst))
                self.log(f"Moved: {filename} -> tests/", "SUCCESS")
                self.moved_count += 1
            except Exception as e:
                self.log(f"Error moving {filename}: {e}", "ERROR")
                self.errors += 1

    def cleanup_pycache(self):
        """Odstran __pycache__ adresare"""
        self.log("\n=== CATEGORY 5: Python Cache ===")

        pycache_dirs = list(self.project_root.rglob("__pycache__"))

        if not pycache_dirs:
            self.log("No __pycache__ directories found")
            return

        self.log(f"Found {len(pycache_dirs)} __pycache__ directories")

        for pycache_dir in pycache_dirs:
            self.safe_remove(pycache_dir, "Cache")

    def cleanup_idea(self):
        """Odstran .idea adresar (PyCharm config)"""
        self.log("\n=== CATEGORY 6: IDE Config ===")

        idea_dir = self.project_root / ".idea"

        if not idea_dir.exists():
            self.log("No .idea directory found")
            return

        self.log("Found .idea directory (PyCharm config)")

        if self.dry_run:
            self.log("Would remove: .idea/", "DRY_RUN")
        else:
            # Archive first
            self.log("Archiving .idea/ before removal...")
            archive_path = self.archive_dir / f"idea_config_{self.timestamp}.zip"
            self.archive_dir.mkdir(exist_ok=True)

            shutil.make_archive(
                str(archive_path.with_suffix('')),
                'zip',
                self.project_root,
                '.idea'
            )

            self.safe_remove(idea_dir, "IDE")

    def cleanup_deployment_artifacts(self):
        """Odstran deployment package artifacts"""
        self.log("\n=== CATEGORY 7: Deployment Artifacts ===")

        artifacts = [
            "deployment_package/",  # build artifact adresar
            "create_deployment_package.bat",
            "DEPLOYMENT_PACKAGE_CHECKLIST.md",
        ]

        items_to_remove = []
        for item_name in artifacts:
            item_path = self.project_root / item_name.rstrip('/')
            if item_path.exists():
                items_to_remove.append(item_path)

        if not items_to_remove:
            self.log("No deployment artifacts found")
            return

        self.log(f"Found {len(items_to_remove)} deployment artifacts")

        # Archive directories
        dirs_to_archive = [p for p in items_to_remove if p.is_dir()]
        if dirs_to_archive:
            for dir_path in dirs_to_archive:
                if not self.dry_run:
                    archive_name = f"{dir_path.name}_{self.timestamp}"
                    archive_path = self.archive_dir / archive_name
                    self.archive_dir.mkdir(exist_ok=True)
                    shutil.make_archive(str(archive_path), 'zip', dir_path)
                    self.log(f"Archived: {dir_path.name}/")

        # Remove all
        for item_path in items_to_remove:
            self.safe_remove(item_path, "Deployment")

    def update_gitignore(self):
        """Aktualizuj .gitignore"""
        self.log("\n=== UPDATE .gitignore ===")

        gitignore_path = self.project_root / ".gitignore"

        if not gitignore_path.exists():
            self.log(".gitignore not found", "ERROR")
            return

        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Patterns to ensure
        patterns_to_add = []

        if '.cleanup_archive/' not in content:
            patterns_to_add.append('.cleanup_archive/  # Deep cleanup archives')

        if '.idea/' not in content and '.idea' not in content:
            patterns_to_add.append('.idea/  # PyCharm IDE config')

        if not patterns_to_add:
            self.log(".gitignore is up to date")
            return

        if self.dry_run:
            self.log(f"Would add {len(patterns_to_add)} patterns to .gitignore", "DRY_RUN")
            return

        # Add patterns
        new_content = content
        if '.cleanup/' in content:
            # Add after existing cleanup section
            new_content = content.replace(
                '.cleanup/',
                '.cleanup/\n' + '\n'.join(patterns_to_add)
            )
        else:
            # Add at end
            new_content = content + '\n\n# Deep cleanup\n' + '\n'.join(patterns_to_add) + '\n'

        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        self.log(f"Added {len(patterns_to_add)} patterns to .gitignore", "SUCCESS")

    def generate_summary(self):
        """Vygeneruj summary"""
        self.log("\n" + "=" * 60)
        self.log("DEEP CLEANUP SUMMARY")
        self.log("=" * 60)

        self.log(f"Files removed: {self.removed_count}")
        self.log(f"Files moved: {self.moved_count}")
        self.log(f"Errors: {self.errors}")

        if self.archive_dir.exists() and not self.dry_run:
            archives = list(self.archive_dir.glob("*.zip"))
            self.log(f"Archives created: {len(archives)}")
            self.log(f"Archive location: {self.archive_dir}")

        if self.dry_run:
            self.log("\nDRY RUN MODE - No files were modified", "INFO")
        elif self.removed_count > 0 or self.moved_count > 0:
            self.log(f"\nSuccessfully cleaned {self.removed_count + self.moved_count} items!", "SUCCESS")
            self.log("\nNext steps:")
            self.log("1. Review changes: git status")
            self.log("2. Run diagnostics: python cleanup_diagnostics.py")
            self.log("3. Commit: git add . && git commit -m 'chore: Deep cleanup - Remove dead code'")
        else:
            self.log("\nNo cleanup needed - project is clean!", "SUCCESS")

    def run(self):
        """Spusti deep cleanup"""
        self.log("=" * 60)
        self.log("DEEP CLEANUP - REMOVE DEAD CODE")
        self.log("=" * 60)

        if self.dry_run:
            self.log("DRY RUN MODE - No files will be modified", "INFO")

        self.log(f"Project: {self.project_root}")
        self.log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            self.cleanup_docker()
            self.cleanup_obsolete_scripts()
            self.cleanup_old_databases_logs()
            self.cleanup_test_files()
            self.cleanup_pycache()
            self.cleanup_idea()
            self.cleanup_deployment_artifacts()
            self.update_gitignore()
            self.generate_summary()

        except Exception as e:
            self.log(f"Unexpected error: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            return 1

        return 0 if self.errors == 0 else 1


def main():
    parser = argparse.ArgumentParser(description='Deep cleanup for Supplier Invoice Loader')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without modifying files')
    parser.add_argument('--keep-tests', action='store_true',
                        help='Keep test files in root (do not move to tests/)')
    args = parser.parse_args()

    cleanup = DeepCleanup(dry_run=args.dry_run, keep_tests=args.keep_tests)
    exit_code = cleanup.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()