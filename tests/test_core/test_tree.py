import os

import pytest

from pyteleport.core import TeleportTree, teleport_tree
from pyteleport.rule import HiddenFileRule


@pytest.fixture
def temp_dir():
    temp_dir = os.path.join("./", "dummy", "example_tree")

    yield temp_dir


class TestTreeFunction:
    @pytest.mark.parametrize(
        "include_hidden,expected_count,should_have_hidden",
        [
            (False, 11, False),  # Default behavior - hidden files excluded
            (True, 13, True),  # Include hidden files
        ],
    )
    def test_tree_hidden_files(
        self, temp_dir, include_hidden, expected_count, should_have_hidden
    ):
        """Test tree functionality with and without hidden files."""
        hidden_rule = HiddenFileRule()
        if include_hidden:
            hidden_rule.is_include = lambda query: True

        result = teleport_tree(temp_dir, rule_fn=hidden_rule)

        # Check root is included
        assert result[0]["name"] == temp_dir
        assert result[0]["is_dir"] is True

        # Check total number of entries
        assert len(result) == expected_count

    def test_tree_file_path(self, temp_dir):
        """Test tree with a file path instead of directory."""
        file_path = os.path.join(temp_dir, "file1.txt")
        result = teleport_tree(file_path)

        # Should only contain the file itself
        assert len(result) == 1
        assert result[0]["name"] == file_path
        assert result[0]["is_dir"] is False

    def test_tree_structure_and_properties(self, temp_dir):
        """Test that the tree structure and various properties are correct."""
        result = teleport_tree(temp_dir)

        # Check that directories have the correct structure
        dir1_entry = next((item for item in result if item["name"] == "dir1"), None)
        assert dir1_entry is not None
        assert dir1_entry["is_dir"] is True

        # Check that the symbols are correct
        # Root has no symbol
        assert result[0]["symbol"] == ""

        # Check that the paths are correct
        file1_entry = next(
            (item for item in result if item["name"] == "file1.txt"), None
        )
        assert file1_entry is not None
        assert file1_entry["path"] == os.path.join(temp_dir, "file1.txt")


class TestTreeClass:
    def test_tree_class_initialization(self, temp_dir):
        """Test Tree class initialization and basic properties."""
        tree_obj = TeleportTree(temp_dir)

        # Check that the tree list is populated
        assert len(tree_obj.tree_list) > 0
        assert tree_obj.tree_list[0]["name"] == temp_dir

        # Check that __len__ returns the correct number of entries
        assert tree_obj.__len__ == len(tree_obj.tree_list)

    @pytest.mark.parametrize(
        "test_name,method_to_call,args,expected_check",
        [
            (
                "root_name_change",
                "change_name_root",
                ["new_root"],
                lambda obj: obj.tree_list[0]["name"] == "new_root",
            ),
            (
                "leaf_name_change",
                "all_change_name_leaf",
                ["prefix_"],
                lambda obj: all(
                    item["name"].startswith("prefix_")
                    for item in obj.tree_list
                    if item["parent"] != -1
                ),
            ),
        ],
    )
    def test_name_change_operations(
        self, temp_dir, test_name, method_to_call, args, expected_check
    ):
        """Test various name change operations."""
        tree_obj = TeleportTree(temp_dir)

        # Call the method with the given arguments
        method = getattr(tree_obj, method_to_call)
        method(*args)

        # Verify the result
        assert expected_check(tree_obj)

    def test_exclude_leaf(self, temp_dir):
        """Test excluding leaves from the tree."""
        tree_obj = TeleportTree(temp_dir)

        initial_count = len(tree_obj.tree_list)

        # Exclude .txt files
        tree_obj.exclude_leaf(["*.txt"])

        # Check that .txt files have been excluded
        txt_files = [
            item for item in tree_obj.tree_list if item["name"].endswith(".txt")
        ]
        assert len(txt_files) == 0

        # Check that the total count has decreased
        assert len(tree_obj.tree_list) < initial_count

    @pytest.mark.parametrize(
        "mode,input_value,expected_result",
        [
            (
                "add",
                "prefix_*",
                lambda obj, orig: obj.tree_list[1]["name"] == "prefix_" + orig,
            ),
            (
                "replace",
                "new_name",
                lambda obj, orig: obj.tree_list[1]["name"] == "new_name",
            ),
        ],
    )
    def test_update_tree_modes(self, temp_dir, mode, input_value, expected_result):
        """Test _update_tree with different modes."""
        tree_obj = TeleportTree(temp_dir)
        original_name = tree_obj.tree_list[1]["name"]

        tree_obj._update_tree(1, input_value, mode=mode)

        # Check the result using the provided function
        assert expected_result(tree_obj, original_name)

    def test_update_tree_invalid_mode(self, temp_dir):
        """Test _update_tree with invalid mode."""
        tree_obj = TeleportTree(temp_dir)

        # Should raise ValueError for invalid mode
        with pytest.raises(ValueError):
            tree_obj._update_tree(1, "test", mode="invalid")
