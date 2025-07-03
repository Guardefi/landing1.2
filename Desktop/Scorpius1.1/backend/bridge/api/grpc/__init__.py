"""gRPC service definitions for Scorpius Bridge."""

from .bridge_service import BridgeServicer
from .validator_service import ValidatorServicer

__all__ = ["BridgeServicer", "ValidatorServicer"]
