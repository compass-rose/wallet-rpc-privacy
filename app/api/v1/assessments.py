"""
Risk assessment API router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_db
from app.models import NetworkTraffic, Session
from app.services.risk_service import RiskService
from app.services.risk_service import RiskService

from app.services.risk import compare_with_baselines, generate_industry_comparison
from app.services.risk import simulate_distinguishing_attack
from app.services.risk.adversarial import evaluate_defense_effectiveness
from app.services.risk.attack_simulation import extract_session_features

from app.services.detection_service import DetectionService, RuleLoader
from uuid import uuid4
from datetime import datetime, timezone
from typing import Dict, Any

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
        from app.models.risk import RiskLevel
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


@router.post("/sessions/{session_id}/baseline-compare")
async def baseline_comparison(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    比与会话指标与随机和理想基线

    Args:
        session_id: 会话UUID
        db: 数据库会话

    Returns:
        基线比较结果
    """
    result = await db.execute(
        select(NetworkTraffic).where(NetworkTraffic.session_id == session_id)
    )
    traffic_records = list(result.scalars().all())

    if not traffic_records:
        return {
            "success": True,
            "data": {"message": "未找到流量记录用于基线比较"},
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    risk_service = RiskService()
    assessment = await risk_service.get_latest_assessment(session_id, db)

    if not assessment:
        return {
            "success": False,
            "error": "未找到该会话的风险评估，请先运行评估",
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    actual_metrics = {
        "entropy": assessment.entropy_score,
        "uniqueness": assessment.uniqueness_score,
        "correlation": assessment.correlation_score,
        "temporal": assessment.temporal_score
    }

    baseline_result = compare_with_baselines(actual_metrics, len(traffic_records))
    industry_result = generate_industry_comparison(actual_metrics)

    return {
        "success": True,
        "data": {
            "baseline_comparison": baseline_result,
            "industry_comparison": industry_result
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.post("/sessions/{session_id}/simulate-attack")
async def simulate_attack(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    运行基于ML的会话区分度攻击模拟

    Args:
        session_id: 会话UUID
        db: 数据库会话

    Returns:
        攻击模拟结果
    """
    result = await db.execute(
        select(NetworkTraffic)
    )
    all_traffic = result.scalars().all()

    if len(all_traffic) < 2:
        return {
            "success": False,
            "error": "需要至少2个会话进行攻击模拟",
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    traffic_by_session: Dict[str, Any] = {}
    for record in all_traffic:
        if record.session_id not in traffic_by_session:
            traffic_by_session[record.session_id] = []
        traffic_by_session[record.session_id].append(record)

    attack_result = simulate_distinguishing_attack(traffic_by_session)

    return {
        "success": True,
        "data": attack_result,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.post("/sessions/{session_id}/adversarial-test")
async def adversarial_testing(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    评估隐私防御策略的有效性

    Args:
        session_id: 会话UUID
        db: 数据库会话

    Returns:
        防御有效性评估结果
    """
    result = await db.execute(
        select(NetworkTraffic)
    )
    all_traffic = result.scalars().all()

    if len(all_traffic) < 2:
        return {
            "success": False,
            "error": "需要至少2个会话进行对抗性测试",
            "metadata": {
                "request_id": str(uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }

    traffic_by_session: Dict[str, Any] = {}
    for record in all_traffic:
        if record.session_id not in traffic_by_session:
            traffic_by_session[record.session_id] = []
        traffic_by_session[record.session_id].append(record)

    defense_result = evaluate_defense_effectiveness(traffic_by_session)

    return {
        "success": True,
        "data": defense_result,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
