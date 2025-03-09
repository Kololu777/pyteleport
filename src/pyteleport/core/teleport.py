from pyteleport import Tree

if __name__ == "__main__":
    a = Tree("./src")
    a.print

    b = Tree("./src/pyteleport/__pycache__/__init__.cpython-312.pyc")
    b.print

    a.change_name_root("tests")
    a.all_change_name_leaf(
        change_leef_name="test_",
        include=["*.py"],
        exclude={"*pyc", "*.egg-info", "*__pycache__", "__init__.py"},
        is_dir=True
    )
    a.print

