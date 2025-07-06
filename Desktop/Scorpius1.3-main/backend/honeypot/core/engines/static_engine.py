import asyncio
import re
from typing import Any, Dict, List


class StaticEngine:
    def __init__(self):
        self.patterns = {}
        self.initialized = False

    async def load_patterns(self):
        """Load honeypot detection patterns"""
        self.patterns = {
            "selfdestruct": {
                "regex": r"SELFDESTRUCT|SUICIDE",
                "severity": 0.7,
                "technique": "Hidden Self Destruct",
            },
            "hidden_transfer": {
                "regex": r"CALL.*(?=.*BALANCE)(?=.*ZERO)",
                "severity": 0.8,
                "technique": "Hidden Transfer",
            },
            "balance_check": {
                "regex": r"BALANCE.*(?=.*ISZERO)",
                "severity": 0.6,
                "technique": "Balance Disorder",
            },
            "owner_check": {
                "regex": r"CALLER.*(?=.*EQ)(?=.*JUMPI)",
                "severity": 0.5,
                "technique": "Access Restriction",
            },
            "timestamp_dependency": {
                "regex": r"TIMESTAMP",
                "severity": 0.4,
                "technique": "Timestamp Manipulation",
            },
            "reentry_guard": {
                "regex": r"SLOAD.*(?=.*ISZERO)",
                "severity": 0.5,
                "technique": "Unexpected Revert",
            },
        }
        self.initialized = True

    async def analyze(self, contract_data: dict) -> Dict[str, Any]:
        """Run static analysis on contract bytecode and source code"""
        if not self.initialized:
            await self.load_patterns()

        bytecode = contract_data.get("bytecode", "")
        source_code = contract_data.get("source_code", "")
        abi = contract_data.get("abi", [])

        if not bytecode:
            return {"confidence": 0, "techniques": [], "error": "No bytecode available"}

        try:
            # Apply different analysis techniques
            pattern_matches = await self._find_pattern_matches(bytecode)
            function_analysis = await self._analyze_function_signatures(abi)
            source_analysis = (
                await self._analyze_source_code(source_code) if source_code else {}
            )

            # Combine results
            techniques = (
                pattern_matches.get("techniques", [])
                + function_analysis.get("techniques", [])
                + source_analysis.get("techniques", [])
            )

            # Calculate combined confidence
            confidence_values = [
                pattern_matches.get("confidence", 0),
                function_analysis.get("confidence", 0),
                source_analysis.get("confidence", 0),
            ]
            non_zero_values = [c for c in confidence_values if c > 0]
            confidence = (
                sum(non_zero_values) / len(non_zero_values) if non_zero_values else 0
            )

            return {
                "confidence": confidence,
                "techniques": list(set(techniques)),
                "pattern_matches": pattern_matches.get("matches", {}),
                "suspicious_functions": function_analysis.get(
                    "suspicious_functions", []
                ),
            }

        except Exception as e:
            return {"confidence": 0, "techniques": [], "error": str(e)}

    async def _find_pattern_matches(self, bytecode: str) -> Dict[str, Any]:
        """Find patterns in bytecode that indicate honeypot techniques"""
        matches = {}
        techniques = []
        total_severity = 0

        for name, pattern in self.patterns.items():
            regex = pattern["regex"]
            match_count = len(re.findall(regex, bytecode))

            if match_count > 0:
                severity = pattern["severity"]
                matches[name] = {"count": match_count, "severity": severity}
                techniques.append(pattern["technique"])
                total_severity += severity

        confidence = min(total_severity, 1.0)

        return {"confidence": confidence, "techniques": techniques, "matches": matches}

    async def _analyze_function_signatures(self, abi: List[Dict]) -> Dict[str, Any]:
        """Analyze function signatures for suspicious patterns"""
        suspicious_functions = []
        techniques = []

        if not abi:
            return {"confidence": 0, "techniques": [], "suspicious_functions": []}

        # Check for honeypot indicators in function signatures
        honeypot_indicators = {
            "claim": {"severity": 0.5, "technique": "False Advertising"},
            "collect": {"severity": 0.5, "technique": "False Advertising"},
            "withdraw": {"severity": 0.6, "technique": "False Advertising"},
            "getReward": {"severity": 0.4, "technique": "False Advertising"},
            "mint": {"severity": 0.3, "technique": "False Advertising"},
        }

        public_functions = [
            func
            for func in abi
            if func.get("type") == "function"
            and func.get("stateMutability") in ["nonpayable", "payable"]
        ]

        total_severity = 0

        for func in public_functions:
            name = func.get("name", "").lower()
            inputs = func.get("inputs", [])
            payable = func.get("stateMutability") == "payable"

            # Check for indicator matches
            for indicator, data in honeypot_indicators.items():
                if indicator in name and payable:
                    suspicious_functions.append(
                        {
                            "name": func.get("name"),
                            "payable": payable,
                            "reason": f"Suspicious {indicator} function",
                        }
                    )

                    if data["technique"] not in techniques:
                        techniques.append(data["technique"])

                    total_severity += data["severity"]
                    break

        confidence = min(total_severity, 1.0)

        return {
            "confidence": confidence,
            "techniques": techniques,
            "suspicious_functions": suspicious_functions,
        }

    async def _analyze_source_code(self, source_code: str) -> Dict[str, Any]:
        """Analyze source code for honeypot patterns if available"""
        if not source_code:
            return {"confidence": 0, "techniques": []}

        techniques = []
        suspicious_patterns = []

        # Honeypot indicators in source code
        source_indicators = [
            {
                "regex": r"require\s*\(\s*msg\.sender\s*==\s*owner\s*\)",
                "technique": "Access Restriction",
                "severity": 0.3,
            },
            {
                "regex": r"selfdestruct\s*\(",
                "technique": "Hidden Self Destruct",
                "severity": 0.7,
            },
            {
                "regex": r"block\.timestamp",
                "technique": "Timestamp Manipulation",
                "severity": 0.4,
            },
            {
                "regex": r"require\s*\(\s*.*?\.balance\s*",
                "technique": "Balance Disorder",
                "severity": 0.6,
            },
        ]

        total_severity = 0

        for indicator in source_indicators:
            matches = re.findall(indicator["regex"], source_code)
            if matches:
                suspicious_patterns.append(
                    {
                        "pattern": indicator["regex"],
                        "matches": len(matches),
                        "context": str(
                            matches[:3]
                        ),  # Include first 3 matches as context
                    }
                )

                if indicator["technique"] not in techniques:
                    techniques.append(indicator["technique"])

                total_severity += indicator["severity"]

        confidence = min(total_severity, 1.0)

        return {
            "confidence": confidence,
            "techniques": techniques,
            "suspicious_patterns": suspicious_patterns,
        }
