"""gRPC service for validator operations."""

import logging
from typing import AsyncIterator, List

import grpc
from grpc import aio

logger = logging.getLogger(__name__)


class ValidatorInfo:
    """Validator information message."""

    def __init__(self, validator_id: str, status: str, stake: str, reputation: float):
        self.validator_id = validator_id
        self.status = status
        self.stake = stake
        self.reputation = reputation


class ValidatorListRequest:
    """Request to list validators."""

    def __init__(self, active_only: bool = True):
        self.active_only = active_only


class ValidatorListResponse:
    """Response containing list of validators."""

    def __init__(self, validators: List[ValidatorInfo]):
        self.validators = validators


class ValidatorStatusRequest:
    """Request for validator status."""

    def __init__(self, validator_id: str):
        self.validator_id = validator_id


class ValidatorStatusResponse:
    """Response with validator status."""

    def __init__(
        self, validator: ValidatorInfo, last_seen: str, performance_metrics: dict
    ):
        self.validator = validator
        self.last_seen = last_seen
        self.performance_metrics = performance_metrics


class ValidatorEvent:
    """Validator event message."""

    def __init__(self, event_type: str, validator_id: str, data: dict, timestamp: str):
        self.event_type = event_type
        self.validator_id = validator_id
        self.data = data
        self.timestamp = timestamp


class ValidatorEventRequest:
    """Request to stream validator events."""

    def __init__(self, validator_id: str = None):
        self.validator_id = validator_id


class ValidatorServicer:
    """gRPC service implementation for validator operations."""

    async def ListValidators(
        self, request: ValidatorListRequest, context: grpc.aio.ServicerContext
    ) -> ValidatorListResponse:
        """List active validators."""
        logger.info(f"gRPC list validators request: active_only={request.active_only}")

        try:
            # Here you would query your actual validator registry
            # For now, return mock validators
            mock_validators = [
                ValidatorInfo(
                    validator_id="validator_1",
                    status="active",
                    stake="100000",
                    reputation=0.95,
                ),
                ValidatorInfo(
                    validator_id="validator_2",
                    status="active",
                    stake="75000",
                    reputation=0.88,
                ),
                ValidatorInfo(
                    validator_id="validator_3",
                    status="inactive" if not request.active_only else "active",
                    stake="50000",
                    reputation=0.72,
                ),
            ]

            if request.active_only:
                mock_validators = [v for v in mock_validators if v.status == "active"]

            return ValidatorListResponse(validators=mock_validators)

        except Exception as e:
            logger.error(f"List validators failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to list validators: {str(e)}")
            return ValidatorListResponse(validators=[])

    async def GetValidatorStatus(
        self, request: ValidatorStatusRequest, context: grpc.aio.ServicerContext
    ) -> ValidatorStatusResponse:
        """Get detailed status of a specific validator."""
        logger.info(f"gRPC validator status request: {request.validator_id}")

        try:
            # Here you would query your actual validator data
            # For now, return mock data
            from datetime import datetime

            validator = ValidatorInfo(
                validator_id=request.validator_id,
                status="active",
                stake="100000",
                reputation=0.95,
            )

            performance_metrics = {
                "uptime_percentage": 99.5,
                "avg_response_time": 150,  # milliseconds
                "successful_validations": 1234,
                "failed_validations": 5,
                "last_24h_earnings": "50.25",
            }

            return ValidatorStatusResponse(
                validator=validator,
                last_seen=datetime.utcnow().isoformat(),
                performance_metrics=performance_metrics,
            )

        except Exception as e:
            logger.error(f"Validator status query failed: {e}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Validator not found: {str(e)}")
            return ValidatorStatusResponse(
                validator=ValidatorInfo(
                    validator_id=request.validator_id,
                    status="not_found",
                    stake="0",
                    reputation=0.0,
                ),
                last_seen="",
                performance_metrics={},
            )

    async def StreamValidatorEvents(
        self, request: ValidatorEventRequest, context: grpc.aio.ServicerContext
    ) -> AsyncIterator[ValidatorEvent]:
        """Stream validator events for real-time monitoring."""
        logger.info(f"gRPC validator event stream: {request.validator_id or 'all'}")

        try:
            # Here you would integrate with your validator event system
            # For now, yield mock events
            import asyncio
            from datetime import datetime

            events = [
                ("validator_joined", {"stake": "100000"}),
                ("status_changed", {"old_status": "inactive", "new_status": "active"}),
                (
                    "validation_completed",
                    {"transaction_id": "tx_123", "result": "success"},
                ),
                ("performance_update", {"uptime": 99.8, "response_time": 120}),
                ("stake_updated", {"old_stake": "100000", "new_stake": "110000"}),
            ]

            for i, (event_type, data) in enumerate(events):
                await asyncio.sleep(2)  # Simulate real-time events

                yield ValidatorEvent(
                    event_type=event_type,
                    validator_id=request.validator_id or f"validator_{i % 3 + 1}",
                    data=data,
                    timestamp=datetime.utcnow().isoformat(),
                )

        except Exception as e:
            logger.error(f"Validator event streaming failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Event streaming failed: {str(e)}")


# Add validator servicer to the gRPC server setup
async def add_validator_service_to_server(server: aio.Server):
    """Add validator service to the gRPC server."""
    validator_servicer = ValidatorServicer()
    # server.add_ValidatorServiceServicer_to_server(validator_servicer, server)  # This would be generated from proto
    logger.info("Validator service added to gRPC server")
