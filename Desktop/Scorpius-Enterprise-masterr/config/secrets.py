from typing import Optional

import boto3
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings


class SecretsManager:
    def __init__(self):
        self.client = boto3.client("secretsmanager")

    def get_secret(self, secret_name: str) -> Optional[str]:
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return response["SecretString"]
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                raise ValueError(f"Secret {secret_name} not found")
            raise


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        secrets_manager = SecretsManager()

        # Load secrets from AWS Secrets Manager
        try:
            secrets = secrets_manager.get_secret("scorpius-enterprise-secrets")
            secrets_dict = json.loads(secrets)

            # Update settings with secrets
            for key, value in secrets_dict.items():
                setattr(self, key, value)
        except Exception as e:
            print(f"Warning: Failed to load secrets from AWS Secrets Manager: {e}")
            # Fall back to environment variables
            pass


settings = Settings()
