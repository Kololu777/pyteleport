import os

from rich import print

from pyteleport.core.algorithm import apply_asterisk_rule
from pyteleport.rule import CompositeRule


def tree(
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
        print(entries)
        print(rule_fn.matches("pyteleport"))
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
            tree(full_path, rule_fn, next_prefix, _visited_list)
    return _visited_list


class Tree:
    def __init__(self, path: str, rule_fn: CompositeRule | None = None):
        self._path = self._first_path = path
        self.rule_fn = rule_fn
        self._tree_list = tree(path, rule_fn)

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


if __name__ == "__main__":
    from pyteleport.rule import RuleFactory

    config = [
        {
            "type": "glob",
            #"include_patterns": ["*.py"],
            "exclude_patterns": [
                "*.egg-info",
                "*.pyc",
                "__pycache__/**",
                "*__pycache__*",
                "**/__pycache__/**",
            ],
        },
        {"type": "hidden_file"},
    ]
    rule_fn = RuleFactory.create_composite_rule(config)

    #rule_fn = RuleFactory.create_rule("glob", include_patterns=["pyteleport/**"])
    tree = Tree("./src/", rule_fn=rule_fn)
    tree.print
    tree.change_name_root("./tests")
    tree.all_change_name_leaf(change_rule="test_*")
    tree.print

    print(tree._tree_list)