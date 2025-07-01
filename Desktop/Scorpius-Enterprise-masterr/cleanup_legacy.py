#!/usr/bin/env python3
"""
Legacy File Cleanup Script for Scorpius Enterprise
This script helps clean up old/legacy files and organize the project structure.
"""

import os
import shutil
import glob
from pathlib import Path

def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)

def move_file_safely(src, dst):
    """Move file safely, creating directories if needed."""
    try:
        create_directory_if_not_exists(os.path.dirname(dst))
        shutil.move(src, dst)
        print(f"✓ Moved: {src} -> {dst}")
        return True
    except Exception as e:
        print(f"✗ Failed to move {src}: {e}")
        return False

def remove_file_safely(file_path):
    """Remove file safely."""
    try:
        os.remove(file_path)
        print(f"✓ Removed: {file_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to remove {file_path}: {e}")
        return False

def cleanup_legacy_files():
    """Clean up legacy and duplicate files."""
    
    # Files to remove (legacy/duplicate)
    files_to_remove = [
        "unified_gateway_backup.py",
        "orchestrator_new_backup.py",
        "README-new.md",
        "README-DOCKER.md",
        "test_high_impact_coverage.py",
        "test_final_coverage_boost_fixed.py",
        "test_final_coverage_boost.py",
        "test_backend_coverage_boost.py",
        "test_backend_coverage.py",
        "enhanced_coverage_tests.py",
        "comprehensive_bytecode_tests.py",
        "final_test_validation.py",
        "final_coverage_analysis.py",
        "coverage_summary.py",
        "setup_tests.py",
        "run_bytecode_tests.py",
        "fix-npm.ps1",
        "start-services.sh",
        "start-services.ps1",
        "start-everything.ps1",
        "start-all.ps1",
        "package-lock.json",  # Keep only the one in config/
        "requirements-dev.txt",  # Keep only the one in config/
        "pyproject.toml",  # Keep only the one in config/
    ]
    
    # Files to move to appropriate directories
    files_to_move = {
        # Test files -> tests/
        "test_runner.py": "tests/",
        "test_enterprise_command_router.py": "tests/",
        "test_comprehensive.py": "tests/",
        "test_backend_functional.py": "tests/",
        
        # Docker files -> docker/
        "docker-compose.yml": "docker/",
        "docker-compose.secure.yml": "docker/",
        "docker-compose.dev.yml": "docker/",
        
        # Documentation -> docs/
        "COMPLETION_SUMMARY.md": "docs/",
        "BYTECODE_TESTS_SUMMARY.md": "docs/",
        "BACKEND_COVERAGE_REPORT.md": "docs/",
        
        # Configuration -> config/
        "pytest.ini": "config/",
        ".coveragerc": "config/",
        
        # IDE/Editor files -> .vscode/ (create if needed)
        "Scorpius-Vulnerability-Scanner.code-workspace": ".vscode/",
    }
    
    print("🧹 Starting legacy file cleanup...")
    
    # Remove legacy files
    print("\n📁 Removing legacy/duplicate files:")
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            remove_file_safely(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Move files to appropriate directories
    print("\n📦 Moving files to appropriate directories:")
    for src, dst_dir in files_to_move.items():
        if os.path.exists(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            move_file_safely(src, dst)
        else:
            print(f"⚠️  File not found: {src}")
    
    print("\n✅ Legacy file cleanup completed!")

def organize_artifacts():
    """Organize artifacts and reports."""
    
    # Create organized structure for artifacts
    artifacts_structure = {
        "reports": [
            "COMPLETION_SUMMARY.md",
            "BYTECODE_TESTS_SUMMARY.md", 
            "BACKEND_COVERAGE_REPORT.md"
        ],
        "test-results": [
            "test_runner.py",
            "test_enterprise_command_router.py",
            "test_comprehensive.py",
            "test_backend_functional.py"
        ]
    }
    
    print("\n📊 Organizing artifacts...")
    
    # Move files from docs/ to artifacts/reports/ if they exist
    for report_file in artifacts_structure["reports"]:
        src = os.path.join("docs", report_file)
        dst = os.path.join("artifacts", "reports", report_file)
        if os.path.exists(src):
            move_file_safely(src, dst)
    
    # Move test files to artifacts/test-results/ if they exist
    for test_file in artifacts_structure["test-results"]:
        src = os.path.join("tests", test_file)
        dst = os.path.join("artifacts", "test-results", test_file)
        if os.path.exists(src):
            move_file_safely(src, dst)

def create_enterprise_structure():
    """Create enterprise-level directory structure."""
    
    enterprise_dirs = [
        "docs/enterprise",
        "docs/api",
        "docs/deployment", 
        "docs/security",
        "docs/compliance",
        "config/environments",
        "config/secrets",
        "scripts/deployment",
        "scripts/maintenance",
        "scripts/security",
        "tools/development",
        "tools/operations",
        "tools/security",
        "artifacts/logs",
        "artifacts/backups",
        "artifacts/reports",
        "artifacts/test-results",
        "monitoring/dashboards",
        "monitoring/alerts",
        "monitoring/logs",
        ".vscode",
        ".github/workflows",
        ".github/ISSUE_TEMPLATE",
        ".github/PULL_REQUEST_TEMPLATE"
    ]
    
    print("\n🏗️  Creating enterprise directory structure:")
    for dir_path in enterprise_dirs:
        create_directory_if_not_exists(dir_path)
        print(f"✓ Created: {dir_path}")

def main():
    """Main cleanup function."""
    print("🚀 Scorpius Enterprise Project Cleanup")
    print("=" * 50)
    
    # Create enterprise structure first
    create_enterprise_structure()
    
    # Clean up legacy files
    cleanup_legacy_files()
    
    # Organize artifacts
    organize_artifacts()
    
    print("\n🎉 Cleanup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the new structure")
    print("2. Update any hardcoded paths in your code")
    print("3. Update documentation references")
    print("4. Test the build and deployment processes")

if __name__ == "__main__":
    main() 