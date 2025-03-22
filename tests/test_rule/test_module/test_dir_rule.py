import pytest

from pyteleport.rule import DirRule


@pytest.fixture
def temp_structure():
    return {
        "test_dir": "./dummy/dummy_test_rule/dummy_dir",
        "test_file": "./dummy/dummy_test_rule/dummy_dir/not_dir.py",
    }


class TestDirRule:
    @pytest.mark.parametrize(
        "path_key, expected",
        [
            ("test_dir", True),
            ("test_file", False),
        ],
    )
    def test_matches(self, temp_structure, path_key, expected):
        rule = DirRule()
        assert rule.matches(temp_structure[path_key]) == expected

    @pytest.mark.parametrize(
        "path_key, expected",
        [
            ("test_dir", True),
            ("test_file", False),
        ],
    )
    def test_is_include(self, temp_structure, path_key, expected):
        rule = DirRule()
        assert rule.is_include(temp_structure[path_key]) == expected

    @pytest.mark.parametrize(
        "path_key, expected",
        [
            ("test_dir", False),
            ("test_file", True),
        ],
    )
    def test_is_exclude(self, temp_structure, path_key, expected):
        rule = DirRule()
        assert rule.is_exclude(temp_structure[path_key]) == expected
