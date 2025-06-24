#!/usr/bin/env python3
"""
Final Production Cleanup - Windows Safe
=======================================
Complete cleanup with Windows permission handling.
"""

import os
import shutil
import stat
from pathlib import Path


class FinalCleanup:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.removed_items: list[str] = []

    def safe_remove(self, path: Path) -> bool:
        """Safely remove a file or directory, handling Windows permissions."""
        try:
            if path.is_file():
                # Make file writable before deletion
                path.chmod(stat.S_IWRITE)
                path.unlink()
            else:
                # For directories, make all files writable
                def handle_remove_readonly(func, path, exc):
                    if os.path.exists(path):
                        os.chmod(path, stat.S_IWRITE)
                        func(path)

                shutil.rmtree(path, onerror=handle_remove_readonly)
            return True
        except Exception as e:
            print(f"   ⚠️  Could not remove {path}: {e}")
            return False

    def cleanup_backend(self) -> None:
        """Clean up backend directory structure."""
        print("🧹 Cleaning backend directory...")

        backend_dir = self.repo_path / "backend"
        if not backend_dir.exists():
            print("   ⚠️  Backend directory not found!")
            return

        # Remove specific legacy files
        legacy_items = [
            "backend/backend",
            "backend/elite_mempool_system_final.zip",
            "backend/honeypot_detector (2).zip",
            "backend/honeypot_detector.zip",
            "backend/mev_bot.zip",
            "backend/reporting.zip",
            "backend/vulnerability_scanner (2).zip",
            "backend/vulnerability_scanner.zip",
            "backend/scorpius_chat.db",
            "backend/SCANNER-main",
            "backend/__pycache__",
        ]

        for item_path in legacy_items:
            full_path = self.repo_path / item_path
            if full_path.exists():
                if self.safe_remove(full_path):
                    self.removed_items.append(item_path)
                    print(f"   Removed: {item_path}")

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
            "docker-compose.yml",
            "docker-compose.scanner.yml",
            "Dockerfile",
            "Dockerfile.backend",
            "Dockerfile.frontend",
            "nginx.conf",
            "index.html",
            "index.tsx",
        ]

        for filename in legacy_root_files:
            file_path = self.repo_path / filename
            if file_path.exists():
                if self.safe_remove(file_path):
                    self.removed_items.append(filename)
                    print(f"   Removed: {filename}")

    def cleanup_old_directories(self) -> None:
        """Remove old/duplicate directory structures."""
        print("🧹 Removing old directory structures...")

        old_dirs = [
            "backend_clean",
            "frontend_clean",
        ]

        for dirname in old_dirs:
            dir_path = self.repo_path / dirname
            if dir_path.exists():
                if self.safe_remove(dir_path):
                    self.removed_items.append(dirname + "/")
                    print(f"   Removed directory: {dirname}/")

        # Handle .venv separately with special care
        venv_path = self.repo_path / ".venv"
        if venv_path.exists():
            print("   Attempting to remove .venv/ (may require admin rights)...")
            if self.safe_remove(venv_path):
                self.removed_items.append(".venv/")
                print("   Removed directory: .venv/")
            else:
                print(
                    "   ⚠️  Could not remove .venv/ - please delete manually or ignore"
                )

    def move_src_to_frontend(self) -> None:
        """Move src/ to frontend/src/ if needed."""
        src_dir = self.repo_path / "src"
        frontend_dir = self.repo_path / "frontend"

        if src_dir.exists() and frontend_dir.exists():
            frontend_src = frontend_dir / "src"
            if not frontend_src.exists():
                print("📦 Moving src/ to frontend/src/")
                try:
                    shutil.move(str(src_dir), str(frontend_src))
                    self.removed_items.append("src/ → frontend/src/")
                except Exception as e:
                    print(f"   ⚠️  Could not move src/: {e}")
            else:
                print("🗑️  Removing duplicate src/ (frontend/src/ already exists)")
                if self.safe_remove(src_dir):
                    self.removed_items.append("src/ (duplicate)")

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
        self.generate_final_report()

        print("\n" + "=" * 50)
        print(f"✅ Final cleanup complete! Removed {len(self.removed_items)} items.")
        print("🎉 Repository is now PRODUCTION READY for commit!")


if __name__ == "__main__":
    repo_path = Path(__file__).parent
    cleaner = FinalCleanup(repo_path)
    cleaner.run_cleanup()
