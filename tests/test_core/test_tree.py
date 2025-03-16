import os

import pytest

from pyteleport.core import Tree, tree


@pytest.fixture
def temp_dir():
    temp_dir = os.path.join("./", "dummy", "example_01")

    yield temp_dir


class TestTreeFunction:
    def test_tree_basic(self, temp_dir):
        """Test basic tree functionality."""
        result = tree(temp_dir)

        # Check root is included
        assert result[0]["name"] == temp_dir
        assert result[0]["is_dir"] is True

        # Check total number of entries (excluding hidden files)
        # 1 root + 3 dirs + 7 files (excluding hidden ones)
        assert len(result) == 11

        # Check that hidden files are not included by default
        # Skip the root entry when checking for hidden files
        hidden_files = [
            item
            for item in result[1:]
            if os.path.basename(item["name"]).startswith(".")
        ]
        assert len(hidden_files) == 0

    def test_tree_with_hidden_files(self, temp_dir):
        """Test tree with hidden files included."""
        result = tree(temp_dir, is_hidden_file=True)

        # Check total number of entries (including hidden files)
        # 1 root + 4 dirs + 8 files (including hidden ones)
        assert len(result) == 13

        # Check that hidden files are included
        hidden_files = [item for item in result if item["name"].startswith(".")]
        assert len(hidden_files) > 0

    def test_tree_file_path(self, temp_dir):
        """Test tree with a file path instead of directory."""
        file_path = os.path.join(temp_dir, "file1.txt")
        result = tree(file_path)

        # Should only contain the file itself
        assert len(result) == 1
        assert result[0]["name"] == file_path
        assert result[0]["is_dir"] is False

    def test_tree_structure(self, temp_dir):
        """Test that the tree structure is correct."""
        result = tree(temp_dir)

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
    def test_tree_class_init(self, temp_dir):
        """Test Tree class initialization."""
        tree_obj = Tree(temp_dir)

        # Check that the tree list is populated
        assert len(tree_obj.tree_list) > 0
        assert tree_obj.tree_list[0]["name"] == temp_dir

    def test_tree_class_len(self, temp_dir):
        """Test Tree class __len__ property."""
        tree_obj = Tree(temp_dir)

        # Check that __len__ returns the correct number of entries
        assert tree_obj.__len__ == len(tree_obj.tree_list)

    def test_change_name_root(self, temp_dir):
        """Test changing the root name."""
        tree_obj = Tree(temp_dir)
        new_root_name = "new_root"

        tree_obj.change_name_root(new_root_name)

        # Check that the root name has been changed
        assert tree_obj.tree_list[0]["name"] == new_root_name

    def test_all_change_name_leaf_with_include(self, temp_dir):
        """Test changing leaf names with include patterns."""
        tree_obj = Tree(temp_dir)
        prefix = "prefix_"

        # Change all .txt files
        tree_obj.all_change_name_leaf(prefix, include=["*.txt"])

        # Check that .txt files have been prefixed
        txt_files = [
            item for item in tree_obj.tree_list if item["name"].endswith(".txt")
        ]
        for file in txt_files:
            assert file["name"].startswith(prefix)

        # Check that .py files have not been prefixed
        py_files = [item for item in tree_obj.tree_list if item["name"].endswith(".py")]
        for file in py_files:
            assert not file["name"].startswith(prefix)

    def test_all_change_name_leaf_with_exclude(self, temp_dir):
        """Test changing leaf names with exclude patterns."""
        tree_obj = Tree(temp_dir)
        prefix = "prefix_"

        # Change all files except .py files
        tree_obj.all_change_name_leaf(prefix, include=["*"], exclude=["*.py"])

        # Check that non-.py files have been prefixed
        non_py_files = [
            item
            for item in tree_obj.tree_list
            if not item["name"].endswith(".py") and not item["is_dir"]
        ]
        for file in non_py_files:
            assert file["name"].startswith(prefix)

        # Check that .py files have not been prefixed
        py_files = [item for item in tree_obj.tree_list if item["name"].endswith(".py")]
        for file in py_files:
            assert not file["name"].startswith(prefix)

    def test_all_change_name_leaf_with_dir_change(self, temp_dir):
        """Test changing leaf names with is_if_dir_change=True."""
        tree_obj = Tree(temp_dir)
        prefix = "prefix_"

        # Change only directories
        tree_obj.all_change_name_leaf(
            prefix, include=[], exclude=["*"], is_if_dir_change=True
        )

        # Check that directories have been prefixed
        dirs = [item for item in tree_obj.tree_list if item["is_dir"]]
        for dir_item in dirs:
            assert dir_item["name"].startswith(prefix)

        # Check that files have not been prefixed
        files = [item for item in tree_obj.tree_list if not item["is_dir"]]
        for file in files:
            assert not file["name"].startswith(prefix)

    def test_exclude_leaf(self, temp_dir):
        """Test excluding leaves from the tree."""
        tree_obj = Tree(temp_dir)
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

    def test_update_tree_add_mode(self, temp_dir):
        """Test _update_tree with 'add' mode."""
        tree_obj = Tree(temp_dir)
        original_name = tree_obj.tree_list[1]["name"]
        prefix = "prefix_"

        tree_obj._update_tree(1, prefix, mode="add")

        # Check that the name has been prefixed
        assert tree_obj.tree_list[1]["name"] == prefix + original_name

    def test_update_tree_replace_mode(self, temp_dir):
        """Test _update_tree with 'replace' mode."""
        tree_obj = Tree(temp_dir)
        new_name = "new_name"

        tree_obj._update_tree(1, new_name, mode="replace")

        # Check that the name has been replaced
        assert tree_obj.tree_list[1]["name"] == new_name

    def test_update_tree_invalid_mode(self, temp_dir):
        """Test _update_tree with invalid mode."""
        tree_obj = Tree(temp_dir)

        # Should raise ValueError for invalid mode
        with pytest.raises(ValueError):
            tree_obj._update_tree(1, "test", mode="invalid")
