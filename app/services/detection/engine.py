"""
Detection rule engine - evaluates rules against traffic
"""
from typing import List, Dict
from collections import Counter
from app.services.detection.loader import RuleLoader, DetectionRule
from app.models import NetworkTraffic, PrivacyLeakEvent, LeakType
from uuid import uuid4
from datetime import datetime
from app.utils import hash_address


class RuleEngine:
    """Engine for evaluating detection rules against traffic records"""

    def __init__(self, rules_dir: str = "app/config/rules"):
        self.loader = RuleLoader(rules_dir)
        self.rules = self.loader.load_rules()

    async def evaluate_session(
        self, session_id: str, traffic_records: List[NetworkTraffic]
    ) -> List[PrivacyLeakEvent]:
        """
        Evaluate all enabled rules against session traffic

        Args:
            session_id: Session UUID
            traffic_records: List of traffic records

        Returns:
            List of detected privacy leak events
        """
        events = []

        for rule in self.loader.get_enabled_rules():
            if await self._matches_conditions(rule, traffic_records):
                event = self._create_leak_event(rule, session_id, traffic_records)
                events.append(event)

        return events

    async def _matches_conditions(
        self, rule: DetectionRule, records: List[NetworkTraffic]
    ) -> bool:
        """Check if traffic records match all rule conditions"""
        for condition in rule.conditions:
            condition_type = condition["type"]

            if condition_type == "method_pattern":
                methods = condition["methods"]
                matching = [r for r in records if r.rpc_method in methods]
                min_freq = condition.get("min_frequency", 1)
                if len(matching) < min_freq:
                    return False

            elif condition_type == "address_pattern":
                # For demo: simplified check
                check_type = condition.get("check", "")
                if check_type == "same_address_across_sessions":
                    # In real implementation, query DB for other sessions
                    pass
                elif check_type == "multiple_addresses_same_session":
                    # Check for multiple unique addresses (simplified)
                    pass

            elif condition_type == "temporal_pattern":
                check_type = condition.get("check", "")
                if check_type == "fixed_request_intervals":
                    result = self._check_fixed_intervals(records, condition)
                    if not result:
                        return False

            elif condition_type == "sequence_pattern":
                result = self._check_sequence_pattern(records, condition)
                if not result:
                    return False

            elif condition_type == "behavior_pattern":
                # Behavioral patterns - simplified for demo
                pass

            elif condition_type == "frequency_pattern":
                result = self._check_frequency_pattern(records, condition)
                if not result:
                    return False

        return True

    def _check_fixed_intervals(self, records: List[NetworkTraffic], condition: Dict) -> bool:
        """Check for fixed request intervals (bot detection)"""
        min_requests = condition.get("min_requests", 10)
        if len(records) < min_requests:
            return False

        timestamps = [r.request_timestamp for r in records if r.request_timestamp]
        if len(timestamps) < min_requests:
            return False

        # Calculate intervals
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i-1]).total_seconds() * 1000
            intervals.append(interval)

        if not intervals:
            return False

        # Check variance
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
        max_variance = condition.get("max_variance_ms", 100)

        return variance < max_variance ** 2

    def _check_sequence_pattern(self, records: List[NetworkTraffic], condition: Dict) -> bool:
        """Check for specific method sequences"""
        sequence = condition.get("sequence", [])
        if not sequence:
            return True

        # Extract methods from records
        methods = [r.rpc_method for r in records if r.rpc_method]

        # Check if sequence appears
        min_sequences = condition.get("min_sequences", 1)
        count = 0
        seq_len = len(sequence)

        for i in range(len(methods) - seq_len + 1):
            subseq = methods[i:i+seq_len]
            if subseq == sequence:
                count += 1
                i += seq_len  # Skip ahead

        return count >= min_sequences

    def _check_frequency_pattern(self, records: List[NetworkTraffic], condition: Dict) -> bool:
        """Check for high frequency patterns"""
        min_freq = condition.get("min_requests_per_second", 2)
        duration = condition.get("duration_seconds", 30)
        methods = condition.get("methods", [])

        # Filter by methods
        if methods:
            records = [r for r in records if r.rpc_method in methods]

        # Group by time windows
        if not records:
            return False

        timestamps = [r.request_timestamp for r in records if r.request_timestamp]
        if not timestamps:
            return False

        # Simple check: total count / duration
        total_time_seconds = (timestamps[-1] - timestamps[0]).total_seconds()
        if total_time_seconds == 0:
            return False

        freq = len(timestamps) / total_time_seconds
        return freq >= min_freq

    def _create_leak_event(
        self, rule: DetectionRule, session_id: str, records: List[NetworkTraffic]
    ) -> PrivacyLeakEvent:
        """Create a privacy leak event from a rule trigger"""
        method_name = records[0].rpc_method if records else "unknown"

        # Get base confidence from actions
        base_confidence = 0.7
        for action in rule.actions:
            if action.get("type") == "create_leak_event":
                base_confidence = action.get("confidence_base", 0.7)
                break

        # Calculate confidence interval (simplified bootstrap)
        ci_low = max(0.0, base_confidence - 0.1)
        ci_high = min(1.0, base_confidence + 0.1)

        # Get details
        details = {
            "rule_id": rule.rule_id,
            "rule_name": rule.name,
            "rule_priority": rule.priority
        }

        # Get a sample address hash (in real implementation, extract from traffic)
        sample_address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"

        return PrivacyLeakEvent(
            id=str(uuid4()),
            session_id=session_id,
            leak_type=LeakType(rule.category),
            method_name=method_name,
            description=rule.description,
            confidence=base_confidence,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            details=details,
            timestamp=records[-1].request_timestamp if records else datetime.utcnow(),
            address_hash=hash_address(sample_address),
            rule_id=rule.rule_id
        )

    def get_all_rules(self) -> List[Dict]:
        """Get all rules as dictionaries"""
        return [
            {
                "id": r.rule_id,
                "name": r.name,
                "category": r.category,
                "enabled": r.enabled,
                "priority": r.priority,
                "description": r.description
            }
            for r in self.rules.values()
        ]

    def get_rules_summary(self) -> Dict:
        """Get summary statistics for rules"""
        total = len(self.rules)
        enabled = len(self.loader.get_enabled_rules())
        by_category = {}

        for rule in self.rules.values():
            cat = rule.category
            if cat not in by_category:
                by_category[cat] = {"total": 0, "enabled": 0}
            by_category[cat]["total"] += 1
            if rule.enabled:
                by_category[cat]["enabled"] += 1

        return {
            "total": total,
            "enabled": enabled,
            "disabled": total - enabled,
            "by_category": by_category
        }
