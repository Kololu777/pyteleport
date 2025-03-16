from pyteleport.rule import HiddenFileRule


class TestHiddenFileRule:
    def test_matches_non_hidden_file(self):
        rule = HiddenFileRule()
        assert rule.matches("test.py")

    def test_matches_hidden_file(self):
        rule = HiddenFileRule()
        assert not rule.matches(".hidden.py")

    def test_is_exclude_non_hidden_file(self):
        rule = HiddenFileRule()
        assert not rule.is_exclude("test.py")

    def test_is_exclude_hidden_file(self):
        rule = HiddenFileRule()
        assert rule.is_exclude(".hidden.py")
