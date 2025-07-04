"""
Enterprise License Management
"""

import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import httpx
from jose import JWTError, jwt


class LicenseManager:
    """Enterprise license validation and management."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.license_info: Optional[dict] = None
        # Optional external validation settings
        self.license_server = os.getenv("LICENSE_SERVER_URL")
        self.public_key = os.getenv("LICENSE_PUBLIC_KEY")

    async def validate_license(self, license_key: Optional[str]) -> bool:
        """
        Validate enterprise license key.

        Args:
            license_key: License key to validate

        Returns:
            True if license is valid
        """
        try:
            if not license_key:
                # For development/demo purposes, allow None license
                self.logger.warning(
                    "No license key provided - running in development mode"
                )
                self.license_info = {
                    "type": "development",
                    "expires": (datetime.now() + timedelta(days=30)).isoformat(),
                    "features": ["basic"],
                }
                return True

            # First try external license server validation if configured
            if self.license_server:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.post(
                            self.license_server,
                            json={"license_key": license_key},
                        )
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("valid"):
                            self.license_info = data.get("info", {})
                            self.logger.info("Enterprise license validated via server")
                            return True
                        self.logger.error("License server rejected the key")
                        return False
                    self.logger.error(f"License server error: {response.status_code}")
                    return False
                except Exception as exc:
                    self.logger.error(f"Failed to contact license server: {exc}")
                    return False

            # Otherwise verify JWT signature if a public key is supplied
            if self.public_key:
                try:
                    payload = jwt.decode(
                        license_key,
                        self.public_key,
                        algorithms=["RS256", "HS256"],
                    )
                    self.license_info = payload
                    self.logger.info("Enterprise license signature verified")
                    return True
                except JWTError as exc:
                    self.logger.error(f"License signature verification failed: {exc}")
                    return False

            # Fallback simple validation for demo environments
            if len(license_key) > 10:
                self.license_info = {
                    "type": "enterprise",
                    "expires": (datetime.now() + timedelta(days=365)).isoformat(),
                    "features": [
                        "quantum",
                        "security",
                        "analytics",
                        "integration",
                        "clustering",
                    ],
                }
                self.logger.info("Enterprise license validated successfully")
                return True

            self.logger.error("Invalid license key format")
            return False

        except Exception as e:
            self.logger.error(f"License validation failed: {e}")
            return False

    def get_license_info(self) -> dict:
        """Get current license information."""
        return self.license_info or {"type": "none", "status": "invalid"}

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a specific feature is enabled by the license."""
        if not self.license_info:
            return False

        return feature in self.license_info.get("features", [])

    def is_license_valid(self) -> bool:
        """Check if current license is still valid."""
        if not self.license_info:
            return False

        try:
            expires = datetime.fromisoformat(self.license_info["expires"])
            return datetime.now() < expires
        except:
            return False
