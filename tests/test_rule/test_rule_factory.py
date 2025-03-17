import os
from unittest.mock import MagicMock, patch

import pytest

from pyteleport.rule import (
    BaseRule,
    CompositeRule,
    DirRule,
    GitignoreRule,
    GlobRule,
    HiddenFileRule,
)
from pyteleport.rule.rule_factory import RuleFactory


@pytest.fixture
def glob_rule_params():
    return {"include_patterns": ["*.py"], "exclude_patterns": ["test_*.py"]}


@pytest.fixture
def composite_rule_config():
    return [
        {"type": "glob", "include_patterns": ["*.py"]},
        {"type": "hidden_file"},
    ]


@pytest.fixture
def nested_composite_rule_config():
    return [
        {
            "type": "composite",
            "rules": [
                {"type": "glob", "include_patterns": ["*.py"]},
                {"type": "glob", "include_patterns": ["*.js"]},
            ],
        },
        {"type": "hidden_file"},
    ]


def test_create_glob_rule(glob_rule_params):
    """Test creating a GlobRule."""
    rule = RuleFactory.create_rule("glob", **glob_rule_params)

    assert isinstance(rule, GlobRule)
    assert rule.include_patterns == glob_rule_params["include_patterns"]
    assert rule.exclude_patterns == glob_rule_params["exclude_patterns"]


def test_create_hidden_file_rule():
    """Test creating a HiddenFileRule."""
    rule = RuleFactory.create_rule("hidden_file")

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 1
    assert isinstance(rule.rules[0], HiddenFileRule)


def test_create_dir_rule():
    """Test creating a DirRule."""
    rule = RuleFactory.create_rule("dir")

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 1
    assert isinstance(rule.rules[0], DirRule)


@pytest.mark.parametrize(
    "gitignore_path",
    [
        "/path/to/.gitignore",
    ],
)
def test_create_gitignore_rule_with_path(gitignore_path):
    """Test creating a GitignoreRule with a specified path."""
    with (
        patch("os.path.exists") as mock_exists,
        patch.object(GitignoreRule, "load") as mock_load,
    ):
        mock_exists.return_value = True
        mock_load.return_value = GitignoreRule([])

        rule = RuleFactory.create_rule("gitignore", gitignore_path=gitignore_path)

        mock_load.assert_called_once_with(gitignore_path)
        assert isinstance(rule, CompositeRule)
        assert len(rule.rules) == 1
        assert isinstance(rule.rules[0], GitignoreRule)


def test_create_gitignore_rule_default_path():
    """Test creating a GitignoreRule with default path."""
    with (
        patch("os.path.exists") as mock_exists,
        patch.object(GitignoreRule, "load") as mock_load,
    ):
        mock_exists.return_value = True
        mock_load.return_value = GitignoreRule([])

        rule = RuleFactory.create_rule("gitignore")

        mock_load.assert_called_once_with("./.gitignore")
        assert isinstance(rule, CompositeRule)
        assert len(rule.rules) == 1
        assert isinstance(rule.rules[0], GitignoreRule)


def test_create_gitignore_rule_missing_path():
    """Test creating a GitignoreRule with missing path."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = False

        with pytest.raises(ValueError, match="gitignore_path is required"):
            RuleFactory.create_rule("gitignore")


def test_create_invalid_rule_type():
    """Test creating an invalid rule type."""
    with pytest.raises(ValueError, match="Invalid rule type: invalid"):
        RuleFactory.create_rule("invalid")


def test_create_composite_rule(composite_rule_config):
    """Test creating a CompositeRule using create_rule."""
    rule = RuleFactory.create_rule("composite", rules=composite_rule_config)

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], GlobRule)
    assert isinstance(rule.rules[1], CompositeRule)
    assert len(rule.rules[1].rules) == 1
    assert isinstance(rule.rules[1].rules[0], HiddenFileRule)


def test_create_composite_rule_missing_rules():
    """Test creating a CompositeRule without rules parameter."""
    with pytest.raises(ValueError, match="rules is required for composite rule"):
        RuleFactory.create_rule("composite")


def test_create_composite_rule_helper(composite_rule_config):
    """Test the create_composite_rule helper method."""
    rule = RuleFactory.create_composite_rule(composite_rule_config)

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 2
    assert isinstance(rule.rules[0], GlobRule)
    assert isinstance(rule.rules[1], CompositeRule)
    assert len(rule.rules[1].rules) == 1
    assert isinstance(rule.rules[1].rules[0], HiddenFileRule)


def test_nested_composite_rule(nested_composite_rule_config):
    """Test creating a nested CompositeRule."""
    rule = RuleFactory.create_composite_rule(nested_composite_rule_config)

    # Verify structure
    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 2

    # First rule should be a composite
    assert isinstance(rule.rules[0], CompositeRule)
    assert len(rule.rules[0].rules) == 2
    assert isinstance(rule.rules[0].rules[0], GlobRule)
    assert isinstance(rule.rules[0].rules[1], GlobRule)

    # Second rule should be a composite containing a hidden file rule
    assert isinstance(rule.rules[1], CompositeRule)
    assert len(rule.rules[1].rules) == 1
    assert isinstance(rule.rules[1].rules[0], HiddenFileRule)
