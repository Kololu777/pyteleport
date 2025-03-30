import difflib
import re
from pathlib import Path
from typing import Optional, Protocol

from pyteleport.constant import LINENO_PADDING_WIDTH


class TreeProtocol(Protocol):
    """Protocol defining the interface required from TeleportTree."""

    def add_binary_info(self) -> None: ...

    _tree_list: list[dict]


class _SingleFile:
    def __init__(
        self,
        tree_instance: Optional[
            "TreeProtocol"
        ] = None,  # Use forward reference with Protocol
        template_symbol_and_length: tuple[str, int] | None = None,
        output_path: str | None = None,
    ):
        if tree_instance is not None:
            # need to `to_single_file` method.
            self._tree = tree_instance
            self._tree.add_binary_info()

        if template_symbol_and_length is None:
            template_symbols = "%" * 10 + "\n"
        else:
            template_symbols = (
                template_symbol_and_length[0] * template_symbol_and_length[1] + "\n"
            )
        self._template = template_symbols
        self._template += "file: {file_name}\n"
        self._template += template_symbols

        self._pattern = template_symbols + "file: (.*?)\n" + template_symbols
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
                    onefile_text += self._add_line_numbers(text)

                else:
                    onefile_text += text
                onefile_text += "\n"
        with open(self._output_path, "w") as f:
            f.write(onefile_text)

    def _add_line_numbers(self, content: str) -> str:
        """
        Add line numbers to the content.
        """
        result_txt = ""
        lines = content.splitlines()
        for lineno, line in enumerate(lines):
            lineno_str = str(lineno)
            padding_width = LINENO_PADDING_WIDTH - len(lineno_str)
            result_txt += f"{lineno_str}:{' ' * padding_width}{line}\n"
        return result_txt

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
            if re.match(r"^\d+:", line):
                cleaned_line = line[LINENO_PADDING_WIDTH + 1 :]
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

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

        files, contents = self._split_txt_to_files_and_contents(onefile_text)
        return files, contents

    def update(
        self,
        onefile_txt_path: str | Path,
        target_file_name: str,
        update_txt_file: str | Path | None = None,
        update_txt_str: str | None = None,
    ) -> None:
        """
        Update the content of a specific file in the onefile.txt.

        Args:
            onefile_txt_path: Path to the onefile.txt to update
            target_file_name: Name of the file to update
            update_txt_file: Path to the file containing the update text
            update_txt_str: String containing the update text.
        Note:
            Either update_txt_file or update_txt_str must be provided.
            If both are provided, Error will be raised.
        """
        with open(onefile_txt_path, "r") as f:
            onefile_text = f.read()
        if update_txt_file is None and update_txt_str is None:
            raise ValueError(
                "Either update_txt_file or update_txt_str must be provided."
            )
        elif update_txt_file is not None and update_txt_str is not None:
            raise ValueError(
                "Either update_txt_file or update_txt_str must be provided."
            )
        elif update_txt_file is not None:
            with open(update_txt_file, "r") as f:
                update_txt = f.read()
        else:
            update_txt = update_txt_str

        files, contents = self._split_txt_to_files_and_contents(onefile_text)
        for index, (file_name, _) in enumerate(zip(files, contents)):
            if file_name == target_file_name:
                contents[index] = update_txt
        onefile_text = self._concat_parse(files, contents, is_lineno=True)
        with open(onefile_txt_path, "w") as f:
            f.write(onefile_text)

    def _concat_parse(
        self, files: list[str], contents: list[str], is_lineno: bool = False
    ) -> str:
        """
        Concatenate the files and contents and return onefile_text.
        Reverse of `parse` method.
        """
        onefile_text = ""
        for file_name, content in zip(files, contents):
            onefile_text += self._get_template(file_name)
            if is_lineno:
                onefile_text += self._add_line_numbers(content)
            else:
                onefile_text += content
            onefile_text += "\n"
        return onefile_text

    def _split_txt_to_files_and_contents(self, txt: str) -> list[str]:
        # Pattern to match the file header and content
        pattern = f"{self._pattern}(.*?)(?={self._pattern}|\Z)"

        # Find all matches
        matches = re.finditer(pattern, txt, re.DOTALL)

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

    def _nearest_file(
        self,
        onefile_txt_path: str | Path,
        target_name: str,
        topk: int = 5,
        cutoff: float = 0.2,
    ) -> str:
        """
        Find the nearest file to the given file name.
        """
        with open(onefile_txt_path, "r") as f:
            onefile_text = f.read()
        files, _ = self._split_txt_to_files_and_contents(onefile_text)
        matches = difflib.get_close_matches(target_name, files, n=topk, cutoff=cutoff)
        return matches
