#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verification script for supplier-invoice-loader installation.
Tests all core imports and basic functionality.
"""

import sys
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_python_version():
    """Verify Python version."""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 11:
        print("✅ Python version OK (3.11+)")
        return True
    else:
        print("❌ Python version must be 3.11+")
        return False


def test_core_imports():
    """Test core library imports."""
    print_header("Core Library Imports")

    imports = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("pdfplumber", "PDF extraction"),
        ("PyPDF2", "PDF manipulation"),
        ("lxml", "XML processing"),
        ("sqlite3", "Database (built-in)"),
        ("requests", "HTTP client"),
        ("psutil", "System monitoring"),
    ]

    success = True
    for module, description in imports:
        try:
            __import__(module)
            print(f"✅ {module:15} - {description}")
        except ImportError as e:
            print(f"❌ {module:15} - FAILED: {e}")
            success = False

    return success


def test_dev_imports():
    """Test development tool imports."""
    print_header("Development Tools Imports")

    imports = [
        ("pytest", "Testing framework"),
        ("black", "Code formatter"),
        ("flake8", "Linter"),
        ("mypy", "Type checker"),
        ("safety", "Security scanner"),
        ("bandit", "Security linter"),
        ("coverage", "Code coverage"),
    ]

    success = True
    for module, description in imports:
        try:
            __import__(module)
            print(f"✅ {module:15} - {description}")
        except ImportError as e:
            print(f"❌ {module:15} - FAILED: {e}")
            success = False

    return success


def test_project_structure():
    """Verify project structure."""
    print_header("Project Structure Check")

    required_paths = [
        ("src/", "Source code directory"),
        ("src/api/", "API models"),
        ("src/database/", "Database operations"),
        ("src/extractors/", "PDF extractors"),
        ("src/business/", "Business logic"),
        ("src/utils/", "Utilities"),
        ("tests/", "Test suite"),
        ("config/", "Configuration"),
        ("docs/", "Documentation"),
        ("main.py", "Application entry point"),
        ("requirements.txt", "Production dependencies"),
        ("requirements-dev.txt", "Dev dependencies"),
    ]

    project_root = Path.cwd()
    success = True

    for path, description in required_paths:
        full_path = project_root / path
        if full_path.exists():
            print(f"✅ {path:25} - {description}")
        else:
            print(f"❌ {path:25} - NOT FOUND")
            success = False

    return success


def test_project_imports():
    """Test project module imports."""
    print_header("Project Module Imports")

    imports = [
        ("src.api.models", "API models"),
        ("src.database.database", "Database client"),
        ("src.extractors.ls_extractor", "L&Š extractor"),
        ("src.extractors.generic_extractor", "Generic extractor"),
        ("src.business.isdoc_service", "ISDOC service"),
        ("src.utils.config", "Configuration"),
        ("src.utils.notifications", "Email notifications"),
        ("src.utils.monitoring", "System monitoring"),
    ]

    success = True
    for module, description in imports:
        try:
            __import__(module)
            print(f"✅ {module:40} - {description}")
        except ImportError as e:
            print(f"❌ {module:40} - FAILED: {e}")
            success = False

    return success


def test_basic_functionality():
    """Test basic functionality."""
    print_header("Basic Functionality Tests")

    try:
        # Test FastAPI app creation
        from fastapi import FastAPI
        app = FastAPI()
        print("✅ FastAPI app creation")

        # Test Pydantic model
        from pydantic import BaseModel
        class TestModel(BaseModel):
            name: str
            value: int

        test = TestModel(name="test", value=42)
        print("✅ Pydantic model validation")

        # Test PDF libraries
        import pdfplumber
        import PyPDF2
        print("✅ PDF libraries accessible")

        # Test XML processing
        from lxml import etree
        root = etree.Element("root")
        print("✅ XML processing")

        return True

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  SUPPLIER INVOICE LOADER - Installation Verification".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")

    results = []

    # Run all tests
    results.append(("Python Version", test_python_version()))
    results.append(("Core Libraries", test_core_imports()))
    results.append(("Dev Tools", test_dev_imports()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Project Imports", test_project_imports()))
    results.append(("Basic Functionality", test_basic_functionality()))

    # Summary
    print_header("VERIFICATION SUMMARY")

    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Installation verified successfully!")
        print("=" * 60)
        return 0
    else:
        print("⚠️  SOME TESTS FAILED - Review errors above")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())