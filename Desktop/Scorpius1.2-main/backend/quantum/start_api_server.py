#!/usr/bin/env python3
"""
Scorpius Enterprise API Server Launcher
Quick script to start the FastAPI backend with proper configuration.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import uvicorn

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    """Main function to start the API server."""
    parser = argparse.ArgumentParser(description="Start Scorpius Enterprise API Server")
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload for development"
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="Number of worker processes"
    )
    parser.add_argument(
        "--log-level", default="info", choices=["debug", "info", "warning", "error"]
    )

    args = parser.parse_args()

    # Print startup information
    print("🚀 Starting Scorpius Enterprise API Server")
    print("=" * 50)
    print(f"📡 Host: {args.host}")
    print(f"🔌 Port: {args.port}")
    print(f"🔄 Auto-reload: {args.reload}")
    print(f"👥 Workers: {args.workers}")
    print(f"📝 Log level: {args.log_level}")
    print("=" * 50)
    print(f"🌐 API URL: http://{args.host}:{args.port}")
    print(f"📚 API Docs: http://{args.host}:{args.port}/docs")
    print(f"🔗 WebSocket: ws://{args.host}:{args.port}/ws/dashboard")
    print("=" * 50)

    # Check if enterprise config exists
    config_path = project_root / "config" / "enterprise.yml"
    if not config_path.exists():
        logger.warning(f"Enterprise config not found at {config_path}")
        logger.info("The server will use default configuration")

    try:
        # Start the server
        uvicorn.run(
            "scorpius.api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers
            if not args.reload
            else 1,  # Workers don't work with reload
            log_level=args.log_level,
            app_dir=str(project_root),
        )
    except KeyboardInterrupt:
        print("\n⏹️ Server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
