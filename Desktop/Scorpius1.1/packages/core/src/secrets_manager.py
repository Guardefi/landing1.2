"""
AWS Secrets Manager Integration for Scorpius Enterprise Platform
Implements secure secret retrieval with fail-fast behavior and rotation support.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from functools import lru_cache
from dataclasses import dataclass

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pydantic import BaseSettings, Field

logger = logging.getLogger(__name__)

@dataclass
class SecretConfig:
    """Configuration for a secret in AWS Secrets Manager"""
    secret_name: str
    region: str = "us-east-1"
    required: bool = True
    cache_ttl: int = 300  # 5 minutes


class SecretsManager:
    """
    Enterprise-grade secrets manager with AWS integration
    """
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._client = None
        self._cache = {}
    
    @property
    def client(self):
        """Lazy initialization of AWS Secrets Manager client"""
        if self._client is None:
            try:
                self._client = boto3.client(
                    'secretsmanager',
                    region_name=self.region
                )
            except NoCredentialsError:
                logger.error("❌ AWS credentials not configured")
                raise RuntimeError("AWS credentials required for production deployment")
        return self._client
    
    def get_secret(self, secret_name: str, required: bool = True) -> Optional[str]:
        """
        Retrieve a secret from AWS Secrets Manager
        
        Args:
            secret_name: Name of the secret in AWS Secrets Manager
            required: Whether to fail fast if secret is missing
            
        Returns:
            Secret value as string, or None if not required and missing
            
        Raises:
            RuntimeError: If required secret is missing or inaccessible
        """
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            
            # Try to parse as JSON first
            try:
                return json.loads(secret_value)
            except json.JSONDecodeError:
                return secret_value
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ResourceNotFoundException':
                if required:
                    logger.error(f"❌ Required secret '{secret_name}' not found in AWS Secrets Manager")
                    raise RuntimeError(f"Required secret '{secret_name}' not found")
                else:
                    logger.warning(f"⚠️ Optional secret '{secret_name}' not found")
                    return None
                    
            elif error_code == 'InvalidRequestException':
                logger.error(f"❌ Invalid request for secret '{secret_name}'")
                raise RuntimeError(f"Invalid secret configuration: {secret_name}")
                
            elif error_code == 'InvalidParameterException':
                logger.error(f"❌ Invalid parameter for secret '{secret_name}'")
                raise RuntimeError(f"Invalid secret parameter: {secret_name}")
                
            else:
                logger.error(f"❌ Failed to retrieve secret '{secret_name}': {e}")
                raise RuntimeError(f"Failed to retrieve secret: {secret_name}")
    
    def get_secrets_batch(self, secret_configs: Dict[str, SecretConfig]) -> Dict[str, Any]:
        """
        Retrieve multiple secrets efficiently
        
        Args:
            secret_configs: Dictionary mapping config keys to SecretConfig objects
            
        Returns:
            Dictionary of retrieved secrets
        """
        secrets = {}
        
        for config_key, secret_config in secret_configs.items():
            secret_value = self.get_secret(
                secret_config.secret_name, 
                secret_config.required
            )
            
            if secret_value is not None:
                secrets[config_key] = secret_value
        
        return secrets


class SecureSettings(BaseSettings):
    """
    Enterprise settings with AWS Secrets Manager integration
    """
    
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Application Configuration  
    app_name: str = Field(default="scorpius", env="APP_NAME")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Database Configuration (will be retrieved from AWS Secrets Manager)
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Security Configuration
    jwt_secret_key: Optional[str] = None
    encryption_key: Optional[str] = None
    
    # External API Keys
    web3_provider_url: Optional[str] = None
    coinbase_api_key: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_secrets()
    
    def _load_secrets(self):
        """Load secrets from AWS Secrets Manager on startup"""
        if self.environment == "development":
            logger.info("🔧 Development mode: using environment variables for secrets")
            self._load_dev_secrets()
        else:
            logger.info("🔒 Production mode: loading secrets from AWS Secrets Manager")
            self._load_aws_secrets()
    
    def _load_dev_secrets(self):
        """Load secrets from environment variables in development"""
        self.database_url = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:postgres@localhost:5432/scorpius_dev"
        )
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
        self.web3_provider_url = os.getenv("WEB3_PROVIDER_URL", "https://mainnet.infura.io/v3/demo")
    
    def _load_aws_secrets(self):
        """Load secrets from AWS Secrets Manager in production"""
        secrets_manager = SecretsManager(region=self.aws_region)
        
        # Define secret configurations
        secret_configs = {
            "database": SecretConfig(
                secret_name=f"scorpius/{self.environment}/database",
                required=True
            ),
            "redis": SecretConfig(
                secret_name=f"scorpius/{self.environment}/redis", 
                required=True
            ),
            "jwt": SecretConfig(
                secret_name=f"scorpius/{self.environment}/jwt-secret",
                required=True
            ),
            "web3": SecretConfig(
                secret_name=f"scorpius/{self.environment}/web3-providers",
                required=True
            ),
            "coinbase": SecretConfig(
                secret_name=f"scorpius/{self.environment}/coinbase-api",
                required=False
            )
        }
        
        # Retrieve secrets
        try:
            secrets = secrets_manager.get_secrets_batch(secret_configs)
            
            # Map secrets to settings
            if "database" in secrets:
                db_config = secrets["database"]
                if isinstance(db_config, dict):
                    self.database_url = db_config.get("url")
                else:
                    self.database_url = db_config
            
            if "redis" in secrets:
                redis_config = secrets["redis"]
                if isinstance(redis_config, dict):
                    self.redis_url = redis_config.get("url")
                else:
                    self.redis_url = redis_config
            
            if "jwt" in secrets:
                jwt_config = secrets["jwt"]
                if isinstance(jwt_config, dict):
                    self.jwt_secret_key = jwt_config.get("secret_key")
                else:
                    self.jwt_secret_key = jwt_config
            
            if "web3" in secrets:
                web3_config = secrets["web3"]
                if isinstance(web3_config, dict):
                    self.web3_provider_url = web3_config.get("infura_url")
                else:
                    self.web3_provider_url = web3_config
            
            if "coinbase" in secrets:
                coinbase_config = secrets["coinbase"]
                if isinstance(coinbase_config, dict):
                    self.coinbase_api_key = coinbase_config.get("api_key")
                else:
                    self.coinbase_api_key = coinbase_config
            
            logger.info("✅ Successfully loaded secrets from AWS Secrets Manager")
            
        except Exception as e:
            logger.error(f"❌ Failed to load secrets from AWS Secrets Manager: {e}")
            raise RuntimeError("Failed to initialize secure configuration")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
@lru_cache()
def get_settings() -> SecureSettings:
    """Get cached settings instance"""
    return SecureSettings()


# Convenience functions
def get_database_url() -> str:
    """Get database URL with fail-fast behavior"""
    settings = get_settings()
    if not settings.database_url:
        raise RuntimeError("Database URL not configured")
    return settings.database_url


def get_redis_url() -> str:
    """Get Redis URL with fail-fast behavior"""
    settings = get_settings()
    if not settings.redis_url:
        raise RuntimeError("Redis URL not configured")
    return settings.redis_url


def get_jwt_secret() -> str:
    """Get JWT secret with fail-fast behavior"""
    settings = get_settings()
    if not settings.jwt_secret_key:
        raise RuntimeError("JWT secret not configured")
    return settings.jwt_secret_key
