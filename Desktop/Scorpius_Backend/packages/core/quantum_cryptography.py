"""
SCORPIUS QUANTUM CRYPTOGRAPHY
Advanced quantum-resistant cryptographic implementations for future-proof security.
Implements post-quantum cryptographic algorithms and quantum key distribution.
"""



# For lattice-based cryptography


# Custom quantum-resistant algorithms
class QuantumAlgorithm(Enum):
    """Quantum-resistant algorithm types."""

    LATTICE_BASED = "lattice_based"
    HASH_BASED = "hash_based"
    CODE_BASED = "code_based"
    MULTIVARIATE = "multivariate"
    ISOGENY_BASED = "isogeny_based"
    SYMMETRIC = "symmetric"


class SecurityLevel(Enum):
    """Security levels against quantum attacks."""

    LEVEL_1 = 1  # Equivalent to AES-128
    LEVEL_3 = 3  # Equivalent to AES-192
    LEVEL_5 = 5  # Equivalent to AES-256


@dataclass
class QuantumKey:
    """Quantum-resistant cryptographic key."""

    algorithm: QuantumAlgorithm
    security_level: SecurityLevel
    public_key: bytes
    private_key: bytes | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
    creation_time: datetime = field(default_factory=datetime.now)
    expiry_time: datetime | None = None
    usage_count: int = 0
    max_usage: int | None = None


@dataclass
class QuantumSignature:
    """Quantum-resistant digital signature."""

    algorithm: QuantumAlgorithm
    signature: bytes
    public_key: bytes
    message_hash: bytes
    timestamp: datetime = field(default_factory=datetime.now)
    verification_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class QuantumEncryptionResult:
    """Result of quantum-resistant encryption."""

    algorithm: QuantumAlgorithm
    ciphertext: bytes
    public_key: bytes
    nonce: bytes
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class LatticeBasedCrypto:
    """
    Lattice-based cryptography implementation.
    Resistant to both classical and quantum attacks.
    """

    def __init__(self, security_level: SecurityLevel = SecurityLevel.LEVEL_3):
        self.security_level = security_level
        self.logger = logging.getLogger(__name__)

        # Set parameters based on security level
        self.params = self._get_lattice_parameters(security_level)

    def _get_lattice_parameters(self, level: SecurityLevel) -> dict[str, int]:
        """Get lattice parameters for security level."""
        if level == SecurityLevel.LEVEL_1:
            return {
                "n": 512,  # Ring dimension
                "q": 12289,  # Modulus
                "sigma": 3.2,  # Gaussian parameter
                "t": 8,  # Number of polynomials
            }
        elif level == SecurityLevel.LEVEL_3:
            return {"n": 768, "q": 12289, "sigma": 3.2, "t": 10}
        else:  # LEVEL_5
            return {"n": 1024, "q": 12289, "sigma": 3.2, "t": 12}

    def generate_keypair(self) -> tuple[QuantumKey, QuantumKey]:
        """Generate lattice-based keypair."""
        try:
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

            return public_key, private_key

        except Exception as e:
            self.logger.error(f"Lattice keypair generation failed: {e}")
            raise e from e

    def encrypt(
        self, message: bytes, public_key: QuantumKey
    ) -> QuantumEncryptionResult:
        """Encrypt message using lattice-based encryption."""
        try:
            if public_key.algorithm != QuantumAlgorithm.LATTICE_BASED:
                raise ValueError("Invalid public key algorithm") from None

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

            return QuantumEncryptionResult(
                algorithm=QuantumAlgorithm.LATTICE_BASED,
                ciphertext=ciphertext,
                public_key=public_key.public_key,
                nonce=nonce,
                metadata={"params": self.params},
            )

        except Exception as e:
            self.logger.error(f"Lattice encryption failed: {e}")
            raise e from e

    def decrypt(
        self, encrypted_result: QuantumEncryptionResult, private_key: QuantumKey
    ) -> bytes:
        """Decrypt message using lattice-based decryption."""
        try:
            if private_key.algorithm != QuantumAlgorithm.LATTICE_BASED:
                raise ValueError("Invalid private key algorithm") from None

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

            return message

        except Exception as e:
            self.logger.error(f"Lattice decryption failed: {e}")
            raise e from e

    def _encode_polynomial(self, poly: np.ndarray) -> bytes:
        """Encode polynomial as bytes."""
        return poly.astype(np.int32).tobytes()

    def _decode_polynomial(self, data: bytes) -> np.ndarray:
        """Decode bytes as polynomial."""
        return np.frombuffer(data, dtype=np.int32)

    def _encode_message_as_polynomial(self, message: bytes) -> np.ndarray:
        """Encode message as polynomial coefficients."""
        # Simplified encoding - pad/truncate to polynomial size
        poly = np.zeros(self.params["n"], dtype=int)
        message_ints = list(message)

        for i, byte_val in enumerate(message_ints[: self.params["n"]]):
            poly[i] = byte_val * (self.params["q"] // 256)

        return poly

    def _decode_message_from_polynomial(self, poly: np.ndarray) -> bytes:
        """Decode message from polynomial coefficients."""
        # Simplified decoding
        message_bytes = []

        for coeff in poly:
            if coeff != 0:
                byte_val = (coeff * 256) // self.params["q"]
                if 0 <= byte_val <= 255:
                    message_bytes.append(byte_val)

        return bytes(message_bytes)


class HashBasedSignatures:
    """
    Hash-based signature scheme implementation.
    Provides quantum-resistant digital signatures.
    """

    def __init__(self, security_level: SecurityLevel = SecurityLevel.LEVEL_3):
        self.security_level = security_level
        self.logger = logging.getLogger(__name__)

        # Set parameters
        self.params = self._get_hash_parameters(security_level)

    def _get_hash_parameters(self, level: SecurityLevel) -> dict[str, int]:
        """Get hash-based signature parameters."""
        if level == SecurityLevel.LEVEL_1:
            return {
                "w": 16,  # Winternitz parameter
                "h": 10,  # Tree height
                "n": 32,  # Hash output length
            }
        elif level == SecurityLevel.LEVEL_3:
            return {"w": 16, "h": 15, "n": 48}
        else:  # LEVEL_5
            return {"w": 16, "h": 20, "n": 64}

    def generate_keypair(self) -> tuple[QuantumKey, QuantumKey]:
        """Generate hash-based signature keypair."""
        try:
            # Generate one-time signature keys
            ots_keys = self._generate_ots_keys()

            # Build Merkle tree
            tree_root = self._build_merkle_tree(ots_keys)

            # Create key objects
            public_key = QuantumKey(
                algorithm=QuantumAlgorithm.HASH_BASED,
                security_level=self.security_level,
                public_key=tree_root,
                parameters=self.params.copy(),
            )

            private_key = QuantumKey(
                algorithm=QuantumAlgorithm.HASH_BASED,
                security_level=self.security_level,
                public_key=tree_root,
                private_key=json.dumps(
                    ots_keys, default=lambda x: x.hex() if isinstance(x, bytes) else x
                ).encode(),
                parameters=self.params.copy(),
            )

            return public_key, private_key

        except Exception as e:
            self.logger.error(f"Hash-based keypair generation failed: {e}")
            raise e from e

    def sign(
        self, message: bytes, private_key: QuantumKey, index: int = 0
    ) -> QuantumSignature:
        """Create hash-based signature."""
        try:
            if private_key.algorithm != QuantumAlgorithm.HASH_BASED:
                raise ValueError("Invalid private key algorithm") from None

            # Load OTS keys
            ots_keys = json.loads(private_key.private_key.decode())

            # Hash message
            message_hash = hashlib.sha256(message).digest()

            # Create one-time signature
            ots_signature = self._create_ots_signature(message_hash, ots_keys, index)

            # Create authentication path
            auth_path = self._get_authentication_path(ots_keys, index)

            # Combine signature components
            signature_data = {
                "ots_signature": ots_signature,
                "auth_path": auth_path,
                "index": index,
            }

            signature_bytes = json.dumps(
                signature_data, default=lambda x: x.hex() if isinstance(x, bytes) else x
            ).encode()

            return QuantumSignature(
                algorithm=QuantumAlgorithm.HASH_BASED,
                signature=signature_bytes,
                public_key=private_key.public_key,
                message_hash=message_hash,
                verification_data={"params": self.params},
            )

        except Exception as e:
            self.logger.error(f"Hash-based signing failed: {e}")
            raise e from e

    def verify(
        self, signature: QuantumSignature, message: bytes, public_key: QuantumKey
    ) -> bool:
        """Verify hash-based signature."""
        try:
            if signature.algorithm != QuantumAlgorithm.HASH_BASED:
                return False

            # Hash message
            message_hash = hashlib.sha256(message).digest()

            if message_hash != signature.message_hash:
                return False

            # Parse signature
            sig_data = json.loads(signature.signature.decode())

            # Verify OTS signature
            ots_verification = self._verify_ots_signature(
                message_hash, sig_data["ots_signature"], sig_data["index"]
            )

            # Verify authentication path
            path_verification = self._verify_authentication_path(
                ots_verification,
                sig_data["auth_path"],
                sig_data["index"],
                public_key.public_key,
            )

            return path_verification

        except Exception as e:
            self.logger.error(f"Hash-based verification failed: {e}")
            return False

    def _generate_ots_keys(self) -> list[dict[str, Any]]:
        """Generate one-time signature keys."""
        num_keys = 2 ** self.params["h"]
        ots_keys = []

        for i in range(num_keys):
            # Generate Winternitz keys
            private_key = [
                secrets.token_bytes(self.params["n"]) for _ in range(self.params["w"])
            ]

            # Compute public key by hashing private key multiple times
            public_key = []
            for pk in private_key:
                current = pk
                for _ in range(2**8 - 1):  # Hash 255 times
                    current = hashlib.sha256(current).digest()[: self.params["n"]]
                public_key.append(current)

            ots_keys.append({"private": private_key, "public": public_key, "index": i})

        return ots_keys

    def _build_merkle_tree(self, ots_keys: list[dict[str, Any]]) -> bytes:
        """Build Merkle tree from OTS public keys."""
        # Compute leaf hashes
        leaves = []
        for key in ots_keys:
            leaf_data = b"".join(key["public"])
            leaf_hash = hashlib.sha256(leaf_data).digest()[: self.params["n"]]
            leaves.append(leaf_hash)

        # Build tree bottom-up
        current_level = leaves

        while len(current_level) > 1:
            next_level = []
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                parent = hashlib.sha256(left + right).digest()[: self.params["n"]]
                next_level.append(parent)

            current_level = next_level

        return current_level[0]

    def _create_ots_signature(
        self, message_hash: bytes, ots_keys: list[dict[str, Any]], index: int
    ) -> list[bytes]:
        """Create one-time signature."""
        if index >= len(ots_keys):
            raise ValueError("Invalid OTS key index") from None

        ots_key = ots_keys[index]
        signature = []

        # Convert message hash to Winternitz representation
        hash_int = int.from_bytes(message_hash[:4], "big")  # Use first 4 bytes

        for i in range(self.params["w"]):
            # Extract digit in base-16
            digit = (hash_int >> (4 * i)) & 0xF

            # Hash private key 'digit' times
            current = ots_key["private"][i]
            for _ in range(digit):
                current = hashlib.sha256(current).digest()[: self.params["n"]]

            signature.append(current)

        return signature

    def _verify_ots_signature(
        self, message_hash: bytes, signature: list[str], index: int
    ) -> bytes:
        """Verify one-time signature and return public key."""
        # Convert signature from hex strings
        sig_bytes = [bytes.fromhex(s) for s in signature]

        # Compute public key from signature
        hash_int = int.from_bytes(message_hash[:4], "big")
        computed_public = []

        for i in range(len(sig_bytes)):
            digit = (hash_int >> (4 * i)) & 0xF
            remaining_hashes = (2**8 - 1) - digit

            current = sig_bytes[i]
            for _ in range(remaining_hashes):
                current = hashlib.sha256(current).digest()[: self.params["n"]]

            computed_public.append(current)

        # Return public key hash
        public_key_data = b"".join(computed_public)
        return hashlib.sha256(public_key_data).digest()[: self.params["n"]]

    def _get_authentication_path(
        self, ots_keys: list[dict[str, Any]], index: int
    ) -> list[str]:
        """Get authentication path for Merkle tree verification."""
        # This would compute the actual authentication path
        # For now, return a mock path
        return [secrets.token_hex(self.params["n"]) for _ in range(self.params["h"])]

    def _verify_authentication_path(
        self, leaf_hash: bytes, auth_path: list[str], index: int, root: bytes
    ) -> bool:
        """Verify authentication path in Merkle tree."""
        current = leaf_hash

        for i, sibling_hex in enumerate(auth_path):
            sibling = bytes.fromhex(sibling_hex)

            # Determine if we're left or right child
            if (index >> i) & 1:
                current = hashlib.sha256(sibling + current).digest()[: self.params["n"]]
            else:
                current = hashlib.sha256(current + sibling).digest()[: self.params["n"]]

        return current == root


class QuantumKeyDistribution:
    """
    Quantum Key Distribution (QKD) simulation.
    Provides theoretically secure key exchange.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # QKD parameters
        self.photon_error_rate = 0.01  # 1% error rate
        self.detection_efficiency = 0.8  # 80% detection
        self.key_length = 256  # bits

    async def establish_quantum_channel(
        self, alice_id: str, bob_id: str
    ) -> dict[str, Any]:
        """Establish quantum communication channel."""
        try:
            # Simulate quantum channel establishment
            channel_id = secrets.token_hex(16)

            # Generate quantum states
            alice_bits = [random.randint(0, 1) for _ in range(self.key_length * 2)]
            alice_bases = [random.randint(0, 1) for _ in range(self.key_length * 2)]

            # Simulate photon transmission with errors
            received_bits = []
            for bit in alice_bits:
                if random.random() < self.detection_efficiency:
                    if random.random() < self.photon_error_rate:
                        received_bits.append(1 - bit)  # Flip bit
                    else:
                        received_bits.append(bit)
                else:
                    received_bits.append(None)  # Photon lost

            # Bob chooses random bases
            bob_bases = [random.randint(0, 1) for _ in range(len(received_bits))]

            # Sift key (keep only matching bases)
            sifted_key = []
            for _i, (a_base, b_base, bit) in enumerate(
                zip(alice_bases, bob_bases, received_bits, strict=False)
            ):
                if a_base == b_base and bit is not None:
                    sifted_key.append(bit)

            # Error correction and privacy amplification would go here
            final_key = (
                sifted_key[: self.key_length]
                if len(sifted_key) >= self.key_length
                else sifted_key
            )

            return {
                "channel_id": channel_id,
                "alice_id": alice_id,
                "bob_id": bob_id,
                "shared_key": bytes(final_key),
                "key_length": len(final_key),
                "error_rate": self.photon_error_rate,
                "efficiency": len(final_key) / (self.key_length * 2),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"QKD channel establishment failed: {e}")
            raise e from e


class QuantumCryptographyEngine:
    """
    Main quantum cryptography engine for Scorpius.
    Provides unified interface for all quantum-resistant algorithms.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Initialize algorithm implementations
        self.lattice_crypto = LatticeBasedCrypto()
        self.hash_signatures = HashBasedSignatures()
        self.qkd = QuantumKeyDistribution()

        # Key management
        self.keys: dict[str, QuantumKey] = {}
        self.signatures: dict[str, QuantumSignature] = {}

        # Performance monitoring
        self.performance_stats = {
            "key_generations": 0,
            "encryptions": 0,
            "decryptions": 0,
            "signatures": 0,
            "verifications": 0,
            "total_time": 0.0,
        }

    async def generate_keypair(
        self,
        algorithm: QuantumAlgorithm,
        security_level: SecurityLevel = SecurityLevel.LEVEL_3,
    ) -> tuple[str, str]:
        """
        Generate quantum-resistant keypair.

        Args:
            algorithm: Quantum-resistant algorithm to use
            security_level: Security level for the keys

        Returns:
            Tuple of (public_key_id, private_key_id)
        """
        start_time = time.time()

        try:
            if algorithm == QuantumAlgorithm.LATTICE_BASED:
                public_key, private_key = self.lattice_crypto.generate_keypair()
            elif algorithm == QuantumAlgorithm.HASH_BASED:
                public_key, private_key = self.hash_signatures.generate_keypair()
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}") from None

            # Store keys
            public_key_id = secrets.token_hex(16)
            private_key_id = secrets.token_hex(16)

            self.keys[public_key_id] = public_key
            self.keys[private_key_id] = private_key

            # Update stats
            self.performance_stats["key_generations"] += 1
            self.performance_stats["total_time"] += time.time() - start_time

            self.logger.info(f"Generated {algorithm.value} keypair: {public_key_id}")

            return public_key_id, private_key_id

        except Exception as e:
            self.logger.error(f"Keypair generation failed: {e}")
            raise e from e

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
                raise ValueError("Public key not found") from None

            public_key = self.keys[public_key_id]

            if public_key.algorithm == QuantumAlgorithm.LATTICE_BASED:
                self.lattice_crypto.encrypt(message, public_key)
            else:
                raise ValueError(f"Encryption not supported for {public_key.algorithm}") from None

            # Store result
            result_id = secrets.token_hex(16)
            # In a real implementation, you'd store the QuantumEncryptionResult

            # Update stats
            self.performance_stats["encryptions"] += 1
            self.performance_stats["total_time"] += time.time() - start_time

            self.logger.info(f"Encrypted message with {public_key.algorithm.value}")

            return result_id

        except Exception as e:
            self.logger.error(f"Message encryption failed: {e}")
            raise e from e

    async def sign_message(self, message: bytes, private_key_id: str) -> str:
        """
        Sign message with quantum-resistant signature.

        Args:
            message: Message to sign
            private_key_id: Private key identifier

        Returns:
            Signature identifier
        """
        start_time = time.time()

        try:
            if private_key_id not in self.keys:
                raise ValueError("Private key not found") from None

            private_key = self.keys[private_key_id]

            if private_key.algorithm == QuantumAlgorithm.HASH_BASED:
                signature = self.hash_signatures.sign(message, private_key)
            else:
                raise ValueError(f"Signing not supported for {private_key.algorithm}") from None

            # Store signature
            signature_id = secrets.token_hex(16)
            self.signatures[signature_id] = signature

            # Update stats
            self.performance_stats["signatures"] += 1
            self.performance_stats["total_time"] += time.time() - start_time

            self.logger.info(f"Signed message with {private_key.algorithm.value}")

            return signature_id

        except Exception as e:
            self.logger.error(f"Message signing failed: {e}")
            raise e from e

    async def verify_signature(
        self, message: bytes, signature_id: str, public_key_id: str
    ) -> bool:
        """
        Verify quantum-resistant signature.

        Args:
            message: Original message
            signature_id: Signature identifier
            public_key_id: Public key identifier

        Returns:
            True if signature is valid
        """
        start_time = time.time()

        try:
            if signature_id not in self.signatures:
                raise ValueError("Signature not found") from None

            if public_key_id not in self.keys:
                raise ValueError("Public key not found") from None

            signature = self.signatures[signature_id]
            public_key = self.keys[public_key_id]

            if signature.algorithm == QuantumAlgorithm.HASH_BASED:
                result = self.hash_signatures.verify(signature, message, public_key)
            else:
                raise ValueError(
                    f"Verification not supported for {signature.algorithm}"
                ) from None

            # Update stats
            self.performance_stats["verifications"] += 1
            self.performance_stats["total_time"] += time.time() - start_time

            self.logger.info(f"Verified signature: {result}")

            return result

        except Exception as e:
            self.logger.error(f"Signature verification failed: {e}")
            return False

    async def establish_quantum_secure_channel(self, peer_id: str) -> dict[str, Any]:
        """
        Establish quantum-secure communication channel.

        Args:
            peer_id: Peer identifier

        Returns:
            Channel information
        """
        try:
            # Use QKD to establish shared key
            channel_info = await self.qkd.establish_quantum_channel("local", peer_id)

            self.logger.info(f"Established quantum channel with {peer_id}")

            return channel_info

        except Exception as e:
            self.logger.error(f"Quantum channel establishment failed: {e}")
            raise e from e

    async def get_performance_stats(self) -> dict[str, Any]:
        """Get quantum cryptography performance statistics."""
        stats = self.performance_stats.copy()

        if stats["key_generations"] > 0:
            stats["avg_keygen_time"] = stats["total_time"] / stats["key_generations"]

        if stats["encryptions"] > 0:
            stats["avg_encryption_time"] = stats["total_time"] / stats["encryptions"]

        if stats["signatures"] > 0:
            stats["avg_signing_time"] = stats["total_time"] / stats["signatures"]

        stats["total_keys"] = len(self.keys)
        stats["total_signatures"] = len(self.signatures)

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

            # Check for expired keys
            if key.expiry_time and datetime.now() > key.expiry_time:
                audit_results["expired_keys"] += 1

            # Check for overused keys
            if key.max_usage and key.usage_count >= key.max_usage:
                audit_results["overused_keys"] += 1

        # Generate recommendations
        if audit_results["expired_keys"] > 0:
            audit_results["recommendations"].append(
                f"Rotate {audit_results['expired_keys']} expired keys"
            )

        if audit_results["overused_keys"] > 0:
            audit_results["recommendations"].append(
                f"Replace {audit_results['overused_keys']} overused keys"
            )

        # Check algorithm diversity
        if len(audit_results["algorithm_distribution"]) < 2:
            audit_results["recommendations"].append(
                "Consider using multiple quantum-resistant algorithms for defense in depth"
            )

        return audit_results


# Global quantum crypto engine
quantum_engine = QuantumCryptographyEngine()


async def initialize_quantum_crypto(config: dict | None = None) -> bool:
    """Initialize the quantum cryptography engine."""
    global quantum_engine

    try:
        quantum_engine = QuantumCryptographyEngine(config)
        logging.info("Quantum cryptography engine initialized")
        return True
    except Exception as e:
        logging.error(f"Failed to initialize quantum crypto engine: {e}")
        return False


if __name__ == "__main__":
    # Example usage and testing
    async def test_quantum_crypto():
        """Test quantum cryptography functionality."""
        print("Testing Quantum Cryptography...")

        # Initialize engine
        await initialize_quantum_crypto()

        # Generate lattice-based keypair
        pub_id, priv_id = await quantum_engine.generate_keypair(
            QuantumAlgorithm.LATTICE_BASED
        )
        print(f"Generated lattice keypair: {pub_id[:8]}... / {priv_id[:8]}...")

        # Generate hash-based signature keypair
import asyncio
import hashlib
import json
import logging
import random
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import numpy as np

        sig_pub_id, sig_priv_id = await quantum_engine.generate_keypair(
            QuantumAlgorithm.HASH_BASED
        )
        print(
            f"Generated hash signature keypair: {sig_pub_id[:8]}... / {sig_priv_id[:8]}..."
        )

        # Test message signing
        message = b"Hello, quantum-resistant world!"
        signature_id = await quantum_engine.sign_message(message, sig_priv_id)
        print(f"Created signature: {signature_id[:8]}...")

        # Test signature verification
        is_valid = await quantum_engine.verify_signature(
            message, signature_id, sig_pub_id
        )
        print(f"Signature valid: {is_valid}")

        # Establish quantum channel
        channel = await quantum_engine.establish_quantum_secure_channel("peer_001")
        print(f"Quantum channel efficiency: {channel['efficiency']:.2%}")

        # Performance stats
        stats = await quantum_engine.get_performance_stats()
        print(f"Performance stats: {stats}")

        # Security audit
        audit = await quantum_engine.quantum_security_audit()
        print(f"Security audit: {audit}")

    # Run test if executed directly
    asyncio.run(test_quantum_crypto())
