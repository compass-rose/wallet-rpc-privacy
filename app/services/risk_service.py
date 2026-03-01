"""
Risk assessment service - high-level interface
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services.risk.assessment import compute_risk_assessment, classify_risk_level
from app.models import RiskAssessment, NetworkTraffic


class RiskService:
    """Service for privacy risk assessment"""

    async def assess_session(
        self, session_id: str, traffic_records: list[NetworkTraffic]
    ) -> RiskAssessment:
        """
        Compute risk assessment for a session

        Args:
            session_id: Session UUID
            traffic_records: List of traffic records

        Returns:
            RiskAssessment model
        """
        return await compute_risk_assessment(session_id, traffic_records)

    async def store_assessment(
        self, assessment: RiskAssessment, db: AsyncSession
    ) -> RiskAssessment:
        """
        Store assessment in database

        Args:
            assessment: RiskAssessment to store
            db: Database session

        Returns:
            Stored and refreshed assessment
        """
        db.add(assessment)
        await db.commit()
        await db.refresh(assessment)
        return assessment

    async def get_latest_assessment(
        self, session_id: str, db: AsyncSession
    ) -> RiskAssessment | None:
        """
        Get the latest risk assessment for a session

        Args:
            session_id: Session UUID
            db: Database session

        Returns:
            Latest RiskAssessment or None
        """
        result = await db.execute(
            select(RiskAssessment)
            .where(RiskAssessment.session_id == session_id)
            .order_by(RiskAssessment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_all_assessments(
        self, db: AsyncSession, skip: int = 0, limit: int = 50
    ) -> list[RiskAssessment]:
        """
        Get all risk assessments with pagination

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            List of RiskAssessment models
        """
        result = await db.execute(
            select(RiskAssessment)
            .offset(skip)
            .limit(limit)
            .order_by(RiskAssessment.created_at.desc())
        )
        return list(result.scalars().all())
