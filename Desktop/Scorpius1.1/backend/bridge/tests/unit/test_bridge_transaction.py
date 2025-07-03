"""Unit tests for bridge transaction domain model."""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from scorpius_bridge.domain.errors import InvalidTransferError
from scorpius_bridge.domain.models.bridge_tx import (
    BridgeTransaction,
    SecurityLevel,
    TransferStatus,
)


class TestBridgeTransaction:
    """Test cases for BridgeTransaction domain model."""

    def test_create_valid_transaction(self):
        """Test creating a valid bridge transaction."""
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
        )

        assert tx.id is not None
        assert tx.source_chain == "ethereum"
        assert tx.destination_chain == "polygon"
        assert tx.amount == Decimal("100.0")
        assert tx.status == TransferStatus.PENDING
        assert tx.security_level == SecurityLevel.STANDARD

    def test_invalid_amount(self):
        """Test transaction with invalid amount."""
        with pytest.raises(InvalidTransferError):
            BridgeTransaction(
                source_chain="ethereum",
                destination_chain="polygon",
                token_address="0x123...abc",
                amount=Decimal("0"),
                sender_address="0xsender...",
                recipient_address="0xrecipient...",
            )

    def test_same_source_destination(self):
        """Test transaction with same source and destination."""
        with pytest.raises(InvalidTransferError):
            BridgeTransaction(
                source_chain="ethereum",
                destination_chain="ethereum",
                token_address="0x123...abc",
                amount=Decimal("100.0"),
                sender_address="0xsender...",
                recipient_address="0xrecipient...",
            )

    def test_status_transitions(self):
        """Test valid status transitions."""
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
        )

        # Valid transition: PENDING -> INITIATED
        tx.update_status(TransferStatus.INITIATED)
        assert tx.status == TransferStatus.INITIATED

        # Valid transition: INITIATED -> LOCKED
        tx.update_status(TransferStatus.LOCKED)
        assert tx.status == TransferStatus.LOCKED

    def test_invalid_status_transition(self):
        """Test invalid status transition."""
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
        )

        # Invalid transition: PENDING -> COMPLETED
        with pytest.raises(InvalidTransferError):
            tx.update_status(TransferStatus.COMPLETED)

    def test_add_validator_signature(self):
        """Test adding validator signatures."""
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
        )

        tx.add_validator_signature("validator1", "signature1")
        assert "validator1" in tx.validator_signatures
        assert tx.validator_signatures["validator1"] == "signature1"

    def test_has_required_signatures(self):
        """Test checking for required signatures."""
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
        )

        # Not enough signatures
        assert not tx.has_required_signatures(3)

        # Add signatures
        tx.add_validator_signature("validator1", "sig1")
        tx.add_validator_signature("validator2", "sig2")
        tx.add_validator_signature("validator3", "sig3")

        # Now has enough
        assert tx.has_required_signatures(3)

    def test_is_expired(self):
        """Test expiration checking."""
        # Create transaction that expires in 1 hour
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
            expires_at=datetime.utcnow() + timedelta(hours=1),
        )

        assert not tx.is_expired()

        # Set expiration to past
        tx.expires_at = datetime.utcnow() - timedelta(hours=1)
        assert tx.is_expired()

    def test_security_level_confirmations(self):
        """Test security level affects confirmations."""
        tx = BridgeTransaction(
            source_chain="ethereum",
            destination_chain="polygon",
            token_address="0x123...abc",
            amount=Decimal("100.0"),
            sender_address="0xsender...",
            recipient_address="0xrecipient...",
        )

        # Standard level
        assert tx.required_confirmations == 12

        # High security
        tx.set_security_level(SecurityLevel.HIGH)
        assert tx.required_confirmations == 24

        # Maximum security
        tx.set_security_level(SecurityLevel.MAXIMUM)
        assert tx.required_confirmations == 64
