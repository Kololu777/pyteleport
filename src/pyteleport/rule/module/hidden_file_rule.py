from pyteleport.rule import BaseRule


class HiddenFileRule(BaseRule):
    """
    Judge if a query matches the hidden file rule.

    Example:
        >>> rule = HiddenFileRule(hidden_file=True)
        >>> rule.matches("test.py") # not hidden file
        False
        >>> rule.matches(".hidden.py") # hidden file
        True
        >>> rule.is_exclude("test.py") # not hidden file
        False
        >>> rule.is_exclude(".hidden.py") # hidden file
        True
    """

    def matches(self, query: str) -> bool:
        if self.is_include(query): # not hidden file
            return True
        return False # hidden file

    def is_include(self, query: str) -> bool:
        return not query.startswith(".") # not hidden file

    def is_exclude(self, query: str) -> bool:
        return query.startswith(".") # hidden file
