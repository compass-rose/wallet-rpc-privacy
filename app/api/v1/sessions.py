"""
Sessions API router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.api.deps import get_db
from app.models import Session, SessionStatus, NetworkTraffic
from app.models.common import SessionCreate, SessionResponse
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.post("/sessions", response_model=dict, status_code=201)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new capture session

    Args:
        data: Session creation data (wallet_type, rpc_provider)
        db: Database session

    Returns:
        Created session ID and status
    """
    session = Session(
        id=str(uuid4()),
        wallet_type=data.wallet_type,
        rpc_provider=data.rpc_provider,
        start_time=datetime.now(timezone.utc).isoformat(),
        status=SessionStatus.ACTIVE
    )

    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "success": True,
        "data": {
            "id": session.id,
            "wallet_type": session.wallet_type,
            "rpc_provider": session.rpc_provider,
            "status": "active",
            "created_at": session.created_at.isoformat()
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get session details by ID

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Session details
    """
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": f"Session {session_id} not found"
            }
        )

    return {
        "success": True,
        "data": {
            "id": session.id,
            "wallet_type": session.wallet_type,
            "rpc_provider": session.rpc_provider,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "packet_count": session.packet_count,
            "duration_seconds": session.duration_seconds,
            "status": session.status.value,
            "session_metadata": session.session_metadata,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/sessions")
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    wallet_type: str | None = None,
    rpc_provider: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all sessions with optional filtering

    Args:
        skip: Number of records to skip
        limit: Number of records to return
        wallet_type: Filter by wallet type
        rpc_provider: Filter by RPC provider
        status: Filter by status
        db: Database session

    Returns:
        List of sessions
    """
    query = select(Session)
    result = await db.execute(
        query
        .where(Session.wallet_type == wallet_type if wallet_type else True)
        .where(Session.rpc_provider == rpc_provider if rpc_provider else True)
        .where(Session.status == SessionStatus(status) if status else True)
        .offset(skip)
        .limit(limit)
        .order_by(Session.created_at.desc())
    )

    sessions = result.scalars().all()

    # Get total count
    count_result = await db.execute(select(func.count(Session.id)))
    total = count_result.scalar_one() or 0

    return {
        "success": True,
        "data": {
            "sessions": [
                {
                    "id": s.id,
                    "wallet_type": s.wallet_type,
                    "rpc_provider": s.rpc_provider,
                    "status": s.status.value,
                    "packet_count": s.packet_count,
                    "created_at": s.created_at.isoformat()
                }
                for s in sessions
            ],
            "total": total,
            "limit": limit,
            "offset": skip
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.put("/sessions/{session_id}")
async def update_session(
    session_id: str,
    status: str | None = None,
    end_time: str | None = None,
    packet_count: int | None = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Update session details

    Args:
        session_id: Session UUID
        status: New status
        end_time: End time (ISO format)
        packet_count: Total packet count
        db: Database session

    Returns:
        Updated session
    """
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Session not found"}
        )

    # Update fields if provided
    if status:
        session.status = SessionStatus(status)
    if end_time:
        session.end_time = end_time
    if packet_count is not None:
        session.packet_count = packet_count

    await db.commit()
    await db.refresh(session)

    return {
        "success": True,
        "data": {
            "id": session.id,
            "status": session.status.value,
            "packet_count": session.packet_count
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a session

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Deletion confirmation
    """
    # Check if session exists
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=404,
            detail={"code": "NOT_FOUND", "message": "Session not found"}
        )

    # Delete session (cascade will delete related records)
    await db.execute(delete(Session).where(Session.id == session_id))
    await db.commit()

    return {
        "success": True,
        "data": {"message": "Session deleted successfully"},
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
