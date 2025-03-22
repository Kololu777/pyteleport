from pyteleport.rule import CompositeRule, GlobRule, HiddenFileRule


class TestCompositeRuleMatches:
    def test_init(self):
        """Test initialization of CompositeRule."""
        rule1 = GlobRule(include_patterns=["*.py"])
        rule2 = HiddenFileRule()
        composite_rule = CompositeRule(rules=[rule1, rule2])

        assert len(composite_rule.rules) == 2
        assert composite_rule.rules[0] == rule1
        assert composite_rule.rules[1] == rule2

    def test_matches_all_rules(self):
        """Test that matches() returns True only if all rules match."""
        # Create rules
        glob_rule = GlobRule(include_patterns=["*.py"], exclude_patterns=["test_*.py"])
        hidden_rule = HiddenFileRule()
        composite_rule = CompositeRule(rules=[glob_rule, hidden_rule])

        # Should match both rules
        assert composite_rule.matches("example.py") is True

        # Doesn't match glob_rule (excluded pattern)
        assert composite_rule.matches("test_example.py") is False

        # Doesn't match hidden_rule
        assert composite_rule.matches(".example.py") is False

        # Doesn't match either rule
        assert composite_rule.matches(".test_example.py") is False

    def test_is_include_any_rule(self):
        """Test that is_include() returns True if any rule includes."""
        # Create rules
        glob_rule = GlobRule(include_patterns=["*.py"], exclude_patterns=["test_*.py"])
        hidden_rule = HiddenFileRule()
        composite_rule = CompositeRule(rules=[glob_rule, hidden_rule])

        # Included by glob_rule
        assert composite_rule.is_include("example.py")

        # Not included by either rule
        assert composite_rule.is_include("test_example.py")

        # Not included by either rule
        assert composite_rule.is_include(".example.py")

        # Not included by either rule
        assert composite_rule.is_include(".test_example.py")

    def test_is_exclude_any_rule(self):
        """Test that is_exclude() returns True if any rule excludes."""
        # Create rules
        glob_rule = GlobRule(include_patterns=["*.py"], exclude_patterns=["test_*.py"])
        hidden_rule = HiddenFileRule()
        composite_rule = CompositeRule(rules=[glob_rule, hidden_rule])

        # Not excluded by either rule
        assert composite_rule.is_exclude("example.py") is False

        # Excluded by glob_rule
        assert composite_rule.is_exclude("test_example.py") is True

        # Excluded by hidden_rule
        assert composite_rule.is_exclude(".example.py") is True

        # Excluded by both rules
        assert composite_rule.is_exclude(".test_example.py") is True

    def test_empty_rules_list(self):
        """Test behavior with empty rules list."""
        composite_rule = CompositeRule(rules=[])

        # With no rules, all() returns True for empty iterables
        assert composite_rule.matches("any_file.txt") is True

        # With no rules, any() returns False for empty iterables
        assert composite_rule.is_include("any_file.txt") is False
        assert composite_rule.is_exclude("any_file.txt") is False

    def test_nested_composite_rules(self):
        """Test nesting composite rules."""
        # Create individual rules
        py_rule = GlobRule(include_patterns=["*.py"])
        js_rule = GlobRule(include_patterns=["*.js"])
        hidden_rule = HiddenFileRule()

        # Create first composite rule - matches either .py OR .js files
        # This is an OR condition because we're checking if ANY rule matches
        code_files_rule = CompositeRule(rules=[])
        code_files_rule.matches = lambda query: py_rule.matches(
            query
        ) or js_rule.matches(query)
        code_files_rule.is_exclude = lambda query: py_rule.is_exclude(
            query
        ) and js_rule.is_exclude(query)

        # Create nested composite rule
        nested_rule = CompositeRule(rules=[code_files_rule, hidden_rule])

        # Should match all rules
        assert nested_rule.matches("example.py") is True
        assert nested_rule.matches("example.js") is True

        # Doesn't match code_rule
        assert nested_rule.matches("example.txt") is False

        # Doesn't match hidden_rule
        assert nested_rule.matches(".example.py") is False
        assert nested_rule.matches(".example.js") is False

    def test_append_rule(self):
        """Test appending a rule to a composite rule."""
        # Create individual rules
        glob_rule = GlobRule(include_patterns=["*.py"])
        hidden_rule = HiddenFileRule()

        composite_rule = CompositeRule(rules=[])
        composite_rule.append(glob_rule)
        assert len(composite_rule.rules) == 1

        composite_rule2 = CompositeRule(rules=[hidden_rule])
        composite_rule.append(composite_rule2)
        assert len(composite_rule.rules) == 2
        assert composite_rule.rules[0] == glob_rule
        assert composite_rule.rules[1] == hidden_rule
