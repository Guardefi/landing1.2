"""System Settings management for Scorpius API Gateway.

Settings are persisted to a JSON file on disk (default: /app/config/system_settings.json)
so that they survive container restarts without requiring a database.

In production you might swap this for a proper DB or Parameter Store mapping.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, Field

DEFAULT_SETTINGS_PATH = os.getenv(
    "SCORPIUS_SYSTEM_SETTINGS_PATH", "/app/config/system_settings.json"
)


class PluginsSettings(BaseModel):
    slither: bool = True
    mythx: bool = False
    manticore: bool = True
    mythril: bool = True
    echidna: bool = False


class SystemSettings(BaseModel):
    # API Keys
    slitherApiKey: str = ""
    mythxApiKey: str = ""
    mantecoreApiKey: str = ""
    mythrilApiKey: str = ""

    # RPC URLs
    ethereumRpc: str = "https://mainnet.infura.io/v3/"
    polygonRpc: str = "https://polygon-mainnet.infura.io/v3/"
    bscRpc: str = "https://bsc-dataseed.binance.org/"
    arbitrumRpc: str = "https://arb1.arbitrum.io/rpc"

    # Wallet Configuration
    privateKey: str = ""
    walletAddress: str = ""

    # Notification Settings
    slackWebhook: str = ""
    telegramBotToken: str = ""
    telegramChatId: str = ""
    emailNotifications: bool = True

    # Plugin Settings
    plugins: PluginsSettings = Field(default_factory=PluginsSettings)

    # System Settings
    autoScan: bool = True
    realTimeMonitoring: bool = True
    advancedLogging: bool = False

    class Config:
        allow_population_by_field_name = True


class SettingsStore:
    """File-based settings store."""

    def __init__(self, path: str | Path = DEFAULT_SETTINGS_PATH):
        self._path = Path(path)
        # Ensure directory exists
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            # Create file with defaults
            self.save(SystemSettings().model_dump(mode="json"))

    def load(self) -> Dict[str, Any]:
        try:
            with self._path.open("r", encoding="utf-8") as fp:
                return json.load(fp)
        except (FileNotFoundError, json.JSONDecodeError):
            return SystemSettings().model_dump(mode="json")

    def save(self, data: Dict[str, Any]) -> None:
        with self._path.open("w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=2)


_store = SettingsStore()


def get_settings() -> SystemSettings:
    return SystemSettings(**_store.load())


def update_settings(new_settings: SystemSettings) -> SystemSettings:
    _store.save(new_settings.model_dump(mode="json"))
    return new_settings
