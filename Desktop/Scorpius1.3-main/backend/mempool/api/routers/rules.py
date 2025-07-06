"""
Rules API Router

Handles all rule-related API endpoints including:
- Rule CRUD operations
- Rule testing and validation
- Rule performance analytics
"""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ..dependencies import get_current_user, get_database
from ..models import (
    PaginationParams,
    RuleAction,
    RuleCondition,
    RuleRequest,
    RuleResponse,
)

router = APIRouter(prefix="/api/v1/rules", tags=["rules"])


class RuleFilters(BaseModel):
    """Rule filtering parameters"""

    enabled: Optional[bool] = None
    name_contains: Optional[str] = None
    tag: Optional[str] = None


class RuleTestRequest(BaseModel):
    """Rule testing request"""

    transaction_data: dict[str, Any]
    rule_conditions: list[RuleCondition]


class RuleTestResponse(BaseModel):
    """Rule testing response"""

    matched: bool
    matched_conditions: list[str]
    execution_time_ms: float
    confidence: float


class RulePerformanceResponse(BaseModel):
    """Rule performance metrics"""

    rule_id: UUID
    rule_name: str
    total_triggers: int
    true_positives: int
    false_positives: int
    precision: float
    recall: float
    avg_execution_time_ms: float
    last_triggered: Optional[datetime]


@router.get("", response_model=list[RuleResponse])
async def get_rules(
    pagination: PaginationParams = Depends(),
    filters: RuleFilters = Depends(),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """
    Get rules with filtering and pagination.
    """
    try:
        query_parts = ["SELECT * FROM rules WHERE 1=1"]
        params = []
        param_count = 0

        if filters.enabled is not None:
            param_count += 1
            query_parts.append(f"AND enabled = ${param_count}")
            params.append(filters.enabled)

        if filters.name_contains:
            param_count += 1
            query_parts.append(f"AND name ILIKE ${param_count}")
            params.append(f"%{filters.name_contains}%")

        if filters.tag:
            param_count += 1
            query_parts.append(f"AND ${param_count} = ANY(tags)")
            params.append(filters.tag)

        query_parts.append("ORDER BY created_at DESC")

        param_count += 1
        query_parts.append(f"LIMIT ${param_count}")
        params.append(pagination.limit)

        param_count += 1
        query_parts.append(f"OFFSET ${param_count}")
        params.append(pagination.offset)

        query = " ".join(query_parts)

        async with db.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve rules: {str(e)}"
        )


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get a specific rule by ID."""
    try:
        query = "SELECT * FROM rules WHERE id = $1"

        async with db.acquire() as conn:
            row = await conn.fetchrow(query, rule_id)

            if not row:
                raise HTTPException(status_code=404, detail="Rule not found")

            return dict(row)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve rule: {str(e)}"
        )


@router.post("", response_model=dict)
async def create_rule(
    rule_data: RuleRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Create a new rule."""
    try:
        # Validate rule conditions and actions
        await _validate_rule(rule_data)

        rule_id = uuid4()
        query = """
        INSERT INTO rules (id, name, description, conditions, actions, enabled, created_by)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id
        """

        import json

        conditions_json = json.dumps([cond.dict() for cond in rule_data.conditions])
        actions_json = json.dumps([action.dict() for action in rule_data.actions])

        async with db.acquire() as conn:
            result = await conn.fetchval(
                query,
                rule_id,
                rule_data.name,
                rule_data.description,
                conditions_json,
                actions_json,
                rule_data.enabled,
                current_user["user_id"],
            )

            return {
                "id": result,
                "message": "Rule created successfully",
                "name": rule_data.name,
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


@router.put("/{rule_id}", response_model=dict)
async def update_rule(
    rule_id: UUID,
    rule_data: RuleRequest,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Update an existing rule."""
    try:
        # Validate rule conditions and actions
        await _validate_rule(rule_data)

        query = """
        UPDATE rules 
        SET name = $1, description = $2, conditions = $3, actions = $4, 
            enabled = $5, updated_at = NOW(), updated_by = $6
        WHERE id = $7
        RETURNING id
        """

        import json

        conditions_json = json.dumps([cond.dict() for cond in rule_data.conditions])
        actions_json = json.dumps([action.dict() for action in rule_data.actions])

        async with db.acquire() as conn:
            result = await conn.fetchval(
                query,
                rule_data.name,
                rule_data.description,
                conditions_json,
                actions_json,
                rule_data.enabled,
                current_user["user_id"],
                rule_id,
            )

            if not result:
                raise HTTPException(status_code=404, detail="Rule not found")

            return {
                "id": rule_id,
                "message": "Rule updated successfully",
                "name": rule_data.name,
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Delete a rule."""
    try:
        # Check if rule has associated alerts
        async with db.acquire() as conn:
            alert_count = await conn.fetchval(
                "SELECT COUNT(*) FROM alerts WHERE rule_id = $1", rule_id
            )

            if alert_count > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Cannot delete rule with {alert_count} associated alerts. "
                    "Consider disabling the rule instead.",
                )

            # Delete the rule
            result = await conn.fetchval(
                "DELETE FROM rules WHERE id = $1 RETURNING id", rule_id
            )

            if not result:
                raise HTTPException(status_code=404, detail="Rule not found")

            return {"id": rule_id, "message": "Rule deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")


@router.patch("/{rule_id}/toggle")
async def toggle_rule(
    rule_id: UUID,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Toggle rule enabled/disabled status."""
    try:
        query = """
        UPDATE rules 
        SET enabled = NOT enabled, updated_at = NOW(), updated_by = $1
        WHERE id = $2
        RETURNING id, enabled
        """

        async with db.acquire() as conn:
            result = await conn.fetchrow(query, current_user["user_id"], rule_id)

            if not result:
                raise HTTPException(status_code=404, detail="Rule not found")

            status = "enabled" if result["enabled"] else "disabled"

            return {
                "id": rule_id,
                "enabled": result["enabled"],
                "message": f"Rule {status} successfully",
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle rule: {str(e)}")


@router.post("/test", response_model=RuleTestResponse)
async def test_rule(
    test_data: RuleTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """Test rule conditions against sample transaction data."""
    try:
        import time

        start_time = time.time()

        # Simulate rule evaluation
        matched_conditions = []
        total_conditions = len(test_data.rule_conditions)

        for condition in test_data.rule_conditions:
            if _evaluate_condition(condition, test_data.transaction_data):
                matched_conditions.append(condition.type)

        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        matched = len(matched_conditions) > 0
        confidence = (
            len(matched_conditions) / total_conditions if total_conditions > 0 else 0
        )

        return RuleTestResponse(
            matched=matched,
            matched_conditions=matched_conditions,
            execution_time_ms=round(execution_time, 2),
            confidence=round(confidence, 2),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test rule: {str(e)}")


@router.get("/{rule_id}/performance", response_model=RulePerformanceResponse)
async def get_rule_performance(
    rule_id: UUID,
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database),
):
    """Get rule performance metrics."""
    try:
        async with db.acquire() as conn:
            # Get rule info
            rule_info = await conn.fetchrow(
                "SELECT name FROM rules WHERE id = $1", rule_id
            )

            if not rule_info:
                raise HTTPException(status_code=404, detail="Rule not found")

            # Get performance metrics
            time_filter = f"created_at > NOW() - INTERVAL '{days} days'"

            # Total triggers
            total_triggers = await conn.fetchval(
                f"""
                SELECT COUNT(*) FROM alerts 
                WHERE rule_id = $1 AND {time_filter}
            """,
                rule_id,
            )

            # True/false positives (placeholder logic)
            true_positives = int(total_triggers * 0.85) if total_triggers else 0
            false_positives = total_triggers - true_positives if total_triggers else 0

            # Calculate precision and recall
            precision = true_positives / total_triggers if total_triggers > 0 else 0
            recall = 0.90  # Placeholder

            # Average execution time (placeholder)
            avg_execution_time = 2.5

            # Last triggered
            last_triggered = await conn.fetchval(
                f"""
                SELECT MAX(created_at) FROM alerts 
                WHERE rule_id = $1
            """,
                rule_id,
            )

            return RulePerformanceResponse(
                rule_id=rule_id,
                rule_name=rule_info["name"],
                total_triggers=total_triggers or 0,
                true_positives=true_positives,
                false_positives=false_positives,
                precision=round(precision, 3),
                recall=round(recall, 3),
                avg_execution_time_ms=avg_execution_time,
                last_triggered=last_triggered,
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get rule performance: {str(e)}"
        )


@router.get("/templates/list")
async def get_rule_templates(
    current_user: dict = Depends(get_current_user),
):
    """Get predefined rule templates."""
    templates = [
        {
            "id": "high_value_transfer",
            "name": "High Value Transfer",
            "description": "Detect transfers above a certain value threshold",
            "category": "financial",
            "conditions": [
                {
                    "type": "value_threshold",
                    "field": "value",
                    "operator": "greater_than",
                    "value": "1000000000000000000",  # 1 ETH in wei
                }
            ],
            "actions": [
                {
                    "type": "create_alert",
                    "severity": "medium",
                    "title": "High Value Transfer Detected",
                    "description": "Transfer above 1 ETH detected",
                }
            ],
        },
        {
            "id": "suspicious_contract",
            "name": "Suspicious Contract Interaction",
            "description": "Detect interactions with known suspicious contracts",
            "category": "security",
            "conditions": [
                {
                    "type": "address_blacklist",
                    "field": "to_address",
                    "addresses": ["0x..."],  # Placeholder addresses
                }
            ],
            "actions": [
                {
                    "type": "create_alert",
                    "severity": "high",
                    "title": "Suspicious Contract Interaction",
                    "description": "Transaction to blacklisted contract",
                }
            ],
        },
        {
            "id": "mev_sandwich",
            "name": "MEV Sandwich Attack",
            "description": "Detect potential sandwich attacks",
            "category": "mev",
            "conditions": [{"type": "mev_pattern", "value": "sandwich"}],
            "actions": [
                {
                    "type": "create_alert",
                    "severity": "high",
                    "title": "MEV Sandwich Attack Detected",
                    "description": "Potential sandwich attack pattern",
                }
            ],
        },
    ]

    return {"templates": templates}


# Helper functions
async def _validate_rule(rule_data: RuleRequest):
    """Validate rule conditions and actions."""
    if not rule_data.conditions:
        raise HTTPException(
            status_code=400, detail="Rule must have at least one condition"
        )

    if not rule_data.actions:
        raise HTTPException(
            status_code=400, detail="Rule must have at least one action"
        )

    # Validate condition types
    valid_condition_types = [
        "value_threshold",
        "gas_threshold",
        "address_whitelist",
        "address_blacklist",
        "chain_filter",
        "mev_pattern",
    ]

    for condition in rule_data.conditions:
        if condition.type not in valid_condition_types:
            raise HTTPException(
                status_code=400, detail=f"Invalid condition type: {condition.type}"
            )

    # Validate action types
    valid_action_types = ["create_alert", "webhook", "email"]

    for action in rule_data.actions:
        if action.type not in valid_action_types:
            raise HTTPException(
                status_code=400, detail=f"Invalid action type: {action.type}"
            )


def _evaluate_condition(condition: RuleCondition, transaction_data: dict) -> bool:
    """Evaluate a single condition against transaction data."""
    try:
        if condition.type == "value_threshold":
            tx_value = float(transaction_data.get("value", 0))
            threshold_value = float(condition.value)

            if condition.operator == "greater_than":
                return tx_value > threshold_value
            elif condition.operator == "less_than":
                return tx_value < threshold_value
            elif condition.operator == "equals":
                return tx_value == threshold_value

        elif condition.type == "address_whitelist":
            field_value = transaction_data.get(condition.field, "")
            return field_value in (condition.addresses or [])

        elif condition.type == "address_blacklist":
            field_value = transaction_data.get(condition.field, "")
            return field_value not in (condition.addresses or [])

        elif condition.type == "chain_filter":
            tx_chain = transaction_data.get("chain_id", 0)
            return tx_chain in (condition.chain_ids or [])

        elif condition.type == "mev_pattern":
            mev_patterns = transaction_data.get("mev_patterns", [])
            return condition.value in mev_patterns

        return False

    except Exception:
        return False
