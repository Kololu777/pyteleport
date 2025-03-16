import pytest

from src.pyteleport.core.algorithm import apply_asterisk_rule


def test_apply_asterisk_rule_prefix():
    """Test applying a rule with asterisk as a prefix."""
    name = "a.py"
    rule = "test_*"
    expected = "test_a.py"
    result = apply_asterisk_rule(name, rule)
    assert result == expected


def test_apply_asterisk_rule_suffix():
    """Test applying a rule with asterisk as a suffix."""
    name = "test"
    rule = "*_suffix"
    expected = "test_suffix"
    result = apply_asterisk_rule(name, rule)
    assert result == expected


def test_apply_asterisk_rule_middle():
    """Test applying a rule with asterisk in the middle."""
    name = "file"
    rule = "prefix_*_suffix"
    expected = "prefix_file_suffix"
    result = apply_asterisk_rule(name, rule)
    assert result == expected


def test_apply_asterisk_rule_multiple_asterisks():
    """Test applying a rule with multiple asterisks."""
    name = "file"
    rule = "*_*"
    expected = "file_file"
    result = apply_asterisk_rule(name, rule)
    assert result == expected


def test_apply_asterisk_rule_no_asterisk():
    """Test applying a rule without an asterisk."""
    name = "file.py"
    rule = "test"
    expected = "test"  # No replacement happens
    result = apply_asterisk_rule(name, rule)
    assert result == expected


# Parametrized test to test multiple cases at once
@pytest.mark.parametrize(
    "name,rule,expected",
    [
        ("a.py", "test_*", "test_a.py"),
        ("test", "*_suffix", "test_suffix"),
        ("file", "prefix_*_suffix", "prefix_file_suffix"),
        ("file", "*_*", "file_file"),
        ("file.py", "test", "test"),
    ],
)
def test_apply_asterisk_rule_parametrized(name, rule, expected):
    """Test apply_asterisk_rule with multiple test cases using parametrize."""
    result = apply_asterisk_rule(name, rule)
    assert result == expected
