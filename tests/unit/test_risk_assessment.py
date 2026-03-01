"""
Unit tests for risk assessment metrics
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.services.risk.metrics import (
    calculate_entropy,
    calculate_uniqueness,
    calculate_correlation,
    calculate_temporal
)


def test_calculate_entropy_single_method():
    """Test entropy with single method (should be 0)"""
    frequencies = {"eth_getBalance": 100}
    entropy = calculate_entropy(frequencies)

    assert entropy == 0.0


def test_calculate_entropy_multiple_methods():
    """Test entropy with multiple methods"""
    frequencies = {
        "eth_getBalance": 50,
        "eth_call": 30,
        "eth_blockNumber": 20
    }
    entropy = calculate_entropy(frequencies)

    assert 0.0 < entropy <= 1.0


def test_calculate_entropy_empty():
    """Test entropy with empty input"""
    frequencies = {}
    entropy = calculate_entropy(frequencies)

    assert entropy == 0.0


def test_calculate_entropy_uniform():
    """Test entropy with uniform distribution (should be 1.0)"""
    frequencies = {"eth_getBalance": 1, "eth_call": 1, "eth_blockNumber": 1}
    entropy = calculate_entropy(frequencies)

    assert entropy == 1.0


def test_calculate_uniqueness_no_reference():
    """Test uniqueness with no reference sessions"""
    target = {"eth_getBalance": 10, "eth_call": 5}
    references = []
    uniqueness = calculate_uniqueness(target, references)

    assert uniqueness == 1.0


def test_calculate_uniqueness_identical():
    """Test uniqueness with identical reference"""
    target = {"eth_getBalance": 10, "eth_call": 5}
    references = [{"eth_getBalance": 10, "eth_call": 5}]
    uniqueness = calculate_uniqueness(target, references)

    assert uniqueness < 1e-10  # Floating point precision tolerance


def test_calculate_correlation_single_set():
    """Test correlation with single address (should be 0)"""
    method_sets = [{"eth_getBalance", "eth_call"}]
    correlation = calculate_correlation(method_sets)

    assert correlation == 0.0


def test_calculate_correlation_overlapping():
    """Test correlation with overlapping method sets"""
    method_sets = [
        {"eth_getBalance", "eth_call"},
        {"eth_getBalance", "eth_blockNumber"}
    ]
    correlation = calculate_correlation(method_sets)

    # Jaccard similarity = 1/3 ≈ 0.33
    expected = 1.0 / 3.0
    assert abs(correlation - expected) < 0.01


def test_calculate_correlation_identical():
    """Test correlation with identical sets (should be 1.0)"""
    method_sets = [
        {"eth_getBalance", "eth_call"},
        {"eth_getBalance", "eth_call"}
    ]
    correlation = calculate_correlation(method_sets)

    assert correlation == 1.0


def test_calculate_temporal_single_timestamp():
    """Test temporal with single timestamp (should be 0)"""
    timestamps = [datetime.now(timezone.utc)]
    temporal = calculate_temporal(timestamps)

    assert temporal == 0.0


def test_calculate_temporal_uniform_intervals():
    """Test temporal with uniform intervals (should be 0)"""
    base = datetime.now(timezone.utc)
    timestamps = [
        base,
        base + timedelta(seconds=1),
        base + timedelta(seconds=2),
        base + timedelta(seconds=3)
    ]
    temporal = calculate_temporal(timestamps)

    # Uniform intervals = low variance
    assert temporal < 0.1


def test_calculate_temporal_variable_intervals():
    """Test temporal with variable intervals"""
    base = datetime.now(timezone.utc)
    timestamps = [
        base,
        base + timedelta(seconds=0.1),
        base + timedelta(seconds=5),
        base + timedelta(seconds=0.2)
    ]
    temporal = calculate_temporal(timestamps)

    # Variable intervals = higher variance
    assert temporal > 0.5
