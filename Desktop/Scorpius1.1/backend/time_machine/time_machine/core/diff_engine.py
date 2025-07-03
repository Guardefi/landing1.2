"""
Advanced Diff Engine with Trie-based and JSON Diffing
Generates comprehensive diffs between blockchain states with multiple output formats.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import Diff

logger = logging.getLogger(__name__)


class DiffFormat(str, Enum):
    """Supported diff output formats."""

    JSON = "json"
    HTML = "html"
    SARIF = "sarif"
    TEXT = "text"
    COMPACT = "compact"


class ChangeType(str, Enum):
    """Types of changes detected."""

    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class StateChange:
    """Represents a single state change."""

    path: str
    change_type: ChangeType
    old_value: Any = None
    new_value: Any = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DiffStatistics:
    """Statistics about a diff operation."""

    total_changes: int
    additions: int
    deletions: int
    modifications: int
    unchanged_items: int
    addresses_affected: int
    storage_slots_changed: int

    def to_dict(self) -> Dict[str, int]:
        return {
            "total_changes": self.total_changes,
            "additions": self.additions,
            "deletions": self.deletions,
            "modifications": self.modifications,
            "unchanged_items": self.unchanged_items,
            "addresses_affected": self.addresses_affected,
            "storage_slots_changed": self.storage_slots_changed,
        }


class DiffEngine:
    """
    Advanced diff engine that can generate comprehensive diffs between
    blockchain states using trie-based algorithms and multiple output formats.
    """

    def __init__(
        self,
        include_unchanged: bool = False,
        max_depth: int = 10,
        ignore_metadata: bool = True,
    ):
        self.include_unchanged = include_unchanged
        self.max_depth = max_depth
        self.ignore_metadata = ignore_metadata
        self.custom_comparators: Dict[str, callable] = {}
        self._load_default_comparators()

    def _load_default_comparators(self):
        """Load default field comparators."""
        self.custom_comparators.update(
            {
                "balance": self._compare_numeric_hex,
                "nonce": self._compare_numeric,
                "gas": self._compare_numeric,
                "timestamp": self._compare_timestamp,
                "block_number": self._compare_numeric,
            }
        )

    async def generate_diff(
        self,
        from_branch_id: str,
        to_branch_id: str,
        from_state: Dict[str, Any],
        to_state: Dict[str, Any],
        format: DiffFormat = DiffFormat.JSON,
    ) -> Diff:
        """
        Generate a comprehensive diff between two states.

        Args:
            from_branch_id: Source branch ID
            to_branch_id: Target branch ID
            from_state: Source state data
            to_state: Target state data
            format: Output format for the diff

        Returns:
            Diff: Generated diff object
        """
        logger.info(f"Generating diff between {from_branch_id} and {to_branch_id}")

        # Analyze state changes
        changes = self._analyze_state_changes(from_state, to_state)

        # Categorize changes
        storage_changes = self._extract_storage_changes(changes)
        balance_changes = self._extract_balance_changes(changes)
        code_changes = self._extract_code_changes(changes)
        nonce_changes = self._extract_nonce_changes(changes)
        log_changes = self._extract_log_changes(changes, from_state, to_state)
        gas_changes = self._extract_gas_changes(changes, from_state, to_state)

        # Calculate statistics
        stats = self._calculate_diff_statistics(changes)

        # Create diff object
        diff = Diff(
            from_branch=from_branch_id,
            to_branch=to_branch_id,
            storage_changes=storage_changes,
            balance_changes=balance_changes,
            code_changes=code_changes,
            nonce_changes=nonce_changes,
            log_changes=log_changes,
            gas_changes=gas_changes,
            metadata={
                "format": format.value,
                "statistics": stats.to_dict(),
                "generated_at": datetime.now().isoformat(),
                "include_unchanged": self.include_unchanged,
            },
        )

        logger.info(f"Generated diff with {stats.total_changes} changes")
        return diff

    def _analyze_state_changes(
        self, from_state: Dict[str, Any], to_state: Dict[str, Any]
    ) -> List[StateChange]:
        """Analyze changes between two states."""
        changes = []

        # Get all keys from both states
        all_keys = set(from_state.keys()) | set(to_state.keys())

        for key in all_keys:
            change = self._compare_values(key, from_state.get(key), to_state.get(key))
            if change:
                changes.append(change)

        # Deep analysis for nested structures
        for key in all_keys:
            if (
                key in from_state
                and key in to_state
                and isinstance(from_state[key], dict)
                and isinstance(to_state[key], dict)
            ):
                nested_changes = self._analyze_nested_changes(
                    key, from_state[key], to_state[key], depth=1
                )
                changes.extend(nested_changes)

        return changes

    def _analyze_nested_changes(
        self,
        base_path: str,
        from_dict: Dict[str, Any],
        to_dict: Dict[str, Any],
        depth: int,
    ) -> List[StateChange]:
        """Recursively analyze nested dictionary changes."""
        if depth > self.max_depth:
            return []

        changes = []
        all_keys = set(from_dict.keys()) | set(to_dict.keys())

        for key in all_keys:
            full_path = f"{base_path}.{key}"
            change = self._compare_values(
                full_path, from_dict.get(key), to_dict.get(key)
            )

            if change:
                changes.append(change)

            # Recurse for nested dictionaries
            if (
                key in from_dict
                and key in to_dict
                and isinstance(from_dict[key], dict)
                and isinstance(to_dict[key], dict)
            ):
                nested_changes = self._analyze_nested_changes(
                    full_path, from_dict[key], to_dict[key], depth + 1
                )
                changes.extend(nested_changes)

        return changes

    def _compare_values(
        self, path: str, old_value: Any, new_value: Any
    ) -> Optional[StateChange]:
        """Compare two values and return a StateChange if different."""
        # Determine change type
        if old_value is None and new_value is not None:
            change_type = ChangeType.ADDED
        elif old_value is not None and new_value is None:
            change_type = ChangeType.REMOVED
        elif old_value != new_value:
            change_type = ChangeType.MODIFIED
        else:
            change_type = ChangeType.UNCHANGED
            if not self.include_unchanged:
                return None

        # Use custom comparator if available
        field_name = path.split(".")[-1]
        if field_name in self.custom_comparators:
            comparator = self.custom_comparators[field_name]
            is_different, metadata = comparator(old_value, new_value)
            if not is_different and not self.include_unchanged:
                return None
        else:
            metadata = {}

        return StateChange(
            path=path,
            change_type=change_type,
            old_value=old_value,
            new_value=new_value,
            metadata=metadata,
        )

    def _extract_storage_changes(
        self, changes: List[StateChange]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract storage-related changes."""
        storage_changes = {}

        for change in changes:
            if "storage" in change.path.lower() or "slot" in change.path.lower():
                # Extract address and slot from path
                path_parts = change.path.split(".")

                # Try to identify address and slot
                address = None
                slot = None

                for i, part in enumerate(path_parts):
                    if part.startswith("0x") and len(part) == 42:  # Ethereum address
                        address = part
                    elif part.startswith("0x") and len(part) > 42:  # Storage slot
                        slot = part

                if address:
                    if address not in storage_changes:
                        storage_changes[address] = {}

                    slot_key = slot or change.path
                    storage_changes[address][slot_key] = {
                        "old_value": change.old_value,
                        "new_value": change.new_value,
                        "change_type": change.change_type.value,
                        "metadata": change.metadata,
                    }

        return storage_changes

    def _extract_balance_changes(
        self, changes: List[StateChange]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract balance-related changes."""
        balance_changes = {}

        for change in changes:
            if "balance" in change.path.lower():
                # Extract address from path
                path_parts = change.path.split(".")
                address = None

                for part in path_parts:
                    if part.startswith("0x") and len(part) == 42:
                        address = part
                        break

                if address:
                    balance_changes[address] = {
                        "old_balance": change.old_value,
                        "new_balance": change.new_value,
                        "change_type": change.change_type.value,
                        "delta": self._calculate_balance_delta(
                            change.old_value, change.new_value
                        ),
                        "metadata": change.metadata,
                    }

        return balance_changes

    def _extract_code_changes(
        self, changes: List[StateChange]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract code-related changes."""
        code_changes = {}

        for change in changes:
            if "code" in change.path.lower() or "bytecode" in change.path.lower():
                path_parts = change.path.split(".")
                address = None

                for part in path_parts:
                    if part.startswith("0x") and len(part) == 42:
                        address = part
                        break

                if address:
                    code_changes[address] = {
                        "old_code": change.old_value,
                        "new_code": change.new_value,
                        "change_type": change.change_type.value,
                        "code_size_change": self._calculate_code_size_change(
                            change.old_value, change.new_value
                        ),
                        "metadata": change.metadata,
                    }

        return code_changes

    def _extract_nonce_changes(
        self, changes: List[StateChange]
    ) -> Dict[str, Dict[str, Any]]:
        """Extract nonce-related changes."""
        nonce_changes = {}

        for change in changes:
            if "nonce" in change.path.lower():
                path_parts = change.path.split(".")
                address = None

                for part in path_parts:
                    if part.startswith("0x") and len(part) == 42:
                        address = part
                        break

                if address:
                    nonce_changes[address] = {
                        "old_nonce": change.old_value,
                        "new_nonce": change.new_value,
                        "change_type": change.change_type.value,
                        "nonce_delta": self._calculate_nonce_delta(
                            change.old_value, change.new_value
                        ),
                        "metadata": change.metadata,
                    }

        return nonce_changes

    def _extract_log_changes(
        self,
        changes: List[StateChange],
        from_state: Dict[str, Any],
        to_state: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Extract log-related changes."""
        log_changes = []

        # Compare logs if they exist in states
        from_logs = from_state.get("logs", [])
        to_logs = to_state.get("logs", [])

        # Simple log comparison - would be more sophisticated in reality
        if len(from_logs) != len(to_logs):
            log_changes.append(
                {
                    "change_type": "log_count_changed",
                    "old_count": len(from_logs),
                    "new_count": len(to_logs),
                    "description": f"Log count changed from {len(from_logs)} to {len(to_logs)}",
                }
            )

        return log_changes

    def _extract_gas_changes(
        self,
        changes: List[StateChange],
        from_state: Dict[str, Any],
        to_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Extract gas-related changes."""
        gas_changes = {}

        # Compare gas usage if available
        from_gas = from_state.get("gas_used", 0)
        to_gas = to_state.get("gas_used", 0)

        if from_gas != to_gas:
            gas_changes = {
                "old_gas": from_gas,
                "new_gas": to_gas,
                "gas_delta": to_gas - from_gas,
                "percentage_change": ((to_gas - from_gas) / from_gas * 100)
                if from_gas > 0
                else 0,
            }

        return gas_changes

    def _calculate_diff_statistics(self, changes: List[StateChange]) -> DiffStatistics:
        """Calculate statistics about the diff."""
        total_changes = len(changes)
        additions = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
        deletions = sum(1 for c in changes if c.change_type == ChangeType.REMOVED)
        modifications = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)
        unchanged_items = sum(
            1 for c in changes if c.change_type == ChangeType.UNCHANGED
        )

        # Count unique addresses affected
        addresses = set()
        storage_slots = 0

        for change in changes:
            path_parts = change.path.split(".")
            for part in path_parts:
                if part.startswith("0x") and len(part) == 42:
                    addresses.add(part)
                    break

            if "storage" in change.path.lower() or "slot" in change.path.lower():
                storage_slots += 1

        return DiffStatistics(
            total_changes=total_changes,
            additions=additions,
            deletions=deletions,
            modifications=modifications,
            unchanged_items=unchanged_items,
            addresses_affected=len(addresses),
            storage_slots_changed=storage_slots,
        )

    def format_diff(self, diff: Diff, format: DiffFormat) -> str:
        """
        Format diff for output in specified format.

        Args:
            diff: Diff object to format
            format: Output format

        Returns:
            str: Formatted diff
        """
        if format == DiffFormat.JSON:
            return self._format_json(diff)
        elif format == DiffFormat.HTML:
            return self._format_html(diff)
        elif format == DiffFormat.SARIF:
            return self._format_sarif(diff)
        elif format == DiffFormat.TEXT:
            return self._format_text(diff)
        elif format == DiffFormat.COMPACT:
            return self._format_compact(diff)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _format_json(self, diff: Diff) -> str:
        """Format diff as JSON."""
        return json.dumps(diff.to_dict(), indent=2)

    def _format_html(self, diff: Diff) -> str:
        """Format diff as HTML."""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Blockchain State Diff</title>
            <style>
                body {{ font-family: monospace; margin: 20px; }}
                .added {{ background-color: #d4edda; }}
                .removed {{ background-color: #f8d7da; }}
                .modified {{ background-color: #fff3cd; }}
                .section {{ margin: 20px 0; padding: 10px; border: 1px solid #ccc; }}
                h2 {{ color: #333; }}
                .stats {{ background-color: #f8f9fa; padding: 10px; }}
            </style>
        </head>
        <body>
            <h1>Blockchain State Diff</h1>
            <div class="stats">
                <h2>Statistics</h2>
                <p>From: {from_branch}</p>
                <p>To: {to_branch}</p>
                <p>Total Changes: {total_changes}</p>
            </div>
        """

        html = html_template.format(
            from_branch=diff.from_branch,
            to_branch=diff.to_branch,
            total_changes=len(diff.storage_changes)
            + len(diff.balance_changes)
            + len(diff.code_changes),
        )

        # Add sections for different change types
        if diff.storage_changes:
            html += '<div class="section"><h2>Storage Changes</h2>'
            for addr, changes in diff.storage_changes.items():
                html += f"<h3>Address: {addr}</h3>"
                for slot, change in changes.items():
                    html += f'<div class="modified">Slot {slot}: {change["old_value"]} → {change["new_value"]}</div>'
            html += "</div>"

        html += "</body></html>"
        return html

    def _format_sarif(self, diff: Diff) -> str:
        """Format diff as SARIF (Static Analysis Results Interchange Format)."""
        sarif = {
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Time Machine Diff Engine",
                            "version": "1.0.0",
                        }
                    },
                    "results": [],
                }
            ],
        }

        # Add storage changes as results
        for addr, changes in diff.storage_changes.items():
            for slot, change in changes.items():
                sarif["runs"][0]["results"].append(
                    {
                        "ruleId": "storage-change",
                        "message": {"text": f"Storage change at {addr} slot {slot}"},
                        "locations": [
                            {
                                "physicalLocation": {
                                    "artifactLocation": {
                                        "uri": f"blockchain://ethereum/address/{addr}"
                                    },
                                    "region": {
                                        "startLine": 1,
                                        "snippet": {"text": f"Storage slot {slot}"},
                                    },
                                }
                            }
                        ],
                    }
                )

        return json.dumps(sarif, indent=2)

    def _format_text(self, diff: Diff) -> str:
        """Format diff as plain text."""
        lines = [
            "Blockchain State Diff",
            f"From: {diff.from_branch}",
            f"To: {diff.to_branch}",
            f"Generated: {diff.created_at}",
            "",
        ]

        if diff.storage_changes:
            lines.append("=== Storage Changes ===")
            for addr, changes in diff.storage_changes.items():
                lines.append(f"Address: {addr}")
                for slot, change in changes.items():
                    lines.append(
                        f"  Slot {slot}: {change['old_value']} → {change['new_value']}"
                    )
            lines.append("")

        if diff.balance_changes:
            lines.append("=== Balance Changes ===")
            for addr, change in diff.balance_changes.items():
                lines.append(f"Address: {addr}")
                lines.append(
                    f"  Balance: {change['old_balance']} → {change['new_balance']}"
                )
            lines.append("")

        return "\n".join(lines)

    def _format_compact(self, diff: Diff) -> str:
        """Format diff in compact form."""
        stats = diff.metadata.get("statistics", {})
        return f"Diff: {stats.get('total_changes', 0)} changes, {stats.get('addresses_affected', 0)} addresses"

    # Custom comparators
    def _compare_numeric_hex(
        self, old_val: Any, new_val: Any
    ) -> Tuple[bool, Dict[str, Any]]:
        """Compare hex numeric values."""
        try:
            old_num = int(old_val, 0) if isinstance(old_val, str) else old_val
            new_num = int(new_val, 0) if isinstance(new_val, str) else new_val

            is_different = old_num != new_num
            metadata = {
                "old_numeric": old_num,
                "new_numeric": new_num,
                "delta": new_num - old_num if is_different else 0,
            }
            return is_different, metadata
        except (ValueError, TypeError):
            return old_val != new_val, {}

    def _compare_numeric(
        self, old_val: Any, new_val: Any
    ) -> Tuple[bool, Dict[str, Any]]:
        """Compare numeric values."""
        try:
            old_num = int(old_val) if old_val is not None else 0
            new_num = int(new_val) if new_val is not None else 0

            is_different = old_num != new_num
            metadata = {
                "old_numeric": old_num,
                "new_numeric": new_num,
                "delta": new_num - old_num if is_different else 0,
            }
            return is_different, metadata
        except (ValueError, TypeError):
            return old_val != new_val, {}

    def _compare_timestamp(
        self, old_val: Any, new_val: Any
    ) -> Tuple[bool, Dict[str, Any]]:
        """Compare timestamp values."""
        try:
            old_ts = int(old_val) if old_val is not None else 0
            new_ts = int(new_val) if new_val is not None else 0

            is_different = old_ts != new_ts
            metadata = {
                "old_timestamp": old_ts,
                "new_timestamp": new_ts,
                "time_delta_seconds": new_ts - old_ts if is_different else 0,
            }
            return is_different, metadata
        except (ValueError, TypeError):
            return old_val != new_val, {}

    def _calculate_balance_delta(self, old_balance: Any, new_balance: Any) -> str:
        """Calculate balance change delta."""
        try:
            old_val = (
                int(old_balance, 0)
                if isinstance(old_balance, str)
                else (old_balance or 0)
            )
            new_val = (
                int(new_balance, 0)
                if isinstance(new_balance, str)
                else (new_balance or 0)
            )
            delta = new_val - old_val
            return f"{delta:+d}"
        except (ValueError, TypeError):
            return "N/A"

    def _calculate_nonce_delta(self, old_nonce: Any, new_nonce: Any) -> int:
        """Calculate nonce change delta."""
        try:
            old_val = int(old_nonce) if old_nonce is not None else 0
            new_val = int(new_nonce) if new_nonce is not None else 0
            return new_val - old_val
        except (ValueError, TypeError):
            return 0

    def _calculate_code_size_change(
        self, old_code: Any, new_code: Any
    ) -> Dict[str, int]:
        """Calculate code size change."""
        old_size = len(str(old_code or ""))
        new_size = len(str(new_code or ""))
        return {
            "old_size": old_size,
            "new_size": new_size,
            "size_delta": new_size - old_size,
        }
