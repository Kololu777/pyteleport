import asyncio

import pyperclip


class Clipboard:
    """
    Clippboard class using pyperclip for copy and paste.
    Implemented as a singleton pattern.

    Example:
    >>> # Copy text to clipboard:
    >>> Clipboard.copy("Hello, World!")
    >>> # Paste text from clipboard:
    >>> Clipboard.paste()
    >>> 'Hello, World!'
    """

    _instance = None
    _last_text: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Clipboard, cls).__new__(cls)
        return cls._instance

    @staticmethod
    def copy(text: str) -> None:
        Clipboard._last_text = text
        pyperclip.copy(text)

    @staticmethod
    def paste(sync: bool = True) -> str:
        if sync:
            Clipboard._last_text = pyperclip.paste()
        return Clipboard._last_text

    @staticmethod
    async def watch_clipboard(interval: float = 1.0) -> str:
        last_text = Clipboard.paste()

        while True:
            await asyncio.sleep(interval)
            current_text = Clipboard.paste()
            if current_text != last_text:
                Clipboard._last_text = current_text
                return Clipboard.paste(sync=False)
