from typing import Protocol, Optional
from pyteleport.constant import LINENO_PADDING_WIDTH
from pathlib import Path
import re

class TreeProtocol(Protocol):
    """Protocol defining the interface required from TeleportTree."""
    def add_binary_info(self) -> None: ...
    _tree_list: list[dict]


class _SingleFile:
    def __init__(
        self,
        tree_instance: Optional["TreeProtocol"] = None,  # Use forward reference with Protocol
        template_symbol_and_length: tuple[str, int] | None  = None,
        output_path: str | None = None,
    ):
        if tree_instance is not None:
            # need to `to_single_file` method.
            self._tree = tree_instance
            self._tree.add_binary_info()

        if template_symbol_and_length is None:
            template_symbols = "%" * 10 + "\n"
        else:
            template_symbols = template_symbol_and_length[0] * template_symbol_and_length[1] + "\n"
        self._template = template_symbols
        self._template += "file: {file_name}\n"
        self._template += template_symbols
      
        self._pattern = template_symbols + "file: (.*?)\n"  + template_symbols
        self._output_path = "onefile.txt" if output_path is None else output_path

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
    
    def _remove_line_numbers(self, content: str) -> str:
        """
        Remove line numbers from the content if they exist.
        
        Args:
            content: The content that might contain line numbers
            
        Returns:
            str: Content with line numbers removed
        """
        lines = content.splitlines()
        cleaned_lines = []
        
        for line in lines:
            # Check if line starts with a number followed by colon
            if re.match(r'^\d+:', line):
                cleaned_line = line[LINENO_PADDING_WIDTH+1:]
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    def parse(self, onefile_txt_path: str | Path) -> None:
        """
        Parse a single file containing multiple files and return file names and their contents.
        
        Args:
            onefile_txt_path: Path to the onefile.txt to parse
            
        Returns:
            tuple: (list of file names, list of code blocks)
        """
        with open(onefile_txt_path, "r") as f:
            onefile_text = f.read()
        
        # Pattern to match the file header and content
        pattern = f"{self._pattern}(.*?)(?={self._pattern}|\Z)"
        
        # Find all matches
        matches = re.finditer(pattern, onefile_text, re.DOTALL)
        
        # Extract file names and contents
        files = []
        contents = []
        for match in matches:
            file_name = match.group(1).strip()
            content = match.group(2).strip()
            # Remove line numbers from content
            content = self._remove_line_numbers(content)
            files.append(file_name)
            contents.append(content)
        
        return files, contents
