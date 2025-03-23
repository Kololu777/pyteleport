# Avoid circular import by using TYPE_CHECKING
from typing import TYPE_CHECKING, Any, Protocol
from pyteleport.constant import LINENO_PADDING_WIDTH
if TYPE_CHECKING:
    from pyteleport.core.tree import TeleportTree


class TreeProtocol(Protocol):
    """Protocol defining the interface required from TeleportTree."""
    def add_binary_info(self) -> None: ...
    _tree_list: list[dict]


class _SingleFile:
    def __init__(
        self,
        tree_instance: "TreeProtocol",  # Use forward reference with Protocol
        template: str | None = None,
        output_path: str | None = None,
    ):
        self._tree = tree_instance
        self._tree.add_binary_info()
        if template is None:
            self._template = "%" * 10 + "\n"
            self._template += "file: {file_name}\n"
            self._template += "%" * 10 + "\n"
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

    def to_single_file(self, is_lineno: bool = False) -> None:
        onefile_text = ""
        for tree_dict in self._tree._tree_list:
            if tree_dict["is_binary"] == "text":
                with open(tree_dict["path"], "r") as f:
                    text = f.read()
                onefile_text += self._get_template(tree_dict["path"])
                if is_lineno:
                    lines = text.splitlines()
                    for lineno, line in enumerate(lines):
                        lineno_str = str(lineno)
                        padding_width = LINENO_PADDING_WIDTH - len(lineno_str)
                        onefile_text += f"{lineno_str}:{' ' * padding_width}{line}\n"
                else:
                    onefile_text += text
                onefile_text += "\n"
        with open(self._output_path, "w") as f:
            f.write(onefile_text)

    def parse(self, onefile_text: str) -> None:
        """
        Parse a single file containing multiple files and return a list of files.
        
        Args:
            onefile_text: The text of the single file to parse.
            
        Returns:
            None
        """
        # Split the text by the template pattern
        template_prefix = "%" * 10
        files = []
        current_file = None
        current_content = []
        is_lineno = False
        
        lines = onefile_text.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this is a template header
            if line.startswith(template_prefix) and i + 2 < len(lines) and lines[i+2].startswith(template_prefix):
                # If we have a current file, save it
                if current_file is not None:
                    content = "\n".join(current_content)
                    files.append({"file": current_file, "content": content})
                    current_content = []
                
                # Extract the file name
                file_line = lines[i+1]
                if file_line.startswith("file: "):
                    current_file = file_line[6:].strip()
                    i += 3  # Skip the template lines
                    continue
            
            # Check if this line has line numbers (e.g., "0:      import os")
            if ":" in line and line.split(":", 1)[0].strip().isdigit():
                is_lineno = True
                # Extract the content after the line number
                content_part = line.split(":", 1)[1]
                if content_part.startswith(" " * LINENO_PADDING_WIDTH):
                    content_part = content_part[LINENO_PADDING_WIDTH:]
                current_content.append(content_part)
            else:
                # Regular line without line numbers
                current_content.append(line)
            
            i += 1
        
        # Don't forget the last file
        if current_file is not None:
            content = "\n".join(current_content)
            files.append({"file": current_file, "content": content})
        
        return files