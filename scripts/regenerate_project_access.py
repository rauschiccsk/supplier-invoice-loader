#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate project_file_access files from scratch
Generates fresh file lists from current project state.
"""

import json
from pathlib import Path
from datetime import datetime


class ProjectAccessGenerator:
    def __init__(self, project_root: str = r"C:\Development\supplier_invoice_loader"):
        self.project_root = Path(project_root)
        self.files = []

        # Directories to skip
        self.skip_dirs = {
            'venv', 'ENV', '.venv', 'env',
            '__pycache__', '.pytest_cache',
            '.git', '.github',
            'node_modules',
            '.cleanup_backup', '.cleanup_archive',
            'logs',
            'data',  # Customer data
        }

        # File extensions to skip
        self.skip_extensions = {
            '.pyc', '.pyo', '.pyd',
            '.db', '.sqlite', '.sqlite3',
            '.log',
            '.pdf', '.xml',  # Customer invoices
            '.zip', '.tar', '.gz', '.7z',
        }

    def should_skip(self, path: Path) -> bool:
        """Check if path should be skipped"""
        # Skip directories
        if path.is_dir() and path.name in self.skip_dirs:
            return True

        # Skip by extension
        if path.is_file() and path.suffix.lower() in self.skip_extensions:
            return True

        # Skip hidden files (except .gitignore, .env.example, etc)
        if path.name.startswith('.') and path.name not in [
            '.gitignore', '.env.example', '.flake8', '.dockerignore'
        ]:
            return True

        return False

    def scan_directory(self, directory: Path, category: str = "root"):
        """Recursively scan directory"""
        try:
            for item in directory.iterdir():
                if self.should_skip(item):
                    continue

                if item.is_file():
                    # Add file
                    rel_path = item.relative_to(self.project_root)
                    self.files.append({
                        "path": str(rel_path).replace('\\', '/'),
                        "category": category,
                        "size": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
                elif item.is_dir():
                    # Recursively scan subdirectory
                    subdir_category = item.name if category == "root" else category
                    self.scan_directory(item, subdir_category)
        except PermissionError:
            print(f"[WARN] Permission denied: {directory}")

    def generate_base_file(self):
        """Generate base project_file_access.json"""
        print("📂 Scanning project directory...")
        self.scan_directory(self.project_root)

        print(f"✅ Found {len(self.files)} files")

        # Save base file
        output = {
            "generated": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "total_files": len(self.files),
            "files": self.files
        }

        base_path = self.project_root / "project_file_access.json"
        with open(base_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)

        print(f"💾 Saved: {base_path}")
        return len(self.files)

    def split_by_category(self):
        """Split into category-specific files"""
        print("\n📊 Splitting by category...")

        # Group by category
        categories = {}
        for file_info in self.files:
            cat = file_info['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(file_info)

        # Print statistics
        print("📈 Category statistics:")
        for cat, files in sorted(categories.items()):
            print(f"   {cat:25s}: {len(files):3d} files")

        # Save split files
        print("\n💾 Saving split files...")
        manifest = {
            "generated": datetime.now().isoformat(),
            "categories": {}
        }

        for cat, files in categories.items():
            filename = f"project_file_access_{cat}.json"
            filepath = self.project_root / filename

            output = {
                "category": cat,
                "file_count": len(files),
                "files": files
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)

            manifest["categories"][cat] = {
                "filename": filename,
                "file_count": len(files)
            }

            print(f"   ✅ {filename} ({len(files)} files)")

        # Save manifest
        manifest_path = self.project_root / "project_file_access_manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)

        print(f"\n✅ Manifest: {manifest_path}")

        return len(categories)

    def run(self):
        """Run full generation"""
        print("=" * 60)
        print("PROJECT FILE ACCESS - REGENERATE FROM SCRATCH")
        print("=" * 60)
        print(f"Project: {self.project_root}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        try:
            # Generate base file
            file_count = self.generate_base_file()

            # Split by category
            cat_count = self.split_by_category()

            # Summary
            print("\n" + "=" * 60)
            print("✅ GENERATION COMPLETE")
            print("=" * 60)
            print(f"Total files: {file_count}")
            print(f"Categories: {cat_count}")
            print()
            print("📝 Next steps:")
            print("1. Review generated files")
            print("2. git add project_file_access*.json")
            print("3. git commit -m 'Regenerate project_file_access after cleanup'")
            print("4. git push origin v2.0-multi-customer")
            print()

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return 1

        return 0


if __name__ == "__main__":
    generator = ProjectAccessGenerator()
    exit(generator.run())