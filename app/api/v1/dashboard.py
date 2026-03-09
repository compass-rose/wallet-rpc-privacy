from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.dashboard import DashboardService
from app.services.risk_service import RiskService
from app.services.risk import compare_with_baselines, generate_industry_comparison
from app.services.risk import simulate_distinguishing_attack
from app.services.risk.adversarial import evaluate_defense_effectiveness
from app.models.dashboard import TimeRange, ChartType
from app.models import Session, NetworkTraffic
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from typing import Dict, Any
import asyncio

router = APIRouter()


@router.get("/dashboard/monitor/status")
async def get_monitor_status(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    status = await service.get_monitor_status(db)

    return {
        "success": True,
        "data": status,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard/monitor/leaks/stream")
async def get_realtime_leak_stream(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    stream = await service.get_realtime_leak_stream(db, limit, offset)

    return {
        "success": True,
        "data": stream,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard/monitor/risk/metrics")
async def get_realtime_risk_metrics(
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    metrics = await service.get_realtime_risk_metrics(db)

    return {
        "success": True,
        "data": metrics,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard/reports/timeline")
async def get_timeline(
    time_range: TimeRange = Query(TimeRange.LAST_7D),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    timeline = await service.get_timeline(db, time_range)

    return {
        "success": True,
        "data": timeline,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard/reports/heatmap")
async def get_heatmap(
    heatmap_type: str = Query("timeofday", regex="^(timeofday|method_frequency|dayofweek)$"),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    heatmap = await service.get_heatmap(db, heatmap_type)

    return {
        "success": True,
        "data": heatmap,
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard/charts")
async def get_charts(
    time_range: TimeRange = Query(TimeRange.LAST_7D),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    charts = await service.get_charts(db, time_range)

    return {
        "success": True,
        "data": {
            "charts": charts
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard/charts/{chart_type}")
async def get_chart_by_type(
    chart_type: str,
    time_range: TimeRange = Query(TimeRange.LAST_7D),
    db: AsyncSession = Depends(get_db)
):
    service = DashboardService()
    chart = await service.get_chart_by_type(db, chart_type, time_range)

    if chart is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "CHART_NOT_FOUND",
                "message": f"No chart of type {chart_type} found"
            }
        )

    return {
        "success": True,
        "data": {
            "chart": chart
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.post("/dashboard/comprehensive-report")
async def generate_comprehensive_report(
    time_range: TimeRange = Query(TimeRange.LAST_24H),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate comprehensive security report with all tests (direct service calls, concurrent):
    - Basic assessment for each session
    - Baseline comparison
    - Simulated attack testing
    - Adversarial testing
    """
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
    sessions = list(result.scalars().all())
    
    if not sessions:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NO_SESSIONS_FOUND",
                "message": "No sessions found in the specified time range"
            }
        )
    
    results = {"sessions": []}
    risk_service = RiskService()
    
    async def get_session_with_traffic(session: Session) -> Dict[str, Any]:
        traffic_count_result = await db.execute(
            select(func.count(NetworkTraffic.id)).where(
                NetworkTraffic.session_id == session.id
            )
        )
        traffic_count = traffic_count_result.scalar_one() or 0
        
        return {
            "id": str(session.id),
            "wallet_type": session.wallet_type if session.wallet_type else "Unknown",
            "rpc_provider": session.rpc_provider if session.rpc_provider else "Unknown",
            "status": session.status if session.status else "Unknown",
            "start_time": session.start_time.isoformat() if hasattr(session.start_time, 'isoformat') else str(session.start_time) if session.start_time else None,
            "end_time": session.end_time.isoformat() if hasattr(session.end_time, 'isoformat') else str(session.end_time) if session.end_time else None,
            "traffic_count": traffic_count
        }
    
    async def run_assessment(session_id: str) -> Dict[str, Any]:
        try:
            result = await db.execute(
                select(NetworkTraffic).where(NetworkTraffic.session_id == session_id)
            )
            traffic_records = list(result.scalars().all())
            
            if not traffic_records:
                return {"session_id": session_id, "error": "No traffic records"}
            
            assessment = await risk_service.assess_session(session_id, traffic_records)
            
            return {
                "id": str(assessment.id) if hasattr(assessment, 'id') else None,
                "session_id": session_id,
                "overall_score": float(assessment.overall_score) if hasattr(assessment.overall_score, '__float__') else 0,
                "risk_level": str(assessment.risk_level),
                "entropy_score": float(assessment.entropy_score) if hasattr(assessment.entropy_score, '__float__') else 0,
                "uniqueness_score": float(assessment.uniqueness_score) if hasattr(assessment.uniqueness_score, '__float__') else 0,
                "correlation_score": float(assessment.correlation_score) if hasattr(assessment.correlation_score, '__float__') else 0,
                "temporal_score": float(assessment.temporal_score) if hasattr(assessment.temporal_score, '__float__') else 0,
                "confidence": float(assessment.confidence) if hasattr(assessment.confidence, '__float__') else 0,
                "baseline_comparison": dict(assessment.baseline_comparison) if assessment.baseline_comparison else None
            }
        except Exception as e:
            return {"session_id": session_id, "error": f"Assessment failed: {str(e)}"}
    
    session_infos = await asyncio.gather(*[get_session_with_traffic(s) for s in sessions])
    results["sessions"] = session_infos
    
    test_sessions = sessions[:3]
    
    assessment_tasks = [run_assessment(str(s.id)) for s in test_sessions]
    assessment_results = await asyncio.gather(*assessment_tasks)
    
    for session, result in zip(test_sessions, assessment_results):
        results[f"assessment_{session.id}"] = result
    
    if test_sessions:
        primary_session_id = str(test_sessions[0].id)
        
        baseline_task = None
        attack_task = None
        adversarial_task = None
        
        try:
            result = await db.execute(
                select(NetworkTraffic).where(NetworkTraffic.session_id == primary_session_id)
            )
            traffic_records = list(result.scalars().all())
            
            if traffic_records:
                assessment = await risk_service.get_latest_assessment(primary_session_id, db)
                
                if assessment:
                    actual_metrics = {
                        "entropy": assessment.entropy_score,
                        "uniqueness": assessment.uniqueness_score,
                        "correlation": assessment.correlation_score,
                        "temporal": assessment.temporal_score
                    }
                    
                    async def run_baseline_comparison():
                        baseline_result = compare_with_baselines(actual_metrics, len(traffic_records))
                        industry_result = generate_industry_comparison(actual_metrics)
                        return {
                            "baseline_comparison": baseline_result,
                            "industry_comparison": industry_result
                        }
                    
                    baseline_task = asyncio.create_task(run_baseline_comparison())
        except Exception:
            pass
        
        try:
            result = await db.execute(select(NetworkTraffic))
            all_traffic = result.scalars().all()
            
            if len(all_traffic) >= 2:
                async def run_simulate_attack():
                    traffic_by_session = {}
                    for record in all_traffic:
                        if record.session_id not in traffic_by_session:
                            traffic_by_session[record.session_id] = []
                        traffic_by_session[record.session_id].append(record)
                    return simulate_distinguishing_attack(traffic_by_session)
                
                attack_task = asyncio.create_task(run_simulate_attack())
                
                async def run_adversarial_test():
                    traffic_by_session = {}
                    for record in all_traffic:
                        if record.session_id not in traffic_by_session:
                            traffic_by_session[record.session_id] = []
                        traffic_by_session[record.session_id].append(record)
                    return evaluate_defense_effectiveness(traffic_by_session)
                
                adversarial_task = asyncio.create_task(run_adversarial_test())
        except Exception:
            pass
        
        results_to_await = []
        if baseline_task:
            results_to_await.append(("baseline", baseline_task))
        if attack_task:
            results_to_await.append(("attack", attack_task))
        if adversarial_task:
            results_to_await.append(("adversarial", adversarial_task))
        
        for key, task in results_to_await:
            try:
                results[key] = await task
            except Exception:
                pass
    
    return {
        "success": True,
        "data": {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "time_range": time_range.value,
                "num_sessions_tested": len(test_sessions),
                "total_sessions": len(sessions)
            },
            "results": results
        },
        "metadata": {
            "request_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
