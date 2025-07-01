"""CQRS Commands for Scorpius Bridge.

Commands represent write operations that change system state.
They follow the Command pattern and return results.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, List, Optional

from ..domain.models.bridge_tx import SecurityLevel
from ..domain.models.validator import ValidatorStatus


@dataclass
class Command:
    """Base command class."""

    pass


@dataclass
class InitiateBridgeTransferCommand(Command):
    """Command to initiate a new bridge transfer."""

    source_chain: str
    destination_chain: str
    token_address: str
    amount: Decimal
    sender_address: str
    recipient_address: str
    security_level: SecurityLevel = SecurityLevel.STANDARD
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ValidateTransferCommand(Command):
    """Command to validate a bridge transfer."""

    transfer_id: str
    validator_id: str
    signature: str
    validation_data: Dict[str, Any]


@dataclass
class ExecuteTransferCommand(Command):
    """Command to execute a validated transfer."""

    transfer_id: str
    executor_id: str


@dataclass
class CancelTransferCommand(Command):
    """Command to cancel a pending transfer."""

    transfer_id: str
    reason: str
    canceller_id: str


@dataclass
class AddLiquidityCommand(Command):
    """Command to add liquidity to a pool."""

    pool_id: str
    provider_address: str
    amount: Decimal
    token_address: str


@dataclass
class RemoveLiquidityCommand(Command):
    """Command to remove liquidity from a pool."""

    pool_id: str
    provider_address: str
    shares: Decimal


@dataclass
class CreateLiquidityPoolCommand(Command):
    """Command to create a new liquidity pool."""

    name: str
    source_chain: str
    destination_chain: str
    token_address: str
    token_symbol: str
    initial_liquidity: Decimal
    provider_address: str
    fee_rate: float = 0.003


@dataclass
class RegisterValidatorCommand(Command):
    """Command to register a new validator."""

    address: str
    public_key: str
    stake_amount: Decimal
    supported_chains: List[str]
    commission_rate: float = 0.05
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class StakeCommand(Command):
    """Command to add stake to a validator."""

    validator_id: str
    amount: Decimal
    staker_address: str


@dataclass
class UnstakeCommand(Command):
    """Command to remove stake from a validator."""

    validator_id: str
    amount: Decimal
    staker_address: str


@dataclass
class SlashValidatorCommand(Command):
    """Command to slash a validator for misbehavior."""

    validator_id: str
    slash_amount: Decimal
    reason: str
    evidence: Dict[str, Any]
    slasher_id: str


@dataclass
class UpdateValidatorStatusCommand(Command):
    """Command to update validator status."""

    validator_id: str
    new_status: ValidatorStatus
    reason: str
    updater_id: str


@dataclass
class RecordValidationCommand(Command):
    """Command to record a validation attempt."""

    validator_id: str
    transfer_id: str
    success: bool
    response_time: float
    validation_data: Dict[str, Any]


@dataclass
class PausePoolCommand(Command):
    """Command to pause a liquidity pool."""

    pool_id: str
    reason: str
    pauser_id: str


@dataclass
class UnpausePoolCommand(Command):
    """Command to unpause a liquidity pool."""

    pool_id: str
    reason: str
    unpauser_id: str


@dataclass
class EmergencyStopCommand(Command):
    """Command to emergency stop all operations."""

    reason: str
    stopper_id: str
    scope: str  # "transfer", "pool", "validator", "all"
    target_id: Optional[str] = None
