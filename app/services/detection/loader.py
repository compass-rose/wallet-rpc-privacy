"""
Rule loader - loads YAML-based detection rules
"""
import yaml
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class DetectionRule:
    """Detection rule dataclass"""
    rule_id: str
    name: str
    category: str
    priority: str
    enabled: bool
    description: str
    conditions: List[Dict]
    actions: List[Dict]
    version: int = 1


class RuleLoader:
    """Loads detection rules from YAML files"""

    def __init__(self, rules_dir: str = "app/config/rules"):
        self.rules_dir = Path(rules_dir)
        self.rules: Dict[str, DetectionRule] = {}

    def load_rules(self) -> Dict[str, DetectionRule]:
        """
        Load all YAML rule files from rules directory

        Returns:
            Dictionary mapping rule_id to DetectionRule
        """
        if not self.rules_dir.exists():
            print(f"Warning: Rules directory {self.rules_dir} does not exist")
            return {}

        for yaml_file in self.rules_dir.rglob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    rule_data = yaml.safe_load(f)

                rule = DetectionRule(
                    rule_id=rule_data["rule_id"],
                    name=rule_data["name"],
                    category=rule_data["category"],
                    priority=rule_data["priority"],
                    enabled=rule_data["enabled"],
                    description=rule_data["description"],
                    conditions=rule_data["conditions"],
                    actions=rule_data["actions"],
                    version=rule_data.get("version", 1)
                )
                self.rules[rule.rule_id] = rule

            except Exception as e:
                print(f"Error loading rule file {yaml_file}: {e}")

        return self.rules

    def get_enabled_rules(self) -> List[DetectionRule]:
        """Get list of enabled rules"""
        return [r for r in self.rules.values() if r.enabled]

    def get_rule(self, rule_id: str) -> DetectionRule | None:
        """Get rule by ID"""
        return self.rules.get(rule_id)

    def get_rules_by_category(self, category: str) -> List[DetectionRule]:
        """Get rules filtered by category"""
        return [r for r in self.rules.values() if r.category == category]
