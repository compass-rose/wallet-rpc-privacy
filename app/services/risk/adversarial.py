"""
Adversarial testing - evaluate privacy defense effectiveness
"""
from typing import Dict, List
import numpy as np
from datetime import datetime, timedelta
import random

from app.services.risk.attack_simulation import (
    simulate_distinguishing_attack,
    extract_session_features,
    create_labeled_dataset,
    train_and_evaluate_classifier
)


def apply_padding_defense(
    traffic_records: List,
    padding_ratio: float = 0.2
) -> List:
    """
    Apply padding defense by adding dummy requests

    Padding adds random traffic to obscure real patterns

    Args:
        traffic_records: Original traffic records
        padding_ratio: Ratio of padding requests (0.0-1.0)

    Returns:
        Traffic records with padding added
    """
    num_padding = int(len(traffic_records) * padding_ratio)
    padded_records = traffic_records.copy()

    # Mock RPC methods for padding
    dummy_methods = [
        "eth_getBlockByNumber",
        "eth_chainId",
        "eth_blockNumber",
        "eth_syncing"
    ]

    for _ in range(num_padding):
        # Create padding record mock
        base_record = traffic_records[0] if traffic_records else None
        if base_record:
            # Create new padding record based on random method
            # In real implementation, this would create actual record objects
            pass

    return padded_records


def apply_timing_jitter_defense(
    traffic_records: List,
    jitter_std: float = 30.0
) -> List:
    """
    Apply timing jitter defense by randomizing request intervals

    Args:
        traffic_records: Original traffic records
        jitter_std: Standard deviation of jitter in seconds

    Returns:
        Traffic records with jittered timestamps
    """
    jittered_records = traffic_records.copy()

    for record in jittered_records:
        if hasattr(record, 'request_timestamp') and record.request_timestamp:
            # Add random jitter to timestamp
            jitter = random.gauss(0, jitter_std)
            record.request_timestamp = record.request_timestamp + timedelta(seconds=jitter)

    return jittered_records


def apply_method_randomization_defense(
    traffic_records: List,
    randomization_ratio: float = 0.15
) -> List:
    """
    Apply method randomization defense by inserting random requests

    Args:
        traffic_records: Original traffic records
        randomization_ratio: Ratio of random method insertions

    Returns:
        Traffic records with method randomization
    """
    num_random = int(len(traffic_records) * randomization_ratio)
    randomized_records = traffic_records.copy()

    # In real implementation, this would insert actual random method calls
    # For now, return as-is (mock implementation)

    return randomized_records


def evaluate_defense_effectiveness(
    original_traffic_by_session: Dict[str, List],
    defense_strategies: List[str] = None
) -> Dict:
    """
    Evaluate effectiveness of various privacy defense strategies

    Args:
        original_traffic_by_session: Dict mapping session_id to original traffic
        defense_strategies: List of strategies to test ('padding', 'timing_jitter', 'method_randomization')

    Returns:
        Dictionary with effectiveness evaluation results
    """
    if defense_strategies is None:
        defense_strategies = ["padding", "timing_jitter", "method_randomization"]

    results = {
        "test_timestamp": datetime.utcnow().isoformat(),
        "num_sessions": len(original_traffic_by_session),
        "defense_strategies": {},
        "baseline": {},
        "recommendations": []
    }

    # Baseline: evaluate effectiveness without defense
    baseline_attack = simulate_distinguishing_attack(original_traffic_by_session)
    results["baseline"] = baseline_attack

    if "overall_attack_effectiveness" in baseline_attack:
        baseline_effectiveness = baseline_attack["overall_attack_effectiveness"]["value"]
    else:
        baseline_effectiveness = 0

    # Test each defense strategy
    for strategy in defense_strategies:
        # Apply defense to all sessions
        defended_traffic = {}

        for session_id, traffic_records in original_traffic_by_session.items():
            if strategy == "padding":
                defended = apply_padding_defense(traffic_records, padding_ratio=0.2)
            elif strategy == "timing_jitter":
                defended = apply_timing_jitter_defense(traffic_records, jitter_std=30.0)
            elif strategy == "method_randomization":
                defended = apply_method_randomization_defense(traffic_records, randomization_ratio=0.15)
            else:
                defended = traffic_records

            defended_traffic[session_id] = defended

        # Evaluate attack on defended traffic
        attack_on_defense = simulate_distinguishing_attack(defended_traffic)

        if "overall_attack_effectiveness" in attack_on_defense:
            defended_effectiveness = attack_on_defense["overall_attack_effectiveness"]["value"]
        else:
            defended_effectiveness = 0

        # Calculate reduction in attack effectiveness
        effectiveness_reduction = baseline_effectiveness - defended_effectiveness
        reduction_percentage = (effectiveness_reduction / baseline_effectiveness * 100) if baseline_effectiveness > 0 else 0

        results["defense_strategies"][strategy] = {
            "attack_effectiveness_after": round(defended_effectiveness, 4),
            "effectiveness_reduction": round(effectiveness_reduction, 4),
            "reduction_percentage": round(reduction_percentage, 2),
            "effectiveness_rating": _get_effectiveness_rating(reduction_percentage),
            "attack_details": attack_on_defense
        }

    # Generate recommendations
    results["recommendations"] = _generate_recommendations(
        results["defense_strategies"],
        baseline_effectiveness
    )

    # Determine best strategy
    best_strategy = None
    best_reduction = -1

    for strategy, result in results["defense_strategies"].items():
        if result["reduction_percentage"] > best_reduction:
            best_reduction = result["reduction_percentage"]
            best_strategy = strategy

    results["best_strategy"] = {
        "name": best_strategy,
        "expected_risk_reduction_percent": best_reduction
    }

    # Overall risk reduction estimate
    if best_strategy and best_reduction >= 0:
        results["overall_improvement"] = {
            "baseline_effectiveness": round(baseline_effectiveness, 4),
            "best_defended_effectiveness": round(
                baseline_effectiveness - (best_reduction / 100 * baseline_effectiveness), 4
            ),
            "overall_risk_reduction_percent": best_reduction
        }

    return results


def _get_effectiveness_rating(reduction_percentage: float) -> str:
    """
    Convert reduction percentage to effectiveness rating

    Args:
        reduction_percentage: Percentage reduction in attack effectiveness

    Returns:
        Effectiveness rating string
    """
    if reduction_percentage >= 50:
        return "high"
    elif reduction_percentage >= 25:
        return "medium_high"
    elif reduction_percentage >= 10:
        return "medium"
    elif reduction_percentage >= 5:
        return "low"
    else:
        return "negligible"


def _generate_recommendations(
    defense_results: Dict,
    baseline_effectiveness: float
) -> List[Dict]:
    """
    Generate recommendations based on defense effectiveness

    Args:
        defense_results: Dictionary of defense strategy results
        baseline_effectiveness: Baseline attack effectiveness

    Returns:
        List of recommendation dictionaries
    """
    recommendations = []

    # Find most effective strategy
    if defense_results:
        sorted_strategies = sorted(
            defense_results.items(),
            key=lambda x: x[1]["reduction_percentage"],
            reverse=True
        )

        for strategy, result in sorted_strategies:
            if result["reduction_percentage"] >= 20:
                status = "recommended"
            elif result["reduction_percentage"] >= 10:
                status = "optional"
            else:
                status = "not_recommended"

            recommendations.append({
                "strategy": strategy,
                "risk_reduction_percent": result["reduction_percentage"],
                "status": status,
                "effectiveness": result["effectiveness_rating"]
            })

    # High-level recommendation
    if baseline_effectiveness >= 0.7:
        recommendations.append({
            "type": "high_level",
            "message": "当前隐私风险较高，强烈建议实施至少一种隐私保护措施",
            "priority": "critical"
        })
    elif baseline_effectiveness >= 0.5:
        recommendations.append({
            "type": "high_level",
            "message": "当前存在中等隐私风险，建议实施隐私保护措施",
            "priority": "high"
        })
    else:
        recommendations.append({
            "type": "high_level",
            "message": "当前隐私风险水平可接受，建议持续监控",
            "priority": "medium"
        })

    return recommendations


def evaluate_composite_defense(
    original_traffic_by_session: Dict[str, List],
    strategy_combinations: List[List[str]] = None
) -> Dict:
    """
    Evaluate effectiveness of combined defense strategies

    Args:
        original_traffic_by_session: Dict mapping session_id to traffic
        strategy_combinations: List of strategy combinations to test

    Returns:
        Dictionary with composite defense effectiveness
    """
    if strategy_combinations is None:
        strategy_combinations = [
            ["padding"],
            ["timing_jitter"],
            ["method_randomization"],
            ["padding", "timing_jitter"],
            ["padding", "method_randomization"],
            ["timing_jitter", "method_randomization"],
            ["padding", "timing_jitter", "method_randomization"]
        ]

    results = {
        "test_timestamp": datetime.utcnow().isoformat(),
        "baseline_effectiveness": 0,
        "combination_results": {}
    }

    # Baseline
    baseline_attack = simulate_distinguishing_attack(original_traffic_by_session)
    if "overall_attack_effectiveness" in baseline_attack:
        results["baseline_effectiveness"] = baseline_attack["overall_attack_effectiveness"]["value"]

    # Test each combination
    for strategies in strategy_combinations:
        defended_traffic = {}

        for session_id, traffic_records in original_traffic_by_session.items():
            defended = traffic_records.copy()

            # Apply each strategy in sequence
            for strategy in strategies:
                if strategy == "padding":
                    defended = apply_padding_defense(defended, padding_ratio=0.2)
                elif strategy == "timing_jitter":
                    defended = apply_timing_jitter_defense(defended, jitter_std=30.0)
                elif strategy == "method_randomization":
                    defended = apply_method_randomization_defense(defended, randomization_ratio=0.15)

            defended_traffic[session_id] = defended

        attack_result = simulate_distinguishing_attack(defended_traffic)

        if "overall_attack_effectiveness" in attack_result:
            defended_effectiveness = attack_result["overall_attack_effectiveness"]["value"]
        else:
            defended_effectiveness = 0

        reduction = results["baseline_effectiveness"] - defended_effectiveness
        reduction_percent = (reduction / results["baseline_effectiveness"] * 100) if results["baseline_effectiveness"] > 0 else 0

        combination_key = "+".join(strategies)
        results["combination_results"][combination_key] = {
            "strategies": strategies,
            "attack_effectiveness": round(defended_effectiveness, 4),
            "effectiveness_reduction": round(reduction, 4),
            "reduction_percentage": round(reduction_percent, 2),
            "effectiveness_rating": _get_effectiveness_rating(reduction_percent)
        }

    # Find best combination
    if results["combination_results"]:
        best_combination = max(
            results["combination_results"].items(),
            key=lambda x: x[1]["reduction_percentage"]
        )
        results["best_combination"] = {
            "strategies": best_combination[1]["strategies"],
            "reduction_percentage": best_combination[1]["reduction_percentage"],
            "expected_effectiveness": best_combination[1]["attack_effectiveness"]
        }

    return results


def run_perturbation_analysis(
    traffic_by_session: Dict[str, List],
    defense_strategy: str,
    parameter_range: List[float] = None
) -> Dict:
    """
    Analyze defense effectiveness across different perturbation levels

    Args:
        traffic_by_session: Dict mapping session_id to traffic
        defense_strategy: Defense strategy to analyze ('padding', 'timing_jitter', 'method_randomization')
        parameter_range: List of parameter values to test

    Returns:
        Dictionary with perturbation analysis results
    """
    if parameter_range is None:
        if defense_strategy == "padding":
            parameter_range = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
        elif defense_strategy == "timing_jitter":
            parameter_range = [10, 20, 30, 45, 60, 90]
        else:
            parameter_range = [0.1, 0.15, 0.2, 0.25, 0.3]

    results = {
        "defense_strategy": defense_strategy,
        "parameter_name": _get_parameter_name(defense_strategy),
        "test_timestamp": datetime.utcnow().isoformat(),
        "baseline_effectiveness": 0,
        "effectiveness_by_parameter": {}
    }

    # Baseline
    baseline_attack = simulate_distinguishing_attack(traffic_by_session)
    if "overall_attack_effectiveness" in baseline_attack:
        results["baseline_effectiveness"] = baseline_attack["overall_attack_effectiveness"]["value"]

    # Test each perturbation level
    for param_value in parameter_range:
        defended_traffic = {}

        for session_id, traffic_records in traffic_by_session.items():
            if defense_strategy == "padding":
                defended = apply_padding_defense(traffic_records, padding_ratio=param_value)
            elif defense_strategy == "timing_jitter":
                defended = apply_timing_jitter_defense(traffic_records, jitter_std=param_value)
            elif defense_strategy == "method_randomization":
                defended = apply_method_randomization_defense(traffic_records, randomization_ratio=param_value)
            else:
                defended = traffic_records

            defended_traffic[session_id] = defended

        attack_result = simulate_distinguishing_attack(defended_traffic)

        if "overall_attack_effectiveness" in attack_result:
            defended_effectiveness = attack_result["overall_attack_effectiveness"]["value"]
        else:
            defended_effectiveness = 0

        reduction = results["baseline_effectiveness"] - defended_effectiveness
        reduction_percent = (reduction / results["baseline_effectiveness"] * 100) if results["baseline_effectiveness"] > 0 else 0

        results["effectiveness_by_parameter"][param_value] = {
            "attack_effectiveness": round(defended_effectiveness, 4),
            "effectiveness_reduction": round(reduction, 4),
            "reduction_percentage": round(reduction_percent, 2)
        }

    # Plot recommendation: find optimal point (diminishing returns)
    results["optimal_parameter"] = _find_optimal_parameter(results["effectiveness_by_parameter"])

    return results


def _get_parameter_name(defense_strategy: str) -> str:
    """
    Get parameter name for defense strategy

    Args:
        defense_strategy: Defense strategy name

    Returns:
        Parameter name string
    """
    if defense_strategy == "padding":
        return "padding_ratio"
    elif defense_strategy == "timing_jitter":
        return "jitter_std_seconds"
    elif defense_strategy == "method_randomization":
        return "randomization_ratio"
    else:
        return "parameter_value"


def _find_optimal_parameter(effectiveness_data: Dict) -> Dict:
    """
    Find optimal parameter value based on effectiveness vs cost trade-off

    Optimal point: where marginal benefit < 5%

    Args:
        effectiveness_data: Dict mapping parameter value to effectiveness

    Returns:
        Dictionary with optimal parameter recommendation
    """
    if not effectiveness_data:
        return {"error": "No effectiveness data available"}

    sorted_params = sorted(effectiveness_data.keys())
    optimal_param = sorted_params[len(sorted_params) // 2]  # Default to middle

    # Find point where improvement levels off (diminishing returns)
    for i in range(1, len(sorted_params) - 1):
        prev_param = sorted_params[i - 1]
        curr_param = sorted_params[i]

        prev_improvement = effectiveness_data[prev_param]["reduction_percentage"]
        curr_improvement = effectiveness_data[curr_param]["reduction_percentage"]

        marginal_gain = curr_improvement - prev_improvement

        if marginal_gain < 5:
            optimal_param = curr_param
            break

    return {
        "parameter_value": optimal_param,
        "expected_effectiveness": effectiveness_data[optimal_param].get("attack_effectiveness", 0),
        "expected_reduction": effectiveness_data[optimal_param].get("reduction_percentage", 0),
        "recommendation": f"建议使用 {optimal_param} 作为{optimal_param}值"
    }
