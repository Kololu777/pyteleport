from pyteleport.core.tree import Tree
from pyteleport.rule import CompositeRule


class SingleFile:
    def __init__(self, path: str, rule_fn: CompositeRule, template: str | None = None, output_path: str | None = None):
        self._tree = Tree(path, rule_fn)
        self._tree.add_binary_info()
        if template is None:
            self._template = "#" * 10 + "\n"
            self._template += "file: {file_name}\n"
            self._template += "#" * 10 + "\n"
        else:
            if "{file_name}" not in template:
                raise ValueError("template must contain {file_name}")
            self._template = template

        if output_path is None:
            self._output_path = "onefile.txt"
        else:
            self._output_path = output_path

    def _get_template(self, file_name: str) -> str:
        return self._template.format(file_name=file_name)

    def to_single_file(self) -> None:
        onefile_text = ""
        for tree_dict in self._tree._tree_list:
            if tree_dict["is_binary"] == "text":
                with open(tree_dict["path"], "r") as f:
                    text = f.read()
                onefile_text += self._get_template(tree_dict["name"])
                onefile_text += text
        with open(self._output_path, "w") as f:
            f.write(onefile_text)
