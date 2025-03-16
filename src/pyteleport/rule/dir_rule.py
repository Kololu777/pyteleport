import os

from pyteleport.rule import BaseRule


class DirRule(BaseRule):
    def __init__(self):
        super().__init__()

    def matches(self, query: str) -> bool:
        if self.is_include(query):  # dir
            return True
        else:  # file
            return False

    def is_include(self, query: str) -> bool:
        return os.path.isdir(query)

    def is_exclude(self, query: str) -> bool:
        return not os.path.isdir(query)
