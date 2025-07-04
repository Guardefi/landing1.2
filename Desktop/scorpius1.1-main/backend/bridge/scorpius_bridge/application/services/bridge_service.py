"""Bridge Service - orchestrates bridge transfer operations.

This service coordinates between domain objects and infrastructure
to handle bridge transfer use cases.
"""

import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional

from scorpius_bridge.domain.errors import InsufficientLiquidityError, InvalidTransferError
from scorpius_bridge.domain.events import (
    BridgeTransferCompleted,
    BridgeTransferFailed,
    BridgeTransferInitiated,
)
from scorpius_bridge.domain.models.bridge_tx import BridgeTransaction, SecurityLevel, TransferStatus
from scorpius_bridge.domain.policy import SecurityPolicy, TransferPolicy
from scorpius_bridge.application.commands import (
    CancelTransferCommand,
    ExecuteTransferCommand,
    InitiateBridgeTransferCommand,
    ValidateTransferCommand,
)
from scorpius_bridge.application.queries import (
    GetBridgeTransferQuery,
    GetFeesQuery,
    GetRiskAnalysisQuery,
    GetTransferHistoryQuery,
)

logger = logging.getLogger(__name__)


class BridgeService:
    """Service for managing bridge transfers."""

    def __init__(
        self,
        transfer_repository,
        pool_repository,
        validator_repository,
        blockchain_client,
        event_publisher,
        config,
    ):
        """Initialize bridge service with dependencies."""
        self.transfer_repository = transfer_repository
        self.pool_repository = pool_repository
        self.validator_repository = validator_repository
        self.blockchain_client = blockchain_client
        self.event_publisher = event_publisher
        self.config = config

    async def initiate_transfer(self, command: InitiateBridgeTransferCommand) -> str:
        """Initiate a new bridge transfer."""
        logger.info(
            f"Initiating transfer: {command.amount} from {command.source_chain} to {command.destination_chain}"
        )

        try:
            # Validate transfer limits
            TransferPolicy.validate_transfer_amount(
                command.amount,
                self.config.min_transfer_amount,
                self.config.max_transfer_amount,
            )

            # Assess risk and adjust security level if needed
            sender_history = await self.transfer_repository.get_sender_history(
                command.sender_address
            )
            recommended_security = SecurityPolicy.assess_transfer_risk(
                BridgeTransaction(
                    source_chain=command.source_chain,
                    destination_chain=command.destination_chain,
                    amount=command.amount,
                    sender_address=command.sender_address,
                    recipient_address=command.recipient_address,
                ),
                sender_history,
            )

            # Use higher of requested or recommended security level
            final_security = max(
                command.security_level, recommended_security, key=lambda x: x.value
            )

            # Calculate fees
            bridge_fee = TransferPolicy.calculate_bridge_fee(
                command.amount, self.config.base_bridge_fee_percentage, final_security
            )

            # Create transfer
            transfer = BridgeTransaction(
                source_chain=command.source_chain,
                destination_chain=command.destination_chain,
                token_address=command.token_address,
                amount=command.amount,
                sender_address=command.sender_address,
                recipient_address=command.recipient_address,
                security_level=final_security,
                bridge_fee=bridge_fee,
                metadata=command.metadata or {},
            )

            # Check liquidity availability
            pool = await self.pool_repository.get_by_chains(
                command.source_chain, command.destination_chain, command.token_address
            )

            if not pool or not TransferPolicy.can_execute_transfer(transfer, pool):
                raise InsufficientLiquidityError("Insufficient liquidity for transfer")

            # Reserve liquidity
            total_amount = command.amount + bridge_fee
            pool.reserve_liquidity(total_amount)
            await self.pool_repository.save(pool)

            # Save transfer
            await self.transfer_repository.save(transfer)

            # Publish event
            event = BridgeTransferInitiated(
                aggregate_id=transfer.id,
                transfer_id=transfer.id,
                source_chain=transfer.source_chain,
                destination_chain=transfer.destination_chain,
                amount=str(transfer.amount),
                token=transfer.token_address,
                sender=transfer.sender_address,
                recipient=transfer.recipient_address,
            )
            await self.event_publisher.publish(event)

            logger.info(f"Transfer initiated successfully: {transfer.id}")
            return transfer.id

        except Exception as e:
            logger.error(f"Failed to initiate transfer: {e}")
            raise

    async def validate_transfer(self, command: ValidateTransferCommand) -> bool:
        """Validate a transfer with validator signature."""
        logger.info(
            f"Validating transfer {command.transfer_id} by validator {command.validator_id}"
        )

        try:
            # Get transfer and validator
            transfer = await self.transfer_repository.get_by_id(command.transfer_id)
            if not transfer:
                raise InvalidTransferError("Transfer not found")

            validator = await self.validator_repository.get_by_id(command.validator_id)
            if not validator:
                raise InvalidTransferError("Validator not found")

            # Check validator eligibility
            if not SecurityPolicy.validate_validator_eligibility(validator):
                raise InvalidTransferError("Validator not eligible")

            # Verify signature (simplified - would use cryptographic verification)
            is_valid = await self._verify_validator_signature(
                transfer, validator, command.signature, command.validation_data
            )

            # Record validation attempt
            validator.record_validation(is_valid, 0.5)  # Assume 500ms response time
            await self.validator_repository.save(validator)

            if is_valid:
                # Add validator signature to transfer
                transfer.add_validator_signature(
                    command.validator_id, command.signature
                )

                # Check if we have enough signatures
                required_validators = TransferPolicy.determine_required_validators(
                    transfer.amount,
                    transfer.security_level,
                    await self.validator_repository.count_active(),
                )

                if transfer.has_required_signatures(required_validators):
                    transfer.update_status(TransferStatus.VALIDATED)

                await self.transfer_repository.save(transfer)
                logger.info(f"Transfer {transfer.id} validated by {validator.id}")

            return is_valid

        except Exception as e:
            logger.error(f"Failed to validate transfer: {e}")
            raise

    async def execute_transfer(self, command: ExecuteTransferCommand) -> bool:
        """Execute a validated transfer."""
        logger.info(f"Executing transfer {command.transfer_id}")

        try:
            transfer = await self.transfer_repository.get_by_id(command.transfer_id)
            if not transfer:
                raise InvalidTransferError("Transfer not found")

            if transfer.status != TransferStatus.VALIDATED:
                raise InvalidTransferError("Transfer not validated")

            # Get liquidity pool
            pool = await self.pool_repository.get_by_chains(
                transfer.source_chain,
                transfer.destination_chain,
                transfer.token_address,
            )

            if not pool:
                raise InsufficientLiquidityError("Liquidity pool not found")

            # Execute on destination chain
            tx_hash = await self.blockchain_client.execute_transfer(
                transfer.destination_chain,
                transfer.token_address,
                transfer.recipient_address,
                transfer.amount,
                transfer.id,
            )

            # Update transfer
            transfer.destination_tx_hash = tx_hash
            transfer.update_status(TransferStatus.COMPLETED)

            # Execute transfer in pool (deduct liquidity and collect fees)
            net_amount = pool.execute_transfer(transfer.amount + transfer.bridge_fee)

            # Save updates
            await self.transfer_repository.save(transfer)
            await self.pool_repository.save(pool)

            # Publish success event
            event = BridgeTransferCompleted(
                aggregate_id=transfer.id,
                transfer_id=transfer.id,
                transaction_hash=tx_hash,
                final_amount=str(net_amount),
                fees_paid=str(transfer.bridge_fee),
            )
            await self.event_publisher.publish(event)

            logger.info(f"Transfer {transfer.id} executed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to execute transfer: {e}")

            # Mark transfer as failed and publish event
            try:
                transfer = await self.transfer_repository.get_by_id(command.transfer_id)
                if transfer:
                    transfer.update_status(TransferStatus.FAILED)
                    await self.transfer_repository.save(transfer)

                    event = BridgeTransferFailed(
                        aggregate_id=transfer.id,
                        transfer_id=transfer.id,
                        error_code="EXECUTION_FAILED",
                        error_message=str(e),
                    )
                    await self.event_publisher.publish(event)
            except:
                pass

            raise

    async def cancel_transfer(self, command: CancelTransferCommand) -> bool:
        """Cancel a pending transfer."""
        logger.info(f"Cancelling transfer {command.transfer_id}")

        try:
            transfer = await self.transfer_repository.get_by_id(command.transfer_id)
            if not transfer:
                raise InvalidTransferError("Transfer not found")

            if transfer.status not in [
                TransferStatus.PENDING,
                TransferStatus.INITIATED,
            ]:
                raise InvalidTransferError("Transfer cannot be cancelled")

            # Release reserved liquidity
            pool = await self.pool_repository.get_by_chains(
                transfer.source_chain,
                transfer.destination_chain,
                transfer.token_address,
            )

            if pool:
                total_amount = transfer.amount + transfer.bridge_fee
                pool.release_liquidity(total_amount)
                await self.pool_repository.save(pool)

            # Update transfer status
            transfer.update_status(TransferStatus.CANCELLED)
            transfer.metadata["cancellation_reason"] = command.reason
            transfer.metadata["cancelled_by"] = command.canceller_id

            await self.transfer_repository.save(transfer)

            logger.info(f"Transfer {transfer.id} cancelled successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to cancel transfer: {e}")
            raise

    async def get_transfer(
        self, query: GetBridgeTransferQuery
    ) -> Optional[Dict[str, Any]]:
        """Get a bridge transfer by ID."""
        transfer = await self.transfer_repository.get_by_id(query.transfer_id)
        return transfer.to_dict() if transfer else None

    async def get_transfer_history(
        self, query: GetTransferHistoryQuery
    ) -> Dict[str, Any]:
        """Get transfer history with pagination and filters."""
        transfers, total = await self.transfer_repository.get_with_filters(
            sender_address=query.sender_address,
            recipient_address=query.recipient_address,
            source_chain=query.source_chain,
            destination_chain=query.destination_chain,
            status=query.status,
            security_level=query.security_level,
            min_amount=query.min_amount,
            max_amount=query.max_amount,
            start_date=query.start_date,
            end_date=query.end_date,
            page=query.pagination.page,
            size=query.pagination.size,
            sort_by=query.pagination.sort_by,
            sort_order=query.pagination.sort_order,
        )

        return {
            "transfers": [t.to_dict() for t in transfers],
            "total": total,
            "page": query.pagination.page,
            "size": query.pagination.size,
            "total_pages": (total + query.pagination.size - 1) // query.pagination.size,
        }

    async def get_fees(self, query: GetFeesQuery) -> Dict[str, Any]:
        """Get fee estimation for a transfer."""
        bridge_fee = TransferPolicy.calculate_bridge_fee(
            query.amount, self.config.base_bridge_fee_percentage, query.security_level
        )

        # Estimate gas fees (would query blockchain for current gas prices)
        estimated_gas_fee = await self.blockchain_client.estimate_gas_fee(
            query.destination_chain
        )

        return {
            "bridge_fee": str(bridge_fee),
            "estimated_gas_fee": str(estimated_gas_fee),
            "total_fee": str(bridge_fee + estimated_gas_fee),
            "fee_rate": self.config.base_bridge_fee_percentage,
            "security_level": query.security_level.value,
        }

    async def _verify_validator_signature(
        self,
        transfer: BridgeTransaction,
        validator,
        signature: str,
        validation_data: Dict[str, Any],
    ) -> bool:
        """Verify validator signature (simplified implementation)."""
        # In a real implementation, this would:
        # 1. Verify the cryptographic signature
        # 2. Check the validation data against chain state
        # 3. Ensure validator is authorized for this transfer

        # For now, we'll do basic validation
        return (
            len(signature) > 0
            and validator.supports_chain(transfer.source_chain)
            and validator.supports_chain(transfer.destination_chain)
        )
