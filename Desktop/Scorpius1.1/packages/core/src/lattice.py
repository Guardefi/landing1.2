"""
Lattice-based cryptography implementation.
Resistant to both classical and quantum attacks.
"""

import logging
import secrets
from typing import Any

import numpy as np

from ..core.types import (
    QuantumAlgorithm,
    QuantumEncryptionResult,
    QuantumKey,
    SecurityLevel,
)
from ..exceptions import DecryptionError, EncryptionError, KeyGenerationError


class LatticeBasedCrypto:
    """
    Lattice-based cryptography implementation.
    Uses NTRU-like encryption scheme with configurable security levels.
    """

    def __init__(self, security_level: SecurityLevel = SecurityLevel.LEVEL_3):
        self.security_level = security_level
        self.logger = logging.getLogger(f"{__name__}.LatticeBasedCrypto")

        # Set parameters based on security level
        self.params = self._get_lattice_parameters(security_level)
        self.logger.info(
            f"Initialized lattice crypto with security level {security_level.value}"
        )

    def _get_lattice_parameters(self, level: SecurityLevel) -> dict[str, Any]:
        """Get lattice parameters for security level."""
        if level == SecurityLevel.LEVEL_1:
            return {
                "n": 512,  # Ring dimension
                "q": 12289,  # Modulus
                "sigma": 3.2,  # Gaussian parameter
                "t": 8,  # Number of polynomials
                "name": "NTRU-512",
            }
        elif level == SecurityLevel.LEVEL_3:
            return {"n": 768, "q": 12289, "sigma": 3.2, "t": 10, "name": "NTRU-768"}
        else:  # LEVEL_5
            return {"n": 1024, "q": 12289, "sigma": 3.2, "t": 12, "name": "NTRU-1024"}

    def generate_keypair(self) -> tuple[QuantumKey, QuantumKey]:
        """Generate lattice-based keypair."""
        try:
            self.logger.debug("Generating lattice-based keypair")

            n = self.params["n"]
            q = self.params["q"]
            sigma = self.params["sigma"]

            # Generate secret key (small coefficients)
            secret_key = np.random.normal(0, sigma, n).astype(int) % q

            # Generate error polynomial
            error = np.random.normal(0, sigma, n).astype(int) % q

            # Generate random polynomial a
            a = np.random.randint(0, q, n)

            # Compute public key: b = a*s + e (mod q)
            public_key_poly = (np.convolve(a, secret_key)[:n] + error) % q

            # Encode keys
            public_key_bytes = self._encode_polynomial(
                np.concatenate([a, public_key_poly])
            )
            private_key_bytes = self._encode_polynomial(secret_key)

            # Create key objects
            public_key = QuantumKey(
                algorithm=QuantumAlgorithm.LATTICE_BASED,
                security_level=self.security_level,
                public_key=public_key_bytes,
                parameters=self.params.copy(),
            )

            private_key = QuantumKey(
                algorithm=QuantumAlgorithm.LATTICE_BASED,
                security_level=self.security_level,
                public_key=public_key_bytes,
                private_key=private_key_bytes,
                parameters=self.params.copy(),
            )

            self.logger.info(f"Generated lattice keypair with {n}-bit security")
            return public_key, private_key

        except Exception as e:
            self.logger.error(f"Lattice keypair generation failed: {e}")
            raise KeyGenerationError(f"Failed to generate lattice keypair: {e}") from e

    def encrypt(
        self, message: bytes, public_key: QuantumKey
    ) -> QuantumEncryptionResult:
        """Encrypt message using lattice-based encryption."""
        try:
            if public_key.algorithm != QuantumAlgorithm.LATTICE_BASED:
                raise EncryptionError("Invalid public key algorithm")

            if not public_key.is_valid():
                raise EncryptionError("Public key is not valid for encryption")

            self.logger.debug(f"Encrypting {len(message)} bytes with lattice crypto")

            # Decode public key
            public_poly = self._decode_polynomial(public_key.public_key)
            a = public_poly[: self.params["n"]]
            b = public_poly[self.params["n"] :]

            # Generate random polynomials for encryption
            r = (
                np.random.normal(0, self.params["sigma"], self.params["n"]).astype(int)
                % self.params["q"]
            )
            e1 = (
                np.random.normal(0, self.params["sigma"], self.params["n"]).astype(int)
                % self.params["q"]
            )
            e2 = (
                np.random.normal(0, self.params["sigma"], self.params["n"]).astype(int)
                % self.params["q"]
            )

            # Encode message as polynomial
            message_poly = self._encode_message_as_polynomial(message)

            # Compute ciphertext
            u = (np.convolve(a, r)[: self.params["n"]] + e1) % self.params["q"]
            v = (
                np.convolve(b, r)[: self.params["n"]] + e2 + message_poly
            ) % self.params["q"]

            # Encode ciphertext
            ciphertext = self._encode_polynomial(np.concatenate([u, v]))

            # Generate nonce
            nonce = secrets.token_bytes(32)

            self.logger.info("Lattice encryption completed successfully")

            return QuantumEncryptionResult(
                algorithm=QuantumAlgorithm.LATTICE_BASED,
                ciphertext=ciphertext,
                public_key=public_key.public_key,
                nonce=nonce,
                metadata={
                    "params": self.params,
                    "message_length": len(message),
                    "ciphertext_length": len(ciphertext),
                },
            )

        except Exception as e:
            self.logger.error(f"Lattice encryption failed: {e}")
            raise EncryptionError(f"Lattice encryption failed: {e}") from e

    def decrypt(
        self, encrypted_result: QuantumEncryptionResult, private_key: QuantumKey
    ) -> bytes:
        """Decrypt message using lattice-based decryption."""
        try:
            if private_key.algorithm != QuantumAlgorithm.LATTICE_BASED:
                raise DecryptionError("Invalid private key algorithm")

            if not private_key.is_valid():
                raise DecryptionError("Private key is not valid for decryption")

            self.logger.debug("Decrypting lattice-encrypted message")

            # Decode ciphertext and private key
            ciphertext_poly = self._decode_polynomial(encrypted_result.ciphertext)
            secret_poly = self._decode_polynomial(private_key.private_key)

            u = ciphertext_poly[: self.params["n"]]
            v = ciphertext_poly[self.params["n"] :]

            # Decrypt: m = v - u*s (mod q)
            decrypted_poly = (
                v - np.convolve(u, secret_poly)[: self.params["n"]]
            ) % self.params["q"]

            # Decode message from polynomial
            message = self._decode_message_from_polynomial(decrypted_poly)

            # Increment key usage
            private_key.increment_usage()

            self.logger.info("Lattice decryption completed successfully")
            return message

        except Exception as e:
            self.logger.error(f"Lattice decryption failed: {e}")
            raise DecryptionError(f"Lattice decryption failed: {e}") from e

    def _encode_polynomial(self, poly: np.ndarray) -> bytes:
        """Encode polynomial as bytes."""
        return poly.astype(np.int32).tobytes()

    def _decode_polynomial(self, data: bytes) -> np.ndarray:
        """Decode bytes as polynomial."""
        return np.frombuffer(data, dtype=np.int32)

    def _encode_message_as_polynomial(self, message: bytes) -> np.ndarray:
        """Encode message as polynomial coefficients."""
        # Improved encoding with padding
        poly = np.zeros(self.params["n"], dtype=int)
        message_ints = list(message)

        # Encode length first for proper decoding
        if len(message_ints) < self.params["n"] - 1:
            poly[0] = len(message_ints)
            for i, byte_val in enumerate(message_ints):
                poly[i + 1] = byte_val * (self.params["q"] // 256)
        else:
            # Message too long, truncate
            poly[0] = self.params["n"] - 1
            for i, byte_val in enumerate(message_ints[: self.params["n"] - 1]):
                poly[i + 1] = byte_val * (self.params["q"] // 256)

        return poly

    def _decode_message_from_polynomial(self, poly: np.ndarray) -> bytes:
        """Decode message from polynomial coefficients."""
        # Improved decoding with length prefix
        if len(poly) == 0:
            return b""

        message_length = (poly[0] * 256) // self.params["q"]
        message_bytes = []

        for i in range(1, min(len(poly), message_length + 1)):
            if poly[i] != 0:
                byte_val = (poly[i] * 256) // self.params["q"]
                if 0 <= byte_val <= 255:
                    message_bytes.append(byte_val)

        return bytes(message_bytes)

    def get_key_size(self) -> int:
        """Get key size in bytes."""
        return self.params["n"] * 8  # 8 bytes per polynomial coefficient

    def get_ciphertext_overhead(self) -> int:
        """Get ciphertext overhead in bytes."""
        return self.params["n"] * 8  # Same as key size
