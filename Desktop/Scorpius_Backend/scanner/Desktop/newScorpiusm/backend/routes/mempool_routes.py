"""
Mempool Monitoring Routes Module
Handles mempool transaction monitoring, tracking, and alerts
"""

import logging
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import Alert, MempoolTransaction, get_db
from services.blockchain import MempoolMonitor, Web3Service
from sqlalchemy import desc, func

mempool_bp = Blueprint("mempool", __name__)
logger = logging.getLogger(__name__)


@mempool_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_pending_transactions():
    """Get pending mempool transactions with pagination"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        min_value = request.args.get("min_value", None)
        user_id = get_jwt_identity()

        db = get_db()

        # Build query for mempool transactions
        query = db.query(MempoolTransaction).filter(
            MempoolTransaction.user_id == user_id
        )

        # Apply filters
        if min_value:
            query = query.filter(MempoolTransaction.value >= float(min_value))

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        transactions = (
            query.order_by(desc(MempoolTransaction.detected_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        transactions_data = []
        for tx in transactions:
            tx_data = {
                "hash": tx.transaction_hash,
                "from": tx.from_address,
                "to": tx.to_address,
                "value": float(tx.value or 0),
                "gas_price": float(tx.gas_price or 0),
                "gas_limit": tx.gas_limit or 0,
                "mev_probability": float(tx.mev_probability or 0),
                "threat_level": tx.threat_level or "low",
                "detected_at": tx.detected_at.isoformat() + "Z",
                "status": tx.status,
                "block_number": tx.block_number,
                "nonce": tx.nonce,
            }
            transactions_data.append(tx_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "transactions": transactions_data,
                    "pagination": {
                        "total": total,
                        "page": page,
                        "limit": limit,
                        "totalPages": (total + limit - 1) // limit,
                        "hasNext": (page * limit) < total,
                        "hasPrev": page > 1,
                    },
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Mempool transactions error: {str(e)}")
        return (
            jsonify(
                {"success": False, "error": "Failed to fetch mempool transactions"}
            ),
            500,
        )


@mempool_bp.route("/transactions/scan", methods=["POST"])
@jwt_required()
def scan_mempool():
    """Trigger a new mempool scan"""
    try:
        data = request.get_json()
        scan_duration = data.get("duration", 60)  # seconds
        user_id = get_jwt_identity()

        # Initialize mempool monitor
        mempool_monitor = MempoolMonitor()

        # Get pending transactions
        pending_txs = mempool_monitor.get_pending_transactions(limit=100)

        # Save to database
        db = get_db()
        saved_count = 0

        for tx_data in pending_txs:
            # Check if transaction already exists
            existing_tx = (
                db.query(MempoolTransaction)
                .filter(
                    MempoolTransaction.transaction_hash == tx_data.get("hash"),
                    MempoolTransaction.user_id == user_id,
                )
                .first()
            )

            if not existing_tx:
                mempool_tx = MempoolTransaction(
                    user_id=user_id,
                    transaction_hash=tx_data.get("hash"),
                    from_address=tx_data.get("from"),
                    to_address=tx_data.get("to"),
                    value=tx_data.get("value", 0),
                    gas_price=tx_data.get("gas_price", 0),
                    gas_limit=21000,  # Default gas limit
                    nonce=0,  # Will be updated when tx is mined
                    status="pending",
                    detected_at=datetime.now(),
                    mev_probability=0.5,  # Default, will be analyzed
                    threat_level="low",
                )
                db.add(mempool_tx)
                saved_count += 1

        db.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Mempool scan completed. Found {saved_count} new transactions",
                "data": {"newTransactions": saved_count, "scanDuration": scan_duration},
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Mempool scan error: {str(e)}")
        db.rollback() if "db" in locals() else None
        return jsonify({"success": False, "error": "Failed to scan mempool"}), 500


@mempool_bp.route("/transactions/<tx_hash>", methods=["GET"])
@jwt_required()
def get_transaction_details(tx_hash):
    """Get detailed information about a specific transaction"""
    try:
        user_id = get_jwt_identity()
        db = get_db()

        # Get transaction from database
        tx = (
            db.query(MempoolTransaction)
            .filter(
                MempoolTransaction.transaction_hash == tx_hash,
                MempoolTransaction.user_id == user_id,
            )
            .first()
        )

        if not tx:
            return jsonify({"success": False, "message": "Transaction not found"}), 404

        # Get additional details from blockchain
        web3_service = Web3Service()
        blockchain_tx = web3_service.get_transaction(tx_hash)

        tx_details = {
            "hash": tx.transaction_hash,
            "from": tx.from_address,
            "to": tx.to_address,
            "value": float(tx.value or 0),
            "gas_price": float(tx.gas_price or 0),
            "gas_limit": tx.gas_limit or 0,
            "nonce": tx.nonce,
            "status": tx.status,
            "detected_at": tx.detected_at.isoformat() + "Z",
            "mev_probability": float(tx.mev_probability or 0),
            "threat_level": tx.threat_level,
            "block_number": tx.block_number,
            "blockchain_data": blockchain_tx,
        }

        return jsonify(
            {
                "success": True,
                "data": tx_details,
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Transaction details error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to fetch transaction details"}),
            500,
        )


@mempool_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_mempool_analytics():
    """Get mempool analytics and statistics"""
    try:
        days = int(request.args.get("days", 7))
        user_id = get_jwt_identity()
        db = get_db()

        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get analytics data
        total_transactions = (
            db.query(MempoolTransaction)
            .filter(
                MempoolTransaction.user_id == user_id,
                MempoolTransaction.detected_at >= start_date,
            )
            .count()
        )

        high_value_txs = (
            db.query(MempoolTransaction)
            .filter(
                MempoolTransaction.user_id == user_id,
                MempoolTransaction.detected_at >= start_date,
                MempoolTransaction.value >= 1.0,  # > 1 ETH
            )
            .count()
        )

        mev_opportunities = (
            db.query(MempoolTransaction)
            .filter(
                MempoolTransaction.user_id == user_id,
                MempoolTransaction.detected_at >= start_date,
                MempoolTransaction.mev_probability >= 0.7,
            )
            .count()
        )

        avg_gas_price = (
            db.query(func.avg(MempoolTransaction.gas_price))
            .filter(
                MempoolTransaction.user_id == user_id,
                MempoolTransaction.detected_at >= start_date,
            )
            .scalar()
            or 0
        )

        # Threat level distribution
        threat_stats = {}
        for level in ["low", "medium", "high"]:
            count = (
                db.query(MempoolTransaction)
                .filter(
                    MempoolTransaction.user_id == user_id,
                    MempoolTransaction.detected_at >= start_date,
                    MempoolTransaction.threat_level == level,
                )
                .count()
            )
            threat_stats[level] = count

        return jsonify(
            {
                "success": True,
                "data": {
                    "summary": {
                        "totalTransactions": total_transactions,
                        "highValueTransactions": high_value_txs,
                        "mevOpportunities": mev_opportunities,
                        "averageGasPrice": round(float(avg_gas_price), 2),
                        "periodDays": days,
                    },
                    "threatDistribution": threat_stats,
                    "trends": {
                        "mevRate": round(
                            (
                                (mev_opportunities / total_transactions * 100)
                                if total_transactions > 0
                                else 0
                            ),
                            2,
                        ),
                        "highValueRate": round(
                            (
                                (high_value_txs / total_transactions * 100)
                                if total_transactions > 0
                                else 0
                            ),
                            2,
                        ),
                    },
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Mempool analytics error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to fetch mempool analytics"}),
            500,
        )


@mempool_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_mempool_alerts():
    """Get mempool-related alerts"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        severity = request.args.get("severity", None)
        user_id = get_jwt_identity()

        db = get_db()

        # Build query for alerts
        query = db.query(Alert).filter(
            Alert.user_id == user_id, Alert.alert_type.like("%mempool%")
        )

        if severity:
            query = query.filter(Alert.severity == severity)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        alerts = (
            query.order_by(desc(Alert.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        alerts_data = []
        for alert in alerts:
            alert_data = {
                "id": alert.id,
                "type": alert.alert_type,
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "status": alert.status,
                "created_at": alert.created_at.isoformat() + "Z",
                "metadata": alert.metadata or {},
            }
            alerts_data.append(alert_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "alerts": alerts_data,
                    "pagination": {
                        "total": total,
                        "page": page,
                        "limit": limit,
                        "totalPages": (total + limit - 1) // limit,
                        "hasNext": (page * limit) < total,
                        "hasPrev": page > 1,
                    },
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Mempool alerts error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to fetch mempool alerts"}),
            500,
        )


@mempool_bp.route("/alerts", methods=["POST"])
@jwt_required()
def create_mempool_alert():
    """Create a new mempool alert rule"""
    try:
        data = request.get_json()
        alert_type = data.get("alert_type")
        title = data.get("title")
        conditions = data.get("conditions", {})
        user_id = get_jwt_identity()

        if not alert_type or not title:
            return (
                jsonify(
                    {"success": False, "message": "Alert type and title are required"}
                ),
                400,
            )

        db = get_db()

        # Create new alert rule
        alert = Alert(
            user_id=user_id,
            alert_type=f"mempool_{alert_type}",
            title=title,
            message=data.get("message", ""),
            severity=data.get("severity", "medium"),
            status="active",
            created_at=datetime.now(),
            metadata={"conditions": conditions, "alert_rule": True},
        )

        db.add(alert)
        db.commit()

        return jsonify(
            {
                "success": True,
                "message": "Mempool alert created successfully",
                "data": {
                    "alertId": alert.id,
                    "type": alert.alert_type,
                    "title": alert.title,
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Create mempool alert error: {str(e)}")
        db.rollback() if "db" in locals() else None
        return (
            jsonify({"success": False, "error": "Failed to create mempool alert"}),
            500,
        )


@mempool_bp.route("/monitor/start", methods=["POST"])
@jwt_required()
def start_mempool_monitoring():
    """Start real-time mempool monitoring"""
    try:
        get_jwt_identity()

        # Initialize and start mempool monitor
        MempoolMonitor()

        # In a real implementation, this would start a background task
        # For now, we'll return success

        return jsonify(
            {
                "success": True,
                "message": "Mempool monitoring started",
                "data": {
                    "status": "monitoring",
                    "startedAt": datetime.now().isoformat() + "Z",
                },
            }
        )

    except Exception as e:
        logger.error(f"Start mempool monitoring error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to start mempool monitoring"}),
            500,
        )


@mempool_bp.route("/monitor/stop", methods=["POST"])
@jwt_required()
def stop_mempool_monitoring():
    """Stop real-time mempool monitoring"""
    try:
        get_jwt_identity()

        # Stop mempool monitoring
        # In a real implementation, this would stop the background task

        return jsonify(
            {
                "success": True,
                "message": "Mempool monitoring stopped",
                "data": {
                    "status": "stopped",
                    "stoppedAt": datetime.now().isoformat() + "Z",
                },
            }
        )

    except Exception as e:
        logger.error(f"Stop mempool monitoring error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to stop mempool monitoring"}),
            500,
        )
