"""
Monitoring and metrics collection
"""

import json
import time
from typing import List


class MetricsCollector:
    """Metrics and audit logging collector"""

    async def log_wallet_check(
        self, org_id: str, addresses: List[str], chains: List[str], result_hash: str
    ):
        """Log wallet check for audit trail"""
        audit_record = {
            "event_type": "wallet_check",
            "org_id": org_id,
            "addresses": addresses,
            "chains": chains,
            "result_hash": result_hash,
            "timestamp": time.time(),
        }

        # In production: send to QLDB or audit database
        print(f"AUDIT: {json.dumps(audit_record)}")

    async def log_revoke_request(
        self, org_id: str, wallet_address: str, chain: str, tx_hash: str
    ):
        """Log revoke request for audit trail"""
        audit_record = {
            "event_type": "revoke_request",
            "org_id": org_id,
            "wallet_address": wallet_address,
            "chain": chain,
            "tx_hash": tx_hash,
            "timestamp": time.time(),
        }

        # In production: send to QLDB or audit database
        print(f"AUDIT: {json.dumps(audit_record)}")


# Global metrics instance
metrics = MetricsCollector()
