"""
MEV Operations Routes Module
Handles MEV strategies, opportunities, and performance monitoring
"""

import logging
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import MEVOpportunity, MEVStrategy, get_db
from services.blockchain import MEVDetector
from sqlalchemy import desc, func

mev_bp = Blueprint("mev", __name__)
logger = logging.getLogger(__name__)


@mev_bp.route("/strategies", methods=["GET"])
@jwt_required()
def get_mev_strategies():
    """Get MEV strategies with enhanced data and pagination"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        status_filter = request.args.get("status", None)
        user_id = get_jwt_identity()

        db = get_db()

        # Build query
        query = db.query(MEVStrategy).filter(MEVStrategy.user_id == user_id)

        # Apply status filter
        if status_filter:
            query = query.filter(MEVStrategy.status == status_filter)

        # Get total count for pagination
        total = query.count()

        # Apply pagination and ordering
        strategies = (
            query.order_by(desc(MEVStrategy.created_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        strategies_data = []
        for strategy in strategies:
            strategy_data = {
                "id": f"mev_{strategy.id}",
                "name": strategy.name,
                "type": strategy.strategy_type,
                "description": strategy.description,
                "status": strategy.status,
                "profitability": float(strategy.total_profit or 0),
                "successRate": float(strategy.success_rate or 0),
                "totalProfit": float(strategy.total_profit or 0),
                "totalExecutions": strategy.total_executions or 0,
                "averageGasCost": strategy.average_gas_cost or 0,
                "lastExecuted": (
                    strategy.last_executed.isoformat() + "Z"
                    if strategy.last_executed
                    else None
                ),
                "createdAt": strategy.created_at.isoformat() + "Z",
                "configuration": strategy.config
                or {
                    "maxGasPrice": 100,
                    "minProfitThreshold": 0.01,
                    "slippageTolerance": 0.01,
                },
            }
            strategies_data.append(strategy_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "items": strategies_data,
                    "pagination": {
                        "total": total,
                        "page": page,
                        "limit": limit,
                        "totalPages": (total + limit - 1) // limit,
                        "hasNext": (page * limit) < total,
                        "hasPrev": page > 1,
                    },
                    "summary": {
                        "totalStrategies": total,
                        "activeStrategies": db.query(MEVStrategy)
                        .filter(
                            MEVStrategy.user_id == user_id,
                            MEVStrategy.status == "active",
                        )
                        .count(),
                        "totalProfit": round(
                            float(
                                db.query(func.sum(MEVStrategy.total_profit))
                                .filter(MEVStrategy.user_id == user_id)
                                .scalar()
                                or 0
                            ),
                            2,
                        ),
                        "averageSuccessRate": round(
                            float(
                                db.query(func.avg(MEVStrategy.success_rate))
                                .filter(MEVStrategy.user_id == user_id)
                                .scalar()
                                or 0
                            ),
                            1,
                        ),
                    },
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"MEV strategies error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to fetch MEV strategies"}),
            500,
        )


@mev_bp.route("/strategies/deploy", methods=["POST"])
@jwt_required()
def deploy_mev_strategy():
    """Deploy a new MEV strategy"""
    try:
        data = request.get_json()
        strategy_type = data.get("strategy_type")
        name = data.get("name")
        description = data.get("description", "")
        config = data.get("parameters", {})
        user_id = get_jwt_identity()

        if not strategy_type or not name:
            return (
                jsonify(
                    {"success": False, "message": "Strategy type and name are required"}
                ),
                400,
            )

        db = get_db()

        # Create new strategy
        strategy = MEVStrategy(
            user_id=user_id,
            name=name,
            strategy_type=strategy_type,
            description=description,
            status="paused",  # Start as paused
            config=config,
            created_at=datetime.now(),
        )

        db.add(strategy)
        db.commit()

        return jsonify(
            {
                "success": True,
                "message": "MEV strategy deployed successfully",
                "data": {
                    "strategyId": f"mev_{strategy.id}",
                    "name": strategy.name,
                    "type": strategy.strategy_type,
                    "status": strategy.status,
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"Deploy MEV strategy error: {str(e)}")
        db.rollback()
        return (
            jsonify({"success": False, "message": "Failed to deploy MEV strategy"}),
            500,
        )


@mev_bp.route("/strategies/<strategy_id>", methods=["PUT"])
@jwt_required()
def update_mev_strategy(strategy_id):
    """Update an existing MEV strategy"""
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        db = get_db()

        # Extract numeric ID from strategy_id
        numeric_id = int(strategy_id.replace("mev_", ""))

        strategy = (
            db.query(MEVStrategy)
            .filter(MEVStrategy.id == numeric_id, MEVStrategy.user_id == user_id)
            .first()
        )

        if not strategy:
            return jsonify({"success": False, "message": "Strategy not found"}), 404

        # Update strategy fields
        if "name" in data:
            strategy.name = data["name"]
        if "description" in data:
            strategy.description = data["description"]
        if "status" in data:
            strategy.status = data["status"]
        if "config" in data:
            strategy.config = data["config"]

        strategy.updated_at = datetime.now()
        db.commit()

        return jsonify(
            {
                "success": True,
                "message": "Strategy updated successfully",
                "data": {
                    "id": f"mev_{strategy.id}",
                    "name": strategy.name,
                    "status": strategy.status,
                },
            }
        )

    except Exception as e:
        logger.error(f"Update MEV strategy error: {str(e)}")
        db.rollback()
        return (
            jsonify({"success": False, "message": "Failed to update MEV strategy"}),
            500,
        )


@mev_bp.route("/strategies/<strategy_id>", methods=["DELETE"])
@jwt_required()
def delete_mev_strategy(strategy_id):
    """Delete an MEV strategy"""
    try:
        user_id = get_jwt_identity()
        db = get_db()

        # Extract numeric ID from strategy_id
        numeric_id = int(strategy_id.replace("mev_", ""))

        strategy = (
            db.query(MEVStrategy)
            .filter(MEVStrategy.id == numeric_id, MEVStrategy.user_id == user_id)
            .first()
        )

        if not strategy:
            return jsonify({"success": False, "message": "Strategy not found"}), 404

        db.delete(strategy)
        db.commit()

        return jsonify({"success": True, "message": "Strategy deleted successfully"})

    except Exception as e:
        logger.error(f"Delete MEV strategy error: {str(e)}")
        db.rollback()
        return (
            jsonify({"success": False, "message": "Failed to delete MEV strategy"}),
            500,
        )


@mev_bp.route("/opportunities", methods=["GET"])
@jwt_required()
def get_mev_opportunities():
    """Get current MEV opportunities"""
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
        opportunity_type = request.args.get("type", None)
        min_profit = request.args.get("min_profit", None)
        user_id = get_jwt_identity()

        db = get_db()

        # Build query
        query = db.query(MEVOpportunity).filter(MEVOpportunity.user_id == user_id)

        # Apply filters
        if opportunity_type:
            query = query.filter(MEVOpportunity.opportunity_type == opportunity_type)
        if min_profit:
            query = query.filter(MEVOpportunity.estimated_profit >= float(min_profit))

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        opportunities = (
            query.order_by(desc(MEVOpportunity.detected_at))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )

        opportunities_data = []
        for opp in opportunities:
            opp_data = {
                "id": f"opp_{opp.id}",
                "type": opp.opportunity_type,
                "estimatedProfit": float(opp.estimated_profit or 0),
                "estimatedGas": opp.estimated_gas or 0,
                "probability": float(opp.probability or 0),
                "timeWindow": opp.time_window or 0,
                "protocols": opp.protocols or [],
                "status": opp.status,
                "detectedAt": opp.detected_at.isoformat() + "Z",
                "expiresAt": (
                    opp.expires_at.isoformat() + "Z" if opp.expires_at else None
                ),
                "metadata": opp.metadata or {},
            }
            opportunities_data.append(opp_data)

        return jsonify(
            {
                "success": True,
                "data": {
                    "opportunities": opportunities_data,
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
        logger.error(f"MEV opportunities error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to fetch MEV opportunities"}),
            500,
        )


@mev_bp.route("/opportunities/scan", methods=["POST"])
@jwt_required()
def scan_mev_opportunities():
    """Trigger a new MEV opportunity scan"""
    try:
        data = request.get_json()
        scan_types = data.get("types", ["arbitrage", "sandwich", "liquidation"])
        user_id = get_jwt_identity()

        # Initialize MEV detector
        mev_detector = MEVDetector()

        # Perform scan based on types
        new_opportunities = []
        for scan_type in scan_types:
            if scan_type == "arbitrage":
                opportunities = mev_detector.detect_arbitrage_opportunities()
            elif scan_type == "sandwich":
                opportunities = mev_detector.detect_sandwich_opportunities()
            elif scan_type == "liquidation":
                opportunities = mev_detector.detect_liquidation_opportunities()
            else:
                continue

            new_opportunities.extend(opportunities)

        # Save opportunities to database
        db = get_db()
        saved_count = 0

        for opp_data in new_opportunities:
            opportunity = MEVOpportunity(
                user_id=user_id,
                opportunity_type=opp_data.get("type"),
                estimated_profit=opp_data.get("estimated_profit"),
                estimated_gas=opp_data.get("estimated_gas"),
                probability=opp_data.get("probability"),
                time_window=opp_data.get("time_window"),
                protocols=opp_data.get("protocols", []),
                status="detected",
                detected_at=datetime.now(),
                expires_at=datetime.now()
                + timedelta(seconds=opp_data.get("time_window", 30)),
                metadata=opp_data.get("metadata", {}),
            )
            db.add(opportunity)
            saved_count += 1

        db.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Scan completed. Found {saved_count} new opportunities",
                "data": {"scannedTypes": scan_types, "newOpportunities": saved_count},
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"MEV scan error: {str(e)}")
        db.rollback() if "db" in locals() else None
        return (
            jsonify(
                {"success": False, "error": "Failed to scan for MEV opportunities"}
            ),
            500,
        )


@mev_bp.route("/opportunities/<opportunity_id>/execute", methods=["POST"])
@jwt_required()
def execute_mev_opportunity(opportunity_id):
    """Execute a specific MEV opportunity"""
    try:
        user_id = get_jwt_identity()
        db = get_db()

        # Extract numeric ID
        numeric_id = int(opportunity_id.replace("opp_", ""))

        opportunity = (
            db.query(MEVOpportunity)
            .filter(
                MEVOpportunity.id == numeric_id,
                MEVOpportunity.user_id == user_id,
                MEVOpportunity.status == "detected",
            )
            .first()
        )

        if not opportunity:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Opportunity not found or already executed",
                    }
                ),
                404,
            )

        # Check if opportunity is still valid
        if opportunity.expires_at and opportunity.expires_at < datetime.now():
            opportunity.status = "expired"
            db.commit()
            return (
                jsonify({"success": False, "message": "Opportunity has expired"}),
                400,
            )

        # Mark as executing
        opportunity.status = "executing"
        opportunity.executed_at = datetime.now()
        db.commit()

        # Initialize MEV detector for execution
        mev_detector = MEVDetector()

        # Execute based on opportunity type
        try:
            if opportunity.opportunity_type == "arbitrage":
                result = mev_detector.execute_arbitrage(opportunity.metadata)
            elif opportunity.opportunity_type == "sandwich":
                result = mev_detector.execute_sandwich(opportunity.metadata)
            elif opportunity.opportunity_type == "liquidation":
                result = mev_detector.execute_liquidation(opportunity.metadata)
            else:
                raise ValueError(
                    f"Unknown opportunity type: {opportunity.opportunity_type}"
                )

            # Update opportunity with results
            opportunity.status = "completed" if result.get("success") else "failed"
            opportunity.actual_profit = result.get("profit", 0)
            opportunity.gas_used = result.get("gas_used", 0)
            opportunity.transaction_hash = result.get("tx_hash")

        except Exception as exec_error:
            logger.error(f"MEV execution error: {str(exec_error)}")
            opportunity.status = "failed"
            opportunity.error_message = str(exec_error)

        db.commit()

        return jsonify(
            {
                "success": opportunity.status == "completed",
                "message": f"Opportunity execution {'completed' if opportunity.status == 'completed' else 'failed'}",
                "data": {
                    "opportunityId": opportunity_id,
                    "status": opportunity.status,
                    "actualProfit": float(opportunity.actual_profit or 0),
                    "gasUsed": opportunity.gas_used or 0,
                    "transactionHash": opportunity.transaction_hash,
                },
            }
        )

    except Exception as e:
        logger.error(f"Execute MEV opportunity error: {str(e)}")
        db.rollback() if "db" in locals() else None
        return (
            jsonify({"success": False, "error": "Failed to execute MEV opportunity"}),
            500,
        )


@mev_bp.route("/analytics", methods=["GET"])
@jwt_required()
def get_mev_analytics():
    """Get MEV performance analytics"""
    try:
        days = int(request.args.get("days", 30))
        user_id = get_jwt_identity()
        db = get_db()

        # Date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Get analytics data
        total_strategies = (
            db.query(MEVStrategy).filter(MEVStrategy.user_id == user_id).count()
        )

        active_strategies = (
            db.query(MEVStrategy)
            .filter(MEVStrategy.user_id == user_id, MEVStrategy.status == "active")
            .count()
        )

        total_opportunities = (
            db.query(MEVOpportunity)
            .filter(
                MEVOpportunity.user_id == user_id,
                MEVOpportunity.detected_at >= start_date,
            )
            .count()
        )

        executed_opportunities = (
            db.query(MEVOpportunity)
            .filter(
                MEVOpportunity.user_id == user_id,
                MEVOpportunity.status == "completed",
                MEVOpportunity.detected_at >= start_date,
            )
            .count()
        )

        total_profit = (
            db.query(func.sum(MEVOpportunity.actual_profit))
            .filter(
                MEVOpportunity.user_id == user_id,
                MEVOpportunity.status == "completed",
                MEVOpportunity.detected_at >= start_date,
            )
            .scalar()
            or 0
        )

        avg_success_rate = (
            db.query(func.avg(MEVStrategy.success_rate))
            .filter(MEVStrategy.user_id == user_id)
            .scalar()
            or 0
        )

        return jsonify(
            {
                "success": True,
                "data": {
                    "summary": {
                        "totalStrategies": total_strategies,
                        "activeStrategies": active_strategies,
                        "totalOpportunities": total_opportunities,
                        "executedOpportunities": executed_opportunities,
                        "successRate": round(float(avg_success_rate), 2),
                        "totalProfit": round(float(total_profit), 4),
                        "periodDays": days,
                    },
                    "performance": {
                        "executionRate": round(
                            (
                                (executed_opportunities / total_opportunities * 100)
                                if total_opportunities > 0
                                else 0
                            ),
                            2,
                        ),
                        "averageProfit": round(
                            (
                                float(total_profit / executed_opportunities)
                                if executed_opportunities > 0
                                else 0
                            ),
                            4,
                        ),
                        "profitTrend": "positive" if total_profit > 0 else "neutral",
                    },
                },
                "timestamp": datetime.now().isoformat() + "Z",
            }
        )

    except Exception as e:
        logger.error(f"MEV analytics error: {str(e)}")
        return (
            jsonify({"success": False, "error": "Failed to fetch MEV analytics"}),
            500,
        )
