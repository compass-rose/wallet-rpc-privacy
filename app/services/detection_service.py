"""
Detection service - high-level interface
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.detection.engine import RuleEngine
from app.services.detection.loader import RuleLoader, DetectionRule
from app.models import NetworkTraffic, PrivacyLeakEvent


class DetectionService:
    """Service for privacy leak detection"""

    def __init__(self, rules_dir: str = "app/config/rules"):
        self.engine = RuleEngine(rules_dir)

    async def run_detection(
        self, session_id: str, traffic_records: list[NetworkTraffic]
    ) -> list[PrivacyLeakEvent]:
        """
        Run detection rules on session traffic

        Args:
            session_id: Session UUID
            traffic_records: List of traffic records

        Returns:
            List of detected privacy leak events
        """
        return await self.engine.evaluate_session(session_id, traffic_records)

    async def store_events(
        self, events: list[PrivacyLeakEvent], db: AsyncSession
    ) -> int:
        """
        Store detection events in database

        Args:
            events: List of events to store
            db: Database session

        Returns:
            Number of events stored
        """
        count = 0
        for event in events:
            db.add(event)
            count += 1

        await db.commit()
        return count

    def get_rules(self) -> list:
        """Get all detection rules"""
        return self.engine.get_all_rules()

    def get_rules_summary(self) -> dict:
        """Get rules summary statistics"""
        return self.engine.get_rules_summary()
