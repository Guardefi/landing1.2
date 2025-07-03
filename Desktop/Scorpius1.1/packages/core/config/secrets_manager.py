"""
AWS Secrets Manager integration for secure configuration management.
Provides fail-fast secret loading with automatic rotation support.
"""

import json
import logging
import os
from typing import Any, Dict, Optional
from functools import lru_cache

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pydantic import BaseSettings, validator

logger = logging.getLogger(__name__)


class SecretsManagerConfig(BaseSettings):
    """Configuration for AWS Secrets Manager."""
    
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Secrets configuration
    secrets_prefix: str = "scorpius/"
    cache_ttl: int = 300  # 5 minutes
    fail_fast: bool = True
    
    class Config:
        env_prefix = "SECRETS_"


class SecretsManager:
    """Secure secrets management using AWS Secrets Manager."""
    
    def __init__(self, config: Optional[SecretsManagerConfig] = None):
        self.config = config or SecretsManagerConfig()
        self._client = None
        self._cache = {}
        
    @property
    def client(self):
        """Lazy initialization of AWS Secrets Manager client."""
        if self._client is None:
            try:
                session = boto3.Session(
                    aws_access_key_id=self.config.aws_access_key_id,
                    aws_secret_access_key=self.config.aws_secret_access_key,
                    region_name=self.config.aws_region
                )
                self._client = session.client('secretsmanager')
                
                # Test connection
                self._client.list_secrets(MaxResults=1)
                logger.info("Successfully connected to AWS Secrets Manager")
                
            except NoCredentialsError as e:
                if self.config.fail_fast:
                    logger.error("AWS credentials not found")
                    raise RuntimeError("AWS credentials required for Secrets Manager") from e
                logger.warning("AWS credentials not found, falling back to environment variables")
                self._client = None
            except ClientError as e:
                if self.config.fail_fast:
                    logger.error(f"Failed to connect to AWS Secrets Manager: {e}")
                    raise RuntimeError(f"AWS Secrets Manager connection failed: {e}") from e
                logger.warning(f"AWS Secrets Manager not available: {e}")
                self._client = None
                
        return self._client
    
    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret value from AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret (without prefix)
            default: Default value if secret not found and fail_fast is False
            
        Returns:
            Secret value or default
            
        Raises:
            RuntimeError: If secret not found and fail_fast is True
        """
        full_secret_name = f"{self.config.secrets_prefix}{secret_name}"
        
        # Check cache first
        cache_key = f"{full_secret_name}:{hash(self.config.aws_region)}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Try AWS Secrets Manager
        if self.client:
            try:
                response = self.client.get_secret_value(SecretId=full_secret_name)
                secret_value = response['SecretString']
                
                # Cache the secret
                self._cache[cache_key] = secret_value
                logger.debug(f"Retrieved secret '{secret_name}' from AWS Secrets Manager")
                return secret_value
                
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    logger.warning(f"Secret '{full_secret_name}' not found in AWS Secrets Manager")
                else:
                    logger.error(f"Error retrieving secret '{full_secret_name}': {e}")
                    
                if self.config.fail_fast:
                    raise RuntimeError(f"Failed to retrieve secret '{secret_name}': {e}") from e
        
        # Fallback to environment variable
        env_var = secret_name.upper().replace('-', '_').replace('/', '_')
        env_value = os.getenv(env_var, default)
        
        if env_value is None and self.config.fail_fast:
            raise RuntimeError(f"Secret '{secret_name}' not found in AWS Secrets Manager or environment")
        
        if env_value:
            logger.debug(f"Retrieved secret '{secret_name}' from environment variable")
            self._cache[cache_key] = env_value
            
        return env_value
    
    def get_secret_json(self, secret_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retrieve a JSON secret from AWS Secrets Manager.
        
        Args:
            secret_name: Name of the secret
            default: Default dictionary if secret not found
            
        Returns:
            Parsed JSON secret as dictionary
        """
        secret_value = self.get_secret(secret_name)
        if secret_value is None:
            return default or {}
            
        try:
            return json.loads(secret_value)
        except json.JSONDecodeError as e:
            if self.config.fail_fast:
                raise RuntimeError(f"Secret '{secret_name}' contains invalid JSON: {e}") from e
            logger.warning(f"Secret '{secret_name}' contains invalid JSON, using default")
            return default or {}
    
    def rotate_secret(self, secret_name: str) -> bool:
        """
        Trigger rotation for a secret.
        
        Args:
            secret_name: Name of the secret to rotate
            
        Returns:
            True if rotation was triggered successfully
        """
        if not self.client:
            logger.warning("AWS Secrets Manager not available, cannot rotate secret")
            return False
            
        full_secret_name = f"{self.config.secrets_prefix}{secret_name}"
        
        try:
            self.client.rotate_secret(SecretId=full_secret_name)
            logger.info(f"Triggered rotation for secret '{secret_name}'")
            
            # Clear cache
            cache_key = f"{full_secret_name}:{hash(self.config.aws_region)}"
            self._cache.pop(cache_key, None)
            
            return True
            
        except ClientError as e:
            logger.error(f"Failed to rotate secret '{secret_name}': {e}")
            return False
    
    def clear_cache(self):
        """Clear the secrets cache."""
        self._cache.clear()
        logger.debug("Secrets cache cleared")


# Global secrets manager instance
@lru_cache(maxsize=1)
def get_secrets_manager() -> SecretsManager:
    """Get a singleton instance of the secrets manager."""
    return SecretsManager()


# Convenience functions
def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
    """Convenience function to get a secret value."""
    return get_secrets_manager().get_secret(secret_name, default)


def get_secret_json(secret_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Convenience function to get a JSON secret."""
    return get_secrets_manager().get_secret_json(secret_name, default)


class SecureSettings(BaseSettings):
    """Base settings class that loads secrets from AWS Secrets Manager."""
    
    def __init__(self, **kwargs):
        # Load secrets before initializing
        secrets_manager = get_secrets_manager()
        
        # Override with secrets if available
        for field_name, field_info in self.__fields__.items():
            if field_name not in kwargs:
                secret_value = secrets_manager.get_secret(
                    field_name.replace('_', '-'),
                    default=field_info.default if field_info.default is not ... else None
                )
                if secret_value is not None:
                    kwargs[field_name] = secret_value
        
        super().__init__(**kwargs)
