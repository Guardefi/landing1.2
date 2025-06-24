"""
Quantum cryptography exceptions.
"""


class QuantumCryptoError(Exception):
    """Base exception for quantum crypto operations."""

    pass


class KeyGenerationError(QuantumCryptoError):
    """Raised when key generation fails."""

    pass


class EncryptionError(QuantumCryptoError):
    """Raised when encryption fails."""

    pass


class DecryptionError(QuantumCryptoError):
    """Raised when decryption fails."""

    pass


class SignatureError(QuantumCryptoError):
    """Raised when signature operations fail."""

    pass


class VerificationError(QuantumCryptoError):
    """Raised when verification fails."""

    pass


class ConfigurationError(QuantumCryptoError):
    """Raised when configuration is invalid."""

    pass


class AlgorithmNotSupportedError(QuantumCryptoError):
    """Raised when algorithm is not supported."""

    pass


class KeyNotFoundError(QuantumCryptoError):
    """Raised when a key is not found."""

    pass


class InvalidKeyError(QuantumCryptoError):
    """Raised when a key is invalid or corrupted."""

    pass
