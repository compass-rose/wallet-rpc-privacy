"""
Risk assessment metrics - 4-dimensional scoring algorithms
"""
import math
from typing import Dict, List
from collections import Counter
from datetime import datetime


def calculate_entropy(method_frequencies: Dict[str, int]) -> float:
    """
    Calculate Shannon entropy of request method distribution

    Higher entropy = more method diversity = lower predictability

    Formula: H = -sum(p[i] * log2(p[i]))
    Normalized: entropy_score = H / log2(n)

    Args:
        method_frequencies: Dictionary mapping method names to frequencies

    Returns:
        Entropy score in [0.0, 1.0]
    """
    total = sum(method_frequencies.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in method_frequencies.values():
        if count > 0:
            p = count / total
            entropy -= p * math.log2(p)

    # Normalize by max possible entropy (log2 of number of methods)
    n = len(method_frequencies)
    max_entropy = math.log2(n) if n > 1 else 1.0

    return entropy / max_entropy if max_entropy > 0 else 0.0


def calculate_uniqueness(
    target_features: Dict,
    reference_features: List[Dict]
) -> float:
    """
    Calculate uniqueness score using cosine similarity vs baseline

    Lower similarity = higher uniqueness = better privacy

    Args:
        target_features: Feature dictionary for target session
        reference_features: List of feature dictionaries for reference sessions

    Returns:
        Uniqueness score in [0.0, 1.0]
    """
    if not reference_features:
        return 1.0  # Unique if no reference baseline

    def cosine_sim(a: Dict, b: Dict) -> float:
        """Calculate cosine similarity between two feature vectors"""
        # Get common keys
        keys = set(a.keys()) & set(b.keys())
        if not keys:
            return 0.0

        dot_product = sum(a[k] * b[k] for k in keys)
        magnitude_a = math.sqrt(sum(v**2 for v in a.values()))
        magnitude_b = math.sqrt(sum(v**2 for v in b.values()))

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    # Find maximum similarity with any reference
    max_sim = max(
        cosine_sim(target_features, ref)
        for ref in reference_features
    )

    # Uniqueness = 1 - max_similarity
    return 1.0 - max_sim


def calculate_correlation(method_sets: List[set]) -> float:
    """
    Calculate address correlation using Jaccard similarity

    Higher correlation = more linkable addresses = worse privacy

    Args:
        method_sets: List of sets, each containing methods for an address

    Returns:
        Correlation score in [0.0, 1.0]
    """
    if len(method_sets) < 2:
        return 0.0  # No correlation if single address

    def jaccard(set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets"""
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    # Find maximum Jaccard similarity between any pair of addresses
    max_jaccard = 0.0
    for i in range(len(method_sets)):
        for j in range(i + 1, len(method_sets)):
            sim = jaccard(method_sets[i], method_sets[j])
            max_jaccard = max(max_jaccard, sim)

    return max_jaccard


def calculate_temporal(
    timestamps: List[datetime],
    threshold_cv: float = 1.0
) -> float:
    """
    Calculate temporal distinguishability based on request timing

    Higher CV (coefficient of variation) = more variable timing = worse privacy

    Args:
        timestamps: List of request timestamps
        threshold_cv: Threshold for normalization

    Returns:
        Temporal score in [0.0, 1.0]
    """
    if len(timestamps) < 2:
        return 0.0  # Cannot compute with single timestamp

    # Sort timestamps
    sorted_timestamps = sorted(timestamps)

    # Calculate inter-request intervals
    intervals = []
    for i in range(1, len(sorted_timestamps)):
        interval = (sorted_timestamps[i] - sorted_timestamps[i-1]).total_seconds()
        intervals.append(interval)

    if not intervals:
        return 0.0

    # Calculate mean and standard deviation
    mean = sum(intervals) / len(intervals)
    if mean == 0:
        return 1.0  # All requests at same time

    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    std_dev = math.sqrt(variance)

    # Coefficient of variation
    cv = std_dev / mean

    # Normalize to [0, 1]
    return min(1.0, cv / threshold_cv)
