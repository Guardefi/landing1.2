"""
Enhanced Preprocessing and Normalization
Advanced bytecode normalization for similarity detection
"""

import asyncio
import hashlib
import logging
import re
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class BytecodeNormalizer:
    """Advanced bytecode normalization for similarity detection"""

    def __init__(self):
        self.optimizations = [
            self._normalize_constants,
            self._normalize_addresses,
            self._normalize_function_selectors,
            self._remove_metadata,
            self._normalize_push_sequences,
            self._apply_peephole_optimizations,
            self._normalize_jump_destinations,
        ]

    async def normalize(self, bytecode: str) -> str:
        """Apply all normalization steps"""
        if bytecode.startswith("0x"):
            bytecode = bytecode[2:]

        normalized = bytecode

        # Apply each optimization
        for optimization in self.optimizations:
            try:
                normalized = await optimization(normalized)
            except Exception as e:
                logger.warning(f"Normalization step failed: {e}")
                continue

        return normalized

    async def _normalize_constants(self, bytecode: str) -> str:
        """Normalize constant values while preserving semantic meaning"""
        normalized = bytecode

        # Pattern for PUSH instructions followed by hex values
        push_pattern = r"(6[0-9a-f]|7[0-9a-f])([0-9a-f]*)"

        def replace_constant(match):
            opcode = match.group(1)
            value = match.group(2)

            # Preserve important constants (function selectors, addresses)
            if len(value) == 8:  # Function selector
                return match.group(0)
            elif len(value) == 40:  # Address
                return match.group(0)
            elif value == "00" * (len(value) // 2):  # Zero values
                return match.group(0)
            elif int(value, 16) < 256:  # Small numbers
                return match.group(0)
            else:
                # Replace with normalized constant
                return opcode + "CONST" + str(len(value) // 2).zfill(2)

        normalized = re.sub(
            push_pattern, replace_constant, normalized, flags=re.IGNORECASE
        )
        return normalized

    async def _normalize_addresses(self, bytecode: str) -> str:
        """Normalize contract addresses while preserving special ones"""
        # Pattern for 20-byte addresses (40 hex chars)
        address_pattern = r"73([0-9a-f]{40})"

        def replace_address(match):
            address = match.group(1)

            # Preserve zero address and common precompiles
            if address == "00" * 20:
                return match.group(0)
            elif address.startswith("000000000000000000000000000000000000000"):
                return match.group(0)  # Precompiled contracts
            else:
                return (
                    "73"
                    + "ADDR"
                    + hashlib.md5(address.encode()).hexdigest()[:8].upper()
                )

        return re.sub(address_pattern, replace_address, bytecode, flags=re.IGNORECASE)

    async def _normalize_function_selectors(self, bytecode: str) -> str:
        """Normalize function selectors based on common patterns"""
        # Function selectors are typically 4-byte values
        selector_pattern = r"63([0-9a-f]{8})"

        selectors_seen = {}
        selector_counter = 0

        def replace_selector(match):
            nonlocal selector_counter
            selector = match.group(1)

            if selector not in selectors_seen:
                selectors_seen[selector] = f"FUNC{selector_counter:04d}"
                selector_counter += 1

            return "63" + selectors_seen[selector]

        return re.sub(selector_pattern, replace_selector, bytecode, flags=re.IGNORECASE)

    async def _remove_metadata(self, bytecode: str) -> str:
        """Remove Solidity metadata and constructor code"""
        # Solidity metadata hash pattern (IPFS hash at the end)
        metadata_pattern = r"a2646970667358221220[0-9a-f]{64}64736f6c63[0-9a-f]{6}0033$"
        bytecode = re.sub(metadata_pattern, "", bytecode, flags=re.IGNORECASE)

        # Remove CBOR encoded metadata
        cbor_pattern = r"a264697066735822[0-9a-f]*64736f6c63[0-9a-f]*0033$"
        bytecode = re.sub(cbor_pattern, "", bytecode, flags=re.IGNORECASE)

        return bytecode

    async def _normalize_push_sequences(self, bytecode: str) -> str:
        """Normalize sequences of PUSH operations"""
        # Find sequences of PUSH operations and normalize based on pattern
        push_sequence_pattern = r"(6[0-9a-f]([0-9a-f]*)){2,}"

        def normalize_push_sequence(match):
            sequence = match.group(0)
            # Count pushes and create normalized representation
            push_count = len(re.findall(r"6[0-9a-f]", sequence))
            return f"PUSHSEQ{push_count:02d}"

        return re.sub(
            push_sequence_pattern,
            normalize_push_sequence,
            bytecode,
            flags=re.IGNORECASE,
        )

    async def _apply_peephole_optimizations(self, bytecode: str) -> str:
        """Apply common peephole optimizations"""
        # DUP followed by POP -> remove both
        bytecode = re.sub(r"8[0-9a-f]50", "", bytecode, flags=re.IGNORECASE)

        # PUSH1 0x00 PUSH1 0x00 -> PUSH2 0x0000 (common pattern optimization)
        bytecode = re.sub(r"6000" * 2, "610000", bytecode, flags=re.IGNORECASE)

        # Remove redundant JUMPDEST after unconditional JUMP
        bytecode = re.sub(r"565b", "56", bytecode, flags=re.IGNORECASE)

        return bytecode

    async def _normalize_jump_destinations(self, bytecode: str) -> str:
        """Normalize jump destinations while preserving control flow"""
        # Find all JUMPDEST instructions (5b)
        jumpdests = []
        for match in re.finditer(r"5b", bytecode, re.IGNORECASE):
            jumpdests.append(match.start())

        # Create mapping from position to normalized destination
        dest_mapping = {}
        for i, pos in enumerate(jumpdests):
            dest_mapping[pos] = f"DEST{i:04d}"

        # Replace jump destinations in PUSH instructions that precede JUMP/JUMPI
        normalized = bytecode
        for pos, dest_name in dest_mapping.items():
            # This is a simplified approach - in practice, need to track jumps properly
            hex_pos = hex(pos // 2)[2:].upper().zfill(4)
            if f"61{hex_pos}" in normalized:  # PUSH2 with destination
                normalized = normalized.replace(f"61{hex_pos}", f"61{dest_name}")

        return normalized


class InstructionLevelNormalizer:
    """Instruction-level normalization for noise reduction"""

    def __init__(self):
        self.noise_instructions = {
            "INVALID",
            "REVERT",
            "SELFDESTRUCT",  # Instructions that add noise
        }

    async def normalize_instructions(self, opcodes: List[Dict]) -> List[Dict]:
        """Normalize at instruction level"""
        normalized = []

        for i, opcode in enumerate(opcodes):
            # Skip noise instructions
            if opcode["mnemonic"] in self.noise_instructions:
                continue

            # Normalize stack operations
            if opcode["mnemonic"].startswith("DUP"):
                normalized.append({"mnemonic": "DUP_N", "operand": None})
            elif opcode["mnemonic"].startswith("SWAP"):
                normalized.append({"mnemonic": "SWAP_N", "operand": None})
            elif opcode["mnemonic"].startswith("PUSH"):
                # Preserve important values, normalize others
                if self._is_important_value(opcode.get("operand", "")):
                    normalized.append(opcode)
                else:
                    push_size = opcode["mnemonic"][4:]
                    normalized.append(
                        {"mnemonic": f"PUSH{push_size}", "operand": "NORMALIZED"}
                    )
            else:
                normalized.append(opcode)

        return normalized

    def _is_important_value(self, value: str) -> bool:
        """Check if a value should be preserved during normalization"""
        if not value:
            return False

        # Preserve function selectors (4 bytes)
        if len(value) == 8:
            return True

        # Preserve addresses (20 bytes)
        if len(value) == 40:
            return True

        # Preserve zero values
        if value == "00" * (len(value) // 2):
            return True

        # Preserve small numbers (< 256)
        try:
            if int(value, 16) < 256:
                return True
        except ValueError:
            pass

        return False


class FeatureExtractor:
    """Extract features from normalized bytecode"""

    def __init__(self):
        self.normalizer = BytecodeNormalizer()
        self.instruction_normalizer = InstructionLevelNormalizer()

    async def extract_features(self, bytecode: str) -> Dict:
        """Extract comprehensive features from bytecode"""
        # Normalize bytecode
        normalized = await self.normalizer.normalize(bytecode)

        # Parse to opcodes
        opcodes = await self._parse_bytecode_to_opcodes(normalized)

        # Normalize instructions
        normalized_opcodes = await self.instruction_normalizer.normalize_instructions(
            opcodes
        )

        # Extract various feature types
        features = {
            "opcode_sequence": self._extract_opcode_sequence(normalized_opcodes),
            "opcode_histogram": self._extract_opcode_histogram(normalized_opcodes),
            "control_flow_features": self._extract_control_flow_features(
                normalized_opcodes
            ),
            "data_dependency_features": self._extract_data_dependency_features(
                normalized_opcodes
            ),
            "structural_features": self._extract_structural_features(
                normalized_opcodes
            ),
        }

        return features

    async def _parse_bytecode_to_opcodes(self, bytecode: str) -> List[Dict]:
        """Parse bytecode to opcode list (simplified version)"""
        # This should use the proper parser from comparison_engine
        # Simplified implementation for feature extraction
        opcodes = []
        i = 0

        while i < len(bytecode):
            if i + 1 < len(bytecode):
                hex_byte = bytecode[i : i + 2]
                try:
                    byte_val = int(hex_byte, 16)
                    opcode = self._hex_to_opcode(byte_val)
                    if opcode:
                        opcodes.append({"mnemonic": opcode, "operand": None})
                except ValueError:
                    pass
                i += 2
            else:
                break

        return opcodes

    def _hex_to_opcode(self, byte_val: int) -> str:
        """Convert hex byte to opcode (simplified)"""
        # Simplified mapping - use full mapping in production
        opcode_map = {
            0x00: "STOP",
            0x01: "ADD",
            0x02: "MUL",
            0x03: "SUB",
            0x04: "DIV",
            0x05: "SDIV",
            0x50: "POP",
            0x51: "MLOAD",
            0x52: "MSTORE",
            0x54: "SLOAD",
            0x55: "SSTORE",
            0x56: "JUMP",
            0x57: "JUMPI",
            0x5B: "JUMPDEST",
            0xF3: "RETURN",
            0xFD: "REVERT",
        }

        if 0x60 <= byte_val <= 0x7F:
            return f"PUSH{byte_val - 0x5f}"
        elif 0x80 <= byte_val <= 0x8F:
            return f"DUP{byte_val - 0x7f}"
        elif 0x90 <= byte_val <= 0x9F:
            return f"SWAP{byte_val - 0x8f}"
        else:
            return opcode_map.get(byte_val, "UNKNOWN")

    def _extract_opcode_sequence(self, opcodes: List[Dict]) -> List[str]:
        """Extract sequence of opcodes"""
        return [opcode["mnemonic"] for opcode in opcodes]

    def _extract_opcode_histogram(self, opcodes: List[Dict]) -> Dict[str, int]:
        """Extract opcode frequency histogram"""
        histogram = {}
        for opcode in opcodes:
            mnemonic = opcode["mnemonic"]
            histogram[mnemonic] = histogram.get(mnemonic, 0) + 1
        return histogram

    def _extract_control_flow_features(self, opcodes: List[Dict]) -> Dict:
        """Extract control flow related features"""
        jump_count = 0
        jumpi_count = 0
        jumpdest_count = 0

        for opcode in opcodes:
            if opcode["mnemonic"] == "JUMP":
                jump_count += 1
            elif opcode["mnemonic"] == "JUMPI":
                jumpi_count += 1
            elif opcode["mnemonic"] == "JUMPDEST":
                jumpdest_count += 1

        return {
            "jump_count": jump_count,
            "jumpi_count": jumpi_count,
            "jumpdest_count": jumpdest_count,
            "total_jumps": jump_count + jumpi_count,
        }

    def _extract_data_dependency_features(self, opcodes: List[Dict]) -> Dict:
        """Extract data dependency features"""
        push_count = 0
        pop_count = 0
        dup_count = 0
        swap_count = 0

        for opcode in opcodes:
            if opcode["mnemonic"].startswith("PUSH"):
                push_count += 1
            elif opcode["mnemonic"] == "POP":
                pop_count += 1
            elif opcode["mnemonic"].startswith("DUP"):
                dup_count += 1
            elif opcode["mnemonic"].startswith("SWAP"):
                swap_count += 1

        return {
            "push_count": push_count,
            "pop_count": pop_count,
            "dup_count": dup_count,
            "swap_count": swap_count,
            "stack_balance": push_count - pop_count,
        }

    def _extract_structural_features(self, opcodes: List[Dict]) -> Dict:
        """Extract structural features"""
        return {
            "total_instructions": len(opcodes),
            "unique_opcodes": len(set(op["mnemonic"] for op in opcodes)),
            "complexity_ratio": len(set(op["mnemonic"] for op in opcodes))
            / len(opcodes)
            if opcodes
            else 0,
        }
