#!/usr/bin/env python3
"""
Split large project_file_access.json into smaller parts for efficient loading.

Usage:
    python split_project_access.py

Output:
    - project_file_access_manifest.json (main manifest)
    - project_file_access_root.json
    - project_file_access_docs.json
    - project_file_access_deploy.json
    - project_file_access_deployment_package.json
    - project_file_access_extractors.json
    - project_file_access_tests.json
    - project_file_access_idea.json
"""

import json
from pathlib import Path
from typing import Dict

# Base URL for GitHub raw content
BASE_URL = "https://raw.githubusercontent.com/rauschiccsk/supplier_invoice_loader/v2.0-multi-customer"


def split_project_access():
    """Split project_file_access.json into logical parts."""

    # Load the complete JSON file
    input_file = Path("project_file_access.json")
    if not input_file.exists():
        print(f"❌ ERROR: {input_file} not found!")
        return

    print(f"📂 Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        all_files = json.load(f)

    print(f"✅ Loaded {len(all_files)} files")

    # Initialize parts
    parts = {
        'root': {},
        'docs': {},
        'deploy': {},
        'deployment_package': {},
        'extractors': {},
        'tests': {},
        'idea': {}
    }

    # Categorize files
    for file_path, url in all_files.items():
        # Normalize path
        path = file_path.lstrip('./')

        # Categorize based on directory
        if path.startswith('docs/'):
            parts['docs'][file_path] = url
        elif path.startswith('deployment_package/'):
            parts['deployment_package'][file_path] = url
        elif path.startswith('deploy/'):
            parts['deploy'][file_path] = url
        elif path.startswith('extractors/'):
            parts['extractors'][file_path] = url
        elif path.startswith('tests/'):
            parts['tests'][file_path] = url
        elif path.startswith('.idea/'):
            parts['idea'][file_path] = url
        else:
            # Root level files
            parts['root'][file_path] = url

    # Print statistics
    print("\n📊 Categorization statistics:")
    for part_name, files in parts.items():
        print(f"   {part_name:25s}: {len(files):3d} files")

    # Save individual parts
    print("\n💾 Saving split files...")
    for part_name, files in parts.items():
        if files:  # Only save non-empty parts
            output_file = f"project_file_access_{part_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(files, f, indent=2, ensure_ascii=False)
            print(f"   ✅ {output_file} ({len(files)} files)")

    # Create manifest
    manifest = {
        "manifest_version": "1.0",
        "description": "Split project file access manifest for efficient loading",
        "base_url": BASE_URL,
        "parts": {}
    }

    for part_name in parts.keys():
        if parts[part_name]:  # Only include non-empty parts
            manifest["parts"][part_name] = f"{BASE_URL}/project_file_access_{part_name}.json"

    # Save manifest
    manifest_file = "project_file_access_manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {manifest_file} created")
    print(f"\n🎉 Split complete! Upload these files to GitHub:")
    print(f"   - {manifest_file}")
    for part_name in parts.keys():
        if parts[part_name]:
            print(f"   - project_file_access_{part_name}.json")

    print(f"\n📝 Next steps:")
    print(f"   1. git add project_file_access_*.json")
    print(f"   2. git commit -m 'Split project_file_access.json into smaller parts'")
    print(f"   3. git push origin v2.0-multi-customer")
    print(f"   4. Use manifest URL in Claude: {BASE_URL}/project_file_access_manifest.json")


if __name__ == "__main__":
    split_project_access()