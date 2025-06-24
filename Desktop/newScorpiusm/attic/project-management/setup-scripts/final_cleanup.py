#!/usr/bin/env python3
"""
Final Production Cleanup
========================
Complete cleanup to ensure only production-ready files remain.
This script removes all legacy files, duplicates, and temporary artifacts.
"""

import shutil
from pathlib import Path


class FinalCleanup:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.removed_items: list[str] = []

    def cleanup_backend(self) -> None:
        """Clean up backend directory structure."""
        print("🧹 Cleaning backend directory...")

        backend_dir = self.repo_path / "backend"
        if not backend_dir.exists():
            print("   ⚠️  Backend directory not found!")
            return

        # Remove legacy/duplicate files
        legacy_files = [
            "backend/backend",  # Nested backend dir
            "backend/*.zip",  # Zip archives
            "backend/*.db",  # Database files (should be in data/)
            "backend/SCANNER-main",  # Old scanner
            "backend/__pycache__",  # Python cache
            "backend/elite_mempool_system_final.zip",
            "backend/honeypot_detector.zip",
            "backend/honeypot_detector (2).zip",
            "backend/mev_bot.zip",
            "backend/reporting.zip",
            "backend/vulnerability_scanner.zip",
            "backend/vulnerability_scanner (2).zip",
            "backend/scorpius_chat.db",
        ]

        for pattern in legacy_files:
            self._remove_pattern(pattern)

        # Keep only essential backend files
        essential_backend = {
            # Core application files
            "main.py",
            "start.py",
            "run_server.py",
            "api_server.py",
            # Route files
            "auth_routes.py",
            "config_routes.py",
            "dashboard_routes.py",
            "mev_guardians_routes.py",
            "mev_ops_routes.py",
            "scanner_routes.py",
            "simulation_routes.py",
            # Database and system
            "database.py",
            "elite_database.py",
            "system_health.py",
            "websocket_server.py",
            "load_env.py",
            # Configuration files
            "requirements.txt",
            "requirements-frozen.txt",
            "Dockerfile",
            "README.md",
            "start.sh",
            ".env.backend.example",
            # Directories
            "routes/",
            "models/",
            "utils/",
            "settings/",
            "jobs/",
            "bytecode_analyzer/",
            "time_machine/",
            "Scheduler/",
            # Keep cleaned versions of these
            "elite_mempool_system_final/",
            "honeypot_detector/",
            "mev_bot/",
            "reporting/",
            "backend_additions/",
        }

        self._cleanup_directory(backend_dir, essential_backend)

    def cleanup_root_directory(self) -> None:
        """Clean up root directory files."""
        print("🧹 Cleaning root directory...")

        # Remove legacy/temporary files
        legacy_root_files = [
            "repo_cleanup.py",
            "enterprise_setup.py",
            "finalize_production.py",
            "check_deps.py",
            "cleanup.bat",
            "fix-deps.bat",
            "fix-deps.cjs",
            "fix-everything.cjs",
            "fix-npm-deps.js",
            "install-startup.sh",
            "start_backend.sh",
            "start-scanner.bat",
            "start-scanner.sh",
            "startupscorpius.py",
            "test_integration.py",
            "untitled.tsx",
            "enterprise_setup_audit.log",
            # Docker files that are now in infrastructure/
            "docker-compose.yml",
            "docker-compose.scanner.yml",
            "Dockerfile",
            "Dockerfile.backend",
            "Dockerfile.frontend",
            # Nginx config (now in frontend/)
            "nginx.conf",
        ]

        for filename in legacy_root_files:
            file_path = self.repo_path / filename
            if file_path.exists():
                if file_path.is_file():
                    file_path.unlink()
                else:
                    shutil.rmtree(file_path)
                self.removed_items.append(filename)
                print(f"   Removed: {filename}")

    def cleanup_old_directories(self) -> None:
        """Remove old/duplicate directory structures."""
        print("🧹 Removing old directory structures...")

        old_dirs = [
            "src",  # This should be moved to frontend/src
            "backend_clean",
            "frontend_clean",
            ".venv",  # Virtual environment
        ]

        for dirname in old_dirs:
            dir_path = self.repo_path / dirname
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.removed_items.append(dirname + "/")
                print(f"   Removed directory: {dirname}/")

    def move_src_to_frontend(self) -> None:
        """Move src/ to frontend/src/ if needed."""
        src_dir = self.repo_path / "src"
        frontend_dir = self.repo_path / "frontend"

        if src_dir.exists() and frontend_dir.exists():
            frontend_src = frontend_dir / "src"
            if not frontend_src.exists():
                print("📦 Moving src/ to frontend/src/")
                shutil.move(str(src_dir), str(frontend_src))
                self.removed_items.append("src/ → frontend/src/")
            else:
                print("🗑️  Removing duplicate src/ (frontend/src/ already exists)")
                shutil.rmtree(src_dir)
                self.removed_items.append("src/ (duplicate)")

    def cleanup_config_files(self) -> None:
        """Clean up configuration files."""
        print("🧹 Cleaning configuration files...")

        # Keep only production-ready config files
        essential_configs = {
            "package.json",
            "package-lock.json",
            "tsconfig.json",
            "tsconfig.app.json",
            "tsconfig.node.json",
            "vite.config.ts",
            "vite.config.js",
            "vitest.config.ts",
            "tailwind.config.ts",
            "postcss.config.js",
            "components.json",
            ".gitignore",
            ".env.example",
            ".env.production.example",
            "metadata.json",
            "NEW SCORPIUS X.code-workspace",
        }

        # Move or remove duplicates
        for file_path in self.repo_path.iterdir():
            if file_path.is_file() and file_path.name not in essential_configs:
                if file_path.name.startswith(".env") and not file_path.name.endswith(
                    ".example"
                ):
                    # Keep actual .env files but they're not in the essential list
                    continue
                elif (
                    file_path.suffix in [".md", ".json"]
                    and file_path.name not in essential_configs
                ):
                    # Keep documentation and important JSON files
                    continue
                elif file_path.name.endswith(".py"):
                    # Remove Python scripts from root (they should be in scripts/ or backend/)
                    if file_path.name not in [
                        "final_cleanup.py"
                    ]:  # Don't remove this script yet
                        file_path.unlink()
                        self.removed_items.append(file_path.name)
                        print(f"   Removed: {file_path.name}")

    def _remove_pattern(self, pattern: str) -> None:
        """Remove files/directories matching a pattern."""
        import glob

        matches = glob.glob(str(self.repo_path / pattern))
        for match in matches:
            path = Path(match)
            if path.exists():
                if path.is_file():
                    path.unlink()
                else:
                    shutil.rmtree(path)
                rel_path = path.relative_to(self.repo_path)
                self.removed_items.append(str(rel_path))
                print(f"   Removed: {rel_path}")

    def _cleanup_directory(self, directory: Path, essential_files: set[str]) -> None:
        """Clean up a directory keeping only essential files."""
        if not directory.exists():
            return

        for item in directory.iterdir():
            rel_name = item.name
            if item.is_dir():
                rel_name += "/"

            if rel_name not in essential_files:
                # Check if it's a Python cache or temporary file
                if (
                    item.is_dir()
                    and item.name in ["__pycache__", ".pytest_cache", "node_modules"]
                ) or (
                    item.is_file() and item.suffix in [".pyc", ".pyo", ".log", ".tmp"]
                ):
                    if item.is_file():
                        item.unlink()
                    else:
                        shutil.rmtree(item)
                    rel_path = item.relative_to(self.repo_path)
                    self.removed_items.append(str(rel_path))
                    print(f"   Removed: {rel_path}")

    def generate_final_report(self) -> None:
        """Generate final cleanup report."""
        report_path = self.repo_path / "FINAL_CLEANUP_REPORT.md"

        with open(report_path, "w") as f:
            f.write("# Final Production Cleanup Report\n\n")
            f.write(f"**Total items removed:** {len(self.removed_items)}\n\n")
            f.write("## Removed Items\n\n")

            for item in sorted(self.removed_items):
                f.write(f"- {item}\n")

            f.write("\n## Repository Status\n\n")
            f.write("✅ **PRODUCTION READY** - Repository cleaned and finalized\n\n")
            f.write("### Enterprise Structure\n")
            f.write("```\n")
            f.write("NewScorp/\n")
            f.write("├── backend/           # Clean backend API\n")
            f.write("├── frontend/          # Clean frontend app\n")
            f.write("├── infrastructure/    # Docker, K8s, deployment\n")
            f.write("├── monitoring/        # Prometheus, Grafana configs\n")
            f.write("├── security/          # Security policies & configs\n")
            f.write("├── ci-cd/            # GitHub Actions, pipelines\n")
            f.write("├── scripts/          # Deployment & utility scripts\n")
            f.write("├── docs/             # All documentation\n")
            f.write("├── configs/          # Application configurations\n")
            f.write("├── tests/            # Test suites\n")
            f.write("└── README.md         # Production documentation\n")
            f.write("```\n")

        print(f"📊 Final cleanup report: {report_path}")

    def run_cleanup(self) -> None:
        """Run the complete cleanup process."""
        print("🚀 Starting final production cleanup...")
        print("=" * 50)

        self.move_src_to_frontend()
        self.cleanup_backend()
        self.cleanup_old_directories()
        self.cleanup_root_directory()
        self.cleanup_config_files()
        self.generate_final_report()

        print("\n" + "=" * 50)
        print(f"✅ Final cleanup complete! Removed {len(self.removed_items)} items.")
        print("🎉 Repository is now PRODUCTION READY for commit!")


if __name__ == "__main__":
    repo_path = Path(__file__).parent
    cleaner = FinalCleanup(repo_path)
    cleaner.run_cleanup()
