import os
from typing import Any, Dict, List

from pyteleport.rule import (
    CompositeRule,
    DirRule,
    GitignoreRule,
    GlobRule,
    HiddenFileRule,
)


class RuleFactory:
    @staticmethod
    def create_rule(rule_type: str, **kwargs) -> CompositeRule:
        if rule_type == "glob":
            rule = GlobRule(
                include_patterns=kwargs.get("include_patterns"),
                exclude_patterns=kwargs.get("exclude_patterns"),
            )
            return rule
            # return CompositeRule(rules=[rule])
        elif rule_type == "gitignore":
            if "gitignore_path" not in kwargs:
                if os.path.exists("./.gitignore"):
                    rules = GitignoreRule.load("./.gitignore")
                    return CompositeRule(rules=[rules])
                raise ValueError("gitignore_path is required")
            rules = GitignoreRule.load(kwargs.get("gitignore_path"))
            return CompositeRule(rules=[rules])

        elif rule_type == "hidden_file":
            return CompositeRule(rules=[HiddenFileRule()])

        elif rule_type == "dir":
            return CompositeRule(rules=[DirRule()])

        elif rule_type == "composite":
            if "rules" not in kwargs:
                raise ValueError("rules is required for composite rule")
            rules_config = kwargs.get("rules")
            rules = []
            for rule_config in rules_config:
                config_copy = rule_config.copy()
                rule_type = config_copy.pop("type")
                rules.append(RuleFactory.create_rule(rule_type, **config_copy))
            return CompositeRule(rules=rules)

        else:
            raise ValueError(f"Invalid rule type: {rule_type}")

    @staticmethod
    def create_composite_rule(rule_configs: List[Dict[str, Any]]) -> CompositeRule:
        """
        Create a composite rule from a list of rule configurations.

        Args:
            rule_configs: List of rule configurations, each containing a 'type' key and other parameters

        Returns:
            A CompositeRule that combines all the specified rules

        Example:
            >>> rule_configs = [
            ...     {"type": "glob", "include_patterns": ["*.py"]},
            ...     {"type": "hidden_file"}
            ... ]
            >>> rule = RuleFactory.create_composite_rule(rule_configs)
        """
        rules = []
        for config in rule_configs:
            config_copy = config.copy()
            rule_type = config_copy.pop("type")
            rule = RuleFactory.create_rule(rule_type, **config_copy)
            rules.append(rule)
        return CompositeRule(rules=rules)
