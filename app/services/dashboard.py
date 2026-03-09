from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from app.models import Session, NetworkTraffic, PrivacyLeakEvent, RiskAssessment, SessionStatus
from app.models.dashboard import (
    ChartType,
    TimeRange,
    MonitorStatus,
    RealtimeLeakStream,
    RealtimeRiskMetrics,
    TimelineEvent,
    TimelineResponse,
    HeatmapCell,
    HeatmapResponse,
    SeriesData,
    ChartData,
    StatisticsSummary
)
from sqlalchemy.sql import text


class DashboardService:
    async def get_monitor_status(self, db: AsyncSession) -> Dict:
        result = await db.execute(
            select(func.count()).select_from(Session).where(Session.status == SessionStatus.ACTIVE)
        )
        active_count = result.scalar_one() or 0

        result = await db.execute(select(func.count()).select_from(Session))
        total_sessions = result.scalar_one() or 0

        capturing = active_count > 0

        now = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.count(NetworkTraffic.id)).select_from(
                NetworkTraffic
            ).join(
                Session, NetworkTraffic.session_id == Session.id
            ).where(
                Session.start_time >= now
            )
        )
        today_packets = result.scalar_one() or 0

        result = await db.execute(
            select(func.count(PrivacyLeakEvent.id)).select_from(
                PrivacyLeakEvent
            ).join(
                Session, PrivacyLeakEvent.session_id == Session.id
            ).where(
                Session.start_time >= now
            )
        )
        today_leaks = result.scalar_one() or 0

        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        result = await db.execute(
            select(func.count(NetworkTraffic.id)).where(
                NetworkTraffic.created_at >= one_minute_ago
            )
        )
        recent_packets = result.scalar_one() or 0
        capture_rate = float(recent_packets)

        result = await db.execute(
            select(NetworkTraffic.created_at).order_by(
                NetworkTraffic.created_at.desc()
            ).limit(1)
        )
        last_capture = result.scalar_one_or_none()
        last_capture_time = last_capture.isoformat() if last_capture else None

        return {
            "active_sessions": active_count,
            "total_sessions": total_sessions,
            "capturing": capturing,
            "today_packets": today_packets,
            "today_leaks": today_leaks,
            "capture_rate": capture_rate,
            "last_capture_time": last_capture_time
        }

    async def get_realtime_leak_stream(
        self, db: AsyncSession, limit: int = 20, offset: int = 0
    ) -> Dict:
        result = await db.execute(
            select(
                PrivacyLeakEvent.id,
                PrivacyLeakEvent.session_id,
                PrivacyLeakEvent.leak_type,
                PrivacyLeakEvent.method_name,
                PrivacyLeakEvent.description,
                PrivacyLeakEvent.confidence,
                PrivacyLeakEvent.timestamp,
                PrivacyLeakEvent.created_at
            )
            .order_by(PrivacyLeakEvent.created_at.desc())
            .limit(limit + 1)
            .offset(offset)
        )

        rows = result.all()
        has_more = len(rows) > limit
        events_data = rows[:limit] if has_more else rows

        events = [
            {
                "id": row.id,
                "session_id": row.session_id,
                "leak_type": row.leak_type.value if row.leak_type else None,
                "method_name": row.method_name,
                "description": row.description,
                "confidence": row.confidence,
                "timestamp": row.timestamp.isoformat() if row.timestamp else None,
                "created_at": row.created_at.isoformat() if row.created_at else None
            }
            for row in events_data
        ]

        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        result = await db.execute(
            select(func.count(PrivacyLeakEvent.id)).where(
                PrivacyLeakEvent.created_at >= five_minutes_ago
            )
        )
        recent_leaks = result.scalar_one() or 0
        leak_rate = float(recent_leaks) / 5.0

        return {
            "events": events,
            "stream_position": f"{offset + len(events)}",
            "has_more": has_more,
            "leak_rate": leak_rate
        }

    async def get_realtime_risk_metrics(self, db: AsyncSession) -> Dict:
        result = await db.execute(
            select(func.avg(RiskAssessment.overall_score)).where(
                RiskAssessment.assessed_at >= datetime.now(timezone.utc) - timedelta(hours=1)
            )
        )
        avg_score = result.scalar_one() or 50.0

        if avg_score >= 80:
            current_risk_level = "critical"
        elif avg_score >= 60:
            current_risk_level = "high"
        elif avg_score >= 40:
            current_risk_level = "medium"
        else:
            current_risk_level = "low"

        result = await db.execute(
            select(func.count(RiskAssessment.id)).where(
                and_(
                    RiskAssessment.assessed_at >= datetime.now(timezone.utc) - timedelta(hours=24),
                    RiskAssessment.risk_level.in_(["high", "critical"])
                )
            )
        )
        high_risk_sessions = result.scalar_one() or 0

        result = await db.execute(
            select(
                func.date(RiskAssessment.assessed_at).label('date'),
                func.avg(RiskAssessment.overall_score).label('avg_score')
            )
            .where(
                RiskAssessment.assessed_at >= datetime.now(timezone.utc) - timedelta(days=1)
            )
            .group_by(func.date(RiskAssessment.assessed_at))
            .order_by(func.date(RiskAssessment.assessed_at))
        )
        daily_scores = [row.avg_score for row in result.all()]
        
        if len(daily_scores) >= 2:
            if daily_scores[-1] > daily_scores[-2]:
                risk_trend = "increasing"
            elif daily_scores[-1] < daily_scores[-2]:
                risk_trend = "decreasing"
            else:
                risk_trend = "stable"
        else:
            risk_trend = "stable"

        result = await db.execute(
            select(func.avg(RiskAssessment.confidence)).where(
                RiskAssessment.assessed_at >= datetime.now(timezone.utc) - timedelta(hours=24)
            )
        )
        confidence = result.scalar_one() or 0.5

        return {
            "current_risk_level": current_risk_level,
            "average_risk_score": round(float(avg_score), 2),
            "high_risk_sessions": high_risk_sessions,
            "risk_trend": risk_trend,
            "confidence": round(float(confidence), 2),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

    async def get_timeline(
        self, db: AsyncSession, time_range: TimeRange = TimeRange.LAST_7D
    ) -> Dict:
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

        leak_events = []
        try:
            result = await db.execute(
                select(PrivacyLeakEvent).where(
                    PrivacyLeakEvent.created_at >= cutoff
                )
            )
            for event in result.scalars().all():
                ts = event.created_at if event.created_at else event.timestamp
                ts_iso_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
                leak_events.append(TimelineEvent(
                    timestamp=ts_iso_str,
                    event_type="leak",
                    leak_type=event.leak_type.value if event.leak_type else None,
                    description=str(event.description) if event.description else "",
                    session_id=str(event.session_id) if event.session_id else None
                ).model_dump())
        except Exception:
            pass

        risk_events = []
        try:
            result = await db.execute(
                select(RiskAssessment).where(RiskAssessment.assessed_at >= cutoff)
            )
            for assessment in result.scalars().all():
                ts = assessment.assessed_at
                ts_iso_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
                risk_events.append(TimelineEvent(
                    timestamp=ts_iso_str,
                    event_type="risk",
                    risk_score=int(assessment.overall_score) if assessment.overall_score is not None else None,
                    description=f"Risk assessment: {assessment.risk_level.value}",
                    session_id=str(assessment.session_id) if assessment.session_id else None
                ).model_dump())
        except Exception:
            pass

        session_events = []
        try:
            result = await db.execute(
                select(Session).where(Session.start_time >= cutoff)
            )
            for session in result.scalars().all():
                ts = session.start_time
                ts_iso_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
                session_events.append(TimelineEvent(
                    timestamp=ts_iso_str,
                    event_type="session",
                    description=f"Session: {session.wallet_type}",
                    session_id=str(session.id) if session.id else None
                ).model_dump())
        except Exception:
            pass

        all_events = leak_events + risk_events + session_events
        all_events.sort(key=lambda x: x["timestamp"])

        leak_distribution = {}
        try:
            result = await db.execute(
                select(
                    PrivacyLeakEvent.leak_type,
                    func.count(PrivacyLeakEvent.id).label('count')
                )
                .where(
                    PrivacyLeakEvent.created_at >= cutoff
                )
                .group_by(PrivacyLeakEvent.leak_type)
            )
            leak_distribution = {
                row.leak_type.value if row.leak_type else "unknown": row.count
                for row in result.all()
            }
        except Exception:
            pass

        return {
            "events": all_events,
            "time_range": f"{cutoff.date()} to {now.date()}",
            "total_events": len(all_events),
            "leak_distribution": leak_distribution
        }

    async def get_heatmap(
        self, db: AsyncSession, heatmap_type: str = "timeofday"
    ) -> Dict:
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        if heatmap_type == "timeofday":
            try:
                result = await db.execute(
                    select(NetworkTraffic.created_at).where(
                        NetworkTraffic.created_at >= seven_days_ago
                    )
                )
                timestamps = [row[0] for row in result.all() if row[0]]

                row_labels = list(range(24))
                col_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                cells = []
                counts = {(hour, day): 0 for hour in row_labels for day in range(7)}

                for ts in timestamps:
                    if hasattr(ts, 'hour'):
                        hour = ts.hour
                        day = ts.weekday()
                        counts[(hour, day)] += 1

                for hour in row_labels:
                    for day_idx, day_of_week in enumerate(col_labels):
                        cells.append({
                            "row_label": str(hour),
                            "col_label": day_of_week,
                            "value": float(counts[(hour, day_idx)]),
                            "count": counts[(hour, day_idx)]
                        })

                values = [cell["value"] for cell in cells]
                return {
                    "heatmap_type": heatmap_type,
                    "row_labels": [str(l) for l in row_labels],
                    "col_labels": col_labels,
                    "cells": cells,
                    "max_value": max(values) if values else 0.0,
                    "min_value": min(values) if values else 0.0
                }
            except Exception:
                return {
                    "heatmap_type": heatmap_type,
                    "row_labels": [],
                    "col_labels": [],
                    "cells": [],
                    "max_value": 0.0,
                    "min_value": 0.0
                }

        elif heatmap_type == "method_frequency":
            try:
                result = await db.execute(
                    select(
                        Session.wallet_type.label('wallet'),
                        NetworkTraffic.rpc_method.label('method')
                    )
                    .join(NetworkTraffic, Session.id == NetworkTraffic.session_id)
                    .where(
                        and_(
                            Session.start_time >= seven_days_ago,
                            NetworkTraffic.rpc_method.isnot(None)
                        )
                    )
                )
                rows = result.all()

                wallets = list(set(row.wallet for row in rows if row.wallet))[:10]
                methods = list(set(row.method for row in rows if row.method))[:10]

                row_labels = wallets if wallets else ["unknown"]
                col_labels = methods if methods else ["unknown"]
                cells = []

                for wallet in row_labels:
                    for method in col_labels:
                        result = await db.execute(
                            select(func.count(NetworkTraffic.id))
                            .join(Session, Session.id == NetworkTraffic.session_id)
                            .where(
                                and_(
                                    Session.wallet_type == wallet,
                                    NetworkTraffic.rpc_method == method,
                                    NetworkTraffic.created_at >= seven_days_ago
                                )
                            )
                        )
                        count = result.scalar_one() or 0
                        cells.append({
                            "row_label": wallet,
                            "col_label": method,
                            "value": float(count),
                            "count": count
                        })

                values = [cell["value"] for cell in cells]
                return {
                    "heatmap_type": heatmap_type,
                    "row_labels": row_labels,
                    "col_labels": col_labels,
                    "cells": cells,
                    "max_value": max(values) if values else 0.0,
                    "min_value": min(values) if values else 0.0
                }
            except Exception:
                return {
                    "heatmap_type": heatmap_type,
                    "row_labels": [],
                    "col_labels": [],
                    "cells": [],
                    "max_value": 0.0,
                    "min_value": 0.0
                }

        elif heatmap_type == "dayofweek":
            try:
                result = await db.execute(
                    select(PrivacyLeakEvent.created_at).where(
                        PrivacyLeakEvent.created_at >= seven_days_ago
                    )
                )
                timestamps = [row[0] for row in result.all() if row[0]]

                row_labels = [f"{i:02d}:00" for i in range(24)]
                col_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                cells = []
                counts = {(hour, day): 0 for hour in range(24) for day in range(7)}

                for ts in timestamps:
                    if hasattr(ts, 'hour'):
                        hour = ts.hour
                        day = ts.weekday()
                        counts[(hour, day)] += 1

                for hour in range(24):
                    for day_idx in range(7):
                        cells.append({
                            "row_label": row_labels[hour],
                            "col_label": col_labels[day_idx],
                            "value": float(counts[(hour, day_idx)]),
                            "count": counts[(hour, day_idx)]
                        })

                values = [cell["value"] for cell in cells]
                return {
                    "heatmap_type": heatmap_type,
                    "row_labels": row_labels,
                    "col_labels": col_labels,
                    "cells": cells,
                    "max_value": max(values) if values else 0.0,
                    "min_value": min(values) if values else 0.0
                }
            except Exception:
                return {
                    "heatmap_type": heatmap_type,
                    "row_labels": [],
                    "col_labels": [],
                    "cells": [],
                    "max_value": 0.0,
                    "min_value": 0.0
                }
        else:
            return {
                "heatmap_type": heatmap_type,
                "row_labels": [],
                "col_labels": [],
                "cells": [],
                "max_value": 0.0,
                "min_value": 0.0
            }

        values = [cell["value"] for cell in cells]
        max_value = max(values) if values else 0.0
        min_value = min(values) if values else 0.0

        return {
            "heatmap_type": heatmap_type,
            "row_labels": row_labels,
            "col_labels": col_labels,
            "cells": cells,
            "max_value": max_value,
            "min_value": min_value
        }

    async def get_charts(self, db: AsyncSession, time_range: TimeRange = TimeRange.LAST_7D) -> List[Dict]:
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
            cutoff = datetime.min

        result = await db.execute(
            select(
                func.date(PrivacyLeakEvent.timestamp).label('date'),
                PrivacyLeakEvent.leak_type,
                func.count(PrivacyLeakEvent.id).label('count')
            )
            .where(PrivacyLeakEvent.timestamp >= cutoff)
            .group_by(func.date(PrivacyLeakEvent.timestamp), PrivacyLeakEvent.leak_type)
            .order_by(func.date(PrivacyLeakEvent.timestamp))
        )
        leak_data = result.all()

        leak_types = list(set(row.leak_type.value for row in leak_data if row.leak_type))
        series = []
        for leak_type in leak_types:
            data_points = [
                {"x": str(row.date), "y": row.count}
                for row in leak_data
                if row.leak_type and row.leak_type.value == leak_type
            ]
            series.append({
                "label": leak_type,
                "data_points": data_points
            })

        timeline_chart = {
            "chart_type": ChartType.TIMELINE.value,
            "title": "Privacy Leak Events Over Time",
            "x_axis_label": "Date",
            "y_axis_label": "Count",
            "series": series,
            "metadata": {}
        }

        result = await db.execute(
            select(
                RiskAssessment.risk_level,
                func.count(RiskAssessment.id).label('count')
            )
            .where(RiskAssessment.assessed_at >= cutoff)
            .group_by(RiskAssessment.risk_level)
        )
        risk_data = result.all()

        risk_series = [{
            "label": "Risk Distribution",
            "data_points": [
                {"x": row.risk_level.value, "y": row.count}
                for row in risk_data
            ]
        }]

        pie_chart = {
            "chart_type": ChartType.PIE.value,
            "title": "Risk Level Distribution",
            "series": risk_series,
            "metadata": {}
        }

        result = await db.execute(
            select(
                func.date(NetworkTraffic.created_at).label('date'),
                func.count(NetworkTraffic.id).label('count')
            )
            .where(NetworkTraffic.created_at >= cutoff)
            .group_by(func.date(NetworkTraffic.created_at))
            .order_by(func.date(NetworkTraffic.created_at))
        )
        traffic_data = result.all()

        traffic_series = [{
            "label": "Network Traffic",
            "data_points": [
                {"x": str(row.date), "y": row.count}
                for row in traffic_data
            ]
        }]

        bar_chart = {
            "chart_type": ChartType.BAR.value,
            "title": "Network Traffic Volume",
            "x_axis_label": "Date",
            "y_axis_label": "Request Count",
            "series": traffic_series,
            "metadata": {}
        }

        result = await db.execute(
            select(
                func.avg(NetworkTraffic.response_time_ms).label('avg_time'),
                func.date(NetworkTraffic.created_at).label('date')
            )
            .where(
                and_(
                    NetworkTraffic.created_at >= cutoff,
                    NetworkTraffic.response_time_ms.isnot(None)
                )
            )
            .group_by(func.date(NetworkTraffic.created_at))
            .order_by(func.date(NetworkTraffic.created_at))
        )
        latency_data = result.all()

        latency_series = [{
            "label": "Average Response Time",
            "data_points": [
                {"x": str(row.date), "y": float(row.avg_time)}
                for row in latency_data
                if row.avg_time
            ]
        }]

        line_chart = {
            "chart_type": ChartType.LINE.value,
            "title": "RPC Response Time Latency",
            "x_axis_label": "Date",
            "y_axis_label": "Latency (ms)",
            "series": latency_series,
            "metadata": {}
        }

        return [timeline_chart, pie_chart, bar_chart, line_chart]

    async def get_statistics_summary(self, db: AsyncSession, time_range: TimeRange = TimeRange.LAST_7D) -> Dict:
        monitor_status = await self.get_monitor_status(db)
        realtime_risk = await self.get_realtime_risk_metrics(db)
        charts = await self.get_charts(db, time_range)

        from app.services.analytics import AnalyticsService
        analytics_service = AnalyticsService()

        overall = await analytics_service.get_summary_stats(db)
        leak_dist = await analytics_service.get_leak_distribution(db)
        risk_dist = await analytics_service.get_risk_level_distribution(db)

        return {
            "overall_stats": {**overall, **monitor_status},
            "leak_statistics": leak_dist,
            "risk_statistics": {**risk_dist, **realtime_risk},
            "traffic_statistics": {
                "total_requests": overall.get("total_traffic", 0),
                "capture_rate": monitor_status.get("capture_rate", 0.0)
            },
            "top_charts": charts
        }
