import pytest

from pyteleport.rule import GitignoreRule


@pytest.fixture
def gitignore_path():
    """Fixture that returns the path to the test .gitignore file"""
    return "dummy/example_gitignore/.gitignore"


@pytest.fixture
def gitignore_rule(gitignore_path):
    """Fixture that returns a GitignoreRule instance loaded from the test .gitignore file"""
    return GitignoreRule.load(gitignore_path)


@pytest.fixture
def empty_rule():
    """Fixture that returns an empty GitignoreRule instance"""
    return GitignoreRule([])


class TestGitignoreRule:
    def test_check_instance(self, gitignore_rule):
        """Test that the GitignoreRule can be instantiated"""
        assert isinstance(gitignore_rule, GitignoreRule)

    @pytest.mark.parametrize(
        "query, expected",
        [
            # Basic patterns
            ("a.txt", False),  # *.txt
            ("subdir/b.txt", False),  # *.txt
            ("docs/a.md", False),  # /docs/*.md
            ("subdir/docs/a.md", True),  # /docs/*.md only matches at root
            # Directory patterns
            ("build", False),  # build/
            ("build/subdir", False),  # build/
            ("logs", False),  # **/logs
            ("app/logs", False),  # **/logs
            (".venv", True),  # .venv/* doesn't match .venv itself
            ("node_modules", False),  # node_modules/**
            # Files in excluded directories
            ("build/a.log", False),  # build/
            ("build/subdir/file.js", False),  # build/
            ("logs/error.log", False),  # **/logs
            ("app/logs/debug.log", False),  # **/logs
            (".venv/lib/file.py", False),  # .venv/*
            ("node_modules/package.json", False),  # node_modules/**
            ("node_modules/subdir/file.js", False),  # node_modules/**
            # Complex patterns
            ("a/b", False),  # a/**/b
            ("a/x/y/b", False),  # a/**/b
            ("a/x/y/b/c", False),  # a/**/b doesn't match children
            # Log patterns
            ("error.log", False),  # *log
            ("system.log", False),  # *log
            ("logs.txt", False),  # *log
            ("import.log", True),  # !import.log (negation)
            # Character classes and wildcards
            ("temp1", False),  # temp[0-9]/
            ("temp9", False),  # temp[0-9]/
            ("tempA", True),  # tempA/ doesn't match temp[0-9]/
            ("temp1/file.txt", False),  # temp[0-9]/
            ("file1.js", False),  # file?.js
            ("fileA.js", False),  # file?.js
            ("files.js", False),  # file?.js
            # Root-level patterns
            ("root-only.mdc", False),  # /root-only.txt
            ("subdir/root-only.mdc", True),  # /root-only.txt only at root
            # Nested patterns
            ("src/components/test/button.spec.js", False),  # src/**/test/**/*.spec.js
            ("src/test/utils/format.spec.js", False),  # src/**/test/**/*.spec.js
            ("src/components/button.js", True),  # not a spec file in test dir
            # New patterns
            (".env", False),  # .env*
            (".env.local", False),  # .env*
            (".env.example", True),  # !.env.example (negation)
            ("dist/bundle.js", False),  # dist/*
            ("dist/.gitkeep", True),  # !dist/.gitkeep (negation)
            (".cache", False),  # **/.cache/
            ("src/components/.cache", False),  # **/.cache/
            (".cache/tmp.file", False),  # **/.cache/
            ("src/components/.cache/data.json", False),  # **/.cache/
        ],
    )
    def test_check_match_and_exclude(self, gitignore_rule, query, expected):
        """
        Test that files are correctly matched or excluded based on gitignore rules

        Parameters:
        - query: The file path to check
        - expected: True if the file should be included, False if it should be ignored
        """
        assert gitignore_rule.matches(query) == expected
        assert not gitignore_rule.is_exclude(query) == expected

    @pytest.mark.parametrize(
        "query, expected_match",
        [
            # Negation rules
            ("import.log", True),  # !import.log negates *log
            ("export.log", False),  # *log applies
            # Environment files
            (".env.example", True),  # !.env.example negates .env*
            (".env.local", False),  # .env* applies
        ],
    )
    def test_rule_precedence(self, gitignore_rule, query, expected_match):
        """Test that later rules override earlier rules, and negation works correctly"""
        assert gitignore_rule.matches(query) == expected_match
        assert gitignore_rule.is_exclude(query) != expected_match

    @pytest.mark.parametrize(
        "dir_path, file_path",
        [
            ("build", "build/output.txt"),  # build/ pattern
            ("node_modules", "node_modules/package.json"),  # node_modules/** pattern
            ("src/components/.cache", "src/components/.cache/data.json"),  # **/.cache/ pattern
        ],
    )
    def test_directory_vs_file_patterns(self, gitignore_rule, dir_path, file_path):
        """Test the difference between directory and file pattern matching"""
        # Both directory and its contents should be excluded
        assert gitignore_rule.is_exclude(dir_path)
        assert gitignore_rule.is_exclude(file_path)

    @pytest.mark.parametrize(
        "path, expected_is_dir",
        [
            # Files with extensions
            ("file.txt", False),
            ("path/to/script.py", False),
            ("some/path/image.jpg", False),
            # Paths without extensions (directories)
            ("directory", True),
            ("path/to/folder", True),
            # Wildcard patterns
            ("*.py", False),
            ("file.*", False),
            # Paths with explicit directory marker
            ("directory/", True),
            ("path/to/folder/", True),
            # Edge cases
            (".gitignore", False),  # Hidden file with no extension
            (".git", True),  # Hidden directory (common convention)
        ],
    )
    def test_suffix_weak_hint(self, empty_rule, path, expected_is_dir):
        """Test the suffix_weak_hint method that determines if a path is a directory or file"""
        assert empty_rule.suffix_weak_hint(path) == expected_is_dir

    @pytest.mark.parametrize(
        "path1, path2",
        [
            # With and without leading ./
            ("import.log", "./import.log"),
            ("build/output.txt", "./build/output.txt"),
            # With and without trailing /
            ("build", "build/"),
            ("node_modules", "node_modules/"),
        ],
    )
    def test_path_normalization(self, gitignore_rule, path1, path2):
        """Test that paths are properly normalized before matching"""
        assert gitignore_rule.matches(path1) == gitignore_rule.matches(path2)
