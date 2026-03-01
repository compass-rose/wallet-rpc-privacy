"""
Privacy leak events API router
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.deps import get_db
from app.models import PrivacyLeakEvent, LeakType
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.get("/sessions/{session_id}/leaks")
async def get_session_leaks(
    session_id: str,
    leak_type: LeakType | None = Query(None),
    min_confidence: float | None = Query(None, ge=0.0, le=1.0),
    rule_id: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get privacy leak events for a session

    Args:
        session_id: Session UUID
        leak_type: Filter by leak type
        min_confidence: Filter by minimum confidence
        rule_id: Filter by rule ID
        limit: Number of records to return
        offset: Number of records to skip
        db: Database session

    Returns:
        Privacy leak events
    """
    query = select(PrivacyLeakEvent).where(PrivacyLeakEvent.session_id == session_id)

    # Apply filters
    if leak_type:
        query = query.where(PrivacyLeakEvent.leak_type == leak_type)
    if min_confidence is not None:
        query = query.where(PrivacyLeakEvent.confidence >= min_confidence)
    if rule_id:
        query = query.where(PrivacyLeakEvent.rule_id == rule_id)

    # Get total count
    count_result = await db.execute(
        select(func.count(PrivacyLeakEvent.id)).where(PrivacyLeakEvent.session_id == session_id)
    )
    total = count_result.scalar_one() or 0

    # Apply pagination
    result = await db.execute(
        query
        .order_by(PrivacyLeakEvent.timestamp.desc())
        .offset(offset)
        .limit(limit)
    )

    leaks = result.scalars().all()

    return {
        "success": True,
        "data": {
            "leaks": [
                {
                    "id": l.id,
                    "session_id": l.session_id,
                    "leak_type": l.leak_type.value,
                    "method_name": l.method_name,
                    "description": l.description,
                    "confidence": l.confidence,
                    "confidence_interval_low": l.confidence_interval_low,
                    "confidence_interval_high": l.confidence_interval_high,
                    "details": l.details,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None,
                    "address_hash": l.address_hash,
                    "rule_id": l.rule_id,
                    "created_at": l.created_at.isoformat()
                }
                for l in leaks
            ],
            "total": total,
            "limit": limit,
            "offset": offset
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/leaks")
async def list_all_leaks(
    leak_type: LeakType | None = Query(None),
    min_confidence: float | None = Query(None, ge=0.0, le=1.0),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List all privacy leak events across all sessions

    Args:
        leak_type: Filter by leak type
        min_confidence: Filter by minimum confidence
        skip: Number of records to skip
        limit: Number of records to return
        db: Database session

    Returns:
        All privacy leak events
    """
    query = select(PrivacyLeakEvent)

    # Apply filters
    if leak_type:
        query = query.where(PrivacyLeakEvent.leak_type == leak_type)
    if min_confidence is not None:
        query = query.where(PrivacyLeakEvent.confidence >= min_confidence)

    # Get total count
    count_result = await db.execute(select(func.count(PrivacyLeakEvent.id)))
    total = count_result.scalar_one() or 0

    # Apply pagination
    result = await db.execute(
        query
        .order_by(PrivacyLeakEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    leaks = result.scalars().all()

    return {
        "success": True,
        "data": {
            "leaks": [
                {
                    "id": l.id,
                    "session_id": l.session_id,
                    "leak_type": l.leak_type.value,
                    "method_name": l.method_name,
                    "description": l.description,
                    "confidence": l.confidence,
                    "timestamp": l.timestamp.isoformat() if l.timestamp else None
                }
                for l in leaks
            ],
            "total": total,
            "skip": skip,
            "limit": limit
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
