"""
Quantum Cryptography Module
"""

from enum import Enum


class QuantumAlgorithm(Enum):
    """Quantum-resistant algorithms."""

    LATTICE_BASED = "lattice_based"
    HASH_BASED = "hash_based"
    CODE_BASED = "code_based"
    MULTIVARIATE = "multivariate"


class SecurityLevel(Enum):
    """Security levels for quantum resistance."""

    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5


class QuantumKey:
    """Represents a quantum-resistant key."""

    def __init__(
        self,
        key_data: bytes,
        algorithm: QuantumAlgorithm,
        security_level: SecurityLevel,
    ):
        self.key_data = key_data
        self.algorithm = algorithm
        self.security_level = security_level

    def __str__(self):
        return f"QuantumKey({self.algorithm.value}, Level {self.security_level.value})"
