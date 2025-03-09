import os
from rich import print
import fnmatch

def tree(
        path:str, 
        is_hidden_file:bool = False, 
        _prefix:str="", 
        _visited_list:list[str] | None = None,
        _visited_dict:dict[str, str] | None = None
    ):
    """
    Get tree structure of the path. like `tree` command.

    Args:
        path: start path
        is_hidden_file: if True, hidden files are included.
        verbose: if True, print tree structure.
    Returns:
        list: tree structure of the path.
    
    Examples:
        >>> from pyteleport import tree
        >>> tree("./src", is_hidden_file=True)
    """
    # Init visited list and dict
    if _visited_list is None:
        _visited_list = []
    if _visited_dict is None:
        _visited_dict = {}
        
    if _prefix == "":
       # add root info to visited list and dict
       _visited_dict[path] = {}
       _visited_dict[path]["symbol"] = ""
       _visited_dict[path]["name"] = path
       _visited_dict[path]["path"] = path
       _visited_dict[path]["number"] = len(_visited_list)
       _visited_dict[path]["is_dir"] = os.path.isdir(path) # directory
       
       _visited_list.append(path)

       if not _visited_dict[path]["is_dir"]: # If init path is file, return
            return _visited_list, _visited_dict
    entries = sorted(os.listdir(path))

    if not is_hidden_file:
        entries = [entry for entry in entries if not entry.startswith('.')] # exclude hidden files.
    entries_count = len(entries)
    
    for idx, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        connector = "└── " if idx == entries_count - 1 else "├── "
        if os.path.isdir(full_path):
            _visited_dict[f"{_prefix}{connector}{entry}"] = {}
            _visited_dict[f"{_prefix}{connector}{entry}"]["symbol"] = f"{_prefix}{connector}"
            _visited_dict[f"{_prefix}{connector}{entry}"]["name"] = entry
            _visited_dict[f"{_prefix}{connector}{entry}"]["path"] = full_path
            _visited_dict[f"{_prefix}{connector}{entry}"]["number"] = len(_visited_list)
            _visited_dict[f"{_prefix}{connector}{entry}"]["is_dir"] = True # directory
            _visited_list.append(f"{_prefix}{connector}{entry}")

        else:
            _visited_dict[f"{_prefix}{connector}{entry}"] = {}
            _visited_dict[f"{_prefix}{connector}{entry}"]["symbol"] = f"{_prefix}{connector}"
            _visited_dict[f"{_prefix}{connector}{entry}"]["name"] = entry
            _visited_dict[f"{_prefix}{connector}{entry}"]["path"] = full_path
            _visited_dict[f"{_prefix}{connector}{entry}"]["number"] = len(_visited_list)
            _visited_dict[f"{_prefix}{connector}{entry}"]["is_dir"] = False # file
            _visited_list.append(f"{_prefix}{connector}{entry}")

        if os.path.isdir(full_path):
            next_prefix = _prefix + ("    " if idx == entries_count - 1 else "│   ")
            tree(full_path, is_hidden_file, next_prefix, _visited_list, _visited_dict)
    return _visited_list, _visited_dict

class Tree:
    def __init__(self, path:str, is_hidden_file:bool = False):
        self.path = path
        self.is_hidden_file = is_hidden_file
        self._tree_list, self._tree_dict = tree(path, is_hidden_file)

    @property
    def tree_list(self)->list[str]:
        return self._tree_list

    @property
    def tree_dict(self)->dict[str, str]:
        return self._tree_dict

    @property
    def print(self)->None:
        for k in self._tree_list:
            if self._tree_dict[k]["is_dir"]:
                print(f"{self._tree_dict[k]['symbol']}[magenta]{self._tree_dict[k]['name']}[/magenta]")
            else:
                print(f"{self._tree_dict[k]['symbol']}[cyan]{self._tree_dict[k]['name']}[/cyan]")

    def change_name_root(self, change_root_name:str)->None:
        # {"src": {"path":"./", "number":1}} -> {"tests": {"path":"./tests", "number":1}}
        # Before Data
        self._update_tree(self._tree_list[0], change_root_name, mode="replace")
  

    def all_change_name_leaf(
            self, 
            change_leef_name:str, 
            include:list[str] = [".*"],
            exclude:list[str] | None = None,
            is_dir:bool = True
        )->None:
        if len(self._tree_list) <= 1:
            return
        for _, key in enumerate(self._tree_list[1:]):
            file_name = self._tree_dict[key]["path"]
            if exclude is not None:
                if any(fnmatch.fnmatch(file_name, ext) for ext in exclude):
                    continue
            if include is not None:
                if any(fnmatch.fnmatch(file_name, file) for file in include):
                    self._update_tree(key, update_name=change_leef_name, mode="add")
                elif is_dir and self._tree_dict[key]["is_dir"]:
                    self._update_tree(key, update_name=change_leef_name, mode="add")
                else:
                    continue
            

            
    def _update_tree(self, key:str, update_name:str, mode:str="add")->None:
        if mode == "add":
            new_name = update_name + self._tree_dict[key]["name"]
            new_leef_name = self._tree_dict[key]["symbol"] + new_name
        elif mode == "replace":
            new_name = update_name
            new_leef_name = self._tree_dict[key]["symbol"] + new_name
        else:
            raise ValueError(f"Invalid mode: {mode}")

        idx = self._tree_dict[key]["number"]

        # update tree_list
        self._tree_list[idx] = new_leef_name

        # update tree_dict
        self._tree_dict[new_leef_name] = {}
        self._tree_dict[new_leef_name]["symbol"] = self._tree_dict[key]["symbol"]
        self._tree_dict[new_leef_name]["name"] = new_name
        self._tree_dict[new_leef_name]["path"] = self._tree_dict[key]["path"]
        self._tree_dict[new_leef_name]["number"] = self._tree_dict[key]["number"]
        self._tree_dict[new_leef_name]["is_dir"] = self._tree_dict[key]["is_dir"]
        self._tree_dict.pop(key)
        
        
        
