"""AWS Systems Manager Parameter Store integration for configuration secrets.

Provides cached retrieval of secure string parameters with optional fallback to
environment variables.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Optional

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from pydantic import BaseSettings

logger = logging.getLogger(__name__)


class ParameterStoreConfig(BaseSettings):
    """Configuration options for Parameter Store access."""

    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None

    parameters_prefix: str = "/scorpius/"
    cache_ttl: int = 300  # seconds – currently unused, placeholder for future
    fail_fast: bool = True

    class Config:
        env_prefix = "PARAM_STORE_"


class ParameterStore:
    """Lightweight wrapper around AWS SSM Parameter Store."""

    def __init__(self, cfg: Optional[ParameterStoreConfig] = None):
        self.cfg = cfg or ParameterStoreConfig()
        self._client = None
        self._cache: dict[str, str] = {}

    @property
    def client(self):
        if self._client is None:
            try:
                session = boto3.Session(
                    aws_access_key_id=self.cfg.aws_access_key_id,
                    aws_secret_access_key=self.cfg.aws_secret_access_key,
                    region_name=self.cfg.aws_region,
                )
                self._client = session.client("ssm")

                # Simple connectivity check
                self._client.get_parameters(Names=["test"], WithDecryption=False)
            except (NoCredentialsError, ClientError) as exc:
                if self.cfg.fail_fast:
                    logger.error(
                        "Unable to connect to AWS SSM Parameter Store: %s", exc
                    )
                    raise RuntimeError(
                        "AWS credentials required for Parameter Store"
                    ) from exc
                logger.warning(
                    "Parameter Store unavailable – falling back to env vars: %s", exc
                )
                self._client = None
        return self._client

    def _parameter_name(self, name: str) -> str:
        if name.startswith("/"):
            return name  # assume fully-qualified path supplied
        return f"{self.cfg.parameters_prefix}{name}"

    def get_parameter(
        self, name: str, *, default: Optional[str] = None
    ) -> Optional[str]:
        path = self._parameter_name(name)
        if path in self._cache:
            return self._cache[path]

        if self.client is not None:
            try:
                response = self.client.get_parameter(Name=path, WithDecryption=True)
                value = response["Parameter"]["Value"]
                self._cache[path] = value
                logger.debug("Fetched parameter '%s' from Parameter Store", path)
                return value
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                if code == "ParameterNotFound":
                    logger.warning("Parameter '%s' not found", path)
                else:
                    logger.error("Error fetching parameter '%s': %s", path, exc)
                if self.cfg.fail_fast:
                    raise RuntimeError(
                        f"Failed to fetch parameter {name}: {exc}"
                    ) from exc

        # Fallback to env var
        env_var = name.strip("/").upper().replace("/", "_")
        env_val = os.getenv(env_var, default)
        if env_val is not None:
            logger.debug("Using environment variable for parameter '%s'", name)
            self._cache[path] = env_val
        return env_val

    def clear_cache(self):
        self._cache.clear()


@lru_cache(maxsize=1)
def get_parameter_store() -> ParameterStore:
    return ParameterStore()


def get_parameter(name: str, default: Optional[str] = None) -> Optional[str]:
    return get_parameter_store().get_parameter(name, default=default)
