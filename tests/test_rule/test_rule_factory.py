import os
from unittest.mock import MagicMock

import pytest

from pyteleport.rule import (
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
def test_create_gitignore_rule_with_path(gitignore_path, monkeypatch):
    """Test creating a GitignoreRule with a specified path."""
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(GitignoreRule, "load", lambda path: GitignoreRule([]))

    rule = RuleFactory.create_rule("gitignore", gitignore_path=gitignore_path)

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 1
    assert isinstance(rule.rules[0], GitignoreRule)


def test_create_gitignore_rule_default_path(monkeypatch):
    """Test creating a GitignoreRule with default path."""
    monkeypatch.setattr(os.path, "exists", lambda path: True)

    mock_load = MagicMock(return_value=GitignoreRule([]))
    monkeypatch.setattr(GitignoreRule, "load", mock_load)

    rule = RuleFactory.create_rule("gitignore")

    mock_load.assert_called_once_with("./.gitignore")
    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 1
    assert isinstance(rule.rules[0], GitignoreRule)


def test_create_gitignore_rule_missing_path(monkeypatch):
    """Test creating a GitignoreRule with missing path."""
    monkeypatch.setattr(os.path, "exists", lambda path: False)

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


# Simplified tests for simplify_create_rule
def test_simplify_create_rule_basic():
    """Test simplify_create_rule with basic include and exclude patterns."""
    include_patterns = ["*.py"]
    exclude_patterns = ["test_*.py"]

    rule = RuleFactory.simplify_create_rule(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
    )

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 1
    assert isinstance(rule.rules[0], GlobRule)
    assert rule.rules[0].include_patterns == include_patterns
    assert rule.rules[0].exclude_patterns == exclude_patterns


def test_simplify_create_rule_with_hidden_file():
    """Test simplify_create_rule with HIDDEN special word."""
    include_patterns = ["*.py"]
    exclude_patterns = ["test_*.py"]
    special_words = "HIDDEN"  # Using the actual uppercase key from constants

    rule = RuleFactory.simplify_create_rule(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        special_words=special_words,
    )

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 2

    # Find the hidden file rule and glob rule
    hidden_file_rule = None
    glob_rule = None

    for r in rule.rules:
        if isinstance(r, CompositeRule) and isinstance(r.rules[0], HiddenFileRule):
            hidden_file_rule = r
        elif isinstance(r, GlobRule):
            glob_rule = r

    assert hidden_file_rule is not None, "Hidden file rule not found"
    assert glob_rule is not None, "Glob rule not found"
    assert glob_rule.include_patterns == include_patterns
    assert glob_rule.exclude_patterns == exclude_patterns


def test_simplify_create_rule_with_dir():
    """Test simplify_create_rule with DIR special word."""
    include_patterns = ["*.py"]
    exclude_patterns = ["test_*.py"]
    special_words = "DIR"  # Using the actual uppercase key from constants

    rule = RuleFactory.simplify_create_rule(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        special_words=special_words,
    )

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 2

    # Find the dir rule and glob rule
    dir_rule = None
    glob_rule = None

    for r in rule.rules:
        if isinstance(r, CompositeRule) and isinstance(r.rules[0], DirRule):
            dir_rule = r
        elif isinstance(r, GlobRule):
            glob_rule = r

    assert dir_rule is not None, "Dir rule not found"
    assert glob_rule is not None, "Glob rule not found"
    assert glob_rule.include_patterns == include_patterns
    assert glob_rule.exclude_patterns == exclude_patterns


def test_simplify_create_rule_with_gitignore(monkeypatch):
    """Test simplify_create_rule with GITIGNORE special word and path."""
    include_patterns = ["*.py"]
    exclude_patterns = ["test_*.py"]
    special_words = "GITIGNORE"  # Using the actual uppercase key from constants
    gitignore_path = "./gitignore"

    # We still need to mock these for the test to work
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(GitignoreRule, "load", lambda path: GitignoreRule([]))

    rule = RuleFactory.simplify_create_rule(
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        special_words=special_words,
        gitignore_path=gitignore_path,
    )

    assert isinstance(rule, CompositeRule)
    assert len(rule.rules) == 2

    # Find the gitignore rule and glob rule
    gitignore_rule = None
    glob_rule = None

    for r in rule.rules:
        if isinstance(r, CompositeRule) and isinstance(r.rules[0], GitignoreRule):
            gitignore_rule = r
        elif isinstance(r, GlobRule):
            glob_rule = r

    assert gitignore_rule is not None, "Gitignore rule not found"
    assert glob_rule is not None, "Glob rule not found"
    assert glob_rule.include_patterns == include_patterns
    assert glob_rule.exclude_patterns == exclude_patterns
