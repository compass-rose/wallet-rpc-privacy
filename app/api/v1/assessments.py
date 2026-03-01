"""
Risk assessment API router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models import NetworkTraffic
from app.services.risk_service import RiskService
from app.services.risk_service import RiskService

from app.services.detection_service import DetectionService, RuleLoader
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.post("/sessions/{session_id}/assess")
async def run_assessment(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Run privacy risk assessment for a session

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Risk assessment results
    """
    # Get traffic records for the session
    result = await db.execute(
        select(NetworkTraffic).where(NetworkTraffic.session_id == session_id)
    )
    traffic_records = list(result.scalars().all())

    if not traffic_records:
        return {
            "success": True,
            "data": {"message": "No traffic records found for assessment"},
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    # Run risk assessment
    risk_service = RiskService()
    assessment = await risk_service.assess_session(session_id, traffic_records)
    stored = await risk_service.store_assessment(assessment, db)

    return {
        "success": True,
        "data": {
            "id": stored.id,
            "session_id": stored.session_id,
            "overall_score": stored.overall_score,
            "risk_level": stored.risk_level.value,
            "entropy_score": stored.entropy_score,
            "uniqueness_score": stored.uniqueness_score,
            "correlation_score": stored.correlation_score,
            "temporal_score": stored.temporal_score,
            "confidence": stored.confidence,
            "confidence_interval_low": stored.confidence_interval_low,
            "confidence_interval_high": stored.confidence_interval_high,
            "recommendations": stored.recommendations,
            "baseline_comparison": stored.baseline_comparison,
            "assessed_at": stored.assessed_at,
            "created_at": stored.created_at.isoformat()
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/sessions/{session_id}/assessment")
async def get_assessment(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest risk assessment for a session

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Risk assessment
    """
    risk_service = RiskService()
    assessment = await risk_service.get_latest_assessment(session_id, db)

    if not assessment:
        return {
            "success": True,
            "data": None,
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    return {
        "success": True,
        "data": {
            "id": assessment.id,
            "session_id": assessment.session_id,
            "overall_score": assessment.overall_score,
            "risk_level": assessment.risk_level.value,
            "entropy_score": assessment.entropy_score,
            "uniqueness_score": assessment.uniqueness_score,
            "correlation_score": assessment.correlation_score,
            "temporal_score": assessment.temporal_score,
            "confidence": assessment.confidence,
            "recommendations": assessment.recommendations,
            "baseline_comparison": assessment.baseline_comparison,
            "assessed_at": assessment.assessed_at,
            "created_at": assessment.created_at.isoformat()
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/assessments")
async def list_assessments(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    risk_level: str | None = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """
    List all risk assessments

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        risk_level: Filter by risk level
        db: Database session

    Returns:
        List of risk assessments
    """
    risk_service = RiskService()
    assessments = await risk_service.get_all_assessments(db, skip=skip, limit=limit)

    # Filter by risk level if specified
    if risk_level:
        from app.models import RiskLevelEnum  # Note: using RiskLevel from models
        assessments = [a for a in assessments if a.risk_level.value == risk_level]

    return {
        "success": True,
        "data": {
            "assessments": [
                {
                    "id": a.id,
                    "session_id": a.session_id,
                    "overall_score": a.overall_score,
                    "risk_level": a.risk_level.value,
                    "assessed_at": a.assessed_at,
                    "created_at": a.created_at.isoformat()
                }
                for a in assessments
            ],
            "total": len(assessments),
            "skip": skip,
            "limit": limit
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
