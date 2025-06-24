#!/usr/bin/env python3
"""
Production Repository Finalizer
==============================
Remove old/duplicate directories and files, keeping only the clean production-ready structure.
This script will finalize the repository for production commit.
"""

import shutil
from pathlib import Path


class ProductionFinalizer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.removed_items: list[str] = []

    def remove_old_structure(self) -> None:
        """Remove the old nested and duplicate directories."""
        print("🗑️  Removing old directory structure...")

        # Remove the old nested backend structure
        old_backend = self.repo_path / "backend" / "backend"
        if old_backend.exists():
            print("   Removing: backend/backend/")
            shutil.rmtree(old_backend)
            self.removed_items.append("backend/backend/")
            # Remove the old backend_clean (we'll rename it to backend)
        backend_clean = self.repo_path / "backend_clean"
        if backend_clean.exists():
            # First remove the old backend completely
            old_backend_root = self.repo_path / "backend"
            if old_backend_root.exists():
                print("   Removing old backend/ directory")
                shutil.rmtree(old_backend_root)
                self.removed_items.append("backend/ (old)")

            # Rename backend_clean to backend
            print("   Promoting backend_clean/ → backend/")
            backend_clean.rename(self.repo_path / "backend")
            self.removed_items.append("backend_clean/ → backend/")

        # Remove frontend_clean (keep original frontend or promote it)
        frontend_clean = self.repo_path / "frontend_clean"
        frontend_original = self.repo_path / "frontend"
        src_dir = self.repo_path / "src"

        if frontend_clean.exists():
            if not frontend_original.exists() and src_dir.exists():
                # Promote src to frontend
                print("   Promoting src/ → frontend/")
                src_dir.rename(self.repo_path / "frontend")
                self.removed_items.append("src/ → frontend/")

            print("   Removing frontend_clean/")
            shutil.rmtree(frontend_clean)
            self.removed_items.append("frontend_clean/")

        # Remove other *_clean directories
        clean_dirs = ["docker_clean", "scripts_clean"]
        for clean_dir in clean_dirs:
            clean_path = self.repo_path / clean_dir
            if clean_path.exists():
                print(f"   Removing {clean_dir}/")
                shutil.rmtree(clean_path)
                self.removed_items.append(f"{clean_dir}/")

    def remove_duplicate_files(self) -> None:
        """Remove duplicate and old files."""
        print("🗑️  Removing duplicate and obsolete files...")

        # Remove old cleanup scripts (keep only the enterprise ones)
        old_files = [
            "repo_cleanup.py",
            "repo_cleanup_fixed.py",
            "check_deps.py",
            "cleanup.bat",
            "fix-deps.bat",
            "fix-deps.cjs",
            "fix-everything.cjs",
            "fix-npm-deps.js",
            "startupscorpius.py",
            "test_integration.py",
            "untitled.tsx",
            "index.tsx",
            "index.html",
        ]

        for file_name in old_files:
            file_path = self.repo_path / file_name
            if file_path.exists():
                print(f"   Removing {file_name}")
                file_path.unlink()
                self.removed_items.append(file_name)

        # Remove old Docker files (we have production versions now)
        old_docker_files = [
            "Dockerfile",
            "Dockerfile.backend",
            "Dockerfile.frontend",
            "docker-compose.yml",
        ]

        for file_name in old_docker_files:
            file_path = self.repo_path / file_name
            if file_path.exists():
                print(f"   Removing old {file_name}")
                file_path.unlink()
                self.removed_items.append(file_name)

        # Remove startup scripts (we have enterprise deployment now)
        startup_files = [
            "start_backend.sh",
            "start-scanner.sh",
            "start-scanner.bat",
            "install-startup.sh",
        ]

        for file_name in startup_files:
            file_path = self.repo_path / file_name
            if file_path.exists():
                print(f"   Removing {file_name}")
                file_path.unlink()
                self.removed_items.append(file_name)

    def remove_temp_files(self) -> None:
        """Remove temporary and cache files."""
        print("🗑️  Removing temporary files...")

        # Remove Python cache
        pycache_dirs = list(self.repo_path.rglob("__pycache__"))
        for pycache in pycache_dirs:
            if pycache.is_dir():
                print(f"   Removing {pycache.relative_to(self.repo_path)}")
                shutil.rmtree(pycache)
                self.removed_items.append(str(pycache.relative_to(self.repo_path)))

        # Remove .pyc files
        pyc_files = list(self.repo_path.rglob("*.pyc"))
        for pyc_file in pyc_files:
            print(f"   Removing {pyc_file.relative_to(self.repo_path)}")
            pyc_file.unlink()
            self.removed_items.append(str(pyc_file.relative_to(self.repo_path)))

        # Remove log files
        log_files = list(self.repo_path.rglob("*.log"))
        for log_file in log_files:
            if "audit" not in log_file.name:  # Keep audit logs
                print(f"   Removing {log_file.relative_to(self.repo_path)}")
                log_file.unlink()
                self.removed_items.append(str(log_file.relative_to(self.repo_path)))

    def remove_redundant_configs(self) -> None:
        """Remove redundant configuration files."""
        print("🗑️  Removing redundant configurations...")

        # Remove package-electron.json (not needed for web app)
        electron_config = self.repo_path / "package-electron.json"
        if electron_config.exists():
            print("   Removing package-electron.json")
            electron_config.unlink()
            self.removed_items.append("package-electron.json")

        # Remove duplicate .env.example files
        env_examples = list(self.repo_path.rglob(".env.example.example*"))
        for env_file in env_examples:
            print(f"   Removing duplicate {env_file.relative_to(self.repo_path)}")
            env_file.unlink()
            self.removed_items.append(str(env_file.relative_to(self.repo_path)))

    def create_final_structure(self) -> None:
        """Ensure the final production structure is clean."""
        print("✨ Finalizing production structure...")

        # Make sure scripts are executable
        deploy_script = self.repo_path / "scripts" / "deploy.sh"
        if deploy_script.exists():
            deploy_script.chmod(0o755)
            print("   Made deploy.sh executable")

        # Ensure all README files exist in subdirectories
        enterprise_dirs = [
            "backend",
            "frontend",
            "infrastructure",
            "monitoring",
            "security",
            "ci-cd",
            "scripts",
        ]
        for dir_name in enterprise_dirs:
            dir_path = self.repo_path / dir_name
            readme_path = dir_path / "README.md"
            if dir_path.exists() and not readme_path.exists():
                readme_content = f"# {dir_name.title()}\n\nProduction {dir_name} components for Scorpius Enterprise.\n"
                readme_path.write_text(readme_content, encoding="utf-8")
                print(f"   Created README.md in {dir_name}/")

    def generate_final_report(self) -> str:
        """Generate a report of what was cleaned up."""
        return f"""
🧹 PRODUCTION FINALIZATION REPORT
==================================
Repository: {self.repo_path}

Items Removed: {len(self.removed_items)}
{chr(10).join(f"  ✓ {item}" for item in self.removed_items[:20])}
{"  ... and more" if len(self.removed_items) > 20 else ""}

✅ Repository is now clean and production-ready!
"""

    def finalize(self) -> None:
        """Execute the full finalization process."""
        print("🚀 Starting Production Repository Finalization...")
        print("=" * 50)

        self.remove_old_structure()
        self.remove_duplicate_files()
        self.remove_temp_files()
        self.remove_redundant_configs()
        self.create_final_structure()

        print("\n" + self.generate_final_report())
        print("🎉 Repository finalized for production!")


def main():
    """Main execution function."""
    repo_path = Path.cwd()
    finalizer = ProductionFinalizer(repo_path)

    print("This will clean up the repository to keep only production-ready files.")
    confirm = input("Continue with finalization? [y/N] ").lower().startswith("y")

    if confirm:
        finalizer.finalize()
    else:
        print("Finalization cancelled.")


if __name__ == "__main__":
    main()
