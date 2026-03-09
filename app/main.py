"""
FastAPI application entry point
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from app.api.v1 import sessions, traffic, leaks, assessments, analytics, rules, dashboard
from app.models.base import Base
from app.core.database import engine
from app.core.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Wallet / RPC Privacy Leakage Measurement",
    description="A system to measure and quantify privacy leakage in wallet-RPC communications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event to create tables
@app.on_event("startup")
async def startup_event():
    """Create database tables on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown_event():
    """Graceful shutdown: complete all active sessions and dispose connections"""
    from sqlalchemy import select, func
    from app.models import Session, SessionStatus, NetworkTraffic
    from app.core.database import async_session_maker
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)

    try:
        async with async_session_maker() as db:
            result = await db.execute(
                select(Session).where(Session.status == SessionStatus.ACTIVE)
            )
            active_sessions = result.scalars().all()

            for session in active_sessions:
                count_result = await db.execute(
                    select(func.count()).select_from(NetworkTraffic).where(
                        NetworkTraffic.session_id == session.id
                    )
                )
                session.packet_count = count_result.scalar()
                session.status = SessionStatus.COMPLETED
                session.end_time = now.isoformat()

            await db.commit()
    except Exception:
        pass

    await engine.dispose()


# Include routers
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(traffic.router, prefix="/api/v1", tags=["traffic"])
app.include_router(leaks.router, prefix="/api/v1", tags=["leaks"])
app.include_router(assessments.router, prefix="/api/v1", tags=["assessments"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(rules.router, prefix="/api/v1", tags=["rules"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["dashboard"])


# Root endpoint
@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint"""
    return JSONResponse({
        "message": "Wallet / RPC Privacy Leakage Measurement System",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "redoc": "/redoc"
    })


# Health check endpoint
@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "wallet-privacy-backend"
    })


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred"
            },
            "metadata": {
                "path": request.url.path,
                "method": request.method
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
