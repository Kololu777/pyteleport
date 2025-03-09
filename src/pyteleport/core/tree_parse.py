from pyteleport import Tree
from pyteleport.integration import read_gitignore
import fnmatch
if __name__ == "__main__":
    a = Tree("./src")
    print(a.tree_list)

    tree_change = Tree("./src")
  

    include_list, exclude_list = read_gitignore("./")
    print(include_list)
    print(exclude_list)

    tree_change.print

    
    tree_change.change_name_root("test")
    tree_change.all_change_name_leaf(
        change_leef_name="test_",
        include=include_list,
        exclude=exclude_list,
        is_if_dir_change=True,
    )
    print("--------------------------------")

    tree_change.print

    a = "./src/pyteleport.egg-info/PKG-INFO"
    print(fnmatch.fnmatch(a, "*.egg-info"))