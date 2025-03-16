from pyteleport.rule import GlobRule


class TestGlobRule:
    def test_check_single_asterisk(self):
        glob_rule = GlobRule(
            include_patterns=["*.py", "*.txt"], exclude_patterns=["*.png"]
        )

        assert glob_rule.matches("a/b/c/test.py")
        assert not glob_rule.matches("a/b/c/test.png")
        assert glob_rule.matches("a/b/c/test.txt")
        assert not glob_rule.matches("a/b/c/test.jpg")

    def test_check_double_asterisk(self):
        glob_rule = GlobRule(
            include_patterns=["**/*.py"], exclude_patterns=["**/test/**/*.py"]
        )

        assert glob_rule.matches("src/main.py")
        assert glob_rule.matches("src/utils/helper.py")
        assert not glob_rule.matches("src/test/utils/test_helper.py")
        assert glob_rule.matches("src/utils/main/app.py")

    def test_check_question_mark(self):
        glob_rule = GlobRule(
            include_patterns=["file?.txt"], exclude_patterns=["file[0-9].txt"]
        )

        assert glob_rule.matches("filea.txt")
        assert glob_rule.matches("fileb.txt")
        assert not glob_rule.matches("file1.txt")
        assert not glob_rule.matches("file.txt")
        assert not glob_rule.matches("file12.txt")

    def test_check_bracket(self):
        # [a-c].txt -> a.txt, b.txt, c.txt are ok, ab.txt -> ng
        glob_rule = GlobRule(include_patterns=["[a-c].txt", "file[xyz].py"])

        assert glob_rule.matches("a.txt")
        assert glob_rule.matches("b.txt")
        assert glob_rule.matches("c.txt")
        assert not glob_rule.matches("d.txt")
        assert not glob_rule.matches("ab.txt")

        assert glob_rule.matches("filex.py")
        assert glob_rule.matches("filey.py")
        assert glob_rule.matches("filez.py")
        assert not glob_rule.matches("filew.py")

    def test_check_bracket_negation(self):
        # [!a-c].txt -> not a.txt, b.txt, c.txt
        glob_rule = GlobRule(include_patterns=["[!a-c].txt"])

        assert not glob_rule.matches("a.txt")
        assert not glob_rule.matches("b.txt")
        assert not glob_rule.matches("c.txt")
        assert glob_rule.matches("d.txt")
        assert glob_rule.matches("z.txt")
        assert not glob_rule.matches("ab.txt")  # Not a single character

    def test_check_bracket_specific_chars(self):
        # [abc].txt matches exactly a.txt, b.txt, and c.txt
        glob_rule = GlobRule(include_patterns=["[abc].txt"])

        assert glob_rule.matches("a.txt")
        assert glob_rule.matches("b.txt")
        assert glob_rule.matches("c.txt")
        assert not glob_rule.matches("d.txt")
        assert not glob_rule.matches("e.txt")
        assert not glob_rule.matches("ab.txt")  # Not a single character

    def test_is_exclude(self):
        # Test the is_exclude method
        glob_rule = GlobRule(
            include_patterns=["*.py", "*.txt", "*.md"],
            exclude_patterns=["**/test_*.py", "*.log", "temp/*.txt"],
        )

        # Should be excluded
        assert glob_rule.is_exclude("src/test_main.py")
        assert glob_rule.is_exclude("app/utils/test_helper.py")
        assert glob_rule.is_exclude("error.log")
        assert glob_rule.is_exclude("temp/data.txt")

        # Should not be excluded
        assert not glob_rule.is_exclude("src/main.py")
        assert not glob_rule.is_exclude("docs/README.md")
        assert not glob_rule.is_exclude("data/config.txt")
        assert not glob_rule.is_exclude(
            "temp/data.md"
        )  # Only .txt files in temp are excluded
