"""
Main quantum cryptography engine for Scorpius.
Provides unified interface for all quantum-resistant algorithms.
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any

from ..config import QuantumConfig
from ..core.types import (
    KeyStatus,
    QuantumAlgorithm,
    QuantumChannel,
    QuantumKey,
    QuantumSignature,
    SecurityLevel,
)
from ..crypto.lattice import LatticeBasedCrypto
from ..exceptions import (
    AlgorithmNotSupportedError,
    EncryptionError,
    InvalidKeyError,
    KeyGenerationError,
    KeyNotFoundError,
)
from ..utils.performance import performance_monitor, track_performance


class QuantumCryptographyEngine:
    """
    Main quantum cryptography engine for Scorpius.
    Provides unified interface for all quantum-resistant algorithms.
    """

    def __init__(self, config: QuantumConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.QuantumCryptographyEngine")

        # Initialize algorithm implementations
        try:
            self.lattice_crypto = LatticeBasedCrypto(
                SecurityLevel(config.default_security_level)
            )
            self.logger.info("Lattice-based crypto initialized")

            # Hash-based signatures would be initialized here
            # self.hash_signatures = HashBasedSignatures(...)

            # QKD would be initialized here
            # self.qkd = QuantumKeyDistribution()

        except Exception as e:
            raise KeyGenerationError(
                f"Failed to initialize crypto algorithms: {e}"
            ) from e

        # Key management with expiry
        self.keys: dict[str, QuantumKey] = {}
        self.signatures: dict[str, QuantumSignature] = {}
        self.channels: dict[str, QuantumChannel] = {}

        # Performance monitoring
        self.performance_stats = {
            "key_generations": 0,
            "encryptions": 0,
            "decryptions": 0,
            "signatures": 0,
            "verifications": 0,
            "total_time": 0.0,
            "engine_start_time": datetime.now(),
        }

        # Start background tasks
        if config.key_expiry_hours > 0:
            asyncio.create_task(self._key_cleanup_task())

        self.logger.info("Quantum cryptography engine initialized successfully")

    async def _key_cleanup_task(self):
        """Background task to clean up expired keys."""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []
                overused_keys = []

                for key_id, key in self.keys.items():
                    if key.is_expired():
                        expired_keys.append(key_id)
                        key.status = KeyStatus.EXPIRED
                    elif key.is_overused():
                        overused_keys.append(key_id)
                        key.status = KeyStatus.REVOKED

                # Remove expired and overused keys
                for key_id in expired_keys + overused_keys:
                    del self.keys[key_id]

                if expired_keys or overused_keys:
                    self.logger.info(
                        f"Cleaned up {len(expired_keys)} expired and "
                        f"{len(overused_keys)} overused keys"
                    )

                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                self.logger.error(f"Key cleanup error: {e}")
                await asyncio.sleep(3600)

    @track_performance(
        "keypair_generation", QuantumAlgorithm.LATTICE_BASED, SecurityLevel.LEVEL_3
    )
    async def generate_keypair(
        self,
        algorithm: QuantumAlgorithm,
        security_level: SecurityLevel = SecurityLevel.LEVEL_3,
        max_usage: int | None = None,
        expiry_hours: int | None = None,
    ) -> tuple[str, str]:
        """
        Generate quantum-resistant keypair.

        Args:
            algorithm: Quantum-resistant algorithm to use
            security_level: Security level for the keys
            max_usage: Maximum number of times the key can be used
            expiry_hours: Hours until key expires

        Returns:
            Tuple of (public_key_id, private_key_id)
        """
        start_time = time.time()

        try:
            self.logger.debug(
                f"Generating {algorithm.value} keypair at level {security_level.value}"
            )

            if algorithm == QuantumAlgorithm.LATTICE_BASED:
                public_key, private_key = self.lattice_crypto.generate_keypair()
            else:
                raise AlgorithmNotSupportedError(
                    f"Algorithm {algorithm.value} not yet implemented"
                )

            # Set expiry time
            if expiry_hours is None:
                expiry_hours = self.config.key_expiry_hours

            if expiry_hours > 0:
                expiry_time = datetime.now() + timedelta(hours=expiry_hours)
                public_key.expiry_time = expiry_time
                private_key.expiry_time = expiry_time

            # Set usage limits
            if max_usage is None:
                max_usage = self.config.max_key_usage

            if max_usage > 0:
                public_key.max_usage = max_usage
                private_key.max_usage = max_usage

            # Store keys
            public_key_id = public_key.key_id
            private_key_id = private_key.key_id

            self.keys[public_key_id] = public_key
            self.keys[private_key_id] = private_key

            # Update stats
            self.performance_stats["key_generations"] += 1
            self.performance_stats["total_time"] += time.time() - start_time

            self.logger.info(
                f"Generated {algorithm.value} keypair: {public_key_id[:8]}..."
            )

            return public_key_id, private_key_id

        except Exception as e:
            self.logger.error(f"Keypair generation failed: {e}")
            raise KeyGenerationError(f"Failed to generate keypair: {e}") from e

    async def encrypt_message(self, message: bytes, public_key_id: str) -> str:
        """
        Encrypt message with quantum-resistant encryption.

        Args:
            message: Message to encrypt
            public_key_id: Public key identifier

        Returns:
            Encrypted result identifier
        """
        start_time = time.time()

        try:
            if public_key_id not in self.keys:
                raise KeyNotFoundError(f"Public key {public_key_id} not found")

            public_key = self.keys[public_key_id]

            if not public_key.is_valid():
                raise InvalidKeyError("Public key is not valid for encryption")

            self.logger.debug(
                f"Encrypting {len(message)} bytes with {public_key.algorithm.value}"
            )

            if public_key.algorithm == QuantumAlgorithm.LATTICE_BASED:
                encrypted_result = self.lattice_crypto.encrypt(message, public_key)
            else:
                raise AlgorithmNotSupportedError(
                    f"Encryption not supported for {public_key.algorithm.value}"
                )

            # Store result (in production, might store in database)
            result_id = encrypted_result.encryption_id
            # For now, we don't store the encrypted result, but in production you would

            # Update key usage
            public_key.increment_usage()

            # Update stats
            self.performance_stats["encryptions"] += 1
            self.performance_stats["total_time"] += time.time() - start_time

            self.logger.info(f"Encrypted message with {public_key.algorithm.value}")

            return result_id

        except Exception as e:
            self.logger.error(f"Message encryption failed: {e}")
            raise EncryptionError(f"Failed to encrypt message: {e}") from e

    async def get_public_key(self, key_id: str) -> QuantumKey:
        """Get a public key by ID."""
        if key_id not in self.keys:
            raise KeyNotFoundError(f"Key {key_id} not found")

        key = self.keys[key_id]
        if key.private_key is not None:
            # Return a copy with no private key data
            public_only = QuantumKey(
                algorithm=key.algorithm,
                security_level=key.security_level,
                public_key=key.public_key,
                private_key=None,
                parameters=key.parameters.copy(),
                creation_time=key.creation_time,
                expiry_time=key.expiry_time,
                usage_count=key.usage_count,
                max_usage=key.max_usage,
                status=key.status,
                key_id=key.key_id,
            )
            return public_only

        return key

    async def list_keys(
        self, algorithm: QuantumAlgorithm | None = None, include_expired: bool = False
    ) -> list[dict[str, Any]]:
        """List available keys with metadata."""
        keys_info = []

        for key_id, key in self.keys.items():
            if algorithm and key.algorithm != algorithm:
                continue

            if not include_expired and not key.is_valid():
                continue

            keys_info.append(
                {
                    "key_id": key_id,
                    "algorithm": key.algorithm.value,
                    "security_level": key.security_level.value,
                    "is_private": key.private_key is not None,
                    "status": key.status.value,
                    "creation_time": key.creation_time.isoformat(),
                    "expiry_time": (
                        key.expiry_time.isoformat() if key.expiry_time else None
                    ),
                    "usage_count": key.usage_count,
                    "max_usage": key.max_usage,
                    "is_valid": key.is_valid(),
                }
            )

        return keys_info

    async def revoke_key(self, key_id: str, reason: str = "Manual revocation") -> bool:
        """Revoke a key."""
        if key_id not in self.keys:
            raise KeyNotFoundError(f"Key {key_id} not found")

        key = self.keys[key_id]
        key.status = KeyStatus.REVOKED

        self.logger.info(f"Revoked key {key_id}: {reason}")
        return True

    async def get_performance_stats(self) -> dict[str, Any]:
        """Get quantum cryptography performance statistics."""
        stats = self.performance_stats.copy()

        # Calculate averages
        if stats["key_generations"] > 0:
            stats["avg_keygen_time"] = stats["total_time"] / stats["key_generations"]

        if stats["encryptions"] > 0:
            stats["avg_encryption_time"] = stats["total_time"] / stats["encryptions"]

        # Add current state
        stats["total_keys"] = len(self.keys)
        stats["total_signatures"] = len(self.signatures)
        stats["total_channels"] = len(self.channels)
        stats["uptime_hours"] = (
            datetime.now() - stats["engine_start_time"]
        ).total_seconds() / 3600

        # Add global performance stats
        stats["global_performance"] = performance_monitor.get_global_stats()

        return stats

    async def quantum_security_audit(self) -> dict[str, Any]:
        """Perform quantum security audit."""
        audit_results = {
            "timestamp": datetime.now().isoformat(),
            "total_keys": len(self.keys),
            "algorithm_distribution": {},
            "security_level_distribution": {},
            "expired_keys": 0,
            "overused_keys": 0,
            "compromised_keys": 0,
            "valid_keys": 0,
            "recommendations": [],
        }

        # Analyze key distribution
        for key in self.keys.values():
            alg = key.algorithm.value
            audit_results["algorithm_distribution"][alg] = (
                audit_results["algorithm_distribution"].get(alg, 0) + 1
            )

            level = key.security_level.value
            audit_results["security_level_distribution"][level] = (
                audit_results["security_level_distribution"].get(level, 0) + 1
            )

            # Check key status
            if key.is_expired():
                audit_results["expired_keys"] += 1
            elif key.is_overused():
                audit_results["overused_keys"] += 1
            elif key.status == KeyStatus.COMPROMISED:
                audit_results["compromised_keys"] += 1
            elif key.is_valid():
                audit_results["valid_keys"] += 1

        # Generate recommendations
        if audit_results["expired_keys"] > 0:
            audit_results["recommendations"].append(
                f"Rotate {audit_results['expired_keys']} expired keys"
            )

        if audit_results["overused_keys"] > 0:
            audit_results["recommendations"].append(
                f"Replace {audit_results['overused_keys']} overused keys"
            )

        if audit_results["compromised_keys"] > 0:
            audit_results["recommendations"].append(
                f"Immediately revoke {audit_results['compromised_keys']} compromised keys"
            )

        # Check algorithm diversity
        if len(audit_results["algorithm_distribution"]) < 2:
            audit_results["recommendations"].append(
                "Consider using multiple quantum-resistant algorithms for defense in depth"
            )

        # Check security level distribution
        low_security_keys = audit_results["security_level_distribution"].get(1, 0)
        if low_security_keys > audit_results["total_keys"] * 0.5:
            audit_results["recommendations"].append(
                "Consider upgrading keys to higher security levels"
            )

        return audit_results

    async def cleanup(self) -> None:
        """Cleanup resources."""
        self.logger.info("Cleaning up quantum cryptography engine")

        # Clear sensitive data
        for key in self.keys.values():
            if key.private_key:
                # In production, securely wipe memory
                pass

        self.keys.clear()
        self.signatures.clear()
        self.channels.clear()

        self.logger.info("Quantum cryptography engine cleanup complete")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            # This won't work for async cleanup, but better than nothing
            self.keys.clear()
            self.signatures.clear()
            self.channels.clear()
        except:
            pass
