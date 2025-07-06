#!/usr/bin/env python3
"""
Fix Documentation Links Script
This script fixes broken documentation links after the cleanup.
"""

import os
import re
import glob
from pathlib import Path

def find_markdown_files(directory="."):
    """Find all markdown files in the directory."""
    markdown_files = []
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'venv', 'env'}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.md'):
                markdown_files.append(os.path.join(root, file))
    return markdown_files

def fix_documentation_links():
    """Fix broken documentation links."""
    print("🔧 Fixing documentation links...")
    
    markdown_files = find_markdown_files()
    
    # Common link patterns that need fixing
    link_fixes = {
        # Old paths to new paths
        r'\.\./docs/ARCHITECTURE\.md': 'docs/architecture/',
        r'\.\./docs/SECURITY\.md': 'docs/security/',
        r'\.\./docs/API\.md': 'docs/api/',
        r'\.\./docs/': 'docs/',
        r'\.\./airgap/README\.md': 'deploy/airgap/README.md',
        r'\.\./\.\./docs/': 'docs/',
        r'\.\./\.\./\.\./docs/': 'docs/',
        r'\.\./\.\./\.\./\.\./docs/': 'docs/',
        
        # Configuration file paths
        r'requirements\.txt': 'config/requirements-dev.txt',
        r'requirements-dev\.txt': 'config/requirements-dev.txt',
        r'pyproject\.toml': 'config/pyproject.toml',
        r'pytest\.ini': 'config/pytest.ini',
        
        # Docker file paths
        r'docker-compose\.yml': 'docker/docker-compose.yml',
        r'docker-compose\.dev\.yml': 'docker/docker-compose.dev.yml',
        r'docker-compose\.secure\.yml': 'docker/docker-compose.secure.yml',
        
        # Script paths
        r'\.\./scripts/': 'scripts/',
        r'\.\./\.\./scripts/': 'scripts/',
        
        # Test paths
        r'\.\./tests/': 'tests/',
        r'\.\./\.\./tests/': 'tests/',
        
        # Infrastructure paths
        r'\.\./infrastructure/': 'infrastructure/',
        r'\.\./\.\./infrastructure/': 'infrastructure/',
        
        # Backend paths
        r'\.\./backend/': 'backend/',
        r'\.\./\.\./backend/': 'backend/',
    }
    
    files_updated = 0
    links_fixed = 0
    
    for file_path in markdown_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_updated = False
            
            # Fix markdown links
            for old_pattern, new_path in link_fixes.items():
                # Find markdown links that match the pattern
                pattern = rf'\[([^\]]+)\]\(({old_pattern})\)'
                matches = re.findall(pattern, content)
                
                for link_text, link_url in matches:
                    # Determine the correct new path based on file location
                    file_dir = os.path.dirname(file_path)
                    relative_path = os.path.relpath(new_path, file_dir)
                    
                    # Replace the link
                    old_link = f'[{link_text}]({link_url})'
                    new_link = f'[{link_text}]({relative_path})'
                    content = content.replace(old_link, new_link)
                    file_updated = True
                    links_fixed += 1
            
            # Fix code block references
            for old_pattern, new_path in link_fixes.items():
                # Find code blocks that reference old paths
                pattern = rf'```(?:bash|shell|yaml|yml|json|toml|ini)\n.*?{old_pattern}.*?\n```'
                matches = re.findall(pattern, content, re.DOTALL)
                
                for match in matches:
                    # Replace the old path with new path
                    new_content = re.sub(old_pattern, new_path, match)
                    content = content.replace(match, new_content)
                    file_updated = True
                    links_fixed += 1
            
            # Fix inline code references
            for old_pattern, new_path in link_fixes.items():
                # Find inline code that references old paths
                pattern = rf'`({old_pattern})`'
                matches = re.findall(pattern, content)
                
                for match in matches:
                    # Replace the old path with new path
                    content = content.replace(f'`{match}`', f'`{new_path}`')
                    file_updated = True
                    links_fixed += 1
            
            # Write back if changes were made
            if file_updated:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_updated += 1
                print(f"✓ Updated: {file_path}")
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"  Files updated: {files_updated}")
    print(f"  Links fixed: {links_fixed}")
    
    return files_updated, links_fixed

def create_documentation_index():
    """Create a documentation index file."""
    print("\n📚 Creating documentation index...")
    
    index_content = """# Scorpius Enterprise Documentation Index

## 📖 Overview
This index provides quick access to all documentation in the Scorpius Enterprise project.

## 🏗️ Architecture & Design
- [Project Structure](docs/enterprise/PROJECT_STRUCTURE.md) - Complete project organization guide
- [Architecture Overview](docs/architecture/) - System architecture documentation
- [API Reference](docs/api/) - API documentation and specifications
- [Deployment Guide](docs/deployment/) - Deployment strategies and configurations

## 🔒 Security & Compliance
- [Security Documentation](docs/security/) - Security policies and procedures
- [Compliance Guide](docs/compliance/) - Compliance and audit documentation
- [Enterprise Security](docs/enterprise/) - Enterprise-specific security features

## 🚀 Getting Started
- [Quick Start Guide](docs/getting-started/) - Quick setup and first steps
- [Installation Guide](docs/getting-started/installation.md) - Detailed installation instructions
- [Configuration Guide](docs/getting-started/configuration.md) - Configuration management

## 🛠️ Development
- [Developer Guide](docs/getting-started/development.md) - Development setup and workflows
- [Testing Guide](docs/getting-started/testing.md) - Testing strategies and procedures
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute to the project

## 📊 Operations
- [Operations Guide](docs/operations/) - Day-to-day operations
- [Monitoring Guide](docs/operations/monitoring.md) - Monitoring and observability
- [Troubleshooting Guide](docs/operations/troubleshooting.md) - Common issues and solutions

## 🔧 Integration
- [Integration Guide](docs/integration/) - Third-party integrations
- [API Integration](docs/integration/api.md) - API integration examples
- [Webhook Setup](docs/integration/webhooks.md) - Webhook configuration

## 📋 Enterprise Features
- [Enterprise Overview](docs/enterprise/) - Enterprise-specific features
- [Cleanup Summary](docs/enterprise/CLEANUP_SUMMARY.md) - Project cleanup documentation
- [Quick Reference](docs/enterprise/QUICK_REFERENCE.md) - Developer quick reference
- [Next Steps](docs/enterprise/NEXT_STEPS_REPORT.md) - Post-cleanup next steps

## 🚀 Deployment
- [Deployment Overview](docs/deployment/) - Deployment strategies
- [Kubernetes Deployment](docs/deployment/kubernetes.md) - K8s deployment guide
- [Docker Deployment](docs/deployment/docker.md) - Docker deployment guide
- [AWS Deployment](docs/deployment/aws.md) - AWS deployment guide

## 📞 Support
- [Support Guide](docs/support/) - Getting help and support
- [FAQ](docs/support/faq.md) - Frequently asked questions
- [Contact Information](docs/support/contact.md) - How to contact the team

## 🔄 Maintenance
- [Maintenance Guide](docs/operations/maintenance.md) - System maintenance procedures
- [Backup & Recovery](docs/operations/backup.md) - Backup and recovery procedures
- [Updates & Upgrades](docs/operations/updates.md) - System updates and upgrades

## 📈 Performance
- [Performance Guide](docs/operations/performance.md) - Performance optimization
- [Scaling Guide](docs/operations/scaling.md) - Scaling strategies
- [Benchmarking](docs/operations/benchmarking.md) - Performance benchmarking

## 🔍 Troubleshooting
- [Troubleshooting Guide](docs/operations/troubleshooting.md) - Common issues and solutions
- [Debug Guide](docs/operations/debugging.md) - Debugging procedures
- [Log Analysis](docs/operations/logs.md) - Log analysis and interpretation

---
*Last updated: $(date)*
*Generated by: fix_documentation_links.py*
"""
    
    with open('docs/README.md', 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print("✓ Created: docs/README.md")

def main():
    """Main function."""
    print("🔧 Scorpius Enterprise - Documentation Link Fixer")
    print("=" * 50)
    
    # Fix broken links
    files_updated, links_fixed = fix_documentation_links()
    
    # Create documentation index
    create_documentation_index()
    
    print("\n🎉 Documentation link fixing completed!")
    print(f"\n📊 Results:")
    print(f"  Files updated: {files_updated}")
    print(f"  Links fixed: {links_fixed}")
    print(f"  Documentation index created: docs/README.md")
    
    print("\n📋 Next steps:")
    print("1. Review the updated documentation files")
    print("2. Test any links that were fixed")
    print("3. Update any remaining hardcoded paths")
    print("4. Verify that all documentation is accessible")

if __name__ == "__main__":
    main() 