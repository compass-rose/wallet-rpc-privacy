"""
Recommendations generation based on risk scores
"""
from typing import List, Dict


RECOMMENDATION_TEMPLATES = {
    "low_entropy": [
        "Increase request method diversity to reduce predictability",
        "Explore multiple DApps to diversify behavioral profile",
        "Avoid repetitive request patterns that create predictable signatures"
    ],
    "high_correlation": [
        "Use address rotation: generate fresh addresses for new sessions",
        "Separate activities: use different addresses for different transaction types",
        "Avoid linking multiple addresses through common query patterns"
    ],
    "high_temporal": [
        "Add random timing jitter between requests to obfuscate patterns",
        "Batch requests to reduce timing granularity",
        "Use random delays between related operations"
    ],
    "high_uniqueness": [
        "Use common DApps and methods similar to typical users to blend in",
        "Maintain consistent usage patterns across sessions",
        "Avoid unique behavioral signatures that make you identifiable"
    ],
    "critical_risk": [
        "Review privacy settings and consider using privacy-focused RPC providers",
        "Implement RPC rotation or multi-provider setup",
        "Consider using privacy-enhancing tools like mixers or shields"
    ]
}


def get_recommendations(
    scores: Dict[str, float],
    risk_level: str
) -> List[str]:
    """
    Generate recommendations based on risk scores

    Args:
        scores: Dictionary with entropy, uniqueness, correlation, temporal scores
        risk_level: Risk level (low, medium, high, critical)

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Add risk-specific recommendations
    if risk_level == "critical":
        recommendations.extend(RECOMMENDATION_TEMPLATES["critical_risk"])

    # Add metric-specific recommendations
    if scores.get("entropy", 0) < 0.3:
        recommendations.extend(RECOMMENDATION_TEMPLATES["low_entropy"])

    if scores.get("correlation", 0) > 0.7:
        recommendations.extend(RECOMMENDATION_TEMPLATES["high_correlation"])

    if scores.get("temporal", 0) > 0.7:
        recommendations.extend(RECOMMENDATION_TEMPLATES["high_temporal"])

    if scores.get("uniqueness", 0) > 0.7:
        recommendations.extend(RECOMMENDATION_TEMPLATES["high_uniqueness"])

    # Ensure at least 3 recommendations
    while len(recommendations) < 3:
        recommendations.append("Review privacy settings and follow blockchain best practices")

    # Limit to max 5 recommendations
    return recommendations[:5]


def get_improvement_suggestions(score: int, scores: Dict[str, float]) -> Dict[str, str]:
    """
    Get specific improvement suggestions for each dimension

    Args:
        score: Overall risk score
        scores: Individual dimension scores

    Returns:
        Dictionary mapping dimension to improvement suggestion
    """
    suggestions = {}

    if scores.get("entropy", 0) < 0.3:
        suggestions["entropy"] = "Increase method diversity by using more DApps and RPC methods"

    if scores.get("uniqueness", 0) > 0.7:
        suggestions["uniqueness"] = "Reduce uniqueness by following typical user behavior patterns"

    if scores.get("correlation", 0) > 0.7:
        suggestions["correlation"] = "Reduce address correlation by using separate addresses for different activities"

    if scores.get("temporal", 0) > 0.7:
        suggestions["temporal"] = "Add random timing jitter to reduce time-based linkability"

    return suggestions
