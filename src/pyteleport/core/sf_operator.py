import asyncio

from rich import print

from pyteleport.core._singlefile import _SingleFile
from pyteleport.core.clibboard import Clipboard
from pyteleport.core.tui import SelectFromListTUI
from pyteleport.tui.scanf import single_word_scanf


class SingleFileOperator:
    def __init__(self, onefile_path: str = "onefile.txt"):
        self._onefile_path = onefile_path
        self._single_file = _SingleFile(None, None, onefile_path)

    def get_single_file(self):
        self._single_file.update(
            "mini_scripts/onefile.txt",
            "./mini_scripts/exp/b.py",
            update_txt_file="a.txt",
        )

    def get_update_file(self, target_file_name: str):
        near_file = self._single_file._nearest_file(
            self._onefile_path, target_file_name, topk=1000
        )
        if len(near_file) == 0:
            print("[bold red]No file found.[/bold red]")
            return ""
        text = SelectFromListTUI(near_file)()
        with open(text, "r") as f:
            text = f.read()
        Clipboard.copy(text)
        print("[bold green]Please paste the update text using LLM etc[/bold green]")
        asyncio.run(Clipboard.watch_clipboard())
        Clipboard.paste()



def main():
    sfo = SingleFileOperator()
    while True:
        print("[bold green]What file do you want to update?[/bold green]")
        target_file_name = single_word_scanf()
        text = sfo.get_update_file(target_file_name)
        print(text)


if __name__ == "__main__":
    # SingleFileOperator().get_single_file()
    """
    print(
        SingleFileOperator()._single_file._nearest_file(
            "onefile.txt",
            "word.py",
        )
    )
    """
    main()
