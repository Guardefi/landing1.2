import asyncio
import re
from typing import Any, Dict, List, Optional


class BytecodeAnalyzer:
    def __init__(self):
        self.opcode_patterns = {}

    async def load_patterns(self):
        """Load bytecode analysis patterns"""
        # Common EVM opcodes that might indicate malicious behavior
        self.opcode_patterns = {
            "selfdestruct_pattern": {
                "opcodes": ["SELFDESTRUCT", "SUICIDE"],
                "severity": 0.7,
                "description": "Contract can be self-destructed",
                "technique": "Hidden Self Destruct",
            },
            "delegatecall_pattern": {
                "opcodes": ["DELEGATECALL"],
                "severity": 0.6,
                "description": "Uses delegatecall which can be dangerous",
                "technique": "Proxy Manipulation",
            },
            "balance_check_pattern": {
                "opcodes": ["BALANCE", "SELFBALANCE"],
                "severity": 0.5,
                "description": "Contract checks its own balance",
                "technique": "Balance Disorder",
            },
            "storage_manipulation_pattern": {
                "opcodes": ["SSTORE"],
                "severity": 0.4,
                "description": "Contract manipulates storage",
                "technique": "Hidden State Update",
            },
            "complex_fallback_pattern": {
                "opcodes": ["CALLVALUE", "ISZERO", "PUSH1", "JUMPI"],
                "severity": 0.3,
                "description": "Complex fallback function",
                "technique": "Unexpected Revert",
            },
        }

    def _parse_bytecode(self, bytecode: str) -> List[str]:
        """Parse bytecode into opcodes"""
        # This is a simplified implementation
        # In production, use a proper EVM disassembler

        # Remove '0x' prefix if present
        if bytecode.startswith("0x"):
            bytecode = bytecode[2:]

        # Simple opcode extraction (not complete)
        common_opcodes = {
            "00": "STOP",
            "01": "ADD",
            "02": "MUL",
            "03": "SUB",
            "04": "DIV",
            "10": "LT",
            "11": "GT",
            "54": "SLOAD",
            "55": "SSTORE",
            "31": "BALANCE",
            "33": "CALLER",
            "3B": "EXTCODESIZE",
            "41": "COINBASE",
            "42": "TIMESTAMP",
            "47": "SELFBALANCE",
            "F1": "CALL",
            "F2": "CALLCODE",
            "F4": "DELEGATECALL",
            "F5": "CREATE2",
            "FF": "SELFDESTRUCT",
        }

        opcodes = []

        # Extract opcodes (simplified)
        i = 0
        while i < len(bytecode):
            byte = bytecode[i : i + 2].upper()
            if byte in common_opcodes:
                opcodes.append(common_opcodes[byte])
            i += 2

        return opcodes

    async def analyze_bytecode(self, bytecode: str) -> Dict[str, Any]:
        """Analyze contract bytecode for suspicious patterns"""
        if not bytecode:
            return {
                "confidence": 0,
                "detected_patterns": [],
                "opcode_stats": {},
                "error": "No bytecode provided",
            }

        if not self.opcode_patterns:
            await self.load_patterns()

        try:
            opcodes = self._parse_bytecode(bytecode)

            if not opcodes:
                return {
                    "confidence": 0,
                    "detected_patterns": [],
                    "opcode_stats": {},
                    "error": "Failed to parse bytecode",
                }

            # Analyze opcodes
            detected_patterns = []
            total_severity = 0

            # Count opcodes
            opcode_counts = {}
            for opcode in opcodes:
                if opcode in opcode_counts:
                    opcode_counts[opcode] += 1
                else:
                    opcode_counts[opcode] = 1

            # Check for patterns
            for pattern_name, pattern_data in self.opcode_patterns.items():
                pattern_opcodes = pattern_data["opcodes"]

                # Check if all opcodes in pattern are present
                if all(opcode in opcodes for opcode in pattern_opcodes):
                    detected_patterns.append(
                        {
                            "name": pattern_name,
                            "description": pattern_data["description"],
                            "severity": pattern_data["severity"],
                            "technique": pattern_data["technique"],
                        }
                    )

                    total_severity += pattern_data["severity"]

            # Advanced bytecode metrics
            bytecode_metrics = self._calculate_bytecode_metrics(bytecode, opcode_counts)

            # Calculate confidence (capped at 1.0)
            confidence = min(total_severity, 1.0)

            # Extract unique techniques
            detected_techniques = list(
                set(pattern["technique"] for pattern in detected_patterns)
            )

            return {
                "confidence": confidence,
                "detected_patterns": detected_patterns,
                "detected_techniques": detected_techniques,
                "opcode_stats": {
                    k: v
                    for k, v in sorted(
                        opcode_counts.items(), key=lambda x: x[1], reverse=True
                    )
                },
                "bytecode_metrics": bytecode_metrics,
            }

        except Exception as e:
            return {
                "confidence": 0,
                "detected_patterns": [],
                "opcode_stats": {},
                "error": str(e),
            }

    def _calculate_bytecode_metrics(
        self, bytecode: str, opcode_counts: Dict[str, int]
    ) -> Dict[str, Any]:
        """Calculate advanced bytecode metrics"""
        metrics = {}

        # Bytecode size
        metrics["bytecode_length"] = len(bytecode)

        # Opcode diversity
        metrics["unique_opcodes"] = len(opcode_counts)

        # Complexity estimation
        control_flow_opcodes = ["JUMP", "JUMPI", "JUMPDEST"]
        control_flow_count = sum(
            opcode_counts.get(op, 0) for op in control_flow_opcodes
        )

        metrics["control_flow_complexity"] = control_flow_count

        # Ratio of storage operations
        storage_opcodes = ["SLOAD", "SSTORE"]
        storage_ops_count = sum(opcode_counts.get(op, 0) for op in storage_opcodes)

        if sum(opcode_counts.values()) > 0:
            metrics["storage_op_ratio"] = storage_ops_count / sum(
                opcode_counts.values()
            )
        else:
            metrics["storage_op_ratio"] = 0

        # External call ratio
        external_call_opcodes = ["CALL", "CALLCODE", "DELEGATECALL", "STATICCALL"]
        external_call_count = sum(
            opcode_counts.get(op, 0) for op in external_call_opcodes
        )

        if sum(opcode_counts.values()) > 0:
            metrics["external_call_ratio"] = external_call_count / sum(
                opcode_counts.values()
            )
        else:
            metrics["external_call_ratio"] = 0

        return metrics
