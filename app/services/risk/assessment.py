"""
Risk assessment computation - 4-dimensional risk scoring
"""
from typing import Dict, List
from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy import select

from app.services.risk.metrics import (
    calculate_entropy, calculate_uniqueness,
    calculate_correlation, calculate_temporal
)
from app.services.risk.recommendations import get_recommendations, get_improvement_suggestions
from app.models import RiskAssessment, RiskLevel, NetworkTraffic, Session


def classify_risk_level(score: int) -> RiskLevel:
    """
    Classify risk level from overall score

    Args:
        score: Overall risk score (0-100)

    Returns:
        RiskLevel enum
    """
    if score <= 30:
        return RiskLevel.LOW
    elif score <= 50:
        return RiskLevel.MEDIUM
    elif score <= 70:
        return RiskLevel.HIGH
    else:
        return RiskLevel.CRITICAL


async def compute_risk_assessment(
    session_id: str,
    traffic_records: List[NetworkTraffic]
) -> RiskAssessment:
    """
    Compute 4-dimensional risk assessment for a session

    Args:
        session_id: Session UUID
        traffic_records: List of traffic records

    Returns:
        RiskAssessment model
    """
    # Extract method frequencies
    method_counts = {}
    for record in traffic_records:
        if record.rpc_method:
            method_counts[record.rpc_method] = method_counts.get(record.rpc_method, 0) + 1

    # 1. Calculate Entropy Score
    entropy_score = calculate_entropy(method_counts)

    # 2. Calculate Uniqueness Score
    # For now, assume no reference baseline - use default moderate value
    # In production, this would compare against historical baseline
    uniqueness_score = 0.5

    # 3. Calculate Correlation Score
    # For now, assume single address - no correlation
    # In production, this would check for multiple addresses with similar behavior
    method_sets = [set(method_counts.keys())]
    correlation_score = calculate_correlation(method_sets)

    # 4. Calculate Temporal Score
    timestamps = [r.request_timestamp for r in traffic_records if r.request_timestamp]
    temporal_score = calculate_temporal(timestamps)

    # Calculate overall score
    # Default weights: all 0.25
    w_entropy = 0.25
    w_uniqueness = 0.25
    w_correlation = 0.25
    w_temporal = 0.25

    overall_score = int((
        w_entropy * entropy_score +
        w_uniqueness * uniqueness_score +
        w_correlation * correlation_score +
        w_temporal * temporal_score
    ) * 100)

    # Classify risk level
    risk_level = classify_risk_level(overall_score)

    # Get recommendations
    scores = {
        "entropy": entropy_score,
        "uniqueness": uniqueness_score,
        "correlation": correlation_score,
        "temporal": temporal_score
    }
    recommendations = get_recommendations(scores, risk_level.value)

    # Calculate confidence interval (simplified)
    # In production, use bootstrap resampling for proper CI
    confidence = 0.85
    ci_low = max(0.0, confidence - 0.08)
    ci_high = min(1.0, confidence + 0.08)

    # Create assessment
    assessment = RiskAssessment(
        id=str(uuid4()),
        session_id=session_id,
        overall_score=overall_score,
        entropy_score=entropy_score,
        uniqueness_score=uniqueness_score,
        correlation_score=correlation_score,
        temporal_score=temporal_score,
        confidence=confidence,
        confidence_interval_low=ci_low,
        confidence_interval_high=ci_high,
        risk_level=risk_level,
        recommendations=recommendations,
        baseline_comparison={
            "overall_score": overall_score,
            "risk_level": risk_level.value,
            "ideal_score": 0,  # Best possible
            "worst_score": 100  # Worst possible
        },
        assessed_at=datetime.now(timezone.utc).isoformat()
    )

    return assessment


async def compute_comparative_assessment(
    session_ids: List[str],
    traffic_records_by_session: Dict[str, List[NetworkTraffic]]
) -> Dict[str, RiskAssessment]:
    """
    Compute risk assessments for multiple sessions with comparison

    Args:
        session_ids: List of session UUIDs
        traffic_records_by_session: Dict mapping session_id to traffic records

    Returns:
        Dictionary mapping session_id to RiskAssessment
    """
    assessments = {}

    # Compute all assessments
    for session_id in session_ids:
        records = traffic_records_by_session.get(session_id, [])
        assessment = await compute_risk_assessment(session_id, records)
        assessments[session_id] = assessment

    # Add comparative analysis
    scores = [a.overall_score for a in assessments.values()]
    if scores:
        avg_score = sum(scores) / len(scores)
        min_score = min(scores)
        max_score = max(scores)

        for assessment in assessments.values():
            assessment.baseline_comparison.update({
                "peer_average": avg_score,
                "peer_range": [min_score, max_score],
                "percentile": len([s for s in scores if s < assessment.overall_score]) / len(scores)
            })

    return assessments
