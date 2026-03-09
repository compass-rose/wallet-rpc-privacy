"""
Simulated attack - ML-based session distinguishability attack
"""
from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from datetime import datetime


def extract_session_features(traffic_records: List) -> Dict[str, float]:
    """
    Extract features from session traffic for ML classification

    Features extracted:
    1. Method frequency distribution
    2. Temporal patterns (mean, std of intervals)
    3. Request/response time statistics
    4. Sequential patterns

    Args:
        traffic_records: List of NetworkTraffic records

    Returns:
        Feature dictionary with extracted features
    """
    if not traffic_records:
        return {}

    # Method frequencies
    method_counts = {}
    for record in traffic_records:
        method = record.rpc_method or "unknown"
        method_counts[method] = method_counts.get(method, 0) + 1

    total_requests = len(traffic_records)

    # Method frequency features
    features = {
        "total_requests": total_requests,
        "unique_methods": len(method_counts),
    }

    # Top 10 most common methods frequency
    sorted_methods = sorted(method_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (method, count) in enumerate(sorted_methods[:10]):
        features[f"method_{method}_freq"] = count / total_requests

    # Temporal features
    timestamps = [r.request_timestamp for r in traffic_records if r.request_timestamp]
    if len(timestamps) > 1:
        intervals = []
        sorted_times = sorted(timestamps)
        for i in range(1, len(sorted_times)):
            interval = (sorted_times[i] - sorted_times[i-1]).total_seconds()
            intervals.append(interval)

        features.update({
            "avg_interval": sum(intervals) / len(intervals),
            "std_interval": np.std(intervals) if len(intervals) > 1 else 0,
            "min_interval": min(intervals),
            "max_interval": max(intervals),
        })

        # Interval distribution features
        q25, q50, q75 = np.percentile(intervals, [25, 50, 75])
        features.update({
            "interval_q25": q25,
            "interval_q50": q50,
            "interval_q75": q75,
        })
    else:
        features.update({
            "avg_interval": 0,
            "std_interval": 0,
            "min_interval": 0,
            "max_interval": 0,
            "interval_q25": 0,
            "interval_q50": 0,
            "interval_q75": 0,
        })

    # Response time statistics
    response_times = [r.response_time_ms for r in traffic_records if r.response_time_ms]
    if response_times:
        features.update({
            "avg_response_time": sum(response_times) / len(response_times),
            "std_response_time": np.std(response_times) if len(response_times) > 1 else 0,
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
        })
    else:
        features.update({
            "avg_response_time": 0,
            "std_response_time": 0,
            "min_response_time": 0,
            "max_response_time": 0,
        })

    # Directional features (request/response ratio by method)
    for method in sorted_methods[:5]:
        features[f"method_{method[0]}_direction_entropy"] = _calculate_directional_entropy(
            [r for r in traffic_records if r.rpc_method == method[0]]
        )

    return features


def _calculate_directional_entropy(records: List) -> float:
    """
    Calculate entropy of request/response directions

    Args:
        records: Traffic records for specific method

    Returns:
        Directional entropy value
    """
    if not records:
        return 0.0

    directions = {"request": 0, "response": 0}
    for record in records:
        if hasattr(record, "is_response") and record.is_response:
            directions["response"] += 1
        else:
            directions["request"] += 1

    total = sum(directions.values())
    entropy = 0.0
    for count in directions.values():
        if count > 0:
            p = count / total
            entropy -= p * np.log2(p)

    return entropy


def create_labeled_dataset(
    traffic_by_session: Dict[str, List]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create labeled dataset for training ML models

    Labels:
    - 0: Session from different user
    - 1: Session from same user (assumed based on address_hash)

    Args:
        traffic_by_session: Dict mapping session_id to traffic records

    Returns:
        Tuple of (features, labels)
    """
    features_list = []
    labels = []

    # Group sessions by address_hash
    sessions_by_address = {}
    for session_id, records in traffic_by_session.items():
        if records and len(records) > 0:
            address_hash = records[0].address_hash
            if address_hash not in sessions_by_address:
                sessions_by_address[address_hash] = []
            sessions_by_address[address_hash].append(session_id)

    # For each address, create positive pairs and negative pairs
    for address_hash, session_ids in sessions_by_address.items():
        if len(session_ids) < 2:
            continue

        # Positive pairs (same address → same user)
        for i in range(len(session_ids)):
            for j in range(i + 1, len(session_ids)):
                feat_i = extract_session_features(traffic_by_session[session_ids[i]])
                feat_j = extract_session_features(traffic_by_session[session_ids[j]])

                if feat_i and feat_j:
                    # Combine features: difference and concatenation
                    combined = _combine_features(feat_i, feat_j)
                    features_list.append(combined)
                    labels.append(1)  # Same user

        # Negative pairs (different address → different user)
        for other_address, other_sessions in sessions_by_address.items():
            if other_address == address_hash:
                continue

            for session_id in session_ids:
                for other_session_id in other_sessions[:3]:  # Limit negative pairs
                    feat_i = extract_session_features(traffic_by_session[session_id])
                    feat_j = extract_session_features(traffic_by_session[other_session_id])

                    if feat_i and feat_j:
                        combined = _combine_features(feat_i, feat_j)
                        features_list.append(combined)
                        labels.append(0)  # Different user

    if not features_list:
        return np.array([]), np.array([])

    return np.array(feature_vectorize(features_list)), np.array(labels)


def feature_vectorize(features_list: List[Dict]) -> np.ndarray:
    """
    Convert list of feature dictionaries to numpy array

    Args:
        features_list: List of feature dictionaries

    Returns:
        Numpy array of shape (n_samples, n_features)
    """
    if not features_list:
        return np.array([])

    # Get all feature keys
    all_keys = set()
    for features in features_list:
        all_keys.update(features.keys())

    # Sort keys for consistency
    sorted_keys = sorted(all_keys)

    # Create vectorized features
    vectorized = []
    for features in features_list:
        vector = [features.get(key, 0) for key in sorted_keys]
        vectorized.append(vector)

    return np.array(vectorized)


def _combine_features(feat_i: Dict, feat_j: Dict) -> Dict:
    """
    Combine two session features for pairwise classification

    Args:
        feat_i: Session i features
        feat_j: Session j features

    Returns:
        Combined feature dictionary
    """
    combined = {}

    # Absolute differences
    all_keys = set(feat_i.keys()) | set(feat_j.keys())
    for key in all_keys:
        val_i = feat_i.get(key, 0)
        val_j = feat_j.get(key, 0)
        combined[f"{key}_diff"] = abs(val_i - val_j)

    # Concatenated features (prefixed)
    for key in all_keys:
        combined[f"{key}_i"] = feat_i.get(key, 0)
        combined[f"{key}_j"] = feat_j.get(key, 0)

    return combined


def train_and_evaluate_classifier(
    X: np.ndarray,
    y: np.ndarray,
    model_type: str = "random_forest"
) -> Dict:
    """
    Train and evaluate ML classifier for session distinguishability

    Args:
        X: Feature matrix
        y: Labels (0: different, 1: same)
        model_type: Type of classifier ('random_forest', 'naive_bayes')

    Returns:
        Dictionary with evaluation results
    """
    if len(X) == 0 or len(y) == 0:
        return {
            "error": "Insufficient data for training",
            "accuracy": 0,
            "attack_success_rate": 0
        }

    # Check class balance
    unique, counts = np.unique(y, return_counts=True)
    if len(unique) < 2:
        return {
            "error": "Only one class present in data",
            "accuracy": 0,
            "attack_success_rate": 0
        }

    if np.any(counts < 2):
        return {
            "error": f"Insufficient samples per class. Minimum required: 2, Found: {counts.min()}",
            "accuracy": 0,
            "attack_success_rate": 0
        }

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    # Train classifier
    if model_type == "random_forest":
        classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    elif model_type == "naive_bayes":
        classifier = GaussianNB()
    else:
        return {
            "error": f"Unsupported model type: {model_type}",
            "accuracy": 0,
            "attack_success_rate": 0
        }

    classifier.fit(X_train, y_train)

    # Predict on test set
    y_pred = classifier.predict(X_test)

    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='binary', zero_division=0)
    recall = recall_score(y_test, y_pred, average='binary', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='binary', zero_division=0)

    # Feature importance (for tree-based models)
    feature_importance = {}
    if model_type == "random_forest" and hasattr(classifier, 'feature_importances_'):
        # Get top 10 important features
        indices = np.argsort(classifier.feature_importances_)[::-1][:10]
        feature_importance = {
            f"feature_{i}": float(classifier.feature_importances_[idx])
            for i, idx in enumerate(indices)
        }

    return {
        "model_type": model_type,
        "train_accuracy": round(classifier.score(X_train, y_train), 4),
        "test_accuracy": round(accuracy, 4),
        "attack_success_rate": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "feature_importance": feature_importance,
        "class_distribution": {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "positive_class_ratio": round(np.mean(y_train), 4)
        }
    }


def run_clustering_attack(
    traffic_by_session: Dict[str, List],
    n_clusters: int = 3
) -> Dict:
    """
    Run clustering attack - try to cluster sessions by user

    Args:
        traffic_by_session: Dict mapping session_id to traffic records
        n_clusters: Number of clusters for KMeans

    Returns:
        Dictionary with clustering results
    """
    # Extract features for each session
    session_features = {}
    session_ids = []
    features_list = []

    for session_id, records in traffic_by_session.items():
        features = extract_session_features(records)
        if features:
            session_features[session_id] = features
            session_ids.append(session_id)
            features_list.append(features)

    if len(features_list) < n_clusters:
        return {
            "error": f"Insufficient sessions for clustering ({len(features_list)} < {n_clusters})",
            "n_clusters": n_clusters
        }

    # Vectorize features
    X = feature_vectorize(features_list)

    # Run KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X)

    # Calculate silhouette score (within-cluster cohesion)
    from sklearn.metrics import silhouette_score
    try:
        silhouette = silhouette_score(X, labels)
    except ValueError:
        silhouette = None

    # Analyze cluster distribution by address_hash
    cluster_by_address = {}
    for session_id, label in zip(session_ids, labels):
        records = traffic_by_session[session_id]
        address = records[0].address_hash if records else "unknown"
        cluster_key = f"cluster_{label}"
        if cluster_key not in cluster_by_address:
            cluster_by_address[cluster_key] = {}
        if address not in cluster_by_address[cluster_key]:
            cluster_by_address[cluster_key][address] = 0
        cluster_by_address[cluster_key][address] += 1

    return {
        "n_clusters": n_clusters,
        "silhouette_score": round(silhouette, 4) if silhouette is not None else None,
        "cluster_purity": _calculate_cluster_purity(cluster_by_address),
        "cluster_distribution": {
            f"cluster_{i}": int(np.sum(labels == i))
            for i in range(n_clusters)
        },
        "cluster_by_address": cluster_by_address,
        "attack_effectiveness": round(silhouette, 4) if silhouette is not None else None
    }


def _calculate_cluster_purity(cluster_by_address: Dict) -> float:
    """
    Calculate cluster purity (how pure clusters are by address)

    Args:
        cluster_by_address: Dict mapping cluster to address counts

    Returns:
        Purity score between 0 and 1
    """
    if not cluster_by_address:
        return 0.0

    total_correct = 0
    total_samples = 0

    for cluster, address_counts in cluster_by_address.items():
        if address_counts:
            max_in_cluster = max(address_counts.values())
            cluster_size = sum(address_counts.values())
            total_correct += max_in_cluster
            total_samples += cluster_size

    if total_samples == 0:
        return 0.0

    return total_correct / total_samples


def simulate_distinguishing_attack(
    traffic_by_session: Dict[str, List]
) -> Dict:
    """
    Run complete distinguishing attack simulation

    Args:
        traffic_by_session: Dict mapping session_id to traffic records

    Returns:
        Dictionary with full attack simulation results
    """
    if len(traffic_by_session) < 2:
        return {
            "error": "Insufficient sessions for attack simulation",
            "min_sessions_required": 2
        }

    results = {
        "attack_type": "session_distinguishing_attack",
        "timestamp": datetime.utcnow().isoformat(),
        "num_sessions": len(traffic_by_session),
        "classifiers": {},
        "clustering": {}
    }

    # Train multiple classifiers
    model_types = ["random_forest", "naive_bayes"]

    for model_type in model_types:
        # Create dataset
        X, y = create_labeled_dataset(traffic_by_session)

        if len(X) > 0:
            # Train and evaluate
            eval_results = train_and_evaluate_classifier(X, y, model_type)
            results["classifiers"][model_type] = eval_results

    # Run clustering attack
    n_clusters = min(3, len(traffic_by_session))
    clustering_results = run_clustering_attack(traffic_by_session, n_clusters)
    results["clustering"] = clustering_results

    # Determine overall attack effectiveness
    class_results = results["classifiers"]
    if "random_forest" in class_results and "test_accuracy" in class_results["random_forest"]:
        rf_accuracy = class_results["random_forest"]["test_accuracy"]
    else:
        rf_accuracy = 0

    if "clustering" in clustering_results and "silhouette_score" in clustering_results:
        silhouette = clustering_results["silhouette_score"]
    else:
        silhouette = 0

    # Combined effectiveness
    overall_effectiveness = (rf_accuracy + silhouette) / 2

    results["overall_attack_effectiveness"] = {
        "value": round(overall_effectiveness, 4),
        "percentage": round(overall_effectiveness * 100, 2),
        "risk_level": _get_risk_level_from_effectiveness(overall_effectiveness)
    }

    return results


def _get_risk_level_from_effectiveness(effectiveness: float) -> str:
    """
    Convert attack effectiveness to risk level

    Args:
        effectiveness: Attack effectiveness score (0-1)

    Returns:
        Risk level string
    """
    if effectiveness >= 0.8:
        return "critical"
    elif effectiveness >= 0.6:
        return "high"
    elif effectiveness >= 0.4:
        return "medium"
    else:
        return "low"
