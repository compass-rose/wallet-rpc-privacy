from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from app.models import Session, NetworkTraffic, PrivacyLeakEvent, RiskAssessment
from app.models.dashboard import TimeRange
from pathlib import Path
import os


class ReportService:
    """Overall report generation service"""

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    async def get_sessions_by_time_range(
        self, db: AsyncSession, time_range: TimeRange
    ) -> List[Session]:
        """Get sessions by time range"""
        now = datetime.now(timezone.utc)

        if time_range == TimeRange.LAST_HOUR:
            cutoff = now - timedelta(hours=1)
        elif time_range == TimeRange.LAST_24H:
            cutoff = now - timedelta(hours=24)
        elif time_range == TimeRange.LAST_7D:
            cutoff = now - timedelta(days=7)
        elif time_range == TimeRange.LAST_30D:
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(days=365)

        result = await db.execute(
            select(Session).where(Session.start_time >= cutoff)
        )
        return list(result.scalars().all())

    async def get_session_traffic_count(
        self, db: AsyncSession, session_id: str
    ) -> int:
        """Get traffic count for a session"""
        result = await db.execute(
            select(func.count(NetworkTraffic.id)).where(
                NetworkTraffic.session_id == session_id
            )
        )
        return result.scalar_one() or 0

    async def get_session_leaks(
        self, db: AsyncSession, session_id: str
    ) -> List[PrivacyLeakEvent]:
        """Get privacy leak events for a session"""
        result = await db.execute(
            select(PrivacyLeakEvent).where(
                PrivacyLeakEvent.session_id == session_id
            )
        )
        return list(result.scalars().all())

    async def get_session_assessment(
        self, db: AsyncSession, session_id: str
    ) -> Optional[RiskAssessment]:
        """Get risk assessment for a session"""
        result = await db.execute(
            select(RiskAssessment).where(
                RiskAssessment.session_id == session_id
            ).order_by(RiskAssessment.assessed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def generate_overall_report(
        self,
        db: AsyncSession,
        time_range: TimeRange = TimeRange.LAST_24H,
        include_raw_data: bool = False
    ) -> Dict[str, Any]:
        """Generate overall report content"""
        now = datetime.now(timezone.utc)

        if time_range == TimeRange.LAST_24H:
            time_label = "Last 24 Hours"
        elif time_range == TimeRange.LAST_7D:
            time_label = "Last 7 Days"
        else:
            time_label = time_range.value.replace("_", " ").title()

        # 获取指定时间范围的sessions
        sessions = await self.get_sessions_by_time_range(db, time_range)

        session_details = []
        total_traffic = 0
        total_leaks = 0
        assessment_summary = {
            "total": 0,
            "high_risk": 0,
            "medium_risk": 0,
            "low_risk": 0,
            "avg_score": 0.0,
            "avg_entropy": 0.0,
            "avg_uniqueness": 0.0,
            "avg_correlation": 0.0,
            "avg_temporal": 0.0
        }

        # 收集每个session的详细信息
        for session in sessions:
            traffic_count = await self.get_session_traffic_count(db, session.id)
            leaks = await self.get_session_leaks(db, session.id)
            assessment = await self.get_session_assessment(db, session.id)

            total_traffic += traffic_count
            total_leaks += len(leaks)

            session_info = {
                "id": session.id,
                "wallet_type": session.wallet_type,
                "rpc_provider": session.rpc_provider,
                "start_time": session.start_time.isoformat() if hasattr(session.start_time, 'isoformat') else str(session.start_time) if session.start_time else None,
                "end_time": session.end_time.isoformat() if hasattr(session.end_time, 'isoformat') else str(session.end_time) if session.end_time else None,
                "duration_seconds": session.duration_seconds,
                "packet_count": session.packet_count,
                "traffic_count": traffic_count,
                "leak_count": len(leaks),
                "status": session.status.value if session.status else None
            }

            if assessment:
                assessment_summary["total"] += 1
                session_info["risk_assessment"] = {
                    "overall_score": assessment.overall_score,
                    "risk_level": assessment.risk_level.value if assessment.risk_level else None,
                    "entropy_score": assessment.entropy_score,
                    "uniqueness_score": assessment.uniqueness_score,
                    "correlation_score": assessment.correlation_score,
                    "temporal_score": assessment.temporal_score,
                    "confidence": assessment.confidence,
                    "assessed_at": assessment.assessed_at.isoformat() if assessment.assessed_at else None
                }

                if assessment.risk_level:
                    level = assessment.risk_level.value
                    if level == "high" or level == "critical":
                        assessment_summary["high_risk"] += 1
                    elif level == "medium":
                        assessment_summary["medium_risk"] += 1
                    else:
                        assessment_summary["low_risk"] += 1

                assessment_summary["avg_score"] = (
                    (assessment_summary["avg_score"] * (assessment_summary["total"] - 1) + assessment.overall_score) /
                    assessment_summary["total"]
                )
                assessment_summary["avg_entropy"] = (
                    (assessment_summary["avg_entropy"] * (assessment_summary["total"] - 1) + assessment.entropy_score) /
                    assessment_summary["total"]
                )
                assessment_summary["avg_uniqueness"] = (
                    (assessment_summary["avg_uniqueness"] * (assessment_summary["total"] - 1) + assessment.uniqueness_score) /
                    assessment_summary["total"]
                )
                assessment_summary["avg_correlation"] = (
                    (assessment_summary["avg_correlation"] * (assessment_summary["total"] - 1) + assessment.correlation_score) /
                    assessment_summary["total"]
                )
                assessment_summary["avg_temporal"] = (
                    (assessment_summary["avg_temporal"] * (assessment_summary["total"] - 1) + assessment.temporal_score) /
                    assessment_summary["total"]
                )

            session_details.append(session_info)

        # 汇总统计
        summary = {
            "time_range": time_range.value,
            "time_label": time_label,
            "generated_at": now.isoformat(),
            "total_sessions": len(sessions),
            "total_traffic": total_traffic,
            "total_leaks": total_leaks,
            "avg_traffic_per_session": round(total_traffic / len(sessions), 2) if sessions else 0.0,
            "avg_leaks_per_session": round(total_leaks / len(sessions), 2) if sessions else 0.0,
            "assessment_summary": assessment_summary
        }

        return {
            "summary": summary,
            "sessions": session_details,
            "include_raw_data": include_raw_data
        }

    def save_report_to_file(
        self,
        report_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """Save report to text file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            time_label = report_data["summary"]["time_label"]
            filename = f"privacy_report_{time_label}_{timestamp}.txt"

        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            summary = report_data["summary"]
            sessions = report_data["sessions"]

            f.write("=" * 80 + "\n")
            f.write("Wallet RPC Privacy Leakage Measurement System - Overall Analysis Report\n")
            f.write("=" * 80 + "\n\n")

            f.write(f"Report Generated: {summary['generated_at']}\n")
            f.write(f"Statistical Time Range: {summary['time_label']}\n\n")

            f.write("=" * 80 + "\n")
            f.write("Overall Statistics\n")
            f.write("=" * 80 + "\n")
            f.write(f"Total Sessions: {summary['total_sessions']}\n")
            f.write(f"Total Traffic Data: {summary['total_traffic']} records\n")
            f.write(f"Total Privacy Leaks: {summary['total_leaks']} records\n")
            f.write(f"Average Traffic per Session: {summary['avg_traffic_per_session']:.2f} records\n")
            f.write(f"Average Leaks per Session: {summary['avg_leaks_per_session']:.2f} records\n\n")

            f.write("=" * 80 + "\n")
            f.write("Risk Assessment Summary\n")
            f.write("=" * 80 + "\n")
            assess = summary["assessment_summary"]
            f.write(f"Assessed Sessions: {assess['total']}\n")
            f.write(f"High Risk: {assess['high_risk']}\n")
            f.write(f"Medium Risk: {assess['medium_risk']}\n")
            f.write(f"Low Risk: {assess['low_risk']}\n\n")

            if assess['total'] > 0:
                f.write("Average Metrics:\n")
                f.write(f"  Overall Score: {assess['avg_score']:.2f}/100\n")
                f.write(f"  Information Entropy: {assess['avg_entropy']:.3f}\n")
                f.write(f"  Uniqueness: {assess['avg_uniqueness']:.3f}\n")
                f.write(f"  Correlation: {assess['avg_correlation']:.3f}\n")
                f.write(f"  Temporal: {assess['avg_temporal']:.3f}\n\n")

            f.write("=" * 80 + "\n")
            f.write("Session Details\n")
            f.write("=" * 80 + "\n\n")

            for i, session in enumerate(sessions, 1):
                f.write(f"Session {i}: {session['id']}\n")
                f.write(f"  Wallet Type: {session['wallet_type']}\n")
                f.write(f"  RPC Provider: {session['rpc_provider']}\n")
                f.write(f"  Start Time: {session['start_time']}\n")
                f.write(f"  End Time: {session['end_time']}\n")
                f.write(f"  Duration: {session['duration_seconds']} seconds\n")
                f.write(f"  Captured Packets: {session['packet_count']}\n")
                f.write(f"  Traffic Data: {session['traffic_count']} records\n")
                f.write(f"  Privacy Leaks: {session['leak_count']} records\n")
                f.write(f"  Status: {session['status']}\n")

                if "risk_assessment" in session:
                    risk = session["risk_assessment"]
                    f.write(f"\n  Risk Assessment:\n")
                    f.write(f"    Overall Score: {risk['overall_score']}/100\n")
                    f.write(f"    Risk Level: {risk['risk_level']}\n")
                    f.write(f"    Information Entropy: {risk['entropy_score']:.3f}\n")
                    f.write(f"    Uniqueness: {risk['uniqueness_score']:.3f}\n")
                    f.write(f"    Correlation: {risk['correlation_score']:.3f}\n")
                    f.write(f"    Temporal: {risk['temporal_score']:.3f}\n")
                    f.write(f"    Confidence: {risk['confidence']:.3f}\n")

                f.write("\n" + "-" * 80 + "\n\n")

            f.write("=" * 80 + "\n")
            f.write("End of Report\n")
            f.write("=" * 80 + "\n")

        return str(filepath.absolute())

    async def generate_and_save_report(
        self,
        db: AsyncSession,
        time_range: TimeRange = TimeRange.LAST_24H,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate and save overall report"""
        report_data = await self.generate_overall_report(db, time_range)
        filepath = self.save_report_to_file(report_data, filename)

        return {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "report_data": report_data
        }
