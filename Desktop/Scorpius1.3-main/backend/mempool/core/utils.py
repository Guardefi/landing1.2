import asyncio
import functools
import hashlib
import json
import logging
import re
import time
from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from typing import Any, Dict, List, Optional, TypeVar

getcontext().prec = 50
logger = logging.getLogger(__name__)

T = TypeVar("T")


def async_retry(retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """
    Decorator for async functions that provides retry logic with exponential backoff.

    Args:
        retries: Number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry

    Returns:
        Decorated function with retry logic
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            _delay = delay
            for i in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:
                        logger.error(
                            f"Function {func.__name__} failed after {retries} retries: {e}"
                        )
                        raise e from e
                    logger.warning(
                        f"Attempt {i+1} for {func.__name__} failed: {e}. Retrying in {_delay:.2f}s..."
                    )
                    await asyncio.sleep(_delay)
                    _delay *= backoff

        return wrapper

    return decorator


def ether_to_wei(eth_value: float) -> int:
    """
    Convert Ether value to Wei.

    Args:
        eth_value: Value in Ether

    Returns:
        Value in Wei

    Raises:
        TypeError: If eth_value is not a number
    """
    if not isinstance(eth_value, int | float | Decimal):
        raise TypeError("eth_value must be a number") from None
    return int(Decimal(str(eth_value)) * Decimal(10**18))


def wei_to_ether(wei_value: int) -> float:
    """
    Convert Wei value to Ether.

    Args:
        wei_value: Value in Wei

    Returns:
        Value in Ether

    Raises:
        TypeError: If wei_value is not an integer or Decimal
    """
    if not isinstance(wei_value, int | Decimal):
        raise TypeError("wei_value must be an integer or Decimal") from None
    return float(Decimal(str(wei_value)) / Decimal(10**18))


def calculate_risk_score(transaction_data: Dict[str, Any]) -> float:
    """
    Calculate a risk score for a transaction based on various factors.

    Args:
        transaction_data: Dictionary containing transaction information

    Returns:
        Risk score between 0.0 (low risk) and 1.0 (high risk)
    """
    risk_factors = []

    try:
        # Gas price analysis
        gas_price = float(transaction_data.get("gas_price", 0))
        if gas_price > 100_000_000_000:  # > 100 Gwei
            risk_factors.append(("high_gas_price", 0.3))
        elif gas_price > 50_000_000_000:  # > 50 Gwei
            risk_factors.append(("elevated_gas_price", 0.15))

        # Value analysis
        value = float(transaction_data.get("value", 0))
        if value > 10**18:  # > 1 ETH
            risk_factors.append(("high_value", 0.2))
        elif value > 10**17:  # > 0.1 ETH
            risk_factors.append(("medium_value", 0.1))

        # Address analysis
        from_address = transaction_data.get("from_address", "")
        to_address = transaction_data.get("to_address", "")

        # Check if addresses are new (placeholder logic)
        if _is_new_address(from_address):
            risk_factors.append(("new_sender", 0.25))

        if _is_new_address(to_address):
            risk_factors.append(("new_recipient", 0.2))

        # Check for suspicious patterns
        if _has_suspicious_data_pattern(transaction_data.get("data", "")):
            risk_factors.append(("suspicious_data", 0.4))

        # MEV patterns
        mev_patterns = transaction_data.get("mev_patterns", [])
        if mev_patterns:
            risk_factors.append(("mev_detected", 0.35))

        # Contract interaction analysis
        if _is_contract_interaction(transaction_data):
            risk_factors.append(("contract_interaction", 0.1))

        # Time-based factors
        if _is_off_hours_transaction(transaction_data.get("timestamp", 0)):
            risk_factors.append(("off_hours", 0.05))

        # Calculate final risk score
        if not risk_factors:
            return 0.0

        # Weight and combine risk factors
        total_risk = 0.0
        for factor_name, weight in risk_factors:
            total_risk += weight

        # Apply diminishing returns for multiple factors
        if len(risk_factors) > 1:
            total_risk = total_risk * (1 - 0.1 * (len(risk_factors) - 1))

        # Ensure score is between 0 and 1
        return min(1.0, max(0.0, total_risk))

    except Exception:
        # If calculation fails, return medium risk
        return 0.5


def validate_ethereum_address(address: str) -> bool:
    """
    Validate Ethereum address format.

    Args:
        address: Address string to validate

    Returns:
        True if valid Ethereum address format
    """
    if not address:
        return False

    # Check if it starts with 0x and has correct length
    if not address.startswith("0x") or len(address) != 42:
        return False

    # Check if all characters after 0x are valid hex
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False


def validate_transaction_hash(tx_hash: str) -> bool:
    """
    Validate transaction hash format.

    Args:
        tx_hash: Transaction hash to validate

    Returns:
        True if valid transaction hash format
    """
    if not tx_hash:
        return False

    # Check if it starts with 0x and has correct length (64 hex chars + 0x)
    if not tx_hash.startswith("0x") or len(tx_hash) != 66:
        return False

    # Check if all characters after 0x are valid hex
    try:
        int(tx_hash[2:], 16)
        return True
    except ValueError:
        return False


def normalize_hex_value(hex_str: str) -> str:
    """
    Normalize hex string to standard format.

    Args:
        hex_str: Hex string to normalize

    Returns:
        Normalized hex string with 0x prefix and lowercase
    """
    if not hex_str:
        return "0x0"

    # Remove any whitespace
    hex_str = hex_str.strip()

    # Add 0x prefix if missing
    if not hex_str.startswith("0x"):
        hex_str = "0x" + hex_str

    # Convert to lowercase
    return hex_str.lower()


def sanitize_transaction_data(tx_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize and validate transaction data.

    Args:
        tx_data: Raw transaction data

    Returns:
        Sanitized transaction data
    """
    sanitized = {}

    # Required fields with validation
    required_fields = {
        "hash": validate_transaction_hash,
        "from_address": validate_ethereum_address,
        "chain_id": lambda x: isinstance(x, int) and x > 0,
    }

    for field, validator in required_fields.items():
        value = tx_data.get(field)
        if value and validator(value):
            sanitized[field] = value
        else:
            # Handle missing required fields
            if field == "chain_id":
                sanitized[field] = 1  # Default to Ethereum mainnet

    # Optional fields with normalization
    optional_fields = {
        "to_address": lambda x: normalize_hex_value(x) if x else None,
        "value": lambda x: normalize_hex_value(x) if x else "0x0",
        "gas": lambda x: normalize_hex_value(x) if x else "0x0",
        "gas_price": lambda x: normalize_hex_value(x) if x else "0x0",
        "data": lambda x: normalize_hex_value(x) if x else "0x",
        "nonce": lambda x: normalize_hex_value(x) if x else "0x0",
    }

    for field, normalizer in optional_fields.items():
        value = tx_data.get(field)
        if value is not None:
            try:
                sanitized[field] = normalizer(value)
            except Exception:
                # Use default if normalization fails
                sanitized[field] = "0x0" if field != "data" else "0x"

    # Timestamp handling
    timestamp = tx_data.get("timestamp")
    if timestamp:
        try:
            sanitized["timestamp"] = int(timestamp)
        except (ValueError, TypeError):
            sanitized["timestamp"] = int(time.time())
    else:
        sanitized["timestamp"] = int(time.time())

    return sanitized


# Helper functions (internal use)
def _is_new_address(address: str) -> bool:
    """Check if address appears to be new (placeholder logic)."""
    # In production, this would check against a database of known addresses
    # For now, use simple heuristics
    if not address:
        return False

    # Very basic heuristic - addresses with repeating patterns might be new/generated
    hex_part = address[2:] if address.startswith("0x") else address

    # Check for obvious patterns
    if len(set(hex_part)) < 10:  # Too few unique characters
        return True

    if hex_part.count("0") > len(hex_part) * 0.7:  # Too many zeros
        return True

    return False


def _has_suspicious_data_pattern(data: str) -> bool:
    """Check for suspicious patterns in transaction data."""
    if not data or data == "0x":
        return False

    # Check for unusually long data (potential for complex operations)
    if len(data) > 10000:
        return True

    # Check for patterns that might indicate obfuscation
    hex_part = data[2:] if data.startswith("0x") else data

    # Look for repetitive patterns
    if len(hex_part) > 100:
        # Check for repeating chunks
        for chunk_size in [8, 16, 32]:
            if len(hex_part) >= chunk_size * 3:
                chunks = [
                    hex_part[i : i + chunk_size]
                    for i in range(0, len(hex_part), chunk_size)
                ]
                if len(set(chunks)) < len(chunks) * 0.5:  # More than 50% repetition
                    return True

    return False


def _is_contract_interaction(tx_data: Dict[str, Any]) -> bool:
    """Check if transaction is a contract interaction."""
    data = tx_data.get("data", "")

    # If there's significant data, it's likely a contract call
    if data and data != "0x" and len(data) > 10:
        return True

    # Check for zero value transactions (often contract interactions)
    value = tx_data.get("value", "0")
    if value == "0" or value == "0x0":
        return True

    return False


def _is_off_hours_transaction(timestamp: int) -> bool:
    """Check if transaction occurred during off-hours (placeholder logic)."""
    if not timestamp:
        return False

    try:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        hour = dt.hour

        # Consider 2 AM to 6 AM UTC as off-hours
        return 2 <= hour <= 6
    except (ValueError, OSError):
        return False


import functools
from collections.abc import Callable
from decimal import Decimal
from typing import Any
