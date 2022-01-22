import sys
from typing import Optional, List

import click
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.text import Text


console = Console()
error_console = Console(stderr=True)


def on_error(message: str, error: Optional[object] = None, code=-1) -> None:
    if error:
        error_console.print(
            f"[b][red]{escape(message)}[/b]:[/red] {escape(str(error))}"
        )
    else:
        error_console.print(f"[b red]{escape(message)}")
    sys.exit(code)


BOXES = [
    "none",
    "ascii",
    "ascii2",
    "ascii_double_head",
    "square",
    "square_double_head",
    "minimal",
    "minimal_heavy_head",
    "minimal_double_head",
    "simple",
    "simple_head",
    "simple_heavy",
    "horizontals",
    "rounded",
    "heavy",
    "heavy_edge",
    "heavy_head",
    "double",
    "double_edge",
]


def read_resource(path: str) -> str:
    """Read a resource form a file or stdin."""
    try:
        if path == "-":
            return sys.stdin.read()
        with open(path, "rt") as resource_file:
            return resource_file.read()
    except Exception as error:
        on_error(f"unable to read {escape(path)}", error)


@click.command()
@click.argument("resource")
@click.option("--print", "-p", is_flag=True, help="Display as console markup")
@click.option("--json", "-j", is_flag=True, help="Display as JSON")
@click.option("--markdown", "--md", is_flag=True, help="Display as markdown")
@click.option("--left", is_flag=True, help="Align to left")
@click.option("--right", is_flag=True, help="Align to right")
@click.option("--center", is_flag=True, help="Align to center")
@click.option("--text-left", is_flag=True, help="Justify text to left")
@click.option("--text-right", is_flag=True, help="Justify text to right")
@click.option("--text-center", is_flag=True, help="Justify text to center")
@click.option("--full", is_flag=True, help="Full justify text")
@click.option("--expand", is_flag=True, help="Expand to full width")
@click.option("--width", "-w", type=int, help="width of output", default=-1)
@click.option("--max-width", type=int, help="maximum width", default=-1)
@click.option("--style", "-s", help="Text style", default="")
@click.option("--wrap", type=bool, default=True, help="Wrap syntax")
@click.option("--padding", help="Padding around output")
@click.option("--panel", type=click.Choice(BOXES), default="none", help="Box style")
@click.option("--theme", "-t", help="Syntax theme", default="ansi_dark")
@click.option("--line-numbers", "-n", is_flag=True, help="Enable line number in syntax")
@click.option("--guides", "-g", is_flag=True, help="Enable indentation guides")
@click.option("--lexer", "-x", default="default", help="Lexter for syntax")
@click.option("--hyperlinks", is_flag=False, help="Render hyperlinks in markdown")
def main(
    resource: str,
    print: bool = False,
    json: bool = False,
    markdown: bool = False,
    left: bool = False,
    right: bool = False,
    center: bool = False,
    text_left: bool = False,
    text_right: bool = False,
    text_center: bool = False,
    full: bool = False,
    expand: bool = False,
    width: int = -1,
    max_width: int = -1,
    style: str = "",
    wrap: bool = True,
    padding: str = "",
    panel: str = "",
    theme: str = "",
    line_numbers: bool = False,
    guides: bool = False,
    lexer: str = "",
    hyperlinks: bool = False,
):
    console = Console()

    print_padding: List[int] = []
    if padding:
        try:
            print_padding = [int(pad) for pad in padding.split(",")]
        except TypeError:
            on_error(f"padding should be 1, 2 or 4 integers separated by commas")
        else:
            if len(print_padding) not in (1, 2, 4):
                on_error(f"padding should be 1, 2 or 4 integers separated by commas")
                sys.exit(-1)

    renderable: RenderableType = ""
    if print:
        from rich.text import Text

        justify = "default"
        if text_left:
            justify = "left"
        if text_right:
            justify = "right"
        if text_center:
            justify = "center"
        if full:
            justify = "fill"

        if resource == "-":
            resource = Text(sys.stdin.read(), justify=justify)
        try:
            renderable = Text.from_markup(resource, justify=justify)
        except Exception as error:
            on_error(f"unable to parse console markup", error)

    elif json:
        from rich.json import JSON

        if resource == "-":
            json_data = sys.stdin.read()
        else:
            json_data = read_resource(resource)
        try:
            renderable = JSON(json_data)
        except Exception as error:
            error_console.print(str(error))
            sys.exit(-1)

    elif markdown:
        from rich.markdown import Markdown

        markdown_data = read_resource(resource)
        renderable = Markdown(markdown_data, hyperlinks=hyperlinks)

    else:

        from rich.syntax import Syntax

        if resource == "-":
            renderable = Syntax(
                sys.stdin.read(),
                lexer,
                theme=theme,
                line_numbers=line_numbers,
                indent_guides=guides,
                word_wrap=wrap,
            )
        else:
            try:
                renderable = Syntax.from_path(
                    resource,
                    theme=theme,
                    line_numbers=line_numbers,
                    indent_guides=guides,
                    word_wrap=wrap,
                )
            except Exception as error:
                on_error("unable to read file", error)

    if print_padding:
        from rich.padding import Padding

        renderable = Padding(renderable, tuple(print_padding), expand=expand)

    if panel != "none":
        from rich import box
        from rich.panel import Panel

        renderable = Panel(renderable, getattr(box, panel.upper()), expand=expand)

    if style:
        from rich.style import Style
        from rich.styled import Styled

        try:
            text_style = Style.parse(style)
        except Exception:
            error_console.print(f"unable to parse style: {style!r}")
            sys.exit(-1)
        renderable = Styled(renderable, text_style)

    justify = "default"
    if left:
        justify = "left"
    elif right:
        justify = "right"
    elif center:
        justify = "center"

    if width != -1:
        from rich.constrain import Constrain

        renderable = Constrain(renderable, width)

    console.print(
        renderable, width=None if max_width < 0 else max_width, justify=justify
    )


def run():
    main()


if __name__ == "__main__":
    run()
