from pyteleport import Tree
from pyteleport.integration import read_gitignore
if __name__ == "__main__":
    a = Tree("./src")
    print(a.tree_list)
    print(a.tree_dict)

    tree_change = Tree("./src")
  

    include_list, exclude_list = read_gitignore("./")
    print(include_list)
    print(exclude_list)

    print("--------------------------------")
    for k in tree_change.tree_list:
        print(k)
    print("--------------------------------")
    tree_change.all_change_name_leaf(
        change_leef_name="test_",
        include=include_list,
        exclude=exclude_list,
        is_dir=True
    )
    for k in tree_change.tree_list:
        print(k)
        #print(tree_change.tree_dict[k])
    