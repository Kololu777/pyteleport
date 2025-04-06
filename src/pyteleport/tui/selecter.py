#from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, VSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style


class SelectFromListTUI:
    def __init__(
        self,
        candidates: list[str],
        window_size: int = 5,
        is_result_verbose: bool = True,
    ):
        self.candidates = candidates
        self.window_size = window_size
        self.is_result_verbose = is_result_verbose

        self._upper_limit = len(self.candidates) - 1
        self._lower_limit = 0
        self._selected_index = [0]
        self._scroll_offset = [0]
        self._prefix = "> "
        self._prefix_length = len(self._prefix)
        self._max_length = max(len(item) for item in self.candidates)
        self._max_length += self._prefix_length + 3

    def _get_choice_text(self):
        visible_items = self.candidates[
            self._scroll_offset[0] : self._scroll_offset[0] + self.window_size
        ]
        lines = []
        for i, item in enumerate(visible_items):
            real_index = self._scroll_offset[0] + i
            if real_index == self._selected_index[0]:
                lines.append(("class:selected", f"{self._prefix} {item}\n"))
            else:
                lines.append(("class:unselected", f"  {item}\n"))
        return lines

    def get_scrollbar_text(self):
        bar = []
        # total = len(candidates)
        for i in range(self.window_size):
            position = self._scroll_offset[0] + i
            # ratio = position / total
            # 現在の選択位置は太く
            if position == self._selected_index[0]:
                bar.append(("class:bar.active", "█\n"))
            else:
                bar.append(("class:bar.inactive", "░\n"))
        return bar

    def _key_bindings(self):
        kb = KeyBindings()

        @kb.add("up")
        def move_up(event):
            if self._selected_index[0] > self._lower_limit:
                self._selected_index[0] -= 1
                if self._selected_index[0] < self._scroll_offset[0]:
                    self._scroll_offset[0] = self._selected_index[0]

        @kb.add("down")
        def move_down(event):
            if self._selected_index[0] < self._upper_limit:
                self._selected_index[0] += 1
                if self._selected_index[0] >= self._scroll_offset[0] + self.window_size:
                    self._scroll_offset[0] = (
                        self._selected_index[0] - self.window_size + 1
                    )

        @kb.add("enter")
        def confirm(event):
            event.app.exit(result=self.candidates[self._selected_index[0]])

        @kb.add("c-c")
        def exit_(event):
            event.app.exit(result=None)

        return kb

    def _get_style(self):
        style = Style.from_dict(
            {
                "selected": "#2C3E50 #F1C40F bold",
                "unselected": "default #FFFFFF",
                "bar.active": "#F1C40F bold",
                "bar.inactive": "#7F8C8D",
            }
        )
        return style

    def __call__(self) -> str:
        text_control = FormattedTextControl(self._get_choice_text)
        bar_control = FormattedTextControl(self.get_scrollbar_text)

        text_window = Window(
            content=text_control, width=self._max_length, dont_extend_width=True
        )
        bar_window = Window(content=bar_control, width=1, dont_extend_width=True)

        app = Application(
            layout=Layout(HSplit([VSplit([text_window, bar_window])])),
            key_bindings=self._key_bindings(),
            full_screen=False,
            refresh_interval=0.1,
            style=self._get_style(),
        )
        result: str = app.run()
        if self.is_result_verbose:
            print(f"selected: {result}")
        return result
