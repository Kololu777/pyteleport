import os
from typing import Any, Dict, List, Optional, Union

from pyteleport.constant import SPECIAL_RULES_RESERVED_WORDS
from pyteleport.rule import (
    BaseRule,
    CompositeRule,
    DirRule,
    GitignoreRule,
    GlobRule,
    HiddenFileRule,
)


class RuleFactory:
    @staticmethod
    def simplify_create_rule(
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        special_words: str | List[str] | None = None,
        **kwargs,
    ) -> CompositeRule:
        rule_configs = []
        if special_words is None:
            special_words = []
        elif isinstance(special_words, str):
            special_words = [special_words]
        for special_word in special_words:
            if special_word in SPECIAL_RULES_RESERVED_WORDS.keys():
                if kwargs.get("gitignore_path") and special_word == "GITIGNORE":
                    rule_configs.append(
                        {
                            "type": SPECIAL_RULES_RESERVED_WORDS[special_word],
                            "gitignore_path": kwargs.get("gitignore_path"),
                        }
                    )
                else:  # hidden_file or dir
                    rule_configs.append(
                        {
                            "type": SPECIAL_RULES_RESERVED_WORDS[special_word],
                        }
                    )

        rule_configs.append(
            {
                "type": "glob",
                "include_patterns": include_patterns,
                "exclude_patterns": exclude_patterns,
            }
        )
        return RuleFactory.create_composite_rule(rule_configs)

    @staticmethod
    def create_rule(rule_type: str, **kwargs) -> Union[BaseRule, CompositeRule]:
        """
        Create a rule based on the specified rule type and parameters.

        Args:
            rule_type: The type of rule to create ('glob', 'gitignore', 'hidden_file', 'dir', 'composite')
            **kwargs: Additional parameters specific to the rule type

        Returns:
            The created rule

        Raises:
            ValueError: If the rule type is invalid or required parameters are missing
        """
        if rule_type == "glob":
            return GlobRule(
                include_patterns=kwargs.get("include_patterns", []),
                exclude_patterns=kwargs.get("exclude_patterns", []),
            )
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
                config_rule_type = config_copy.pop("type")
                rules.append(RuleFactory.create_rule(config_rule_type, **config_copy))
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
