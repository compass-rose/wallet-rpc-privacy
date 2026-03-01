"""
Analytics service - statistics and trends
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from app.models import Session, NetworkTraffic, PrivacyLeakEvent, RiskAssessment
from datetime import datetime, timedelta


class AnalyticsService:
    """Service for analytics and reporting"""

    async def get_summary_stats(self, db: AsyncSession) -> Dict:
        """
        Get overall summary statistics

        Args:
            db: Database session

        Returns:
            Dictionary with summary statistics
        """
        # Count sessions
        result = await db.execute(select(func.count(Session.id)))
        session_count = result.scalar_one() or 0

        # Count traffic records
        result = await db.execute(select(func.count(NetworkTraffic.id)))
        traffic_count = result.scalar_one() or 0

        # Count privacy leaks
        result = await db.execute(select(func.count(PrivacyLeakEvent.id)))
        leak_count = result.scalar_one() or 0

        # Count risk assessments
        result = await db.execute(select(func.count(RiskAssessment.id)))
        assessment_count = result.scalar_one() or 0

        # Average risk score
        result = await db.execute(select(func.avg(RiskAssessment.overall_score)))
        avg_risk_score = round(result.scalar_one() or 0, 2)

        # Get session status counts
        result = await db.execute(
            select(Session.status, func.count(Session.id))
            .group_by(Session.status)
        )
        status_counts = {row[0].value: row[1] for row in result.all()}

        return {
            "total_sessions": session_count,
            "total_traffic": traffic_count,
            "total_leaks": leak_count,
            "total_assessments": assessment_count,
            "average_risk_score": avg_risk_score,
            "sessions_by_status": status_counts
        }

    async def get_trends(
        self, db: AsyncSession, days: int = 7
    ) -> Dict:
        """
        Get trend analysis by day

        Args:
            db: Database session
            days: Number of days to analyze

        Returns:
            Dictionary with trend data
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Session trends
        result = await db.execute(
            select(
                func.date(Session.start_time).label('date'),
                func.count(Session.id).label('count')
            )
            .where(Session.start_time >= cutoff)
            .group_by(func.date(Session.start_time))
            .order_by(func.date(Session.start_time))
        )

        session_trends = [
            {"date": str(row.date), "count": row.count}
            for row in result.all()
        ]

        # Risk score trends
        result = await db.execute(
            select(
                func.date(RiskAssessment.assessed_at).label('date'),
                func.avg(RiskAssessment.overall_score).label('avg_score')
            )
            .where(RiskAssessment.assessed_at >= cutoff)
            .group_by(func.date(RiskAssessment.assessed_at))
            .order_by(func.date(RiskAssessment.assessed_at))
        )

        risk_trends = [
            {"date": str(row.date), "average_risk_score": round(float(row.avg_score), 2)}
            for row in result.all()
        ]

        return {
            "days": days,
            "session_trends": session_trends,
            "risk_trends": risk_trends
        }

    async def get_leak_distribution(self, db: AsyncSession) -> Dict:
        """
        Get privacy leak type distribution

        Args:
            db: Database session

        Returns:
            Dictionary with leak type counts
        """
        result = await db.execute(
            select(
                PrivacyLeakEvent.leak_type,
                func.count(PrivacyLeakEvent.id).label('count')
            )
            .group_by(PrivacyLeakEvent.leak_type)
            .order_by(func.count(PrivacyLeakEvent.id).desc())
        )

        return {
            row.leak_type.value: row.count
            for row in result.all()
        }

    async def get_risk_level_distribution(self, db: AsyncSession) -> Dict:
        """
        Get risk level distribution

        Args:
            db: Database session

        Returns:
            Dictionary with risk level counts
        """
        result = await db.execute(
            select(
                RiskAssessment.risk_level,
                func.count(RiskAssessment.id).label('count')
            )
            .group_by(RiskAssessment.risk_level)
            .order_by(func.count(RiskAssessment.id).desc())
        )

        return {
            row.risk_level.value: row.count
            for row in result.all()
        }

    async def get_method_frequencies(self, db: AsyncSession, limit: int = 10) -> List[Dict]:
        """
        Get most frequently used RPC methods

        Args:
            db: Database session
            limit: Maximum number of methods to return

        Returns:
            List of method frequency dictionaries
        """
        result = await db.execute(
            select(
                NetworkTraffic.rpc_method,
                func.count(NetworkTraffic.id).label('count')
            )
            .where(NetworkTraffic.rpc_method.isnot(None))
            .group_by(NetworkTraffic.rpc_method)
            .order_by(func.count(NetworkTraffic.id).desc())
            .limit(limit)
        )

        return [
            {"method": row.rpc_method, "count": row.count}
            for row in result.all()
        ]

    async def get_top_risk_sessions(
        self, db: AsyncSession, limit: int = 10
    ) -> List[Dict]:
        """
        Get sessions with highest risk scores

        Args:
            db: Database session
            limit: Maximum number of sessions to return

        Returns:
            List of session risk dictionaries
        """
        result = await db.execute(
            select(
                RiskAssessment.session_id,
                Session.wallet_type,
                Session.rpc_provider,
                RiskAssessment.overall_score,
                RiskAssessment.risk_level,
                RiskAssessment.assessed_at
            )
            .join(Session, RiskAssessment.session_id == Session.id)
            .order_by(RiskAssessment.overall_score.desc())
            .limit(limit)
        )

        return [
            {
                "session_id": row.session_id,
                "wallet_type": row.wallet_type,
                "rpc_provider": row.rpc_provider,
                "overall_score": row.overall_score,
                "risk_level": row.risk_level.value,
                "assessed_at": row.assessed_at
            }
            for row in result.all()
        ]

    async def get_response_time_stats(self, db: AsyncSession) -> Dict:
        """
        Get RPC response time statistics

        Args:
            db: Database session

        Returns:
            Dictionary with response time statistics
        """
        result = await db.execute(
            select(
                func.avg(NetworkTraffic.response_time_ms).label('avg'),
                func.min(NetworkTraffic.response_time_ms).label('min'),
                func.max(NetworkTraffic.response_time_ms).label('max')
            )
            .where(NetworkTraffic.response_time_ms.isnot(None))
        )

        row = result.one_or_none()
        if not row:
            return {"avg": 0, "min": 0, "max": 0}

        return {
            "average_ms": round(float(row.avg), 2),
            "min_ms": row.min,
            "max_ms": row.max
        }
