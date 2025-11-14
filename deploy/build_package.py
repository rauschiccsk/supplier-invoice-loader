#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Supplier Invoice Loader - Deployment Package Builder
Creates ZIP packages for customer deployments

Usage:
    python build_package.py                    # Interactive mode
    python build_package.py --customer NAME    # Build for specific customer
    python build_package.py --template         # Build template package
    python build_package.py --full            # Build full package with venv
"""

import os
import sys
import zipfile
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Files to always include in package
CORE_FILES = [
    'main.py',
    'config.py',
    'config_template.py',
    'database.py',
    'models.py',
    'isdoc.py',
    'notifications.py',
    'monitoring.py',
    'env_loader.py',
    'migrate_v2.py',
    'rollback_v2.py',
    'migration_v2.sql',
    'requirements.txt',
    'requirements-dev.txt',
    '.env.example',
    'README.md'
]

# Directories to include
CORE_DIRECTORIES = [
    'extractors',
    'deploy',
    'tests'
]

# Documentation files
DOCUMENTATION = [
    'DEPLOYMENT.md',
    'DEVELOPMENT.md',
    'MIGRATION_GUIDE.md',
    'TROUBLESHOOTING.md',
    'MONITORING.md',
    'EMAIL_ALERTING.md',
    'N8N_WORKFLOW_SETUP.md',
    'PYTHON_SETUP.md',
    'SECURITY.md',
    'DEPLOYMENT_CHECKLIST.md',
    'PROJECT_PLAN.md'
]

# Files to exclude
EXCLUDE_FILES = [
    'config_customer.py',
    'invoices.db',
    '*.pyc',
    '__pycache__',
    '.git',
    '.gitignore',
    '.env',
    '*.log',
    'backup_*',
    '*.backup',
    '.idea',
    '.vscode',
    'venv',
    'htmlcov',
    '.coverage',
    '.pytest_cache',
    '*.egg-info'
]

# Customer-specific files (copy if they exist)
CUSTOMER_FILES = [
    'config_customer.py',
    '.env'
]


class PackageBuilder:
    """Deployment package builder"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd().parent
        self.deploy_dir = self.project_root / 'deploy'
        self.packages_dir = self.deploy_dir / 'packages'
        self.packages_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str, level: str = "INFO"):
        """Log message with color"""
        colors = {
            'INFO': '\033[94m',
            'SUCCESS': '\033[92m',
            'WARNING': '\033[93m',
            'ERROR': '\033[91m'
        }
        reset = '\033[0m'

        print(f"{colors.get(level, '')}[{level}]{reset} {message}")

    def should_exclude(self, path: Path) -> bool:
        """Check if file/dir should be excluded"""
        name = path.name

        # Check exact matches
        if name in EXCLUDE_FILES:
            return True

        # Check patterns
        for pattern in EXCLUDE_FILES:
            if '*' in pattern:
                import fnmatch
                if fnmatch.fnmatch(name, pattern):
                    return True

        return False

    def get_version(self) -> str:
        """Get version from main.py or git"""
        try:
            # Try to get from main.py
            main_file = self.project_root / 'main.py'
            if main_file.exists():
                content = main_file.read_text()
                for line in content.split('\n'):
                    if 'version=' in line and '"' in line:
                        return line.split('"')[1]
        except:
            pass

        try:
            # Try git describe
            import subprocess
            result = subprocess.run(
                ['git', 'describe', '--tags', '--always'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        return "2.0.0"

    def create_manifest(self, package_type: str, customer_name: Optional[str] = None) -> Dict:
        """Create package manifest"""
        return {
            'package_type': package_type,
            'version': self.get_version(),
            'created': datetime.now().isoformat(),
            'customer': customer_name,
            'python_required': '>=3.8',
            'contents': {
                'core_files': CORE_FILES,
                'directories': CORE_DIRECTORIES,
                'documentation': DOCUMENTATION
            }
        }

    def build_template_package(self) -> Path:
        """Build template package (no customer-specific files)"""
        self.log("Building template package...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self.get_version()
        package_name = f"supplier_invoice_loader_template_v{version}_{timestamp}.zip"
        package_path = self.packages_dir / package_name

        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add core files
            for file_name in CORE_FILES:
                file_path = self.project_root / file_name
                if file_path.exists():
                    zipf.write(file_path, f"supplier_invoice_loader/{file_name}")
                    self.log(f"  Added: {file_name}", "SUCCESS")
                else:
                    self.log(f"  Missing: {file_name}", "WARNING")

            # Add directories
            for dir_name in CORE_DIRECTORIES:
                dir_path = self.project_root / dir_name
                if dir_path.exists():
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file() and not self.should_exclude(file_path):
                            rel_path = file_path.relative_to(self.project_root)
                            zipf.write(file_path, f"supplier_invoice_loader/{rel_path}")
                    self.log(f"  Added directory: {dir_name}", "SUCCESS")

            # Add documentation
            for doc_name in DOCUMENTATION:
                doc_path = self.project_root / doc_name
                if doc_path.exists():
                    zipf.write(doc_path, f"supplier_invoice_loader/{doc_name}")

            # Add manifest
            manifest = self.create_manifest('template')
            manifest_json = json.dumps(manifest, indent=2)
            zipf.writestr('supplier_invoice_loader/MANIFEST.json', manifest_json)

            # Add quick start guide
            quickstart = self.create_quickstart_guide()
            zipf.writestr('supplier_invoice_loader/QUICKSTART.txt', quickstart)

        self.log(f"Template package created: {package_path}", "SUCCESS")
        self.log(f"Size: {package_path.stat().st_size / 1024 / 1024:.2f} MB")

        return package_path

    def build_customer_package(self, customer_name: str) -> Path:
        """Build customer-specific package"""
        self.log(f"Building package for customer: {customer_name}")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self.get_version()
        package_name = f"supplier_invoice_loader_{customer_name}_v{version}_{timestamp}.zip"
        package_path = self.packages_dir / package_name

        # First, create template package structure
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all template files first
            for file_name in CORE_FILES:
                file_path = self.project_root / file_name
                if file_path.exists():
                    zipf.write(file_path, f"supplier_invoice_loader/{file_name}")

            # Add directories
            for dir_name in CORE_DIRECTORIES:
                dir_path = self.project_root / dir_name
                if dir_path.exists():
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file() and not self.should_exclude(file_path):
                            rel_path = file_path.relative_to(self.project_root)
                            zipf.write(file_path, f"supplier_invoice_loader/{rel_path}")

            # Add customer-specific files if they exist
            config_customer = self.project_root / 'config_customer.py'
            if config_customer.exists():
                # Check if it's actually configured for this customer
                content = config_customer.read_text()
                if customer_name in content:
                    zipf.write(config_customer, 'supplier_invoice_loader/config_customer.py')
                    self.log("  Added customer config", "SUCCESS")
                else:
                    self.log("  Config exists but not for this customer", "WARNING")

            # Add .env if exists (sanitized)
            env_file = self.project_root / '.env'
            if env_file.exists():
                # Create sanitized version
                sanitized_env = self.sanitize_env_file(env_file)
                zipf.writestr('supplier_invoice_loader/.env.configured', sanitized_env)
                self.log("  Added sanitized .env", "SUCCESS")

            # Add manifest
            manifest = self.create_manifest('customer', customer_name)
            manifest_json = json.dumps(manifest, indent=2)
            zipf.writestr('supplier_invoice_loader/MANIFEST.json', manifest_json)

            # Add customer-specific instructions
            instructions = self.create_customer_instructions(customer_name)
            zipf.writestr('supplier_invoice_loader/CUSTOMER_README.md', instructions)

        self.log(f"Customer package created: {package_path}", "SUCCESS")
        self.log(f"Size: {package_path.stat().st_size / 1024 / 1024:.2f} MB")

        return package_path

    def build_full_package(self) -> Path:
        """Build full package including virtual environment"""
        self.log("Building full package with dependencies...")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self.get_version()
        package_name = f"supplier_invoice_loader_full_v{version}_{timestamp}.zip"
        package_path = self.packages_dir / package_name

        # Create temporary directory
        temp_dir = self.packages_dir / f"temp_{timestamp}"
        temp_dir.mkdir()

        try:
            # Copy all files
            package_root = temp_dir / 'supplier_invoice_loader'
            shutil.copytree(
                self.project_root,
                package_root,
                ignore=shutil.ignore_patterns(*EXCLUDE_FILES)
            )

            # Create deployment script
            deploy_script = package_root / 'DEPLOY.bat'
            deploy_script.write_text(self.create_full_deploy_script())

            # Create ZIP
            shutil.make_archive(
                str(package_path.with_suffix('')),
                'zip',
                temp_dir
            )

        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir)

        self.log(f"Full package created: {package_path}", "SUCCESS")
        self.log(f"Size: {package_path.stat().st_size / 1024 / 1024:.2f} MB")

        return package_path

    def sanitize_env_file(self, env_path: Path) -> str:
        """Remove sensitive data from .env file"""
        lines = []
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                # Keep key but remove value for sensitive fields
                if any(sensitive in key.upper() for sensitive in ['PASSWORD', 'KEY', 'SECRET', 'TOKEN']):
                    lines.append(f"{key}=CHANGE_ME")
                else:
                    lines.append(line)
            else:
                lines.append(line)
        return '\n'.join(lines)

    def create_quickstart_guide(self) -> str:
        """Create quick start guide"""
        return """
SUPPLIER INVOICE LOADER - QUICK START GUIDE
==========================================

1. EXTRACT PACKAGE
   - Extract this ZIP to your desired location
   - e.g., C:\\SupplierInvoiceLoader or /opt/supplier_invoice_loader

2. INSTALL PYTHON
   - Ensure Python 3.8+ is installed
   - Download from: https://www.python.org/downloads/

3. RUN DEPLOYMENT SCRIPT

   Windows:
   --------
   cd supplier_invoice_loader\\deploy
   deploy.bat new YOUR_CUSTOMER_NAME

   Linux/Mac:
   ----------
   cd supplier_invoice_loader/deploy
   chmod +x deploy.sh
   ./deploy.sh new YOUR_CUSTOMER_NAME

4. CONFIGURE
   - Edit config_customer.py with actual values
   - Edit .env with API keys and SMTP credentials

5. TEST
   Windows: deploy.bat test
   Linux: ./deploy.sh test

6. START SERVICE
   Windows: net start SupplierInvoiceLoader
   Linux: sudo systemctl start supplier-invoice-loader

For detailed instructions, see:
- DEPLOYMENT.md
- README.md
- DEPLOYMENT_CHECKLIST.md

Support: support@icc.sk
"""

    def create_customer_instructions(self, customer_name: str) -> str:
        """Create customer-specific instructions"""
        return f"""
# Deployment Instructions for {customer_name}

## Package Contents

This package has been pre-configured for **{customer_name}**.

### Included Configuration

- ✅ Core application files
- ✅ Customer configuration template
- ✅ Database migration scripts
- ✅ Deployment scripts
- ✅ Documentation

### Quick Deployment

1. **Extract Package**
   ```
   Extract to: C:\\SupplierInvoiceLoader_{customer_name}
   ```

2. **Run Deployment**
   ```cmd
   cd deploy
   deploy.bat update
   ```

3. **Verify Configuration**
   - Check `config_customer.py` has correct values
   - Verify NEX Genesis API settings
   - Confirm email settings in `.env`

4. **Test Installation**
   ```cmd
   deploy.bat test
   ```

5. **Start Service**
   ```cmd
   net start SupplierInvoiceLoader
   ```

## Configuration Checklist

- [ ] NEX_GENESIS_API_URL configured
- [ ] NEX_GENESIS_API_KEY set
- [ ] OPERATOR_EMAIL verified
- [ ] SMTP credentials in .env
- [ ] Storage paths accessible
- [ ] Database migrated to v2

## Support

Customer: {customer_name}
Version: {self.get_version()}
Support: support@icc.sk

See DEPLOYMENT_CHECKLIST.md for complete deployment guide.
"""

    def create_full_deploy_script(self) -> str:
        """Create deployment script for full package"""
        return """@echo off
echo ==========================================
echo Supplier Invoice Loader - Quick Deploy
echo ==========================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate and install
call venv\\Scripts\\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM Initialize database
python -c "import database; database.init_database()"

echo.
echo Deployment complete!
echo.
echo Next steps:
echo 1. Copy config_template.py to config_customer.py
echo 2. Edit config_customer.py with your settings
echo 3. Create .env file with API keys
echo 4. Run: python main.py
echo.
pause
"""

    def list_packages(self):
        """List existing packages"""
        self.log("Existing packages:")

        packages = list(self.packages_dir.glob('*.zip'))
        if not packages:
            self.log("  No packages found", "WARNING")
            return

        packages.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        for package in packages[:10]:  # Show last 10
            size_mb = package.stat().st_size / 1024 / 1024
            modified = datetime.fromtimestamp(package.stat().st_mtime)
            self.log(f"  {package.name} ({size_mb:.2f} MB) - {modified:%Y-%m-%d %H:%M}")

    def interactive_mode(self):
        """Interactive package builder"""
        print("\n" + "=" * 50)
        print("SUPPLIER INVOICE LOADER - PACKAGE BUILDER")
        print("=" * 50)

        print("\nPackage Types:")
        print("1. Template Package (no customer files)")
        print("2. Customer Package (with config)")
        print("3. Full Package (with dependencies)")
        print("4. List existing packages")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()

        if choice == '1':
            self.build_template_package()
        elif choice == '2':
            customer = input("Enter customer name: ").strip().upper()
            if customer:
                self.build_customer_package(customer)
            else:
                self.log("Customer name required", "ERROR")
        elif choice == '3':
            self.build_full_package()
        elif choice == '4':
            self.list_packages()
        elif choice == '5':
            return
        else:
            self.log("Invalid option", "ERROR")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Build deployment packages for Supplier Invoice Loader"
    )
    parser.add_argument(
        "--customer",
        help="Build package for specific customer"
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Build template package"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Build full package with dependencies"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing packages"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for packages"
    )

    args = parser.parse_args()

    # Create builder
    builder = PackageBuilder()

    if args.output_dir:
        builder.packages_dir = Path(args.output_dir)
        builder.packages_dir.mkdir(parents=True, exist_ok=True)

    # Process arguments
    if args.customer:
        builder.build_customer_package(args.customer)
    elif args.template:
        builder.build_template_package()
    elif args.full:
        builder.build_full_package()
    elif args.list:
        builder.list_packages()
    else:
        # Interactive mode
        builder.interactive_mode()


if __name__ == "__main__":
    main()