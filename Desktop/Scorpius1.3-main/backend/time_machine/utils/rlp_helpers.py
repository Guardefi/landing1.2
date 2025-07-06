"""
Utility functions for RLP encoding/decoding operations
Used for Ethereum data serialization in Time Machine
"""

import struct
from typing import Any, List, Tuple, Union


def encode_length(length: int, offset: int) -> bytes:
    """Encode length for RLP"""
    if length < 56:
        return bytes([length + offset])
    elif length < 256**8:
        length_bytes = length.to_bytes((length.bit_length() + 7) // 8, "big")
        return bytes([len(length_bytes) + offset + 55]) + length_bytes
    else:
        raise ValueError("Input too long")


def decode_length(data: bytes, offset: int) -> Tuple[int, int]:
    """Decode length from RLP data"""
    if not data:
        raise ValueError("Cannot decode length from empty data")

    first_byte = data[0]

    if first_byte < offset:
        raise ValueError(f"Invalid RLP data: first byte {first_byte} < offset {offset}")
    elif first_byte < offset + 56:
        return first_byte - offset, 1
    else:
        length_of_length = first_byte - offset - 55
        if length_of_length > len(data) - 1:
            raise ValueError("Invalid RLP data: length of length too large")
        if length_of_length == 0:
            raise ValueError("Invalid RLP data: length of length is 0")

        length = int.from_bytes(data[1 : 1 + length_of_length], "big")
        return length, 1 + length_of_length


def encode(data: Any) -> bytes:
    """Encode data using RLP"""
    if isinstance(data, bytes):
        if len(data) == 1 and data[0] < 0x80:
            return data
        else:
            return encode_length(len(data), 0x80) + data
    elif isinstance(data, (list, tuple)):
        encoded_items = b"".join(encode(item) for item in data)
        return encode_length(len(encoded_items), 0xC0) + encoded_items
    elif isinstance(data, int):
        if data == 0:
            return b"\x80"
        else:
            return encode(data.to_bytes((data.bit_length() + 7) // 8, "big"))
    elif isinstance(data, str):
        return encode(data.encode("utf-8"))
    elif data is None:
        return b"\x80"
    else:
        raise TypeError(f"Cannot encode data of type {type(data)}")


def decode(data: bytes) -> Any:
    """Decode RLP encoded data"""
    if not data:
        raise ValueError("Cannot decode empty data")

    first_byte = data[0]

    if first_byte < 0x80:
        # Single byte
        return data[:1]
    elif first_byte < 0xB8:
        # Short string
        length = first_byte - 0x80
        if length == 0:
            return b""
        return data[1 : 1 + length]
    elif first_byte < 0xC0:
        # Long string
        length, length_size = decode_length(data, 0x80)
        start = 1 + length_size - 1
        return data[start : start + length]
    elif first_byte < 0xF8:
        # Short list
        length = first_byte - 0xC0
        if length == 0:
            return []
        return decode_list(data[1 : 1 + length])
    else:
        # Long list
        length, length_size = decode_length(data, 0xC0)
        start = 1 + length_size - 1
        return decode_list(data[start : start + length])


def decode_list(data: bytes) -> List[Any]:
    """Decode list from RLP data"""
    items = []
    pos = 0

    while pos < len(data):
        if data[pos] < 0x80:
            items.append(data[pos : pos + 1])
            pos += 1
        elif data[pos] < 0xB8:
            length = data[pos] - 0x80
            items.append(data[pos + 1 : pos + 1 + length])
            pos += 1 + length
        elif data[pos] < 0xC0:
            length, length_size = decode_length(data[pos:], 0x80)
            start = pos + length_size
            items.append(data[start : start + length])
            pos = start + length
        elif data[pos] < 0xF8:
            length = data[pos] - 0xC0
            items.append(decode_list(data[pos + 1 : pos + 1 + length]))
            pos += 1 + length
        else:
            length, length_size = decode_length(data[pos:], 0xC0)
            start = pos + length_size
            items.append(decode_list(data[start : start + length]))
            pos = start + length

    return items


def encode_transaction(tx: dict) -> bytes:
    """Encode transaction for RLP"""
    if tx.get("type") == "0x2":  # EIP-1559
        return encode(
            [
                int(tx.get("chainId", "0x1"), 16),
                int(tx.get("nonce", "0x0"), 16),
                int(tx.get("maxPriorityFeePerGas", "0x0"), 16),
                int(tx.get("maxFeePerGas", "0x0"), 16),
                int(tx.get("gas", "0x0"), 16),
                bytes.fromhex(tx.get("to", "")[2:]) if tx.get("to") else b"",
                int(tx.get("value", "0x0"), 16),
                bytes.fromhex(tx.get("input", "0x")[2:]),
                encode_access_list(tx.get("accessList", [])),
                int(tx.get("v", "0x0"), 16),
                int(tx.get("r", "0x0"), 16),
                int(tx.get("s", "0x0"), 16),
            ]
        )
    else:  # Legacy transaction
        return encode(
            [
                int(tx.get("nonce", "0x0"), 16),
                int(tx.get("gasPrice", "0x0"), 16),
                int(tx.get("gas", "0x0"), 16),
                bytes.fromhex(tx.get("to", "")[2:]) if tx.get("to") else b"",
                int(tx.get("value", "0x0"), 16),
                bytes.fromhex(tx.get("input", "0x")[2:]),
                int(tx.get("v", "0x0"), 16),
                int(tx.get("r", "0x0"), 16),
                int(tx.get("s", "0x0"), 16),
            ]
        )


def encode_access_list(access_list: List[dict]) -> List[List[Any]]:
    """Encode access list for EIP-2930/1559 transactions"""
    encoded = []
    for item in access_list:
        address = bytes.fromhex(item["address"][2:])
        storage_keys = [bytes.fromhex(key[2:]) for key in item.get("storageKeys", [])]
        encoded.append([address, storage_keys])
    return encoded


def encode_receipt(receipt: dict) -> bytes:
    """Encode transaction receipt"""
    if receipt.get("type") == "0x2":  # EIP-1559
        return encode(
            [
                int(receipt.get("status", "0x1"), 16),
                int(receipt.get("cumulativeGasUsed", "0x0"), 16),
                bytes.fromhex(receipt.get("logsBloom", "0x" + "00" * 256)[2:]),
                encode_logs(receipt.get("logs", [])),
            ]
        )
    else:  # Legacy receipt
        return encode(
            [
                int(receipt.get("status", "0x1"), 16),
                int(receipt.get("cumulativeGasUsed", "0x0"), 16),
                bytes.fromhex(receipt.get("logsBloom", "0x" + "00" * 256)[2:]),
                encode_logs(receipt.get("logs", [])),
            ]
        )


def encode_logs(logs: List[dict]) -> List[List[Any]]:
    """Encode logs for receipt"""
    encoded = []
    for log in logs:
        encoded.append(
            [
                bytes.fromhex(log.get("address", "")[2:]),
                [bytes.fromhex(topic[2:]) for topic in log.get("topics", [])],
                bytes.fromhex(log.get("data", "0x")[2:]),
            ]
        )
    return encoded


def encode_block_header(header: dict) -> bytes:
    """Encode block header"""
    return encode(
        [
            bytes.fromhex(header.get("parentHash", "")[2:]),
            bytes.fromhex(header.get("sha3Uncles", "")[2:]),
            bytes.fromhex(header.get("miner", "")[2:]),
            bytes.fromhex(header.get("stateRoot", "")[2:]),
            bytes.fromhex(header.get("transactionsRoot", "")[2:]),
            bytes.fromhex(header.get("receiptsRoot", "")[2:]),
            bytes.fromhex(header.get("logsBloom", "0x" + "00" * 256)[2:]),
            int(header.get("difficulty", "0x0"), 16),
            int(header.get("number", "0x0"), 16),
            int(header.get("gasLimit", "0x0"), 16),
            int(header.get("gasUsed", "0x0"), 16),
            int(header.get("timestamp", "0x0"), 16),
            bytes.fromhex(header.get("extraData", "0x")[2:]),
            bytes.fromhex(header.get("mixHash", "")[2:]),
            bytes.fromhex(header.get("nonce", "0x0000000000000000")[2:]),
        ]
    )


def keccak256(data: bytes) -> bytes:
    """Compute Keccak-256 hash (placeholder - would use actual Keccak implementation)"""
    # This is a placeholder - in practice you'd use a proper Keccak implementation
    # like from Crypto.Hash import keccak
    import hashlib

    return hashlib.sha256(data).digest()  # NOT actual Keccak, just for demo


def compute_transaction_hash(tx: dict) -> str:
    """Compute transaction hash"""
    encoded = encode_transaction(tx)
    if tx.get("type") == "0x2":
        # EIP-1559: prepend type byte
        encoded = bytes([2]) + encoded

    hash_bytes = keccak256(encoded)
    return "0x" + hash_bytes.hex()


def compute_receipt_hash(receipt: dict) -> str:
    """Compute receipt hash"""
    encoded = encode_receipt(receipt)
    if receipt.get("type") == "0x2":
        # EIP-1559: prepend type byte
        encoded = bytes([2]) + encoded

    hash_bytes = keccak256(encoded)
    return "0x" + hash_bytes.hex()


def compute_block_hash(header: dict) -> str:
    """Compute block hash from header"""
    encoded = encode_block_header(header)
    hash_bytes = keccak256(encoded)
    return "0x" + hash_bytes.hex()
