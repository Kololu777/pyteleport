#!/usr/bin/env python
"""
Example demonstrating how to use CompositeRule and RuleFactory.

This example shows different ways to create and use composite rules
for filtering files based on multiple criteria.
"""

import os

from pyteleport.rule import CompositeRule, GlobRule, HiddenFileRule
from pyteleport.rule.rule_factory import RuleFactory


def print_rule_results(rule, files):
    """Print which files match or are excluded by a rule."""
    print(f"\nTesting rule: {rule.__class__.__name__}")
    print("-" * 50)

    for file in files:
        matches = rule.matches(file)
        excluded = rule.is_exclude(file)
        status = "MATCH" if matches else "EXCLUDED" if excluded else "IGNORED"
        print(f"{file:20} - {status}")


def example_direct_creation():
    """Example of creating a composite rule directly."""
    print("\n=== Example: Direct Creation of CompositeRule ===")

    # Create individual rules
    python_rule = GlobRule(include_patterns=["*.py"], exclude_patterns=["test_*.py"])
    hidden_rule = HiddenFileRule()

    # Create a composite rule that combines both rules
    composite_rule = CompositeRule(rules=[python_rule, hidden_rule])

    # Test with some files
    test_files = [
        "example.py",  # Should match (matches both rules)
        "test_example.py",  # Should not match (excluded by python_rule)
        ".example.py",  # Should not match (excluded by hidden_rule)
        "example.txt",  # Should not match (not included by python_rule)
    ]

    print_rule_results(composite_rule, test_files)


def example_factory_creation():
    """Example of creating a composite rule using RuleFactory."""
    print("\n=== Example: Using RuleFactory to Create CompositeRule ===")

    # Define rule configurations
    rule_configs = [
        {
            "type": "glob",
            "include_patterns": ["*.py", "*.js"],
            "exclude_patterns": ["test_*.py"],
        },
        {"type": "hidden_file"},
    ]

    # Create composite rule using the factory
    composite_rule = RuleFactory.create_composite_rule(rule_configs)

    # Test with some files
    test_files = [
        "example.py",  # Should match (matches both rules)
        "example.js",  # Should match (matches both rules)
        "test_example.py",  # Should not match (excluded by glob rule)
        ".example.js",  # Should not match (excluded by hidden rule)
        "example.txt",  # Should not match (not included by glob rule)
    ]

    print_rule_results(composite_rule, test_files)


def example_nested_rules():
    """Example of creating nested composite rules."""
    print("\n=== Example: Nested Composite Rules ===")

    # Create a custom rule for code files (.py or .js)
    class CodeFilesRule(CompositeRule):
        def __init__(self):
            self.py_rule = GlobRule(include_patterns=["*.py"])
            self.js_rule = GlobRule(include_patterns=["*.js"])
            super().__init__(rules=[self.py_rule, self.js_rule])

        def matches(self, query: str) -> bool:
            # Match if either .py or .js rule matches (OR condition)
            return self.py_rule.matches(query) or self.js_rule.matches(query)

        def is_exclude(self, query: str) -> bool:
            # Exclude if both rules exclude (AND condition)
            return self.py_rule.is_exclude(query) and self.js_rule.is_exclude(query)

    # Create the rules
    code_files_rule = CodeFilesRule()
    hidden_rule = HiddenFileRule()

    # Create the final composite rule
    nested_rule = CompositeRule(rules=[code_files_rule, hidden_rule])

    # Test with some files
    test_files = [
        "example.py",  # Should match
        "example.js",  # Should match
        ".example.py",  # Should not match (hidden file)
        "example.txt",  # Should not match (not a .py or .js file)
    ]

    print_rule_results(nested_rule, test_files)


if __name__ == "__main__":
    example_direct_creation()
    example_factory_creation()
    example_nested_rules()

    print("\nDone!")
