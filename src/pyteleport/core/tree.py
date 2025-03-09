import fnmatch
import os

from rich import print


def tree(
    path: str,
    is_hidden_file: bool = False,
    _prefix: str = "",
    _visited_list: list[str] | None = None,
):
    """
    Get tree structure of the path. like `tree` command.

    Args:
        path: start path
        is_hidden_file: if True, hidden files are included.
    Returns:
        list: tree structure of the path.

    Examples:
        >>> from pyteleport import tree
        >>> tree("./src", is_hidden_file=True)
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
            "is_dir": os.path.isdir(path),
        }
        _visited_list.append(visited_dict)

        if not _visited_list[0]["is_dir"]:  # If init path is file, return
            return _visited_list
    entries = sorted(os.listdir(path))

    if not is_hidden_file:
        entries = [
            entry for entry in entries if not entry.startswith(".")
        ]  # exclude hidden files.
    entries_count = len(entries)

    for idx, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if idx == entries_count - 1 else "├── "
        visited_dict = {
            "symbol": f"{_prefix}{connector}",
            "name": entry,
            "path": full_path,
            "is_dir": os.path.isdir(full_path),
        }
        _visited_list.append(visited_dict)

        if os.path.isdir(full_path):
            next_prefix = _prefix + ("    " if idx == entries_count - 1 else "│   ")
            tree(full_path, is_hidden_file, next_prefix, _visited_list)
    return _visited_list


class Tree:
    def __init__(self, path: str, is_hidden_file: bool = False):
        self.path = path
        self.is_hidden_file = is_hidden_file
        self._tree_list = tree(path, is_hidden_file)

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
        # {"src": {"path":"./", "number":1}} -> {"tests": {"path":"./tests", "number":1}}
        # Before Data
        self._update_tree(0, change_root_name, mode="replace")

    def all_change_name_leaf(
        self,
        change_leef_name: str,
        include: list[str] = [".*"],
        exclude: list[str] | None = None,
        is_if_dir_change: bool = True,
    ) -> None:
        if len(self._tree_list) <= 1:
            return
        for idx, tree_dict in enumerate(self._tree_list):
            file_name = tree_dict["path"]
            if exclude is not None:
                if any(fnmatch.fnmatch(file_name, ext) for ext in exclude):
                    continue
            if any(fnmatch.fnmatch(file_name, file) for file in include):
                self._update_tree(idx, update_name=change_leef_name, mode="add")
            elif is_if_dir_change and tree_dict["is_dir"]:
                self._update_tree(idx, update_name=change_leef_name, mode="add")
            else:
                continue

    def _update_tree(self, idx: int, update_name: str, mode: str = "add") -> None:
        if mode == "add":
            update_name = update_name + self._tree_list[idx]["name"]
        elif mode == "replace":
            update_name = update_name
        else:
            raise ValueError(f"Invalid mode: {mode}")
        self._tree_list[idx]["name"] = update_name
        self._tree_list[idx]["path"] = self._tree_list[idx]["path"] + update_name

    def exclude_leaf(self, exclude: list[str] | None = None) -> None:
        if exclude is None:
            return
        for idx, tree_dict in enumerate(self._tree_list):
            if any(fnmatch.fnmatch(tree_dict["path"], file) for file in exclude):
                self._tree_list.pop(idx)
