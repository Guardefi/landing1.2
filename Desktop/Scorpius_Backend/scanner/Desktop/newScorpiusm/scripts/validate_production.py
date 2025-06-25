#!/usr/bin/env python3
"""
Scorpius Production Validation Script
====================================
Validates that the repository is ready for enterprise production deployment.
Checks configuration, security, performance, and compliance readiness.
"""

import json
import sys
from pathlib import Path

import yaml


class ProductionValidator:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.issues: list[str] = []
        self.warnings: list[str] = []
        self.passed_checks: list[str] = []

    def check_file_exists(self, file_path: str, critical: bool = True) -> bool:
        """Check if a required file exists."""
        path = self.repo_path / file_path
        exists = path.exists()

        if exists:
            self.passed_checks.append(f"✅ {file_path} exists")
        elif critical:
            self.issues.append(f"❌ Missing critical file: {file_path}")
        else:
            self.warnings.append(f"⚠️  Optional file missing: {file_path}")

        return exists

    def check_directory_structure(self) -> None:
        """Validate enterprise directory structure."""
        print("📁 Checking directory structure...")

        required_dirs = [
            "backend",
            "frontend",
            "infrastructure",
            "monitoring",
            "security",
            "ci-cd",
            "docs",
            "configs",
            "scripts",
        ]

        for dir_name in required_dirs:
            if (self.repo_path / dir_name).exists():
                self.passed_checks.append(f"✅ Directory {dir_name}/ exists")
            else:
                self.issues.append(f"❌ Missing directory: {dir_name}/")

    def check_docker_configs(self) -> None:
        """Validate Docker configurations."""
        print("🐳 Checking Docker configurations...")

        docker_files = [
            "backend/Dockerfile.prod",
            "frontend/Dockerfile.prod",
            "infrastructure/docker/docker-compose.prod.yml",
        ]

        for docker_file in docker_files:
            self.check_file_exists(docker_file)

        # Validate Docker Compose structure
        compose_file = self.repo_path / "infrastructure/docker/docker-compose.prod.yml"
        if compose_file.exists():
            try:
                with open(compose_file) as f:
                    compose_data = yaml.safe_load(f)

                if "services" in compose_data:
                    services = list(compose_data["services"].keys())
                    self.passed_checks.append(
                        f"✅ Docker services defined: {', '.join(services)}"
                    )

                    # Check for health checks
                    for service_name, service_config in compose_data[
                        "services"
                    ].items():
                        if "healthcheck" in service_config:
                            self.passed_checks.append(
                                f"✅ Health check defined for {service_name}"
                            )
                        else:
                            self.warnings.append(
                                f"⚠️  No health check for service: {service_name}"
                            )

            except Exception as e:
                self.issues.append(f"❌ Invalid Docker Compose file: {e}")

    def check_security_config(self) -> None:
        """Validate security configurations."""
        print("🔒 Checking security configurations...")

        # Check for production environment template
        if self.check_file_exists(".env.production.example"):
            env_file = self.repo_path / ".env.production.example"
            content = env_file.read_text()

            security_vars = ["SECRET_KEY", "JWT_SECRET_KEY", "DB_PASSWORD"]
            for var in security_vars:
                if var in content:
                    self.passed_checks.append(f"✅ Security variable {var} templated")
                else:
                    self.warnings.append(f"⚠️  Missing security variable: {var}")

        # Check gitignore
        gitignore = self.repo_path / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            security_patterns = [".env*", "*.key", "*.pem", "*secret*"]

            for pattern in security_patterns:
                if pattern in content:
                    self.passed_checks.append(f"✅ Gitignore protects: {pattern}")
                else:
                    self.warnings.append(f"⚠️  Gitignore missing pattern: {pattern}")

        # Check security documentation
        self.check_file_exists("security/SECURITY_POLICY.md")

    def check_monitoring_setup(self) -> None:
        """Validate monitoring configurations."""
        print("📊 Checking monitoring setup...")

        monitoring_files = [
            "monitoring/prometheus.yml",
            "monitoring/grafana-datasources.yml",
        ]

        for file_path in monitoring_files:
            self.check_file_exists(file_path)

    def check_cicd_pipeline(self) -> None:
        """Validate CI/CD pipeline configuration."""
        print("🔄 Checking CI/CD pipeline...")

        # Check GitHub Actions
        github_workflow = "ci-cd/.github/workflows/main.yml"
        if self.check_file_exists(github_workflow):
            workflow_file = self.repo_path / github_workflow
            try:
                with open(workflow_file) as f:
                    workflow_data = yaml.safe_load(f)

                if "jobs" in workflow_data:
                    jobs = list(workflow_data["jobs"].keys())
                    self.passed_checks.append(
                        f"✅ CI/CD jobs defined: {', '.join(jobs)}"
                    )

                    # Check for security scanning
                    workflow_content = workflow_file.read_text()
                    if "bandit" in workflow_content or "safety" in workflow_content:
                        self.passed_checks.append("✅ Security scanning in CI/CD")
                    else:
                        self.warnings.append("⚠️  No security scanning in CI/CD")

            except Exception as e:
                self.issues.append(f"❌ Invalid CI/CD workflow: {e}")

    def check_kubernetes_config(self) -> None:
        """Validate Kubernetes configurations."""
        print("☸️  Checking Kubernetes configurations...")

        k8s_file = "infrastructure/kubernetes/production.yaml"
        if self.check_file_exists(k8s_file, critical=False):
            k8s_config = self.repo_path / k8s_file
            try:
                with open(k8s_config) as f:
                    content = f.read()

                # Check for required Kubernetes resources
                resources = ["Deployment", "Service", "Ingress"]
                for resource in resources:
                    if f"kind: {resource}" in content:
                        self.passed_checks.append(f"✅ Kubernetes {resource} defined")
                    else:
                        self.warnings.append(f"⚠️  Missing Kubernetes {resource}")

            except Exception as e:
                self.warnings.append(f"⚠️  Invalid Kubernetes config: {e}")

    def check_dependencies(self) -> None:
        """Check production dependencies."""
        print("📦 Checking dependencies...")

        # Check production requirements
        if self.check_file_exists("requirements.prod.txt"):
            req_file = self.repo_path / "requirements.prod.txt"
            content = req_file.read_text()

            # Check for version pinning
            lines = [
                line.strip()
                for line in content.split("\n")
                if line.strip() and not line.startswith("#")
            ]
            pinned_deps = [line for line in lines if "==" in line]

            if len(pinned_deps) > len(lines) * 0.8:  # 80% of deps should be pinned
                self.passed_checks.append(
                    "✅ Dependencies properly pinned for production"
                )
            else:
                self.warnings.append(
                    "⚠️  Consider pinning more dependencies for production stability"
                )

        # Check package.json for frontend
        package_json = self.repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)

                if "scripts" in package_data:
                    scripts = package_data["scripts"]
                    if "build" in scripts:
                        self.passed_checks.append("✅ Frontend build script defined")
                    else:
                        self.warnings.append("⚠️  No frontend build script found")

            except Exception as e:
                self.warnings.append(f"⚠️  Invalid package.json: {e}")

    def check_documentation(self) -> None:
        """Validate documentation completeness."""
        print("📚 Checking documentation...")

        doc_files = [
            "README.md",
            "PRODUCTION_READINESS.md",
            "docs/API_SPECIFICATION.md",
            "docs/DEPLOYMENT_GUIDE.md",
        ]

        for doc_file in doc_files:
            self.check_file_exists(doc_file, critical=False)

    def run_security_audit(self) -> None:
        """Run security audit if tools are available."""
        print("🛡️  Running security audit...")

        audit_report = self.repo_path / "security_audit_report.json"
        if audit_report.exists():
            try:
                with open(audit_report) as f:
                    audit_data = json.load(f)

                compliance_status = audit_data.get("compliance_status", "UNKNOWN")
                secrets_found = audit_data.get("security_findings", {}).get(
                    "secrets_found", 0
                )

                self.passed_checks.append(
                    f"✅ Security audit completed: {compliance_status}"
                )

                if secrets_found > 0:
                    self.warnings.append(
                        f"⚠️  {secrets_found} potential secrets found - review audit report"
                    )
                else:
                    self.passed_checks.append("✅ No obvious security issues detected")

            except Exception as e:
                self.warnings.append(f"⚠️  Could not parse security audit: {e}")

    def generate_report(self) -> dict:
        """Generate final validation report."""
        total_checks = len(self.passed_checks) + len(self.issues) + len(self.warnings)
        passed_percentage = (
            (len(self.passed_checks) / total_checks * 100) if total_checks > 0 else 0
        )

        status = (
            "PRODUCTION READY"
            if len(self.issues) == 0 and passed_percentage >= 85
            else "NEEDS ATTENTION" if len(self.issues) == 0 else "NOT READY"
        )

        return {
            "status": status,
            "score": f"{passed_percentage:.1f}%",
            "passed_checks": len(self.passed_checks),
            "issues": len(self.issues),
            "warnings": len(self.warnings),
            "details": {
                "passed": self.passed_checks,
                "issues": self.issues,
                "warnings": self.warnings,
            },
        }

    def validate(self) -> dict:
        """Run all validation checks."""
        print("🚀 Starting Scorpius Production Validation...\n")

        self.check_directory_structure()
        self.check_docker_configs()
        self.check_security_config()
        self.check_monitoring_setup()
        self.check_cicd_pipeline()
        self.check_kubernetes_config()
        self.check_dependencies()
        self.check_documentation()
        self.run_security_audit()

        return self.generate_report()


def main():
    """Main validation function."""
    repo_path = Path.cwd()
    validator = ProductionValidator(repo_path)

    report = validator.validate()

    print("\n" + "=" * 60)
    print("🏢 SCORPIUS PRODUCTION VALIDATION REPORT")
    print("=" * 60)
    print(f"Status: {report['status']}")
    print(f"Score: {report['score']}")
    print(f"Checks Passed: {report['passed_checks']}")
    print(f"Issues: {report['issues']}")
    print(f"Warnings: {report['warnings']}")

    if report["details"]["issues"]:
        print("\n❌ CRITICAL ISSUES TO FIX:")
        for issue in report["details"]["issues"]:
            print(f"   {issue}")

    if report["details"]["warnings"]:
        print("\n⚠️  WARNINGS TO REVIEW:")
        for warning in report["details"]["warnings"][:5]:  # Show first 5
            print(f"   {warning}")
        if len(report["details"]["warnings"]) > 5:
            print(f"   ... and {len(report['details']['warnings']) - 5} more warnings")

    print(f"\n✅ SUCCESSFUL CHECKS: {len(report['details']['passed'])}")

    # Save detailed report
    report_file = repo_path / "production_validation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    if report["status"] == "PRODUCTION READY":
        print("\n🎉 CONGRATULATIONS! Repository is ready for production deployment!")
        sys.exit(0)
    elif report["status"] == "NEEDS ATTENTION":
        print("\n⚠️  Repository is mostly ready but has some warnings to review")
        sys.exit(0)
    else:
        print(
            "\n❌ Repository is not ready for production. Please fix critical issues."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
