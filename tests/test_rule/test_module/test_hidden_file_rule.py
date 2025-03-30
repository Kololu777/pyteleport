import pytest

from pyteleport.rule import HiddenFileRule


class TestHiddenFileRule:
    @pytest.mark.parametrize(
        "file_name, expected", [("test.py", True), (".hidden.py", False)]
    )
    def test_matches(self, file_name, expected):
        rule = HiddenFileRule()
        assert rule.matches(file_name) == expected

    @pytest.mark.parametrize(
        "file_name, expected", [("test.py", True), (".hidden.py", False)]
    )
    def test_is_include(self, file_name, expected):
        rule = HiddenFileRule()
        assert rule.is_include(file_name) == expected

    @pytest.mark.parametrize(
        "file_name, expected", [("test.py", False), (".hidden.py", True)]
    )
    def test_is_exclude(self, file_name, expected):
        rule = HiddenFileRule()
        assert rule.is_exclude(file_name) == expected
