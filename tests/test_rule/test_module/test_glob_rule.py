import pytest

from pyteleport.rule import GlobRule


class TestGlobRule:
    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("a/b/c/test.py", True, False, True),
            ("a/b/c/test.png", False, True, False),
            ("a/b/c/test.txt", True, False, True),
            ("a/b/c/test.jpg", False, True, False),
        ],
    )
    def test_check_single_asterisk(
        self, query, expected_include, expected_exclude, expected_matches
    ):
        glob_rule = GlobRule(
            include_patterns=["*.py", "*.txt"], exclude_patterns=["*.png", "*.jpg"]
        )

        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches

    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("src/main.py", True, False, True),
            ("src/utils/helper.py", True, False, True),
            ("src/test/utils/test_helper.py", False, True, False),
            ("src/utils/main/app.py", True, False, True),
        ],
    )
    def test_check_double_asterisk(
        self, query, expected_include, expected_exclude, expected_matches
    ):
        glob_rule = GlobRule(
            include_patterns=["**/*.py"], exclude_patterns=["**/test/**/*.py"]
        )

        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches

    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("filea.txt", True, False, True),
            ("fileb.txt", True, False, True),
            ("file1.txt", False, True, False),
            ("file.txt", False, True, False),
            ("file12.txt", False, True, False),
        ],
    )
    def test_check_question_mark(
        self, query, expected_include, expected_exclude, expected_matches
    ):
        glob_rule = GlobRule(
            include_patterns=["file?.txt"],
            exclude_patterns=["file[0-9].txt", "file.txt", "file12.txt"],
        )

        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches

    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("a.txt", True, False, True),
            ("b.txt", True, False, True),
            ("c.txt", True, False, True),
            ("d.txt", False, True, False),
            ("ab.txt", False, True, False),
            ("filex.py", True, False, True),
            ("filey.py", True, False, True),
            ("filez.py", True, False, True),
            ("filew.py", False, True, False),
        ],
    )
    def test_check_bracket(
        self, query, expected_include, expected_exclude, expected_matches
    ):
        # [a-c].txt -> a.txt, b.txt, c.txt are ok, ab.txt -> ng
        glob_rule = GlobRule(
            include_patterns=["[a-c].txt", "file[xyz].py"],
            exclude_patterns=["d.txt", "ab.txt", "filew.py"],
        )

        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches

    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("a.txt", False, True, False),
            ("b.txt", False, True, False),
            ("c.txt", False, True, False),
            ("d.txt", True, False, True),
            ("z.txt", True, False, True),
            ("ab.txt", False, True, False),  # Not a single character
        ],
    )
    def test_check_bracket_negation(
        self, query, expected_include, expected_exclude, expected_matches
    ):
        # [!a-c].txt -> not a.txt, b.txt, c.txt
        glob_rule = GlobRule(
            include_patterns=["[!a-c].txt"],
            exclude_patterns=["a.txt", "b.txt", "c.txt", "ab.txt"],
        )

        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches

    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("a.txt", True, False, True),
            ("b.txt", True, False, True),
            ("c.txt", True, False, True),
            ("d.txt", False, True, False),
            ("e.txt", False, True, False),
            ("ab.txt", False, True, False),  # Not a single character
        ],
    )
    def test_check_bracket_specific_chars(
        self, query, expected_include, expected_exclude, expected_matches
    ):
        # [abc].txt matches exactly a.txt, b.txt, and c.txt
        glob_rule = GlobRule(
            include_patterns=["[abc].txt"],
            exclude_patterns=["d.txt", "e.txt", "ab.txt"],
        )

        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches

    @pytest.mark.parametrize(
        "query, expected_include, expected_exclude, expected_matches",
        [
            ("sample.py", False, True, False),
            ("sample2.py", False, True, False),
            ("sample.txt", False, True, False),
            ("sample.log", False, True, False),
        ],
    )
    def test_matches(self, query, expected_include, expected_exclude, expected_matches):
        glob_rule = GlobRule(
            include_patterns=["sample.py"],
            exclude_patterns=["*.py", "*.txt"],
        )
        assert glob_rule.is_include(query) == expected_include
        assert glob_rule.is_exclude(query) == expected_exclude
        assert glob_rule.matches(query) == expected_matches
