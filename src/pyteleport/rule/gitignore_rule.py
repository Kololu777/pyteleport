import pathspec

from pyteleport.constant import CONFUSING_DIRS
from pyteleport.rule import BaseRule


class GitignoreRule(BaseRule):
    """
    Judge if a query matches the gitignore rule.

    Args:
        include_patterns: List of patterns to include.
        exclude_patterns: List of patterns to exclude.

    Example:
    >>> # Load from .gitignore file
    >>> rule = GitignoreRule(GitignoreRule.load(".gitignore"))
    >>> # Judge if a query matches the gitignore rule
    >>> rule.matches("src/main.py")
    True # src/main.py is included file.
    >>> rule.matches("logs/")
    False # logs/ is excluded file.
    """

    def __init__(self, patterns: list[str] = None):
        super().__init__()
        self.spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    @classmethod
    def load(cls, gitignore_path: str) -> "GitignoreRule":
        """
        Load patterns from a gitignore file.

        Args:
            gitignore_path: Path to the gitignore file.
        """
        with open(gitignore_path, "r") as f:
            patterns = []
            for line in f:
                line = line.strip()
                # comment or empty line, skip
                if line.startswith("#") or line == "":
                    continue
                patterns.append(line)
            print(patterns)
            return cls(patterns)

    def _setup_query(self, query: str, is_dir: bool = False) -> str:
        if is_dir and not query.endswith("/"):
            query = query + "/"
        if not query.startswith("./") or not query.startswith("/"):
            query = "./" + query
        return query

    @staticmethod
    def suffix_weak_hint(query: str) -> bool:
        """
        Check if the query is a file pattern.
        if the query is a file pattern, return False.
        if the query is a directory pattern, return True.

        Note:
            This method is weak because it checks the suffix of the query and only part
            of hidden directory pattern. It may return False for directory patterns.

        Args:
            query: The query to check.

        Returns:
            True if the query is a directory pattern, False otherwise.

        Examples:
            - "*.py", "file.txt" are file patterns (return False)
            - "dir", "temp" without extensions are directory patterns (return True)
        """

        # Check if the query has a file extension or matches common file patterns
        has_extension = "." in query.split("/")[-1] and not query.endswith("/")
        is_wildcard_file = "*." in query or query.endswith(".*")

        # If it has an extension or is a wildcard file pattern, it's a file
        if has_extension or is_wildcard_file:
            for dir in CONFUSING_DIRS:
                if query.endswith(dir):
                    return True
            return False

        # Otherwise, treat it as a directory
        return True

    def _judge_ignore_file(self, query: str, is_dir: bool | None = None) -> bool:
        if is_dir is None:
            is_dir = self.suffix_weak_hint(query)
        query = self._setup_query(query, is_dir)
        return self.spec.match_file(query)

    def matches(self, query: str, is_dir: bool | None = None) -> bool:
        if self.is_include(query, is_dir): # include
            return True
        return False # exclude

    def is_include(self, query: str, is_dir: bool | None = None) -> bool:
        return not self._judge_ignore_file(query, is_dir)

    def is_exclude(self, query: str, is_dir: bool | None = None) -> bool:
        return self._judge_ignore_file(query, is_dir)
