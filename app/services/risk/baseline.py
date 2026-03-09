"""
Risk assessment baseline comparison - random and ideal pattern comparison
"""
import random
import math
from typing import Dict, List, Tuple
from datetime import datetime, timedelta


def generate_random_baseline(num_requests: int, available_methods: List[str]) -> Dict[str, float]:
    """
    Generate random baseline metrics for comparison

    Args:
        num_requests: Number of requests to simulate
        available_methods: List of available RPC methods

    Returns:
        Dictionary with random metrics (entropy, uniqueness, correlation, temporal)
    """
    # Random method distribution
    method_counts = {}
    for _ in range(num_requests):
        method = random.choice(available_methods)
        method_counts[method] = method_counts.get(method, 0) + 1

    # Calculate entropy
    entropy = _calculate_entropy_score(method_counts)

    # Random timestamps with uniform distribution (low temporal variance)
    base_time = datetime.utcnow()
    timestamps = [
        base_time + timedelta(seconds=i * (60 + random.uniform(-5, 5)))
        for i in range(num_requests)
    ]

    return {
        "entropy": entropy,
        "uniqueness": 0.6,  # Random baseline has moderate uniqueness
        "correlation": 0.3,  # Low correlation for random patterns
        "temporal": 0.4,     # Low temporal variance
        "method_counts": method_counts,
        "num_requests": num_requests
    }


def generate_ideal_baseline(num_requests: int, available_methods: List[str]) -> Dict[str, float]:
    """
    Generate ideal privacy-preserving baseline metrics

    Ideal characteristics:
    - High entropy (diverse method usage)
    - High uniqueness (distinguishable from others)
    - Low correlation (no predictable patterns)
    - Low temporal variance (unpredictable timing)

    Args:
        num_requests: Number of requests to simulate
        available_methods: List of available RPC methods

    Returns:
        Dictionary with ideal metrics
    """
    # Even distribution across all methods (maximum entropy)
    requests_per_method = num_requests // len(available_methods)
    method_counts = {method: requests_per_method for method in available_methods}

    # Add remaining requests randomly
    remaining = num_requests % len(available_methods)
    for i in range(remaining):
        method_counts[available_methods[i]] += 1

    # Calculate entropy
    entropy = _calculate_entropy_score(method_counts)

    # Random timestamps with high variance (jittered)
    base_time = datetime.utcnow()
    timestamps = []
    for i in range(num_requests):
        # Random intervals with exponential distribution
        interval = random.expovariate(1/60)  # Mean 60 seconds
        base_time += timedelta(seconds=interval + random.uniform(-30, 30))
        timestamps.append(base_time)

    return {
        "entropy": entropy,
        "uniqueness": 0.9,  # High uniqueness
        "correlation": 0.1,  # Very low correlation
        "temporal": 0.3,     # Low temporal variance
        "method_counts": method_counts,
        "num_requests": num_requests
    }


def compare_with_baselines(
    actual_metrics: Dict[str, float],
    num_requests: int = 100,
    available_methods: List[str] = None
) -> Dict:
    """
    Compare actual session metrics with random and ideal baselines

    Args:
        actual_metrics: Actual session metrics from traffic analysis
        num_requests: Number of requests in session
        available_methods: Available RPC methods (default common eth methods)

    Returns:
        Dictionary with comparison results
    """
    if available_methods is None:
        available_methods = [
            "eth_call", "eth_getBalance", "eth_getBlockNumber",
            "eth_getTransactionCount", "eth_getBlockByNumber",
            "eth_chainId", "eth_estimateGas", "eth_gasPrice"
        ]

    # Generate baselines
    random_baseline = generate_random_baseline(num_requests, available_methods)
    ideal_baseline = generate_ideal_baseline(num_requests, available_methods)

    # Compare each metric
    comparison = {
        "actual": actual_metrics,
        "random_baseline": random_baseline,
        "ideal_baseline": ideal_baseline,
        "comparison": {}
    }

    metrics = ["entropy", "uniqueness", "correlation", "temporal"]

    for metric in metrics:
        actual = actual_metrics.get(metric, 0)
        random = random_baseline.get(metric, 0)
        ideal = ideal_baseline.get(metric, 0)

        # Note: Higher is better for entropy/uniqueness, Lower is better for correlation/temporal
        is_higher_better = metric in ["entropy", "uniqueness"]

        if is_higher_better:
            vs_random = "better" if actual > random else "worse"
            vs_ideal = "better" if actual > ideal else "worse"
        else:
            vs_random = "better" if actual < random else "worse"
            vs_ideal = "better" if actual < ideal else "worse"

        diff_random = abs(actual - random)
        diff_ideal = abs(actual - ideal)

        comparison["comparison"][metric] = {
            "vs_random": vs_random,
            "vs_ideal": vs_ideal,
            "difference_from_random": diff_random,
            "difference_from_ideal": diff_ideal,
            "raw_actual": actual,
            "raw_random": random,
            "raw_ideal": ideal
        }

    # Calculate overall privacy score (0-100)
    # Score based on closeness to ideal baseline
    overall_score = 0
    for metric in metrics:
        actual = actual_metrics.get(metric, 0)
        ideal = ideal_baseline.get(metric, 0)

        # Calculate percentage of ideal achieved
        if ideal > 0:
            percent = 100 * (1 - abs(actual - ideal))
            overall_score += percent / len(metrics)

    comparison["overall_privacy_score"] = int(max(0, min(100, overall_score)))

    # Determine privacy level
    if overall_score >= 80:
        privacy_level = "excellent"
    elif overall_score >= 60:
        privacy_level = "good"
    elif overall_score >= 40:
        privacy_level = "moderate"
    else:
        privacy_level = "poor"

    comparison["privacy_level"] = privacy_level

    return comparison


def generate_baselines_multiple_sessions(
    session_metrics: List[Dict[str, float]],
    num_requests_list: List[int],
    available_methods: List[str] = None
) -> List[Dict]:
    """
    Generate baseline comparisons for multiple sessions

    Args:
        session_metrics: List of session metric dictionaries
        num_requests_list: List of request counts for each session
        available_methods: Available RPC methods

    Returns:
        List of comparison dictionaries
    """
    results = []
    for i, (metrics, num_reqs) in enumerate(zip(session_metrics, num_requests_list)):
        comparison = compare_with_baselines(
            metrics, num_reqs, available_methods
        )
        comparison["session_index"] = i
        results.append(comparison)

    return results


def _calculate_entropy_score(method_counts: Dict[str, int]) -> float:
    """
    Calculate Shannon entropy score

    Args:
        method_counts: Dictionary mapping method names to counts

    Returns:
        Entropy score in [0.0, 1.0]
    """
    total = sum(method_counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in method_counts.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalize by max possible entropy
    n = len(method_counts)
    max_entropy = math.log2(n) if n > 1 else 1.0

    return entropy / max_entropy if max_entropy > 0 else 0.0


def generate_industry_comparison(
    session_metrics: Dict[str, float],
    industry_stats: Dict[str, Dict[str, float]] = None
) -> Dict:
    """
    Compare session metrics with industry averages

    Args:
        session_metrics: Session metrics
        industry_stats: Industry statistics (default typical wallet RPC patterns)

    Returns:
        Dictionary with industry comparison
    """
    if industry_stats is None:
        # Predefined industry statistics based on typical wallet RPC patterns
        industry_stats = {
            "mean": {
                "entropy": 0.45,      # Typically low diversity
                "uniqueness": 0.50,   # Moderate uniqueness
                "correlation": 0.60,  # High correlation due to patterns
                "temporal": 0.70      # Predictable timing
            },
            "percentiles": {
                "p25": {"entropy": 0.35, "uniqueness": 0.40, "correlation": 0.50, "temporal": 0.60},
                "p50": {"entropy": 0.45, "uniqueness": 0.50, "correlation": 0.60, "temporal": 0.70},
                "p75": {"entropy": 0.55, "uniqueness": 0.60, "correlation": 0.70, "temporal": 0.80},
            }
        }

    comparison = {
        "session_metrics": session_metrics,
        "industry_mean": industry_stats["mean"],
        "percentile_rankings": {},
        "performance": {}
    }

    metrics = ["entropy", "uniqueness", "correlation", "temporal"]

    for metric in metrics:
        actual = session_metrics.get(metric, 0)
        mean = industry_stats["mean"][metric]
        p25 = industry_stats["percentiles"]["p25"][metric]
        p50 = industry_stats["percentiles"]["p50"][metric]
        p75 = industry_stats["percentiles"]["p75"][metric]

        # Determine percentile
        if actual <= p25:
            percentile = 25
        elif actual <= p50:
            percentile = 50
        elif actual <= p75:
            percentile = 75
        else:
            percentile = 90

        comparison["percentile_rankings"][metric] = {
            "percentile": percentile,
            "value": actual,
            "percentile_25": p25,
            "percentile_50": p50,
            "percentile_75": p75
        }

        # Performance assessment
        diff_from_mean = actual - mean
        if abs(diff_from_mean) < 0.05:
            performance = "average"
        elif diff_from_mean > 0:
            performance = "above_average"
        else:
            performance = "below_average"

        comparison["performance"][metric] = {
            "assessment": performance,
            "difference_from_mean": diff_from_mean
        }

    # Overall industry ranking
    avg_percentile = sum(
        comparison["percentile_rankings"][m]["percentile"]
        for m in metrics
    ) / len(metrics)

    comparison["overall_industry_ranking"] = {
        "average_percentile": int(avg_percentile),
        "ranking_text": _get_ranking_text(avg_percentile)
    }

    return comparison


def _get_ranking_text(percentile: float) -> str:
    """
    Get ranking description from percentile

    Args:
        percentile: Average percentile value

    Returns:
        Ranking description text
    """
    if percentile >= 75:
        return "top_quartile"
    elif percentile >= 50:
        return "above_median"
    elif percentile >= 25:
        return "below_median"
    else:
        return "bottom_quartile"
