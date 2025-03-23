import pytest

from pyteleport.core.algorithm import apply_asterisk_rule


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
