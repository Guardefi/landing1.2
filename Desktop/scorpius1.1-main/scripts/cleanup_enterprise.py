#!/usr/bin/env python3
"""
Scorpius Enterprise Cleanup Script
This script performs the actual cleanup operations to organize the project structure.
"""

import os
import shutil
from pathlib import Path

def create_directory_if_not_exists(path):
    """Create directory if it doesn't exist."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return True

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

def write_file_safely(file_path, content):
    """Write content to file safely."""
    try:
        create_directory_if_not_exists(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created: {file_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create {file_path}: {e}")
        return False

def main():
    """Main cleanup function."""
    print("🚀 Scorpius Enterprise Project Cleanup")
    print("=" * 50)
    
    # Create enterprise directory structure
    print("\n🏗️  Creating enterprise directory structure...")
    
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
    
    for dir_path in enterprise_dirs:
        if create_directory_if_not_exists(dir_path):
            print(f"✓ Created: {dir_path}")
    
    # Files to remove (legacy/duplicate)
    print("\n📁 Removing legacy/duplicate files...")
    
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
        "package-lock.json",
        "requirements-dev.txt",
        "pyproject.toml"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            remove_file_safely(file_path)
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Files to move to appropriate directories
    print("\n📦 Moving files to appropriate directories...")
    
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
        
        # IDE/Editor files -> .vscode/
        "Scorpius-Vulnerability-Scanner.code-workspace": ".vscode/",
    }
    
    for src, dst_dir in files_to_move.items():
        if os.path.exists(src):
            dst = os.path.join(dst_dir, os.path.basename(src))
            move_file_safely(src, dst)
        else:
            print(f"⚠️  File not found: {src}")
    
    # Organize artifacts
    print("\n📊 Organizing artifacts...")
    
    # Move report files from docs/ to artifacts/reports/ if they exist
    report_files = [
        "COMPLETION_SUMMARY.md",
        "BYTECODE_TESTS_SUMMARY.md",
        "BACKEND_COVERAGE_REPORT.md"
    ]
    
    for report_file in report_files:
        src = os.path.join("docs", report_file)
        dst = os.path.join("artifacts/reports", report_file)
        if os.path.exists(src):
            move_file_safely(src, dst)
    
    # Move test files to artifacts/test-results/ if they exist
    test_files = [
        "test_runner.py",
        "test_enterprise_command_router.py", 
        "test_comprehensive.py",
        "test_backend_functional.py"
    ]
    
    for test_file in test_files:
        src = os.path.join("tests", test_file)
        dst = os.path.join("artifacts/test-results", test_file)
        if os.path.exists(src):
            move_file_safely(src, dst)
    
    # Create enterprise configuration templates
    print("\n⚙️  Creating enterprise configuration templates...")
    
    # Create environment configuration template
    env_config = """# Environment Configuration Template
# Copy this file to config/environments/ for each environment

[development]
debug = true
log_level = DEBUG
database_url = "postgresql://user:pass@localhost:5432/scorpius_dev"

[staging]
debug = false
log_level = INFO
database_url = "postgresql://user:pass@staging-db:5432/scorpius_staging"

[production]
debug = false
log_level = WARNING
database_url = "postgresql://user:pass@prod-db:5432/scorpius_prod"
"""
    
    write_file_safely("config/environments/config.template.toml", env_config)
    
    # Create secrets template
    secrets_template = """# Secrets Configuration Template
# Copy this file to config/secrets/ and update with actual values
# NEVER commit actual secrets to version control

[database]
username = "your_db_username"
password = "your_db_password"

[api_keys]
openai_api_key = "your_openai_key"
etherscan_api_key = "your_etherscan_key"

[security]
jwt_secret = "your_jwt_secret"
encryption_key = "your_encryption_key"
"""
    
    write_file_safely("config/secrets/secrets.template.toml", secrets_template)
    
    # Create .gitignore for secrets
    secrets_gitignore = """# Ignore actual secret files
*.toml
!*.template.toml
.env
*.key
*.pem
*.p12
"""
    
    write_file_safely("config/secrets/.gitignore", secrets_gitignore)
    
    # Create enterprise README
    enterprise_readme = """# Scorpius Enterprise

## Overview
This is the enterprise-ready version of the Scorpius project, featuring:
* Microservices architecture
* Comprehensive monitoring and observability
* Security-first design
* Compliance-ready documentation
* Scalable deployment strategies

## Quick Start

### Prerequisites
* Docker and Docker Compose
* Python 3.9+
* Node.js 16+
* Kubernetes cluster (for production)

### Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd Scorpius-Enterprise-master

# Install dependencies
pip install -r config/requirements-dev.txt

# Start development environment
docker-compose -f docker/docker-compose.dev.yml up -d

# Run tests
pytest tests/

# Start the application
python scripts/start.py
```

### Production Deployment
```bash
# Deploy to Kubernetes
kubectl apply -f infrastructure/kubernetes/

# Or use Helm
helm install scorpius deploy/helm/
```

## Documentation
* [Architecture](docs/architecture/)
* [API Reference](docs/api/)
* [Deployment Guide](docs/deployment/)
* [Security](docs/security/)
* [Compliance](docs/compliance/)

## Support
For enterprise support, contact: enterprise-support@scorpius.com
"""
    
    write_file_safely("README-ENTERPRISE.md", enterprise_readme)
    
    print("\n🎉 Cleanup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Review the new structure")
    print("2. Update any hardcoded paths in your code")
    print("3. Update documentation references")
    print("4. Test the build and deployment processes")
    print("5. Update CI/CD pipelines to reflect new paths")

if __name__ == "__main__":
    main() 