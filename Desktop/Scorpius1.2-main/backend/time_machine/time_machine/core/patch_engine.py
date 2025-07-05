"""
Advanced Patch Engine with DSL Support and Validation
Handles parsing, validation, composition, and conflict detection of state patches.
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import Patch, PatchType

logger = logging.getLogger(__name__)


class ValidationLevel(str, Enum):
    """Patch validation levels."""

    STRICT = "strict"
    LENIENT = "lenient"
    DISABLED = "disabled"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies."""

    FAIL = "fail"
    MERGE = "merge"
    OVERWRITE = "overwrite"
    SKIP = "skip"


@dataclass
class PatchValidationResult:
    """Result of patch validation."""

    valid: bool
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


@dataclass
class PatchConflict:
    """Represents a conflict between patches."""

    patch1_id: str
    patch2_id: str
    conflict_type: str
    description: str
    resolution: Optional[str] = None


class PatchEngine:
    """
    Advanced patch engine with DSL support, validation, composition,
    macro expansion, and conflict detection.
    """

    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        self.validation_level = validation_level
        self.macro_definitions: Dict[str, Dict[str, Any]] = {}
        self.validation_rules: Dict[str, List[str]] = {}
        self._load_default_macros()
        self._load_default_validation_rules()

    def _load_default_macros(self):
        """Load default patch macros."""
        self.macro_definitions.update(
            {
                "disable_reentrancy": {
                    "description": "Disable reentrancy guard in a contract",
                    "template": {
                        "type": "storage",
                        "address": "${contract_address}",
                        "slot": "${guard_slot:0x0}",
                        "value": "0x1",
                        "description": "Disable reentrancy guard",
                    },
                },
                "set_balance": {
                    "description": "Set account balance",
                    "template": {
                        "type": "balance",
                        "address": "${address}",
                        "value": "${balance}",
                        "description": "Set balance to ${balance}",
                    },
                },
                "fix_oracle_price": {
                    "description": "Fix oracle price to a specific value",
                    "template": {
                        "type": "storage",
                        "address": "${oracle_address}",
                        "slot": "${price_slot:0x1}",
                        "value": "${correct_price}",
                        "description": "Fix oracle price to ${correct_price}",
                    },
                },
                "pause_contract": {
                    "description": "Pause a contract by setting pause flag",
                    "template": {
                        "type": "storage",
                        "address": "${contract_address}",
                        "slot": "${pause_slot:0x0}",
                        "value": "0x1",
                        "description": "Pause contract",
                    },
                },
                "set_owner": {
                    "description": "Change contract owner",
                    "template": {
                        "type": "storage",
                        "address": "${contract_address}",
                        "slot": "${owner_slot:0x0}",
                        "value": "${new_owner}",
                        "description": "Change owner to ${new_owner}",
                    },
                },
            }
        )

    def _load_default_validation_rules(self):
        """Load default validation rules."""
        self.validation_rules.update(
            {
                "address_format": [r"^0x[a-fA-F0-9]{40}$"],
                "storage_slot_format": [r"^0x[a-fA-F0-9]{1,64}$"],
                "balance_format": [r"^0x[a-fA-F0-9]+$", r"^\d+$"],
                "required_fields": ["type", "address"],
            }
        )

    def parse_patch(self, patch_data: Dict[str, Any]) -> Patch:
        """
        Parse patch data into a Patch object with validation.

        Args:
            patch_data: Raw patch data dictionary

        Returns:
            Patch: Validated patch object

        Raises:
            ValueError: If patch is invalid
        """
        # Validate patch data
        validation_result = self.validate_patch(patch_data)
        if (
            not validation_result.valid
            and self.validation_level == ValidationLevel.STRICT
        ):
            raise ValueError(f"Invalid patch: {', '.join(validation_result.errors)}")

        # Log warnings
        for warning in validation_result.warnings:
            logger.warning(f"Patch warning: {warning}")

        # Extract patch type
        patch_type_str = patch_data.get("type", "")
        try:
            patch_type = PatchType(patch_type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid patch type: {patch_type_str}")

        # Create patch object
        patch = Patch(
            patch_type=patch_type,
            target_address=self._normalize_address(patch_data["address"]),
            value=str(patch_data.get("value", "")),
            description=patch_data.get("description", ""),
            validation_rules=patch_data.get("validation_rules", []),
            metadata=patch_data.get("metadata", {}),
        )

        # Set key for storage patches
        if patch_type == PatchType.STORAGE:
            if "slot" not in patch_data:
                raise ValueError("Storage patch must specify 'slot'")
            patch.key = self._normalize_storage_slot(patch_data["slot"])

        return patch

    def validate_patch(self, patch_data: Dict[str, Any]) -> PatchValidationResult:
        """
        Validate patch data against rules.

        Args:
            patch_data: Raw patch data

        Returns:
            PatchValidationResult: Validation result
        """
        errors = []
        warnings = []
        metadata = {}

        # Check required fields
        for field in self.validation_rules["required_fields"]:
            if field not in patch_data:
                errors.append(f"Missing required field: {field}")

        # Validate address format
        address = patch_data.get("address", "")
        if address and not self._validate_regex(
            address, self.validation_rules["address_format"]
        ):
            errors.append(f"Invalid address format: {address}")

        # Validate patch type
        patch_type = patch_data.get("type", "")
        if patch_type not in [pt.value for pt in PatchType]:
            errors.append(f"Invalid patch type: {patch_type}")

        # Type-specific validation
        if patch_type == "storage":
            slot = patch_data.get("slot", "")
            if slot and not self._validate_regex(
                slot, self.validation_rules["storage_slot_format"]
            ):
                errors.append(f"Invalid storage slot format: {slot}")

        elif patch_type == "balance":
            value = patch_data.get("value", "")
            if value and not self._validate_regex(
                value, self.validation_rules["balance_format"]
            ):
                errors.append(f"Invalid balance format: {value}")

        # Check for dangerous operations
        if patch_type == "code" and not patch_data.get("force", False):
            warnings.append("Code patches are dangerous and should be used carefully")

        # Validate value constraints
        if patch_type == "balance":
            try:
                balance_value = int(patch_data.get("value", "0"), 0)
                if balance_value < 0:
                    errors.append("Balance cannot be negative")
                elif balance_value > 10**30:  # Very large balance
                    warnings.append("Very large balance value detected")
                metadata["balance_value"] = balance_value
            except ValueError:
                errors.append("Invalid balance value format")

        return PatchValidationResult(
            valid=len(errors) == 0, errors=errors, warnings=warnings, metadata=metadata
        )

    def expand_macro(self, macro_name: str, **kwargs) -> Dict[str, Any]:
        """
        Expand a macro into a patch.

        Args:
            macro_name: Name of the macro to expand
            **kwargs: Macro parameters

        Returns:
            Dict[str, Any]: Expanded patch data

        Raises:
            ValueError: If macro is unknown or parameters are invalid
        """
        if macro_name not in self.macro_definitions:
            raise ValueError(f"Unknown macro: {macro_name}")

        macro_def = self.macro_definitions[macro_name]
        template = macro_def["template"].copy()

        # Replace template variables
        template_str = json.dumps(template)

        # Replace variables with values
        for key, value in kwargs.items():
            template_str = template_str.replace(f"${{{key}}}", str(value))

        # Handle default values (e.g., ${var:default})
        template_str = re.sub(
            r"\$\{([^:}]+):([^}]+)\}",
            lambda m: kwargs.get(m.group(1), m.group(2)),
            template_str,
        )

        # Check for remaining unreplaced variables
        remaining_vars = re.findall(r"\$\{([^}]+)\}", template_str)
        if remaining_vars:
            raise ValueError(f"Missing macro parameters: {remaining_vars}")

        expanded_patch = json.loads(template_str)
        expanded_patch["metadata"] = expanded_patch.get("metadata", {})
        expanded_patch["metadata"]["macro"] = macro_name
        expanded_patch["metadata"]["macro_params"] = kwargs

        return expanded_patch

    def compose_patches(
        self,
        patches: List[Dict[str, Any]],
        conflict_resolution: ConflictResolution = ConflictResolution.FAIL,
    ) -> List[Dict[str, Any]]:
        """
        Compose multiple patches with conflict detection and resolution.

        Args:
            patches: List of patch data dictionaries
            conflict_resolution: How to handle conflicts

        Returns:
            List[Dict[str, Any]]: Composed patches

        Raises:
            ValueError: If conflicts cannot be resolved
        """
        conflicts = self.detect_conflicts(patches)

        if conflicts and conflict_resolution == ConflictResolution.FAIL:
            conflict_descriptions = [c.description for c in conflicts]
            raise ValueError(f"Patch conflicts detected: {conflict_descriptions}")

        # Apply conflict resolution
        if conflicts:
            patches = self._resolve_conflicts(patches, conflicts, conflict_resolution)

        # Sort patches by dependency order
        return self._sort_patches_by_dependency(patches)

    def detect_conflicts(self, patches: List[Dict[str, Any]]) -> List[PatchConflict]:
        """
        Detect conflicts between patches.

        Args:
            patches: List of patch data dictionaries

        Returns:
            List[PatchConflict]: Detected conflicts
        """
        conflicts = []

        for i, patch1 in enumerate(patches):
            for j, patch2 in enumerate(patches[i + 1 :], i + 1):
                conflict = self._check_patch_conflict(patch1, patch2, i, j)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    def _check_patch_conflict(
        self, patch1: Dict[str, Any], patch2: Dict[str, Any], idx1: int, idx2: int
    ) -> Optional[PatchConflict]:
        """Check if two patches conflict."""
        # Same address conflicts
        if patch1.get("address") == patch2.get("address"):
            # Storage slot conflicts
            if (
                patch1.get("type") == "storage"
                and patch2.get("type") == "storage"
                and patch1.get("slot") == patch2.get("slot")
            ):
                return PatchConflict(
                    patch1_id=str(idx1),
                    patch2_id=str(idx2),
                    conflict_type="storage_slot",
                    description=f"Storage slot {patch1.get('slot')} conflict at {patch1.get('address')}",
                )

            # Balance conflicts
            if patch1.get("type") == "balance" and patch2.get("type") == "balance":
                return PatchConflict(
                    patch1_id=str(idx1),
                    patch2_id=str(idx2),
                    conflict_type="balance",
                    description=f"Balance conflict at {patch1.get('address')}",
                )

            # Code conflicts
            if patch1.get("type") == "code" and patch2.get("type") == "code":
                return PatchConflict(
                    patch1_id=str(idx1),
                    patch2_id=str(idx2),
                    conflict_type="code",
                    description=f"Code conflict at {patch1.get('address')}",
                )

        return None

    def _resolve_conflicts(
        self,
        patches: List[Dict[str, Any]],
        conflicts: List[PatchConflict],
        resolution: ConflictResolution,
    ) -> List[Dict[str, Any]]:
        """Resolve conflicts according to strategy."""
        if resolution == ConflictResolution.OVERWRITE:
            # Keep last patch in conflict
            to_remove = set()
            for conflict in conflicts:
                idx1, idx2 = int(conflict.patch1_id), int(conflict.patch2_id)
                to_remove.add(idx1)  # Remove earlier patch

            return [p for i, p in enumerate(patches) if i not in to_remove]

        elif resolution == ConflictResolution.SKIP:
            # Remove all conflicting patches
            to_remove = set()
            for conflict in conflicts:
                to_remove.add(int(conflict.patch1_id))
                to_remove.add(int(conflict.patch2_id))

            return [p for i, p in enumerate(patches) if i not in to_remove]

        elif resolution == ConflictResolution.MERGE:
            # Try to merge compatible patches
            return self._merge_patches(patches, conflicts)

        return patches

    def _merge_patches(
        self, patches: List[Dict[str, Any]], conflicts: List[PatchConflict]
    ) -> List[Dict[str, Any]]:
        """Attempt to merge conflicting patches."""
        # Simple merge strategy - would be more sophisticated in reality
        merged_patches = patches.copy()

        for conflict in conflicts:
            idx1, idx2 = int(conflict.patch1_id), int(conflict.patch2_id)
            patch1, patch2 = patches[idx1], patches[idx2]

            if conflict.conflict_type == "balance":
                # Merge by taking maximum balance
                try:
                    val1 = int(patch1.get("value", "0"), 0)
                    val2 = int(patch2.get("value", "0"), 0)
                    merged_value = hex(max(val1, val2))

                    merged_patch = patch1.copy()
                    merged_patch["value"] = merged_value
                    merged_patch[
                        "description"
                    ] = f"Merged balance patch (max of {val1} and {val2})"

                    # Replace both patches with merged one
                    merged_patches[idx1] = merged_patch
                    merged_patches[idx2] = None  # Mark for removal

                except ValueError:
                    logger.warning(
                        f"Could not merge balance patches: {conflict.description}"
                    )

        # Remove None entries
        return [p for p in merged_patches if p is not None]

    def _sort_patches_by_dependency(
        self, patches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort patches by dependency order."""
        # Simple ordering: balance -> storage -> code
        type_order = {"balance": 0, "nonce": 1, "storage": 2, "code": 3, "header": 4}

        return sorted(patches, key=lambda p: type_order.get(p.get("type", ""), 999))

    def generate_patch_report(self, patches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive patch report.

        Args:
            patches: List of patch data dictionaries

        Returns:
            Dict[str, Any]: Patch report
        """
        conflicts = self.detect_conflicts(patches)
        validation_results = [self.validate_patch(p) for p in patches]

        # Count patches by type
        type_counts = {}
        for patch in patches:
            patch_type = patch.get("type", "unknown")
            type_counts[patch_type] = type_counts.get(patch_type, 0) + 1

        # Count addresses affected
        addresses = set(patch.get("address") for patch in patches)

        # Validation summary
        valid_patches = sum(1 for vr in validation_results if vr.valid)
        total_errors = sum(len(vr.errors) for vr in validation_results)
        total_warnings = sum(len(vr.warnings) for vr in validation_results)

        return {
            "summary": {
                "total_patches": len(patches),
                "valid_patches": valid_patches,
                "invalid_patches": len(patches) - valid_patches,
                "conflicts": len(conflicts),
                "addresses_affected": len(addresses),
                "total_errors": total_errors,
                "total_warnings": total_warnings,
            },
            "type_breakdown": type_counts,
            "affected_addresses": list(addresses),
            "conflicts": [
                {
                    "type": c.conflict_type,
                    "description": c.description,
                    "patches": [c.patch1_id, c.patch2_id],
                }
                for c in conflicts
            ],
            "validation_errors": [
                {"patch_index": i, "errors": vr.errors, "warnings": vr.warnings}
                for i, vr in enumerate(validation_results)
                if not vr.valid or vr.warnings
            ],
        }

    def _validate_regex(self, value: str, patterns: List[str]) -> bool:
        """Validate value against regex patterns."""
        return any(re.match(pattern, value) for pattern in patterns)

    def _normalize_address(self, address: str) -> str:
        """Normalize Ethereum address format."""
        if not address.startswith("0x"):
            address = "0x" + address
        return address.lower()

    def _normalize_storage_slot(self, slot: str) -> str:
        """Normalize storage slot format."""
        if not slot.startswith("0x"):
            slot = "0x" + slot
        return slot.lower().zfill(66)  # Pad to 32 bytes

    def register_macro(
        self, name: str, template: Dict[str, Any], description: str = ""
    ):
        """Register a custom macro."""
        self.macro_definitions[name] = {
            "description": description,
            "template": template,
        }
        logger.info(f"Registered macro: {name}")

    def list_macros(self) -> List[Dict[str, str]]:
        """List available macros."""
        return [
            {"name": name, "description": defn["description"]}
            for name, defn in self.macro_definitions.items()
        ]
