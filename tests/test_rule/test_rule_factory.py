import os
from unittest.mock import patch

import pytest

from pyteleport.rule import (
    BaseRule,
    CompositeRule,
    GitignoreRule,
    GlobRule,
    HiddenFileRule,
)
from pyteleport.rule.rule_factory import RuleFactory


class TestRuleFactory:
    def test_create_glob_rule(self):
        """Test creating a GlobRule."""
        rule = RuleFactory.create_rule(
            "glob", include_patterns=["*.py"], exclude_patterns=["test_*.py"]
        )

        assert isinstance(rule, GlobRule)
        assert rule.include_patterns == ["*.py"]
        assert rule.exclude_patterns == ["test_*.py"]

    def test_create_hidden_file_rule(self):
        """Test creating a HiddenFileRule."""
        rule = RuleFactory.create_rule("hidden_file")

        assert isinstance(rule, HiddenFileRule)

    @patch("os.path.exists")
    def test_create_gitignore_rule_with_path(self, mock_exists):
        """Test creating a GitignoreRule with a specified path."""
        with patch.object(GitignoreRule, "load") as mock_load:
            mock_exists.return_value = True
            mock_load.return_value = GitignoreRule([])

            rule = RuleFactory.create_rule(
                "gitignore", gitignore_path="/path/to/.gitignore"
            )

            mock_load.assert_called_once_with("/path/to/.gitignore")
            assert isinstance(rule, GitignoreRule)

    @patch("os.path.exists")
    def test_create_gitignore_rule_default_path(self, mock_exists):
        """Test creating a GitignoreRule with default path."""
        with patch.object(GitignoreRule, "load") as mock_load:
            mock_exists.return_value = True
            mock_load.return_value = GitignoreRule([])

            rule = RuleFactory.create_rule("gitignore")

            mock_load.assert_called_once_with("./.gitignore")
            assert isinstance(rule, GitignoreRule)

    @patch("os.path.exists")
    def test_create_gitignore_rule_missing_path(self, mock_exists):
        """Test creating a GitignoreRule with missing path."""
        mock_exists.return_value = False

        with pytest.raises(ValueError, match="gitignore_path is required"):
            RuleFactory.create_rule("gitignore")

    def test_create_invalid_rule_type(self):
        """Test creating an invalid rule type."""
        with pytest.raises(ValueError, match="Invalid rule type: invalid"):
            RuleFactory.create_rule("invalid")

    def test_create_composite_rule(self):
        """Test creating a CompositeRule using create_rule."""
        rules_config = [
            {"type": "glob", "include_patterns": ["*.py"]},
            {"type": "hidden_file"},
        ]

        rule = RuleFactory.create_rule("composite", rules=rules_config)

        assert isinstance(rule, CompositeRule)
        assert len(rule.rules) == 2
        assert isinstance(rule.rules[0], GlobRule)
        assert isinstance(rule.rules[1], HiddenFileRule)

    def test_create_composite_rule_missing_rules(self):
        """Test creating a CompositeRule without rules parameter."""
        with pytest.raises(ValueError, match="rules is required for composite rule"):
            RuleFactory.create_rule("composite")

    def test_create_composite_rule_helper(self):
        """Test the create_composite_rule helper method."""
        rule_configs = [
            {"type": "glob", "include_patterns": ["*.py"]},
            {"type": "hidden_file"},
        ]

        rule = RuleFactory.create_composite_rule(rule_configs)

        assert isinstance(rule, CompositeRule)
        assert len(rule.rules) == 2
        assert isinstance(rule.rules[0], GlobRule)
        assert isinstance(rule.rules[1], HiddenFileRule)

    def test_nested_composite_rule(self):
        """Test creating a nested CompositeRule."""
        # Define a nested structure
        rule_configs = [
            {
                "type": "composite",
                "rules": [
                    {"type": "glob", "include_patterns": ["*.py"]},
                    {"type": "glob", "include_patterns": ["*.js"]},
                ],
            },
            {"type": "hidden_file"},
        ]

        rule = RuleFactory.create_composite_rule(rule_configs)

        # Verify structure
        assert isinstance(rule, CompositeRule)
        assert len(rule.rules) == 2

        # First rule should be a composite
        assert isinstance(rule.rules[0], CompositeRule)
        assert len(rule.rules[0].rules) == 2
        assert isinstance(rule.rules[0].rules[0], GlobRule)
        assert isinstance(rule.rules[0].rules[1], GlobRule)

        # Second rule should be a hidden file rule
        assert isinstance(rule.rules[1], HiddenFileRule)
