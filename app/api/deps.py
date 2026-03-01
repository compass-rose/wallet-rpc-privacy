"""
API dependencies for FastAPI
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session


async def get_db(db: AsyncSession = Depends(get_session)) -> AsyncSession:
    """
    Dependency to get database session

    Args:
        db: AsyncSession from database pool

    Returns:
        AsyncSession for use in endpoints
    """
    return db
