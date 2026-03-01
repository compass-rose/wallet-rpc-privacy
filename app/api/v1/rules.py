"""
Detection rules API router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models import DetectionRule
from app.services.detection_service import DetectionService
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.get("/rules")
async def list_rules(
    category: str | None = None,
    enabled_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    List all detection rules

    Args:
        category: Filter by category
        enabled_only: Return only enabled rules
        db: Database session

    Returns:
        List of detection rules
    """
    service = DetectionService()

    # Get rules from YAML files (primary source)
    rules = service.get_rules()

    # Apply filters
    if category:
        rules = [r for r in rules if r["category"] == category]
    if enabled_only:
        rules = [r for r in rules if r["enabled"]]

    return {
        "success": True,
        "data": {
            "rules": rules,
            "total": len(rules)
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/rules/summary")
async def get_rules_summary(
):
    """
    Get detection rules summary statistics

    Returns:
        Rules summary
    """
    service = DetectionService()
    summary = service.get_rules_summary()

    return {
        "success": True,
        "data": summary,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/rules/{rule_id}")
async def get_rule(
    rule_id: str,
):
    """
    Get a specific detection rule

    Args:
        rule_id: Rule ID

    Returns:
        Detection rule details
    """
    service = DetectionService()

    # Find rule
    from app.services.detection.engine import RuleEngine

    engine = RuleEngine()
    rule = engine.loader.get_rule(rule_id)

    if not rule:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": f"Rule {rule_id} not found"}
        )

    return {
        "success": True,
        "data": {
            "id": rule.rule_id,
            "name": rule.name,
            "category": rule.category,
            "priority": rule.priority,
            "enabled": rule.enabled,
            "description": rule.description,
            "conditions": rule.conditions,
            "actions": rule.actions,
            "version": rule.version
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
