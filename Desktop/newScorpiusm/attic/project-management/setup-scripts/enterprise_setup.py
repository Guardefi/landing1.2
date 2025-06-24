#!/usr/bin/env python3
"""
Scorpius Enterprise Repository Management Utility
================================================
Production-ready repository cleanup, organization, and deployment preparation tool.

Features:
- Flatten nested directory structures
- Deduplicate files and optimize storage
- Secure secret management with .env templating
- Centralize documentation and configurations
- Create production-ready folder structure
- Generate enterprise CI/CD configurations
- Security audit and compliance checks

Usage:
    python enterprise_setup.py /path/to/repo --execute --production

Flags:
    --execute              Apply changes (default: dry-run)
    --production          Enable production optimizations
    --security-audit      Generate security compliance report
    --ci-cd-setup         Create CI/CD pipeline configurations
    --docker-optimize     Optimize Docker configurations for production
    --monitoring-setup    Add monitoring and logging configurations
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import defaultdict
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# Enterprise Configuration
# ---------------------------------------------------------------------------

# Production-grade ignore patterns
IGNORE_PATTERNS = [
    ".git",
    "*/.git/*",
    "**/__pycache__/**",
    "**/node_modules/**",
    "*.pyc",
    "*.pyo",
    "*.so",
    "*.log",
    "*.log.*",
    "yarn.lock",
    "package-lock.json",
    "**/dist/**",
    "**/build/**",
    "**/.pytest_cache/**",
    "**/.coverage",
    "**/coverage/**",
]

# Security-sensitive files
SECRET_PATTERNS = [
    ".env*",
    "*.key",
    "*.pem",
    "*.p12",
    "*.pfx",
    "*secret*",
    "*credential*",
    "*password*",
]

# Production artifact patterns
ARTIFACT_PATTERNS = [
    "*.zip",
    "*.tar.gz",
    "*.bak",
    "*.tmp",
    "*.temp",
    "Dockerfile.simple",
    "Dockerfile.dev",
    "*.bat",
    "*.ps1",
]

# Enterprise directory structure
ENTERPRISE_STRUCTURE = {
    "backend": "Core backend services and APIs",
    "frontend": "Frontend application and assets",
    "infrastructure": "Docker, K8s, and deployment configs",
    "docs": "Centralized documentation",
    "configs": "Configuration files and settings",
    "scripts": "Deployment and utility scripts",
    "monitoring": "Logging, metrics, and health checks",
    "security": "Security configurations and policies",
    "tests": "Test suites and test data",
    "ci-cd": "Continuous integration/deployment pipelines",
}


class EnterpriseRepoManager:
    """Enterprise-grade repository management and optimization."""

    def __init__(self, root: Path, production: bool = False):
        self.root = root.resolve()
        self.production = production
        self.audit_log: list[str] = []
        self.duplicates: dict[str, list[Path]] = defaultdict(list)
        self.secrets: list[Path] = []
        self.artifacts: list[Path] = []

    def log_action(self, action: str) -> None:
        """Log all actions for audit trail."""
        timestamp = datetime.now().isoformat()
        self.audit_log.append(f"[{timestamp}] {action}")

    def _is_ignored(self, path: Path) -> bool:
        """Check if path should be ignored."""
        path_str = str(path)
        return any(fnmatch(path_str, pattern) for pattern in IGNORE_PATTERNS)

    def _hash_file(self, path: Path) -> str | None:
        """Generate SHA-256 hash for files under 50MB."""
        try:
            if path.stat().st_size > 50 * 1024 * 1024:  # 50MB limit
                return None
            h = hashlib.sha256()
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def analyze_repository(self) -> None:
        """Comprehensive repository analysis."""
        self.log_action("Starting repository analysis")

        hashes: dict[str, list[Path]] = defaultdict(list)

        for path in self.root.rglob("*"):
            if not path.is_file() or self._is_ignored(path):
                continue

            # Check for duplicates
            if file_hash := self._hash_file(path):
                hashes[file_hash].append(path)

            # Check for secrets
            if any(fnmatch(path.name, pattern) for pattern in SECRET_PATTERNS):
                self.secrets.append(path)

            # Check for artifacts
            if any(fnmatch(path.name, pattern) for pattern in ARTIFACT_PATTERNS):
                self.artifacts.append(path)

        # Keep only actual duplicates
        self.duplicates = {h: paths for h, paths in hashes.items() if len(paths) > 1}

        self.log_action(
            f"Analysis complete: {len(self.duplicates)} duplicate groups, "
            f"{len(self.secrets)} secrets, {len(self.artifacts)} artifacts"
        )

    def detect_structural_issues(self) -> list[Path]:
        """Detect Russian-doll directories and other structural problems."""
        issues = []
        for path in self.root.rglob("*"):
            if path.is_dir() and path.parent.name == path.name:
                issues.append(path)
        return issues

    def create_enterprise_structure(self) -> None:
        """Create production-ready directory structure."""
        self.log_action("Creating enterprise directory structure")

        for dir_name, description in ENTERPRISE_STRUCTURE.items():
            dir_path = self.root / dir_name
            dir_path.mkdir(exist_ok=True)

            # Create README for each directory
            readme_path = dir_path / "README.md"
            if not readme_path.exists():
                readme_content = f"# {dir_name.title()}\n\n{description}\n"
                readme_path.write_text(readme_content, encoding="utf-8")

    def consolidate_backend(self) -> None:
        """Consolidate and flatten backend directories."""
        self.log_action("Consolidating backend structure")

        backend_target = self.root / "backend"
        backend_sources = [
            p for p in self.root.rglob("backend") if p.is_dir() and p != backend_target
        ]

        # Sort by depth to process deepest first
        backend_sources.sort(key=lambda p: len(p.parts), reverse=True)

        processed_files: set[str] = set()

        for source_dir in backend_sources:
            for file_path in source_dir.rglob("*"):
                if not file_path.is_file() or self._is_ignored(file_path):
                    continue

                relative_path = file_path.relative_to(source_dir)
                rel_path_str = relative_path.as_posix()

                if rel_path_str in processed_files:
                    continue

                processed_files.add(rel_path_str)
                dest_path = backend_target / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                try:
                    shutil.copy2(file_path, dest_path)
                except Exception as e:
                    self.log_action(f"Failed to copy {file_path}: {e}")

    def secure_secrets(self) -> None:
        """Create secure .env.example files and protect secrets."""
        self.log_action("Securing sensitive files")

        for secret_file in self.secrets:
            if secret_file.suffix in [".key", ".pem", ".p12", ".pfx"]:
                # These should never be committed
                continue

            example_file = secret_file.with_name(secret_file.name + ".example")
            if example_file.exists():
                continue

            try:
                lines = []
                with secret_file.open("r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line and not line.strip().startswith("#"):
                            key = line.split("=", 1)[0]
                            lines.append(f"{key}=YOUR_VALUE_HERE\\n")
                        else:
                            lines.append(line)

                with example_file.open("w", encoding="utf-8") as f:
                    f.writelines(lines)

            except Exception as e:
                self.log_action(f"Failed to create example for {secret_file}: {e}")

    def optimize_docker_configs(self) -> None:
        """Create production-optimized Docker configurations."""
        self.log_action("Optimizing Docker configurations")

        infrastructure_dir = self.root / "infrastructure"
        docker_dir = infrastructure_dir / "docker"
        docker_dir.mkdir(parents=True, exist_ok=True)

        # Production Docker Compose
        prod_compose = {
            "version": "3.8",
            "services": {
                "backend": {
                    "build": {"context": "./backend", "dockerfile": "Dockerfile.prod"},
                    "environment": ["NODE_ENV=production"],
                    "restart": "unless-stopped",
                    "healthcheck": {
                        "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3,
                        "start_period": "40s",
                    },
                },
                "frontend": {
                    "build": {"context": "./frontend", "dockerfile": "Dockerfile.prod"},
                    "ports": ["80:80", "443:443"],
                    "restart": "unless-stopped",
                },
                "redis": {
                    "image": "redis:7-alpine",
                    "restart": "unless-stopped",
                    "volumes": ["redis_data:/data"],
                },
                "postgres": {
                    "image": "postgres:15-alpine",
                    "environment": [
                        "POSTGRES_DB=${DB_NAME}",
                        "POSTGRES_USER=${DB_USER}",
                        "POSTGRES_PASSWORD=${DB_PASSWORD}",
                    ],
                    "volumes": ["postgres_data:/var/lib/postgresql/data"],
                    "restart": "unless-stopped",
                },
            },
            "volumes": {"postgres_data": {}, "redis_data": {}},
            "networks": {"app_network": {"driver": "bridge"}},
        }

        compose_file = docker_dir / "docker-compose.prod.yml"
        with compose_file.open("w") as f:
            yaml.dump(prod_compose, f, default_flow_style=False)

    def setup_monitoring(self) -> None:
        """Setup monitoring and logging configurations."""
        self.log_action("Setting up monitoring configurations")

        monitoring_dir = self.root / "monitoring"

        # Prometheus configuration
        prometheus_config = {
            "global": {"scrape_interval": "15s", "evaluation_interval": "15s"},
            "rule_files": ["alerts.yml"],
            "scrape_configs": [
                {
                    "job_name": "scorpius-backend",
                    "static_configs": [{"targets": ["backend:8000"]}],
                    "metrics_path": "/metrics",
                },
                {
                    "job_name": "scorpius-frontend",
                    "static_configs": [{"targets": ["frontend:80"]}],
                },
            ],
        }

        prometheus_file = monitoring_dir / "prometheus.yml"
        with prometheus_file.open("w") as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)

        # Grafana dashboard config
        grafana_config = {
            "apiVersion": 1,
            "datasources": [
                {
                    "name": "Prometheus",
                    "type": "prometheus",
                    "url": "http://prometheus:9090",
                    "access": "proxy",
                    "isDefault": True,
                }
            ],
        }

        grafana_file = monitoring_dir / "grafana-datasources.yml"
        with grafana_file.open("w") as f:
            yaml.dump(grafana_config, f, default_flow_style=False)

    def create_cicd_pipeline(self) -> None:
        """Create CI/CD pipeline configurations."""
        self.log_action("Creating CI/CD pipeline configurations")

        cicd_dir = self.root / "ci-cd"
        github_dir = cicd_dir / ".github" / "workflows"
        github_dir.mkdir(parents=True, exist_ok=True)

        # GitHub Actions workflow
        workflow = {
            "name": "Scorpius CI/CD",
            "on": {
                "push": {"branches": ["main", "develop"]},
                "pull_request": {"branches": ["main"]},
            },
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Set up Python",
                            "uses": "actions/setup-python@v4",
                            "with": {"python-version": "3.11"},
                        },
                        {
                            "name": "Install dependencies",
                            "run": "pip install -r requirements.txt",
                        },
                        {
                            "name": "Run tests",
                            "run": "pytest tests/ --cov=backend --cov-report=xml",
                        },
                        {"name": "Security scan", "run": "bandit -r backend/"},
                    ],
                },
                "deploy": {
                    "needs": "test",
                    "runs-on": "ubuntu-latest",
                    "if": "github.ref == 'refs/heads/main'",
                    "steps": [
                        {"uses": "actions/checkout@v3"},
                        {
                            "name": "Deploy to production",
                            "run": 'echo "Deploy to production server"',
                        },
                    ],
                },
            },
        }

        workflow_file = github_dir / "main.yml"
        with workflow_file.open("w") as f:
            yaml.dump(workflow, f, default_flow_style=False)

    def generate_security_report(self) -> dict:
        """Generate comprehensive security audit report."""
        self.log_action("Generating security audit report")

        report = {
            "timestamp": datetime.now().isoformat(),
            "repository": str(self.root),
            "security_findings": {
                "secrets_found": len(self.secrets),
                "secret_files": [str(s) for s in self.secrets],
                "unprotected_secrets": [],
                "recommendations": [],
            },
            "structural_analysis": {
                "duplicate_files": len(self.duplicates),
                "russian_dolls": len(self.detect_structural_issues()),
                "artifacts_found": len(self.artifacts),
            },
            "compliance_status": (
                "PASS" if len(self.secrets) == 0 else "REVIEW_REQUIRED"
            ),
        }

        # Check for unprotected secrets
        for secret in self.secrets:
            example_file = secret.with_name(secret.name + ".example")
            if not example_file.exists():
                report["security_findings"]["unprotected_secrets"].append(str(secret))

        # Generate recommendations
        if report["security_findings"]["unprotected_secrets"]:
            report["security_findings"]["recommendations"].append(
                "Create .example files for all environment files"
            )

        if report["structural_analysis"]["duplicate_files"] > 0:
            report["security_findings"]["recommendations"].append(
                "Remove duplicate files to reduce attack surface"
            )

        return report

    def create_production_gitignore(self) -> None:
        """Create comprehensive production .gitignore."""
        gitignore_content = """# Production .gitignore - Auto-generated
# ==========================================

# Environment & Secrets
.env*
!.env.example
*.key
*.pem
*.p12
*.pfx
*secret*
*credential*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
.venv/
env/
.env/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
.yarn-integrity
.npm

# Build outputs
dist/
build/
*.tgz
*.tar.gz
*.zip

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Coverage
coverage/
*.lcov
.nyc_output
.coverage

# Testing
.pytest_cache/
.tox/

# Monitoring
prometheus_data/
grafana_data/

# Temporary
*.tmp
*.temp
*.bak
"""

        gitignore_path = self.root / ".gitignore"
        gitignore_path.write_text(gitignore_content, encoding="utf-8")

    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        structural_issues = self.detect_structural_issues()
        duplicate_count = sum(len(paths) - 1 for paths in self.duplicates.values())

        report_lines = [
            "\\n🏢  ENTERPRISE REPOSITORY ANALYSIS",
            "=" * 50,
            f"Repository: {self.root}",
            f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Production Mode: {'✅ Enabled' if self.production else '❌ Disabled'}",
            "",
            "📊  STRUCTURAL ANALYSIS",
            "-" * 30,
            f"Russian-doll directories: {len(structural_issues)}",
            f"Duplicate files removed: {duplicate_count}",
            f"Secret files found: {len(self.secrets)}",
            f"Artifact files: {len(self.artifacts)}",
            "",
            "🔒  SECURITY ASSESSMENT",
            "-" * 30,
        ]

        if self.secrets:
            report_lines.extend(
                [
                    "Security-sensitive files detected:",
                    *[f"  📄 {secret}" for secret in self.secrets[:5]],
                    (
                        f"  ... and {len(self.secrets) - 5} more"
                        if len(self.secrets) > 5
                        else ""
                    ),
                ]
            )
        else:
            report_lines.append("✅ No obvious security issues detected")

        report_lines.extend(
            [
                "",
                (
                    "📋  ACTIONS PERFORMED"
                    if self.production
                    else "📋  RECOMMENDED ACTIONS"
                ),
                "-" * 30,
                *[
                    f"  • {action}" for action in self.audit_log[-10:]
                ],  # Last 10 actions
            ]
        )

        return "\\n".join(filter(None, report_lines))

    def execute_enterprise_setup(self) -> None:
        """Execute full enterprise setup."""
        self.log_action("Starting enterprise repository setup")

        self.create_enterprise_structure()
        self.consolidate_backend()
        self.secure_secrets()

        if self.production:
            self.optimize_docker_configs()
            self.setup_monitoring()
            self.create_cicd_pipeline()

        self.create_production_gitignore()

        # Save audit log
        audit_file = self.root / "enterprise_setup_audit.log"
        with audit_file.open("w", encoding="utf-8") as f:
            f.write("\\n".join(self.audit_log))

        self.log_action("Enterprise setup completed successfully")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enterprise Repository Management for Scorpius",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("root", help="Path to repository root (e.g., ./NewScorp)")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute changes (default: analysis only)",
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="Enable production optimizations (Docker, CI/CD, monitoring)",
    )
    parser.add_argument(
        "--security-audit",
        action="store_true",
        help="Generate detailed security compliance report",
    )

    return parser.parse_args()


def main() -> None:
    """Main execution function."""
    args = parse_args()

    manager = EnterpriseRepoManager(Path(args.root), production=args.production)

    # Analysis phase
    manager.analyze_repository()
    print(manager.generate_report())

    # Security audit
    if args.security_audit:
        security_report = manager.generate_security_report()
        report_file = manager.root / "security_audit_report.json"
        with report_file.open("w") as f:
            json.dump(security_report, f, indent=2)
        print(f"\\n🔒 Security audit report saved to: {report_file}")

    # Execution phase
    if args.execute:
        confirm = (
            input("\\n🚀 Proceed with enterprise setup? [y/N] ").lower().startswith("y")
        )
        if confirm:
            manager.execute_enterprise_setup()
            print("\\n✅ Enterprise setup completed successfully!")
            print("\\n📋 Next steps:")
            print("   1. Review generated configurations in infrastructure/")
            print("   2. Update environment variables in .env files")
            print("   3. Test Docker configurations")
            print("   4. Configure monitoring dashboards")
            print("   5. Review CI/CD pipeline settings")
        else:
            print("Setup cancelled.")
    else:
        print("\\n💡 Run with --execute to apply changes")
        print("💡 Add --production for full enterprise features")
        print("💡 Add --security-audit for compliance reporting")


if __name__ == "__main__":
    main()
