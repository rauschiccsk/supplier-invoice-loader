# -*- coding: utf-8 -*-
"""
Environment Loader - FIXED VERSION
Loads .env file before any other imports
Windows Console compatible - no Unicode characters
"""

import os
import sys
from pathlib import Path
from typing import Optional


def find_env_file() -> Optional[Path]:
    """
    Find .env file in current directory or parent directories

    Returns:
        Path to .env file or None if not found
    """
    current_dir = Path.cwd()

    # Check current directory first
    env_path = current_dir / '.env'
    if env_path.exists():
        return env_path

    # Check parent directories (up to 3 levels)
    for _ in range(3):
        current_dir = current_dir.parent
        env_path = current_dir / '.env'
        if env_path.exists():
            return env_path

    return None


def load_environment() -> bool:
    """
    Load environment variables from .env file

    Returns:
        True if .env file was loaded, False otherwise
    """
    try:
        # Find .env file
        env_path = find_env_file()

        if not env_path:
            print("[INFO] No .env file found, using system environment variables")
            return False

        # Read .env file
        env_vars = {}
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse key=value
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Set environment variable
                    os.environ[key] = value
                    env_vars[key] = value

        # Success message
        print(f"[OK] Loaded environment from: {env_path}")
        if env_vars:
            print(f"  Environment variables loaded: {', '.join(env_vars.keys())}")

        return True

    except Exception as e:
        print(f"[WARNING] Error loading .env file: {e}")
        print("  Continuing with system environment variables...")
        return False


# Auto-load on import
if __name__ != "__main__":
    load_environment()