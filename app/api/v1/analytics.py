"""
Analytics API router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.analytics import AnalyticsService
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.get("/analytics/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall summary statistics

    Args:
        db: Database session

    Returns:
        Summary statistics
    """
    service = AnalyticsService()
    stats = await service.get_summary_stats(db)

    return {
        "success": True,
        "data": stats,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/analytics/trends")
async def get_trends(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trend analysis

    Args:
        days: Number of days to analyze
        db: Database session

    Returns:
        Trend data
    """
    service = AnalyticsService()
    trends = await service.get_trends(db, days)

    return {
        "success": True,
        "data": trends,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/analytics/leaks/distribution")
async def get_leak_distribution(
    db: AsyncSession = Depends(get_db)
):
    """
    Get privacy leak type distribution

    Args:
        db: Database session

    Returns:
        Leak type distribution
    """
    service = AnalyticsService()
    distribution = await service.get_leak_distribution(db)

    return {
        "success": True,
        "data": distribution,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/analytics/risk/distribution")
async def get_risk_distribution(
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk level distribution

    Args:
        db: Database session

    Returns:
        Risk level distribution
    """
    service = AnalyticsService()
    distribution = await service.get_risk_level_distribution(db)

    return {
        "success": True,
        "data": distribution,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/analytics/methods/frequency")
async def get_method_frequency(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most frequently used RPC methods

    Args:
        limit: Number of methods to return
        db: Database session

    Returns:
        Method frequencies
    """
    service = AnalyticsService()
    methods = await service.get_method_frequencies(db, limit)

    return {
        "success": True,
        "data": {"frequencies": methods},
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/analytics/sessions/top-risk")
async def get_top_risk_sessions(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get sessions with highest risk scores

    Args:
        limit: Number of sessions to return
        db: Database session

    Returns:
        Top risk sessions
    """
    service = AnalyticsService()
    sessions = await service.get_top_risk_sessions(db, limit)

    return {
        "success": True,
        "data": {"sessions": sessions},
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/analytics/response-times")
async def get_response_time_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get RPC response time statistics

    Args:
        db: Database session

    Returns:
        Response time statistics
    """
    service = AnalyticsService()
    stats = await service.get_response_time_stats(db)

    return {
        "success": True,
        "data": stats,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
