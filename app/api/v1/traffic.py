"""
Traffic capture API router
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.api.deps import get_db
from app.models import Session, SessionStatus, NetworkTraffic
from app.services.traffic.base import CaptureConfig
from app.services.traffic.factory import get_traffic_provider
from app.services.traffic_service import TrafficService
from app.services.detection_service import DetectionService
from uuid import uuid4
from datetime import datetime, timezone

router = APIRouter()


@router.post("/sessions/{session_id}/traffic/start")
async def start_capture(
    session_id: str,
    packet_count: int = Query(500, ge=1, le=10000),
    duration_seconds: int | None = Query(None, ge=1, le=3600),
    db: AsyncSession = Depends(get_db)
):
    """
    Start traffic capture for a session

    Args:
        session_id: Session UUID
        packet_count: Number of packets to capture (for mock provider)
        duration_seconds: Capture duration in seconds (optional)
        db: Database session

    Returns:
        Capture status
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

    if session.status != SessionStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail={"code": "INVALID_INPUT", "message": "Session is not active"}
        )

    # Get provider from config
    from app.core.config import get_settings
    settings = get_settings()

    provider = get_traffic_provider(settings.traffic_provider, count=packet_count)
    service = TrafficService(provider)

    config = CaptureConfig(
        wallet_type=session.wallet_type,
        rpc_provider=session.rpc_provider,
        packet_count=packet_count,
        duration_seconds=duration_seconds
    )

    status = await service.start_capture(session_id, config)

    # Stream and store traffic
    stored_count = await service.stream_and_store(session_id, db)

    # Update session packet count
    session.packet_count = stored_count

    await db.commit()

    return {
        "success": True,
        "data": {
            "active": status["active"],
            "packets_captured": stored_count,
            "session_id": session_id
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.post("/sessions/{session_id}/traffic/stop")
async def stop_capture(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Stop traffic capture for a session

    Args:
        session_id: Session UUID
        db: Database session

    Returns:
        Final capture status
    """
    from app.core.config import get_settings
    settings = get_settings()

    provider = get_traffic_provider(settings.traffic_provider)
    service = TrafficService(provider)

    status = await service.stop_capture(session_id)

    # Update session
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if session:
        session.packet_count = status["packets_captured"]
        session.status = SessionStatus.COMPLETED
        session.end_time = datetime.now(timezone.utc).isoformat()

        # Calculate duration if we have start_time
        if session.start_time:
            start = datetime.fromisoformat(session.start_time.replace('Z', '+00:00'))
            end = datetime.now(timezone.utc)
            session.duration_seconds = int((end - start).total_seconds())

        await db.commit()

    return {
        "success": True,
        "data": {
            "packets_captured": status["packets_captured"],
            "active": status["active"]
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/sessions/{session_id}/traffic")
async def get_traffic(
    session_id: str,
    method: str | None = Query(None),
    rpc_method: str | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get traffic records for a session

    Args:
        session_id: Session UUID
        method: Filter by HTTP method
        rpc_method: Filter by RPC method
        limit: Number of records to return
        offset: Number of records to skip
        db: Database session

    Returns:
        Traffic records
    """
    query = select(NetworkTraffic).where(NetworkTraffic.session_id == session_id)

    # Apply filters
    if method:
        query = query.where(NetworkTraffic.method == method)
    if rpc_method:
        query = query.where(NetworkTraffic.rpc_method == rpc_method)

    # Apply pagination
    total_result = await db.execute(select(func.count(NetworkTraffic.id)).where(NetworkTraffic.session_id == session_id))
    total = total_result.scalar_one() or 0

    result = await db.execute(
        query
        .order_by(NetworkTraffic.request_timestamp)
        .offset(offset)
        .limit(limit)
    )

    traffic = result.scalars().all()

    return {
        "success": True,
        "data": {
            "traffic": [
                {
                    "id": t.id,
                    "session_id": t.session_id,
                    "method": t.method,
                    "endpoint": t.endpoint,
                    "rpc_method": t.rpc_method,
                    "request_timestamp": t.request_timestamp.isoformat() if t.request_timestamp else None,
                    "response_time_ms": t.response_time_ms,
                    "response_status": t.response_status,
                    "response_size_bytes": t.response_size_bytes,
                    "user_agent": t.user_agent
                }
                for t in traffic
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


@router.post("/sessions/{session_id}/traffic/record")
async def record_single_traffic(
    session_id: str,
    record: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Record a single traffic record (for RPC proxy)
    
    Args:
        session_id: Session UUID
        record: Traffic record data (method, endpoint, rpc_method, etc.)
        db: Database session
    
    Returns:
        Success status
    """
    from datetime import datetime, timezone
    from uuid import uuid4
    
    traffic = NetworkTraffic(
        id=str(uuid4()),
        session_id=session_id,
        method=record.get("method", "POST"),
        endpoint=record.get("endpoint", ""),
        request_body=record.get("request_body"),
        rpc_method=record.get("rpc_method"),
        rpc_params_hash=record.get("rpc_params_hash"),
        request_timestamp=datetime.fromisoformat(record["request_timestamp"]) if record.get("request_timestamp") else datetime.now(timezone.utc),
        response_time_ms=record.get("response_time_ms"),
        response_status=record.get("response_status"),
        response_size_bytes=record.get("response_size_bytes"),
        ip_address_hash=record.get("ip_address_hash"),
        user_agent=record.get("user_agent", "RPC-Proxy")
    )
    
    db.add(traffic)
    await db.commit()
    
    return {
        "success": True,
        "data": {
            "id": traffic.id,
            "message": "Traffic recorded successfully"
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
