import sys
from typing import NoReturn, Optional, List, TYPE_CHECKING

import click
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.text import Text


console = Console()
error_console = Console(stderr=True)


if TYPE_CHECKING:
    from rich.console import ConsoleOptions, RenderResult
    from rich.measure import Measurement


def on_error(message: str, error: Optional[object] = None, code=-1) -> NoReturn:
    """Render an error message then exit the app."""

    if error:
        error_text = Text(message)
        error_text.stylize("bold red")
        error_text += ": "
        error_text += error_console.highlighter(str(error))
        error_console.print(error_text)
    else:
        error_text = Text(message, style="bold red")
        error_console.print(error_text)
    sys.exit(code)


BOXES = ["none", "ascii", "square", "heavy", "double", "rounded"]


def read_resource(path: str) -> str:
    """Read a resource form a file or stdin."""
    try:
        if path == "-":
            return sys.stdin.read()
        with open(path, "rt") as resource_file:
            return resource_file.read()
    except Exception as error:
        on_error(f"unable to read {escape(path)}", error)


class ForceWidth:
    """Force a renderable to a given width."""

    def __init__(self, renderable: "RenderableType", width: int = 80) -> None:
        self.renderable = renderable
        self.width = width

    def __rich_console__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "RenderResult":
        child_options = options.update_width(self.width)
        yield from console.render(self.renderable, child_options)

    def __rich_measure__(
        self, console: "Console", options: "ConsoleOptions"
    ) -> "Measurement":
        from rich.measure import Measurement

        return Measurement(self.width, self.width)


@click.command()
@click.argument("resource", metavar="<PATH, TEXT, or '-' for stdin>")
@click.option("--print", "-p", is_flag=True, help="Display as console markup.")
@click.option("--rule", "-u", is_flag=True, help="Display a horizontal rule.")
@click.option("--json", "-j", is_flag=True, help="Display as JSON.")
@click.option("--markdown", "-m", is_flag=True, help="Display as markdown.")
@click.option("--emoji", "-j", is_flag=True, help="Enable emoji code.")
@click.option("--left", "-l", is_flag=True, help="Align to left.")
@click.option("--right", "-r", is_flag=True, help="Align to right.")
@click.option("--center", "-c", is_flag=True, help="Align to center.")
@click.option("--text-left", "-L", is_flag=True, help="Justify text to left.")
@click.option("--text-right", "-R", is_flag=True, help="Justify text to right.")
@click.option("--text-center", "-C", is_flag=True, help="Justify text to center.")
@click.option("--text-full", "-F", is_flag=True, help="Full justify text.")
@click.option("--soft", "-o", is_flag=True, help="Soft wrap text (requires --print).")
@click.option("--expand", "-e", is_flag=True, help="Expand to full width.")
@click.option("--width", "-w", type=int, help="Width of output.", default=-1)
@click.option("--max-width", "-W", type=int, help="Maximum width.", default=-1)
@click.option("--style", "-s", metavar="STYLE", help="Text style", default="")
@click.option(
    "--rule-style", "-R", metavar="STYLE", help="Rule style", default="bright_green"
)
@click.option("--padding", "-d", help="Padding around output")
@click.option(
    "--panel", "-a", type=click.Choice(BOXES), default="none", help="Panel type."
)
@click.option(
    "--panel-style",
    "-S",
    default="",
    metavar="STYLE",
    help="Border style (panel and table).",
)
@click.option("--theme", "-t", help="Syntax theme.", default="ansi_dark")
@click.option(
    "--line-numbers", "-n", is_flag=True, help="Enable line number in syntax."
)
@click.option("--guides", "-g", is_flag=True, help="Enable indentation guides.")
@click.option("--lexer", "-x", default="default", help="Lexter for syntax.")
@click.option("--hyperlinks", "-y", is_flag=True, help="Render hyperlinks in markdown.")
@click.option("--no-wrap", is_flag=True, help="Wrap syntax.")
@click.option("--title", default="", help="Panel title.")
@click.option("--caption", default="", help="Panel caption.")
@click.option("--export-html", "-o", default="", help="Write HTML")
def main(
    resource: str,
    print: bool = False,
    rule: bool = False,
    json: bool = False,
    markdown: bool = False,
    emoji: bool = False,
    left: bool = False,
    right: bool = False,
    center: bool = False,
    text_left: bool = False,
    text_right: bool = False,
    text_center: bool = False,
    soft: bool = False,
    text_full: bool = False,
    expand: bool = False,
    width: int = -1,
    max_width: int = -1,
    style: str = "",
    rule_style: str = "",
    no_wrap: bool = True,
    padding: str = "",
    panel: str = "",
    panel_style: str = "",
    title: str = "",
    caption: str = "",
    theme: str = "",
    line_numbers: bool = False,
    guides: bool = False,
    lexer: str = "",
    hyperlinks: bool = False,
    export_html: bool = False,
):
    """Rich toolbox for console output."""
    console = Console(emoji=emoji, record=export_html)

    if width > 0:
        expand = True

    print_padding: List[int] = []
    if padding:
        try:
            print_padding = [int(pad) for pad in padding.split(",")]
        except TypeError:
            on_error(f"padding should be 1, 2 or 4 integers separated by commas")
        else:
            if len(print_padding) not in (1, 2, 4):
                on_error(f"padding should be 1, 2 or 4 integers separated by commas")

    renderable: RenderableType = ""
    if print or rule:
        from rich.text import Text

        justify = "default"
        if text_left:
            justify = "left"
        elif text_right:
            justify = "right"
        elif text_center:
            justify = "center"
        elif text_full:
            justify = "full"

        if resource == "-":
            resource = Text(sys.stdin.read(), justify=justify, no_wrap=no_wrap)
        try:
            renderable = Text.from_markup(resource, justify=justify)
            renderable.no_wrap = no_wrap

        except Exception as error:
            on_error(f"unable to parse console markup", error)

        if rule:
            from rich.rule import Rule
            from rich.style import Style

            try:
                render_rule_style = Style.parse(rule_style)
            except Exception as error:
                on_error("unable to parse rule style", error)

            renderable = Rule(
                resource,
                style=render_rule_style,
                align="center" if justify in ("full", "default") else justify,
            )

    elif json:
        from rich.json import JSON

        json_data = read_resource(resource)
        try:
            renderable = JSON(json_data)
        except Exception as error:
            on_error("unable to read json", error)

    elif markdown:
        from rich.markdown import Markdown

        markdown_data = read_resource(resource)
        renderable = Markdown(markdown_data, hyperlinks=hyperlinks)

    else:

        from rich.syntax import Syntax

        try:
            if resource == "-":
                renderable = Syntax(
                    sys.stdin.read(),
                    lexer,
                    theme=theme,
                    line_numbers=line_numbers,
                    indent_guides=guides,
                    word_wrap=not no_wrap,
                )
            else:
                renderable = Syntax.from_path(
                    resource,
                    theme=theme,
                    line_numbers=line_numbers,
                    indent_guides=guides,
                    word_wrap=not no_wrap,
                )
        except Exception as error:
            on_error("unable to read file", error)

    if print_padding:
        from rich.padding import Padding

        renderable = Padding(renderable, tuple(print_padding), expand=expand)

    if panel != "none":
        from rich import box
        from rich.panel import Panel
        from rich.style import Style

        try:
            render_border_style = Style.parse(panel_style)
        except Exception as error:
            on_error("unable to parse panel style", error)

        renderable = Panel(
            renderable,
            getattr(box, panel.upper()),
            expand=expand,
            title=title,
            subtitle=caption,
            border_style=render_border_style,
        )

    if style:
        from rich.style import Style
        from rich.styled import Styled

        try:
            text_style = Style.parse(style)
        except Exception as error:
            on_error("unable to parse style", error)
        else:
            renderable = Styled(renderable, text_style)

    if width > 0:
        renderable = ForceWidth(renderable, width=width)

    justify = "default"
    if left:
        justify = "left"
    elif right:
        justify = "right"
    elif center:
        justify = "center"

    console.print(
        renderable,
        width=None if max_width <= 0 else max_width,
        justify=justify,
        soft_wrap=soft,
    )

    if export_html:
        try:
            console.save_html(export_html)
        except Exception as error:
            on_error("failed to save HTML", error)


def run():
    main()


if __name__ == "__main__":
    run()
