#!/usr/bin/env python3
"""
MevGuardian Quick Start Script

This script provides a simple way to initialize and run the MevGuardian system
for development and testing purposes.
"""

import shutil
import subprocess
import sys
from pathlib import Path


def check_requirements():
    """Check if required tools are installed."""
    print("🔍 Checking requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False

    # Check Docker
    if not shutil.which("docker"):
        print("❌ Docker is not installed")
        return False

    # Check Docker Compose
    if not shutil.which("docker-compose"):
        print("❌ Docker Compose is not installed")
        return False

    print("✅ All requirements met")
    return True


def setup_environment():
    """Setup environment file if it doesn't exist."""
    print("📝 Setting up environment...")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from example")
        print("⚠️  Please edit .env file with your configuration")
        return False
    elif env_file.exists():
        print("✅ Environment file already exists")
        return True
    else:
        print("❌ No environment example file found")
        return False


def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")

    directories = ["logs", "config", "monitoring/grafana/dashboards"]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Directories created")


def run_development_mode():
    """Run in development mode without Docker."""
    print("🚀 Starting MevGuardian in development mode...")

    try:
        # Install requirements
        print("📦 Installing Python requirements...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
        )

        # Run the bot
        print("🤖 Starting MevGuardian bot...")
        subprocess.run([sys.executable, "mev_guardian_bot.py"], check=True)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running development mode: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        return True


def run_docker_mode():
    """Run in Docker mode."""
    print("🐳 Starting MevGuardian with Docker...")

    try:
        # Build and start services
        subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)

        print("✅ Services started successfully!")
        print("\n📊 Access points:")
        print("  • API: http://localhost:8000")
        print("  • Docs: http://localhost:8000/docs")
        print("  • Grafana: http://localhost:3000")
        print("  • Prometheus: http://localhost:9090")

        print("\n📋 Commands:")
        print("  • View logs: docker-compose logs -f")
        print("  • Stop: docker-compose down")
        print("  • Status: docker-compose ps")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Docker mode: {e}")
        return False


def main():
    """Main function."""
    print("🛡️  MevGuardian Quick Start")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Setup environment
    env_ready = setup_environment()

    # Create directories
    create_directories()

    # Ask for run mode
    print("\n🚀 Choose run mode:")
    print("1. Development (Python directly)")
    print("2. Production (Docker)")
    print("3. Exit")

    while True:
        choice = input("\nEnter your choice (1-3): ").strip()

        if choice == "1":
            if not env_ready:
                print("⚠️  Please configure .env file first")
                sys.exit(1)
            run_development_mode()
            break
        elif choice == "2":
            if not env_ready:
                print("⚠️  Please configure .env file first")
                sys.exit(1)
            run_docker_mode()
            break
        elif choice == "3":
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
