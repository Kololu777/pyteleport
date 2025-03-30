import pyperclip


class Clipboard:
    @staticmethod
    def copy(text: str) -> None:
        pyperclip.copy(text)

    @staticmethod
    def paste() -> str:
        return pyperclip.paste()


if __name__ == "__main__":
    with open("onefile.txt", "r") as f:
        text = f.read()
    Clipboard.copy(text)
    print(Clipboard.paste())
