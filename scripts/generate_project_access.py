"""
Generate Project File Access Manifest
======================================

Vygeneruje unified JSON manifest pre supplier-invoice-loader projekt.
Používa sa po každom push do GitHub pre cache-busting.

Použitie:
    python scripts/generate_project_access.py

Output:
    supplier-invoice-loader_project_file_access.json
"""

import os
import json
from pathlib import Path
from datetime import datetime
import subprocess


def get_git_commit_sha():
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"


def get_git_short_sha():
    """Get short git commit SHA (12 chars)."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--short=12', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"


def categorize_file(file_path: Path) -> str:
    """Determine file category."""
    path_str = str(file_path).replace('\\', '/')

    if 'docs/' in path_str:
        return 'documentation'
    elif 'src/extractors/' in path_str:
        return 'extractors'
    elif 'src/business/' in path_str:
        return 'business_logic'
    elif 'src/database/' in path_str:
        return 'database'
    elif 'src/api/' in path_str:
        return 'api'
    elif 'src/utils/' in path_str:
        return 'utilities'
    elif 'src/' in path_str:
        return 'python_sources'
    elif 'config/' in path_str:
        return 'configuration'
    elif 'database/schemas/' in path_str:
        return 'database_schemas'
    elif 'tests/' in path_str:
        return 'tests'
    elif 'scripts/' in path_str:
        return 'scripts'
    elif 'deploy/' in path_str:
        return 'deployment'
    elif 'n8n-workflows/' in path_str:
        return 'n8n_workflows'
    elif file_path.name == 'main.py':
        return 'root_modules'
    else:
        return 'configuration'


def generate_manifest(project_root: Path):
    """Generate project file access manifest."""

    commit_sha = get_git_commit_sha()
    short_sha = get_git_short_sha()

    # GitHub repository info
    repo_url = "https://github.com/rauschiccsk/supplier-invoice-loader"
    base_url = f"{repo_url.replace('github.com', 'raw.githubusercontent.com')}/{commit_sha}"

    # Scan files
    files = []
    ignore_patterns = [
        '.git', '__pycache__', '.pytest_cache', 'venv', '.venv',
        '.idea', '.vscode', '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll',
        'logs', '*.log', '.env', 'data', '*.db', '*.sqlite',
        'deployment_package', 'node_modules'
    ]

    def should_ignore(path: Path) -> bool:
        path_str = str(path)
        for pattern in ignore_patterns:
            if pattern.startswith('*'):
                if path_str.endswith(pattern[1:]):
                    return True
            else:
                if pattern in path_str:
                    return True
        return False

    for root, dirs, filenames in os.walk(project_root):
        dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]

        for filename in filenames:
            file_path = Path(root) / filename

            if should_ignore(file_path):
                continue

            try:
                rel_path = file_path.relative_to(project_root)
                rel_path_str = str(rel_path).replace('\\', '/')
                stat = file_path.stat()

                files.append({
                    "path": rel_path_str,
                    "raw_url": f"{base_url}/{rel_path_str}?v={short_sha}",
                    "size": stat.st_size,
                    "extension": file_path.suffix,
                    "name": file_path.name,
                    "category": categorize_file(rel_path),
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                })
            except Exception as e:
                print(f"Warning: Skipped {file_path}: {e}")

    # Sort by category then path
    files.sort(key=lambda x: (x['category'], x['path']))

    # Category statistics
    category_stats = {}
    for file in files:
        cat = file['category']
        category_stats[cat] = category_stats.get(cat, 0) + 1

    # Build manifest
    manifest = {
        "project_name": "supplier-invoice-loader",
        "description": "Supplier Invoice Loader v2.0 - Automated invoice processing (refactored)",
        "repository": repo_url,
        "generated_at": datetime.now().isoformat(),
        "commit_sha": commit_sha,
        "cache_buster": commit_sha,
        "cache_version": short_sha,
        "base_url": base_url,
        "quick_access": {
            "init_files": [
                {
                    "name": "docs/INIT_PROMPT_NEW_CHAT.md",
                    "description": "Init prompt for new session",
                    "url": f"{base_url}/docs/INIT_PROMPT_NEW_CHAT.md?v={short_sha}"
                },
                {
                    "name": "docs/SESSION_NOTES.md",
                    "description": "Unified session history",
                    "url": f"{base_url}/docs/SESSION_NOTES.md?v={short_sha}"
                }
            ],
            "core_modules": [
                {
                    "name": "main.py",
                    "description": "Application entry point",
                    "url": f"{base_url}/main.py?v={short_sha}"
                },
                {
                    "name": "src/database/database.py",
                    "description": "Database client",
                    "url": f"{base_url}/src/database/database.py?v={short_sha}"
                },
                {
                    "name": "src/extractors/ls_extractor.py",
                    "description": "L&Š PDF extractor",
                    "url": f"{base_url}/src/extractors/ls_extractor.py?v={short_sha}"
                }
            ],
            "configuration": [
                {
                    "name": "config/config.yaml",
                    "description": "Main configuration",
                    "url": f"{base_url}/config/config.yaml?v={short_sha}"
                }
            ]
        },
        "categories": sorted(list(category_stats.keys())),
        "category_descriptions": {
            "root_modules": "Root-level entry points",
            "documentation": "Project documentation",
            "python_sources": "Python source code",
            "extractors": "PDF extraction modules",
            "business_logic": "Business logic services",
            "database": "Database operations",
            "api": "FastAPI routes and models",
            "utilities": "Utility modules",
            "configuration": "Configuration files",
            "database_schemas": "Database schemas",
            "tests": "Test suite",
            "scripts": "Utility scripts",
            "deployment": "Deployment tools",
            "n8n_workflows": "n8n workflows"
        },
        "statistics": {
            "total_files": len(files),
            "by_category": category_stats,
            "generated_by": "scripts/generate_project_access.py"
        },
        "files": files,
        "usage_instructions": {
            "step_1": "Load INIT_PROMPT_NEW_CHAT.md for session start",
            "step_2": "Load SESSION_NOTES.md for history",
            "step_3": "Load this manifest for all project files",
            "step_4": "Access files using raw_url with cache version",
            "note": "Regenerate after each push for fresh cache"
        }
    }

    # Save manifest
    output_file = project_root / "docs\project_file_access.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"✅ Manifest generated: {output_file}")
    print(f"   Total files: {len(files)}")
    print(f"   Commit: {short_sha}")
    print()
    print("📋 Category breakdown:")
    for cat, count in sorted(category_stats.items()):
        print(f"   {cat}: {count} files")


if __name__ == "__main__":
    project_root = Path(__file__).parent.parent
    print(f"🔧 Generating manifest for: {project_root}")
    print()
    generate_manifest(project_root)
