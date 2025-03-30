import os

from binaryornot.check import is_binary
from rich import print

from pyteleport.core.algorithm import apply_asterisk_rule
from pyteleport.rule import CompositeRule
from pyteleport.rule.rule_factory import RuleFactory
from pyteleport.core._singlefile import _SingleFile


def teleport_tree(
    path: str,
    rule_fn: CompositeRule | None = None,
    _prefix: str = "",
    _visited_list: list[str] | None = None,
):
    """
    Get tree structure of the path. like `tree` command.

    Args:
        path: start path
        rule_fn: rule function
    Returns:
        list: tree structure of the path.

    Examples:
        >>> from pyteleport import tree
        >>> tree("./src", rule_fn=HiddenFileRule())
    """
    # Init visited list.
    if _visited_list is None:
        _visited_list = []

    if _prefix == "":
        # add root info to visited list ad dict
        visited_dict = {
            "symbol": "",
            "name": path,
            "path": path,
            "parent": -1,  # -1 means root
            "children": [],
            "is_dir": os.path.isdir(path),
        }
        _visited_list.append(visited_dict)

        if not _visited_list[0]["is_dir"]:  # If init path is file, return
            return _visited_list

    entries = os.listdir(path)
    if rule_fn is not None:
        entries = [entry for entry in entries if rule_fn.matches(entry)]
    entries_count = len(entries)

    parent_idx = len(_visited_list) - 1

    for idx, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if idx == entries_count - 1 else "├── "
        visited_dict = {
            "symbol": f"{_prefix}{connector}",
            "name": entry,
            "path": full_path,
            "parent": parent_idx,
            "children": [],
            "is_dir": os.path.isdir(full_path),
        }
        _visited_list.append(visited_dict)
        _visited_list[parent_idx]["children"].append(len(_visited_list) - 1)
        if os.path.isdir(full_path):
            next_prefix = _prefix + ("    " if idx == entries_count - 1 else "│   ")
            teleport_tree(full_path, rule_fn, next_prefix, _visited_list)
    return _visited_list


class TeleportTree:
    def __init__(
        self,
        path: str,
        include_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
        special_words: list[str] = None,
        gitignore_path: str = "./.gitignore",
    ):
        self._path = self._first_path = path
        self.rule_fn = RuleFactory.simplify_create_rule(
            include_patterns,
            exclude_patterns,
            special_words,
            gitignore_path=gitignore_path,
        )
        print(self.rule_fn.rules[0].matches("test_rule.py"))
        print(self.rule_fn.rules[0].matches("test_rule.pyc"))

        self._tree_list = teleport_tree(path, self.rule_fn)

    @property
    def tree_list(self) -> list[str]:
        return self._tree_list

    @property
    def __len__(self) -> int:
        return len(self._tree_list)

    @property
    def print(self) -> None:
        for tree_dict in self._tree_list:
            if tree_dict["is_dir"]:
                print(f"{tree_dict['symbol']}[magenta]{tree_dict['name']}[/magenta]")
            else:
                print(f"{tree_dict['symbol']}[cyan]{tree_dict['name']}[/cyan]")

    def change_name_root(self, change_root_name: str) -> None:
        self._path = change_root_name
        self._update_tree(0, change_root_name, mode="replace")
        self._tree_list[0]["path"] = self._path

    def all_change_name_leaf(
        self,
        change_rule: str,
    ) -> None:
        """
        Args:
            change_rule: Change rule. (a.py, change_rule=test_*) -> test_a.py, (b_*a_c.py, change_rule=test_*) -> test_b_a_c.py
        """
        if len(self._tree_list) <= 1:
            return

        for idx, tree_dict in enumerate(self._tree_list):
            if idx == 0 and tree_dict["is_dir"]:
                continue
            else:
                self._update_tree(idx, change_rule, mode="add")
        self._update_path()

    def _update_tree(
        self, idx: int, update_name_or_rule: str, mode: str = "add"
    ) -> None:
        if mode == "add":
            update_name = apply_asterisk_rule(
                self._tree_list[idx]["name"], update_name_or_rule
            )
        elif mode == "replace":
            update_name = update_name_or_rule
        else:
            raise ValueError(f"Invalid mode: {mode}")
        self._tree_list[idx]["name"] = update_name

    def _update_path(self):
        # note: this method is able to use when `name` update already completed.
        def _update_path_recursive(idx: int):
            children_idx = self._tree_list[idx]["children"]
            for child_idx in children_idx:
                self._tree_list[child_idx]["path"] = os.path.join(
                    self._tree_list[idx]["path"], self._tree_list[child_idx]["name"]
                )
                _update_path_recursive(child_idx)

        _update_path_recursive(0)

    def _judge_binary_file(self) -> bool:
        for tree_dict in self._tree_list:
            if tree_dict["is_dir"]:
                tree_dict["is_binary"] = "dir"
            elif is_binary(tree_dict["path"]):
                tree_dict["is_binary"] = "binary"
            else:
                tree_dict["is_binary"] = "text"
        return self._tree_list

    def add_binary_info(self) -> None:
        self._tree_list = self._judge_binary_file()

    def to_single_file(
        self,
        output_path: str | None = None,
        is_lineno: bool = False,
        template: str | None = None,
    ) -> None:
        single_file = _SingleFile(self, template, output_path)
        single_file.to_single_file(is_lineno)

    def exclude_leaf(self, exclude_patterns: list[str]) -> None:
        """
        Exclude leaves from the tree that match the given patterns.

        Args:
            exclude_patterns: List of glob patterns to exclude
        """
        if not exclude_patterns:
            return

        from fnmatch import fnmatch

        # Create a new tree_list excluding matching files
        new_tree_list = []
        for item in self._tree_list:
            # Keep directories and files that don't match any exclude pattern
            if item["is_dir"]:
                new_tree_list.append(item)
            else:
                filename = os.path.basename(item["path"])
                if not any(fnmatch(filename, pattern) for pattern in exclude_patterns):
                    new_tree_list.append(item)

        self._tree_list = new_tree_list
