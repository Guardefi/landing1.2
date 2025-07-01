#!/usr/bin/env python3
"""
Scorpius Enterprise Platform Documentation Builder

This script builds the MkDocs documentation site and prepares it for deployment.
It handles copying the main documentation files into the docs structure and
builds the complete documentation site.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def setup_docs_structure():
    """Copy main documentation files to docs directory structure."""
    print("📋 Setting up documentation structure...")
    
    # Create base directory
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Copy main documentation files
    main_docs = {
        "ENTERPRISE_README.md": "docs/enterprise-features.md",
        "ARCHITECTURE.md": "docs/architecture/overview.md", 
        "SECURITY.md": "docs/security/model.md",
        "API.md": "docs/api/authentication.md",
        "DEPLOY_PRIVATE.md": "docs/deployment/private-cloud.md",
        "THREAT_MODEL.md": "docs/security/threat-model.md",
        "RUNBOOK.md": "docs/operations/runbook.md"
    }
    
    for src, dst in main_docs.items():
        if os.path.exists(src):
            # Create target directory
            target_dir = Path(dst).parent
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(src, dst)
            print(f"  ✅ Copied {src} → {dst}")
        else:
            print(f"  ⚠️  Warning: {src} not found")
    
    # Create placeholder files for missing sections
    placeholder_files = [
        "docs/getting-started/quick-start.md",
        "docs/getting-started/installation.md", 
        "docs/getting-started/configuration.md",
        "docs/getting-started/first-steps.md",
        "docs/architecture/components.md",
        "docs/architecture/data-flow.md",
        "docs/architecture/scalability.md",
        "docs/architecture/security.md",
        "docs/api/wallet-guard.md",
        "docs/api/usage-metering.md",
        "docs/api/audit-trail.md",
        "docs/api/reporting.md",
        "docs/api/error-handling.md",
        "docs/api/sdks.md",
        "docs/security/compliance.md",
        "docs/security/best-practices.md", 
        "docs/security/incident-response.md",
        "docs/deployment/aws.md",
        "docs/deployment/azure.md",
        "docs/deployment/gcp.md",
        "docs/deployment/kubernetes.md",
        "docs/deployment/air-gap.md",
        "docs/operations/monitoring.md",
        "docs/operations/troubleshooting.md",
        "docs/operations/maintenance.md",
        "docs/operations/backup-recovery.md",
        "docs/operations/performance.md",
        "docs/compliance/sox.md",
        "docs/compliance/gdpr.md",
        "docs/compliance/hipaa.md",
        "docs/compliance/pci.md",
        "docs/compliance/audit.md",
        "docs/integration/webhooks.md",
        "docs/integration/sso.md",
        "docs/integration/third-party.md",
        "docs/integration/custom.md",
        "docs/support/faq.md",
        "docs/support/troubleshooting.md",
        "docs/support/contact.md",
        "docs/support/training.md",
        "docs/support/community.md",
        "docs/pricing.md",
        "docs/contact.md"
    ]
    
    for placeholder in placeholder_files:
        file_path = Path(placeholder)
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w') as f:
                title = file_path.stem.replace('-', ' ').title()
                f.write(f"# {title}\n\n")
                f.write("!!! info \"Coming Soon\"\n")
                f.write("    This section is under development. Please check back soon for updates.\n\n")
                f.write("For immediate assistance, please contact our enterprise support team:\n\n")
                f.write("- **Email**: [enterprise-support@scorpius.com](mailto:enterprise-support@scorpius.com)\n")
                f.write("- **Phone**: +1-800-SCORPIUS-ENT\n")
                f.write("- **Chat**: Available 24/7 in the platform dashboard\n")
            print(f"  📝 Created placeholder: {placeholder}")

def install_dependencies():
    """Install MkDocs and required dependencies."""
    print("📦 Installing documentation dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "docs-requirements.txt"
        ], check=True)
        print("  ✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to install dependencies: {e}")
        return False
    return True

def build_docs():
    """Build the MkDocs site."""
    print("🏗️  Building documentation site...")
    try:
        subprocess.run(["mkdocs", "build", "--clean"], check=True)
        print("  ✅ Documentation built successfully")
        print("  📁 Output directory: site/")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to build documentation: {e}")
        return False

def serve_docs():
    """Serve the documentation locally for development."""
    print("🌐 Starting local documentation server...")
    try:
        subprocess.run(["mkdocs", "serve", "--dev-addr", "127.0.0.1:8080"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Failed to serve documentation: {e}")
        return False

def main():
    """Main function to build documentation."""
    print("🚀 Scorpius Enterprise Platform - Documentation Builder")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("mkdocs.yml"):
        print("❌ Error: mkdocs.yml not found. Please run from the project root directory.")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "build"
    
    # Setup documentation structure
    setup_docs_structure()
    
    if command == "install":
        # Just install dependencies
        install_dependencies()
    elif command == "serve":
        # Install dependencies and serve
        if install_dependencies():
            serve_docs()
    elif command == "build":
        # Install dependencies and build
        if install_dependencies():
            if build_docs():
                print("\n🎉 Documentation build completed successfully!")
                print("📖 Open site/index.html in your browser to view the documentation")
            else:
                print("\n❌ Documentation build failed")
                sys.exit(1)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: install, build, serve")
        sys.exit(1)

if __name__ == "__main__":
    main()
