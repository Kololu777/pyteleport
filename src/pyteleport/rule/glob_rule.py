import fnmatch

from pyteleport.rule import BaseRule


class GlobRule(BaseRule):
    """
    Judge if a query matches the glob rule.

    Args:
        include_patterns: List of glob patterns to include. Default is [".*"] to include everything.
        exclude_patterns: List of glob patterns to exclude. Default is None.

    Examples(Asterisk):
    >>> rule = GlobRule(include_patterns=["*.txt"], exclude_patterns=["*.log"])
    >>> rule.matches("test.txt")
    True
    >>> rule.matches("test.log")
    False

    Examples(Bracket):
    >>> rule = GlobRule(include_patterns=["[a-c].txt"])
    >>> rule.matches("a.txt")
    True
    >>> rule.matches("d.txt")
    False
    """

    def __init__(
        self, include_patterns: list[str] = None, exclude_patterns: list[str] = None
    ):
        super().__init__()
        self.include_patterns = (
            include_patterns if include_patterns is not None else [".*"]
        )
        self.exclude_patterns = exclude_patterns if exclude_patterns is not None else []

    def matches(self, query: str) -> bool:
        # First check if it's excluded
        if self.is_include(query):
            return True
        
        if self.is_exclude(query):
            return False
        return True

    def is_include(self, query: str) -> bool:
        """
        Check if the query matches the include patterns.
        """
        return any(fnmatch.fnmatch(query, pattern) for pattern in self.include_patterns)

    def is_exclude(self, query: str) -> bool:
        """
        Check if the query matches the exclude patterns.
        """
        return any(fnmatch.fnmatch(query, pattern) for pattern in self.exclude_patterns)
