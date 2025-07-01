"""
Keccak-256 hash implementation for Ethereum compatibility
Pure Python implementation for educational/testing purposes
"""

import struct
from typing import List, Union

# Keccak round constants
RC = [
    0x0000000000000001,
    0x0000000000008082,
    0x800000000000808A,
    0x8000000080008000,
    0x000000000000808B,
    0x0000000080000001,
    0x8000000080008081,
    0x8000000000008009,
    0x000000000000008A,
    0x0000000000000088,
    0x0000000080008009,
    0x8000000000008003,
    0x8000000000008002,
    0x8000000000000080,
    0x000000000000800A,
    0x800000008000000A,
    0x8000000080008081,
    0x8000000000008080,
    0x0000000080000001,
    0x8000000080008008,
]

# Rotation offsets
RHO = [
    0,
    1,
    62,
    28,
    27,
    36,
    44,
    6,
    55,
    20,
    3,
    10,
    43,
    25,
    39,
    41,
    45,
    15,
    21,
    8,
    18,
    2,
    61,
    56,
    14,
]

# Pi permutation
PI = [
    0,
    6,
    12,
    18,
    24,
    3,
    9,
    10,
    16,
    22,
    1,
    7,
    13,
    19,
    20,
    4,
    5,
    11,
    17,
    23,
    2,
    8,
    14,
    15,
    21,
]


def rot64(value: int, amount: int) -> int:
    """64-bit left rotation"""
    return ((value << amount) | (value >> (64 - amount))) & 0xFFFFFFFFFFFFFFFF


def keccak_f(state: List[int]) -> List[int]:
    """Keccak-f[1600] permutation"""
    for round_idx in range(24):
        # Theta step
        c = [0] * 5
        for x in range(5):
            c[x] = (
                state[x] ^ state[x + 5] ^ state[x + 10] ^ state[x + 15] ^ state[x + 20]
            )

        d = [0] * 5
        for x in range(5):
            d[x] = c[(x + 4) % 5] ^ rot64(c[(x + 1) % 5], 1)

        for x in range(5):
            for y in range(5):
                state[x + 5 * y] ^= d[x]

        # Rho and Pi steps
        b = [0] * 25
        for x in range(5):
            for y in range(5):
                b[PI[x + 5 * y]] = rot64(state[x + 5 * y], RHO[x + 5 * y])

        # Chi step
        for x in range(5):
            for y in range(5):
                state[x + 5 * y] = b[x + 5 * y] ^ (
                    (~b[(x + 1) % 5 + 5 * y]) & b[(x + 2) % 5 + 5 * y]
                )

        # Iota step
        state[0] ^= RC[round_idx]

    return state


def keccak256(data: Union[bytes, str]) -> bytes:
    """Compute Keccak-256 hash"""
    if isinstance(data, str):
        data = data.encode("utf-8")

    # Initialize state (25 x 64-bit words = 1600 bits)
    state = [0] * 25

    # Rate for Keccak-256 is 1088 bits = 136 bytes
    rate = 136

    # Padding
    data += b"\x01"  # Keccak padding
    while len(data) % rate != 0:
        data += b"\x00"
    data = data[:-1] + bytes([data[-1] | 0x80])  # Add final padding bit

    # Absorbing phase
    for chunk_start in range(0, len(data), rate):
        chunk = data[chunk_start : chunk_start + rate]

        # Convert chunk to 64-bit words and XOR with state
        for i in range(0, len(chunk), 8):
            if i + 8 <= len(chunk):
                word = struct.unpack("<Q", chunk[i : i + 8])[0]
                state[i // 8] ^= word
            else:
                # Handle partial last word
                remaining = chunk[i:]
                remaining += b"\x00" * (8 - len(remaining))
                word = struct.unpack("<Q", remaining)[0]
                state[i // 8] ^= word

        # Apply Keccak-f permutation
        state = keccak_f(state)

    # Squeezing phase (extract 256 bits = 32 bytes)
    output = b""
    for i in range(4):  # 4 * 8 bytes = 32 bytes
        output += struct.pack("<Q", state[i])

    return output


def keccak256_hex(data: Union[bytes, str]) -> str:
    """Compute Keccak-256 hash and return as hex string"""
    return keccak256(data).hex()


def ethereum_address_checksum(address: str) -> str:
    """Apply EIP-55 checksum to Ethereum address"""
    if not address.startswith("0x"):
        address = "0x" + address

    address = address.lower()
    address_hash = keccak256_hex(address[2:].encode("utf-8"))

    checksum_address = "0x"
    for i, char in enumerate(address[2:]):
        if char.isdigit():
            checksum_address += char
        else:
            if int(address_hash[i], 16) >= 8:
                checksum_address += char.upper()
            else:
                checksum_address += char.lower()

    return checksum_address


def compute_contract_address(sender: str, nonce: int) -> str:
    """Compute contract address from sender and nonce"""
    from .rlp_helpers import encode

    if sender.startswith("0x"):
        sender = sender[2:]

    sender_bytes = bytes.fromhex(sender)
    rlp_encoded = encode([sender_bytes, nonce])

    hash_result = keccak256(rlp_encoded)
    return "0x" + hash_result[-20:].hex()


def compute_create2_address(
    deployer: str, salt: Union[str, bytes], bytecode: Union[str, bytes]
) -> str:
    """Compute CREATE2 contract address"""
    if isinstance(deployer, str) and deployer.startswith("0x"):
        deployer = deployer[2:]
    if isinstance(deployer, str):
        deployer = bytes.fromhex(deployer)

    if isinstance(salt, str) and salt.startswith("0x"):
        salt = salt[2:]
    if isinstance(salt, str):
        salt = bytes.fromhex(salt)

    if isinstance(bytecode, str) and bytecode.startswith("0x"):
        bytecode = bytecode[2:]
    if isinstance(bytecode, str):
        bytecode = bytes.fromhex(bytecode)

    # Ensure salt is 32 bytes
    if len(salt) < 32:
        salt = b"\x00" * (32 - len(salt)) + salt
    elif len(salt) > 32:
        salt = salt[-32:]

    # Compute keccak256(0xff ++ deployer ++ salt ++ keccak256(bytecode))
    bytecode_hash = keccak256(bytecode)
    data = b"\xff" + deployer + salt + bytecode_hash

    hash_result = keccak256(data)
    return "0x" + hash_result[-20:].hex()


def hash_message(message: Union[str, bytes]) -> bytes:
    """Hash a message with Ethereum's personal message prefix"""
    if isinstance(message, str):
        message = message.encode("utf-8")

    prefix = f"\x19Ethereum Signed Message:\n{len(message)}".encode("utf-8")
    return keccak256(prefix + message)


def hash_typed_data(domain_separator: bytes, struct_hash: bytes) -> bytes:
    """Hash typed data according to EIP-712"""
    return keccak256(b"\x19\x01" + domain_separator + struct_hash)


# For testing/validation
def test_keccak256():
    """Test Keccak-256 implementation with known test vectors"""
    # Test empty string
    result = keccak256_hex(b"")
    expected = "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
    assert result == expected, f"Empty string test failed: {result} != {expected}"

    # Test "abc"
    result = keccak256_hex(b"abc")
    expected = "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45"
    assert result == expected, f"'abc' test failed: {result} != {expected}"

    print("Keccak-256 tests passed!")


if __name__ == "__main__":
    test_keccak256()
