import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class TransactionAnalyzer:
    def __init__(self):
        self.suspicious_patterns = {
            "quick_drain": {
                "description": "Funds quickly drained after deposits",
                "severity": 0.8,
                "technique": "Hidden Transfer",
            },
            "owner_only_withdrawals": {
                "description": "Only contract owner can withdraw funds",
                "severity": 0.7,
                "technique": "Access Restriction",
            },
            "failed_user_withdrawals": {
                "description": "User withdrawals consistently fail",
                "severity": 0.9,
                "technique": "Unexpected Revert",
            },
            "honeypot_signature": {
                "description": "Transaction pattern matching known honeypots",
                "severity": 0.95,
                "technique": "Straw Man Contract",
            },
        }

    async def analyze_transactions(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Analyze transaction history for honeypot patterns"""
        if not transactions:
            return {
                "confidence": 0,
                "patterns_detected": [],
                "error": "No transaction data available",
            }

        try:
            # Run different transaction pattern analyses
            quick_drain = await self._detect_quick_drain(transactions)
            owner_withdrawals = await self._detect_owner_only_withdrawals(transactions)
            failed_withdrawals = await self._detect_failed_withdrawals(transactions)

            # Combine results
            patterns_detected = []
            total_severity = 0

            for pattern_result in [quick_drain, owner_withdrawals, failed_withdrawals]:
                if pattern_result.get("detected"):
                    pattern_name = pattern_result.get("pattern")
                    pattern_data = self.suspicious_patterns.get(pattern_name)

                    if pattern_data:
                        patterns_detected.append(
                            {
                                "name": pattern_name,
                                "description": pattern_data["description"],
                                "evidence": pattern_result.get("evidence", {}),
                                "technique": pattern_data["technique"],
                            }
                        )
                        total_severity += pattern_data["severity"]

            # Calculate confidence (cap at 1.0)
            confidence = min(total_severity, 1.0)

            detected_techniques = list(
                set(
                    pattern_data["technique"]
                    for pattern_name in [p["name"] for p in patterns_detected]
                    for pattern_data in [self.suspicious_patterns.get(pattern_name)]
                    if pattern_data
                )
            )

            return {
                "confidence": confidence,
                "patterns_detected": patterns_detected,
                "transaction_count": len(transactions),
                "detected_techniques": detected_techniques,
            }

        except Exception as e:
            return {"confidence": 0, "patterns_detected": [], "error": str(e)}

    async def _detect_quick_drain(self, transactions: List[Dict]) -> Dict[str, Any]:
        """Detect if funds are quickly drained after deposits"""
        deposits = [
            tx
            for tx in transactions
            if tx.get("value", 0) > 0 and tx.get("to") == transactions[0].get("address")
        ]
        withdrawals = [
            tx
            for tx in transactions
            if tx.get("value", 0) > 0
            and tx.get("from") == transactions[0].get("address")
        ]

        if not deposits or not withdrawals:
            return {"detected": False, "pattern": "quick_drain"}

        # Check if significant withdrawals happen shortly after deposits
        suspicious_pairs = []

        for deposit in deposits:
            deposit_time = deposit.get("timestamp", 0)
            deposit_value = deposit.get("value", 0)

            for withdrawal in withdrawals:
                withdrawal_time = withdrawal.get("timestamp", 0)
                withdrawal_value = withdrawal.get("value", 0)

                time_diff = withdrawal_time - deposit_time

                # If withdrawal happened within 5 minutes of deposit
                # and withdrawal amount is similar to deposit
                if (0 < time_diff < 300) and (withdrawal_value > deposit_value * 0.7):
                    suspicious_pairs.append(
                        {
                            "deposit_tx": deposit.get("hash"),
                            "withdrawal_tx": withdrawal.get("hash"),
                            "time_diff_seconds": time_diff,
                            "deposit_value": deposit_value,
                            "withdrawal_value": withdrawal_value,
                        }
                    )

        detected = len(suspicious_pairs) > 0

        return {
            "detected": detected,
            "pattern": "quick_drain",
            "evidence": {
                "suspicious_pairs": suspicious_pairs,
                "deposit_count": len(deposits),
                "withdrawal_count": len(withdrawals),
            },
        }

    async def _detect_owner_only_withdrawals(
        self, transactions: List[Dict]
    ) -> Dict[str, Any]:
        """Detect if only the owner can withdraw funds"""
        if not transactions:
            return {"detected": False, "pattern": "owner_only_withdrawals"}

        # Identify likely contract owner (first address to interact or deployer)
        likely_owner = transactions[0].get("from")

        withdrawals = [
            tx
            for tx in transactions
            if tx.get("value", 0) > 0
            and tx.get("from") == transactions[0].get("address")
        ]

        if not withdrawals:
            return {"detected": False, "pattern": "owner_only_withdrawals"}

        # Check if all withdrawals are to the same address (likely owner)
        withdrawal_recipients = {}

        for withdrawal in withdrawals:
            recipient = withdrawal.get("to")
            amount = withdrawal.get("value", 0)

            if recipient in withdrawal_recipients:
                withdrawal_recipients[recipient] += amount
            else:
                withdrawal_recipients[recipient] = amount

        # If only one recipient for all withdrawals and it's the likely owner
        if len(withdrawal_recipients) == 1 and likely_owner in withdrawal_recipients:
            return {
                "detected": True,
                "pattern": "owner_only_withdrawals",
                "evidence": {
                    "owner": likely_owner,
                    "total_withdrawn": withdrawal_recipients[likely_owner],
                    "withdrawal_count": len(withdrawals),
                },
            }

        return {"detected": False, "pattern": "owner_only_withdrawals"}

    async def _detect_failed_withdrawals(
        self, transactions: List[Dict]
    ) -> Dict[str, Any]:
        """Detect if user withdrawals consistently fail"""
        # In production, we'd analyze failed transaction receipts
        # This is a placeholder implementation
        return {"detected": False, "pattern": "failed_user_withdrawals"}
