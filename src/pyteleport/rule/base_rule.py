from abc import ABC, abstractmethod


class BaseRule(ABC):
    @abstractmethod
    def matches(self, query: str) -> bool:
        """
        Check if the query matches the inherited rule.
        Args:
            query: The query to check against the rule.

        Returns:
            bool: True if the query matches the rule, False otherwise.
        """

        """sample_code:
        if self.is_include(query):
            return True
        if self.is_exclude(query):
            return False
        return True
        """
        raise NotImplementedError

    @abstractmethod
    def is_include(self, query: str) -> bool:
        """
        Check if the query matches the include-pattern.
        """
        raise NotImplementedError

    @abstractmethod
    def is_exclude(self, query: str) -> bool:
        """
        Check if the query matches the exclude-pattern.

        Args:
            query: The query to check against the rule.

        Returns:
            bool: True if the query matches the rule, False otherwise.
        """
        raise NotImplementedError
