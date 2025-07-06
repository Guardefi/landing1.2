"""
Enterprise License Management
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Optional


class LicenseManager:
    """Enterprise license validation and management."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.license_info: Optional[dict] = None

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

            # In a real implementation, this would validate against a license server
            # For now, we'll accept any non-empty string as valid
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
