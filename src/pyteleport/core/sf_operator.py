from pyteleport.core._singlefile import _SingleFile
from pyteleport.core.tui import SelectFromListTUI


class SingleFileOperator:
    def __init__(self):
        self._single_file = _SingleFile(None, None, "onefile.txt")

    def get_single_file(self):
        self._single_file.update(
            "mini_scripts/onefile.txt",
            "./mini_scripts/exp/b.py",
            update_txt_file="a.txt",
        )


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

    near_file = SingleFileOperator()._single_file._nearest_file(
        "onefile.txt",
        "word.py",
        topk=1000
    )
    text = SelectFromListTUI(near_file)()
    print(text)
