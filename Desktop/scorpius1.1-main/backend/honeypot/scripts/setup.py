#!/usr/bin/env python
"""
Setup script for the Enterprise Honeypot Detector
- Creates required directories
- Initializes MongoDB collections and indices
- Prepares initial ML models
- Creates configuration files
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.engines.ml_engine import MLEngine
from database.mongodb_client import MongoDBClient

from config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("setup")


async def ensure_directories():
    """Ensure all required directories exist"""
    logger.info("Creating required directories...")

    directories = [
        "logs",
        "models/ml",
        "models/symbolic",
        "data/training",
        "data/test",
    ]

    for directory in directories:
        path = (
            Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            / directory
        )
        if not path.exists():
            logger.info(f"Creating directory: {path}")
            path.mkdir(parents=True, exist_ok=True)


async def initialize_database():
    """Initialize MongoDB database"""
    logger.info("Initializing MongoDB database...")

    client = MongoDBClient()
    try:
        await client.initialize()

        # Create initial collections
        db = client.client[settings.DATABASE_NAME]
        collections = [
            "analyses",
            "statistics",
            "contracts",
            "training_data",
            "users",
        ]

        for collection in collections:
            if collection not in await db.list_collection_names():
                logger.info(f"Creating collection: {collection}")
                await db.create_collection(collection)

        # Create indices
        logger.info("Creating database indices...")
        await db["analyses"].create_index(
            [("contract_address", 1), ("chain_id", 1)], unique=True
        )
        await db["analyses"].create_index([("risk_level", 1)])
        await db["analyses"].create_index([("created_at", -1)])

        await db["statistics"].create_index([("chain_id", 1)], unique=True)

        await db["contracts"].create_index(
            [("address", 1), ("chain_id", 1)], unique=True
        )
        await db["contracts"].create_index([("created_at", -1)])

        # Create admin user if not exists
        users = db["users"]
        admin_exists = await users.find_one({"username": "admin"})
        if not admin_exists:
            logger.info("Creating admin user...")
            await users.insert_one(
                {
                    "username": "admin",
                    "api_key": settings.API_KEY,
                    "is_admin": True,
                    "rate_limit": 1000,  # Higher rate limit for admin
                    "created_at": datetime.datetime.utcnow(),
                }
            )

        logger.info("Database initialization complete")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        await client.close()


async def initialize_ml_models():
    """Initialize machine learning models"""
    logger.info("Initializing ML models...")

    ml_engine = MLEngine()
    try:
        await ml_engine.initialize()

        # Train initial model with synthetic data if no model exists
        model_path = (
            Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            / "models/ml/honeypot_model.joblib"
        )
        if not model_path.exists():
            logger.info("Training initial ML model with synthetic data...")
            await ml_engine.train(force_synthetic=True)

        logger.info("ML model initialization complete")

    except Exception as e:
        logger.error(f"Error initializing ML models: {e}")


async def create_env_file():
    """Create .env file if it doesn't exist"""
    logger.info("Checking for .env file...")

    env_path = (
        Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / ".env"
    )
    if not env_path.exists():
        logger.info("Creating .env file...")

        with open(env_path, "w") as f:
            f.write(f"# API Configuration\n")
            f.write(f"API_KEY={settings.API_KEY}\n")
            f.write(f"ALLOWED_ORIGINS=['*']\n")
            f.write(f"DEBUG=True\n\n")

            f.write(f"# Database\n")
            f.write(f"MONGODB_URL={settings.MONGODB_URL}\n")
            f.write(f"DATABASE_NAME={settings.DATABASE_NAME}\n\n")

            f.write(f"# Blockchain RPC URLs\n")
            f.write(f"ETHEREUM_RPC_URL={settings.ETHEREUM_RPC_URL}\n")
            f.write(f"BSC_RPC_URL={settings.BSC_RPC_URL}\n\n")

            f.write(f"# Cache Configuration\n")
            f.write(f"REDIS_URL={settings.REDIS_URL}\n")

        logger.info(f"Created .env file at {env_path}")
    else:
        logger.info(".env file already exists")


async def create_prometheus_config():
    """Create Prometheus configuration file for monitoring"""
    logger.info("Creating Prometheus configuration...")

    prometheus_dir = (
        Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "docker"
    )
    if not prometheus_dir.exists():
        prometheus_dir.mkdir(parents=True, exist_ok=True)

    prometheus_config = prometheus_dir / "prometheus.yml"

    config = {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s",
        },
        "scrape_configs": [
            {"job_name": "honeypot-api", "static_configs": [{"targets": ["api:8000"]}]}
        ],
    }

    with open(prometheus_config, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    logger.info(f"Created Prometheus config at {prometheus_config}")


async def main():
    """Main setup function"""
    logger.info("Starting Enterprise Honeypot Detector setup...")

    try:
        # Setup steps
        await ensure_directories()
        await create_env_file()
        await initialize_database()
        await initialize_ml_models()
        await create_prometheus_config()

        logger.info("Setup completed successfully!")

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Fix imports
    import datetime

    import yaml

    # Run setup
    asyncio.run(main())
