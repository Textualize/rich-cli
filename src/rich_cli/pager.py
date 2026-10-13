from typing import Iterable, List, Optional

from rich.console import Console, ConsoleOptions, RenderableType, RenderResult
from rich.measure import Measurement
from rich.segment import Segment

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import ScrollableContainer
from textual.widgets import Static


class PagerRenderable:
    def __init__(
        self, lines: Iterable[List[Segment]], new_lines: bool = False, width: int = 80
    ) -> None:
        """A simple renderable containing a number of lines of segments. May be used as an intermediate
        in rendering process.

        Args:
            lines (Iterable[List[Segment]]): Lists of segments forming lines.
            new_lines (bool, optional): Insert new lines after each line. Defaults to False.
        """
        self.lines = list(lines)
        self.new_lines = new_lines
        self.width = width

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        if self.new_lines:
            new_line = Segment.line()
            for line in self.lines:
                yield from line
                yield new_line
        else:
            for line in self.lines:
                yield from line

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> Measurement:
        return Measurement(self.width, self.width)


class PagerView(ScrollableContainer, can_focus=True):
    """Scrollable view with less / vi style keys, in addition to the
    arrow, page up / page down, home and end keys of ScrollableContainer."""

    BINDINGS = [
        Binding("j", "scroll_down", "Down", show=False),
        Binding("k", "scroll_up", "Up", show=False),
        Binding("space", "page_down", "Page down", show=False),
        Binding("ctrl+d", "half_page_down", "Half page down", show=False),
        Binding("ctrl+u", "half_page_up", "Half page up", show=False),
    ]

    def action_half_page_down(self) -> None:
        self.scroll_relative(y=self.size.height // 2, easing="out_cubic")

    def action_half_page_up(self) -> None:
        self.scroll_relative(y=-(self.size.height // 2), easing="out_cubic")


class PagerApp(App[None]):
    """App to scroll renderable"""

    CSS = """
    PagerView > Static {
        width: auto;
    }
    """

    BINDINGS = [Binding("q", "quit", "Quit")]

    def __init__(
        self, content: RenderableType, title: Optional[str] = None
    ) -> None:
        self.content = content
        super().__init__()
        if title:
            self.title = title

    def compose(self) -> ComposeResult:
        yield PagerView(Static(self.content))

    def on_mount(self) -> None:
        self.query_one(PagerView).focus()
