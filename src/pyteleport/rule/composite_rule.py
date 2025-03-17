from typing import List

from pyteleport.rule import BaseRule


class CompositeRule(BaseRule):
    """
    A rule that combines multiple rules.

    This rule allows you to use multiple rules together. A query matches if it matches
    all the included rules.

    Example:
        >>> from pyteleport.rule import GlobRule, HiddenFileRule
        >>> rule1 = GlobRule(include_patterns=["*.py"])
        >>> rule2 = HiddenFileRule()
        >>> composite_rule = CompositeRule(rules=[rule1, rule2])
        >>> composite_rule.matches("test.py")  # Matches rule1 and rule2
        True
        >>> composite_rule.matches(".hidden.py")  # Doesn't match rule2
        False
    """

    def __init__(self, rules: List[BaseRule]):
        """
        Initialize a CompositeRule with a list of rules.

        Args:
            rules: List of rules to combine
        """
        self.rules = rules

    def matches(self, query: str) -> bool:
        """
        Check if the query matches all rules.

        Args:
            query: The query to check

        Returns:
            True if the query matches all rules, False otherwise
        """
        return all(rule.matches(query) for rule in self.rules)

    def is_include(self, query: str) -> bool:
        """
        Check if the query is included by any rule.
        """
        return any(rule.is_include(query) for rule in self.rules)

    def is_exclude(self, query: str) -> bool:
        """
        Check if the query is excluded by any rule.

        Args:
            query: The query to check

        Returns:
            True if the query is excluded by any rule, False otherwise
        """
        return any(rule.is_exclude(query) for rule in self.rules)

    def append(self, rule: BaseRule) -> None:
        """
        Append a rule to the composite rule.
        """
        if isinstance(rule, CompositeRule):
            self.rules.extend(rule.rules)
        else:
            self.rules.append(rule)