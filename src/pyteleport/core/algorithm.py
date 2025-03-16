def apply_asterisk_rule(name: str, rule: str) -> str:
    """
    Apply the rule to the name.

    Args:
        name: The name of the file or directory.
        rule: The rule to change the name.
    Returns:
        The changed name.
    Examples:
        >>> apply_asterisk_rule("a.py", "test_*")
        "test_a.py"
    """
    if "*" in rule:
        return rule.replace("*", name)
    return rule
