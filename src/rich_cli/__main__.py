import sys
import click

from rich.console import Console, RenderableType


console = Console()
error_console = Console(stderr=True)

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
    try:
        with open(path, "rt") as resource_file:
            return resource_file.read()
    except Exception as error:
        error_console.print(str(error))
        raise SystemExit(-1)


@click.command()
@click.argument("resource")
@click.option("--print", "-p", is_flag=True, help="Print console markup")
@click.option(
    "--align",
    "-a",
    type=click.Choice(["default", "left", "right", "center", "full"]),
    default="default",
    help="Set alignment / justification",
)
@click.option("--width", "-w", type=int, help="maximum width", default=-1)
@click.option("--style", "-s", help="Text style", default="")
@click.option("--padding", help="Padding around output")
@click.option("--panel", type=click.Choice(BOXES), default="none", help="Box style")
@click.option("--theme", "-t", help="Syntax theme", default="ansi_dark")
@click.option("--line-numbers", "-n", is_flag=True, help="Enable line number in syntax")
@click.option("--guides", "-g", is_flag=True, help="Enable indentation guides")
def main(
    resource: str,
    print: bool = False,
    align: str = "left",
    width: int = -1,
    style: str = "",
    padding: str = "",
    panel: str = "",
    theme: str = "",
    line_numbers: bool = False,
    guides: bool = False,
):
    console = Console()

    print_padding = [0]
    if padding:
        try:
            print_padding = [int(pad) for pad in padding.split(",")]
        except TypeError:
            error_console.print(
                f"padding should be 1, 2 or 4 integers separated by commas"
            )
            sys.exit(-1)
        if len(print_padding) not in (1, 2, 4):
            error_console.print(
                f"padding should be 1, 2 or 4 integers separated by commas"
            )
            sys.exit(-1)

    renderable: RenderableType
    if print:
        from rich.text import Text

        try:
            renderable = Text.from_markup(resource)
        except Exception as error:
            error_console.print(f"unable to parse console markup: {error}")
            sys.exit(-1)

    else:

        from rich.syntax import Syntax

        renderable = Syntax.from_path(
            resource, theme=theme, line_numbers=line_numbers, indent_guides=guides
        )

    if print_padding:
        from rich.padding import Padding

        renderable = Padding(renderable, tuple(print_padding))

    if panel != "none":
        from rich import box
        from rich.panel import Panel

        renderable = Panel(renderable, getattr(box, panel.upper()))

    if style:
        from rich.style import Style
        from rich.styled import Styled

        try:
            text_style = Style.parse(style)
        except Exception:
            error_console.print(f"unable to parse style: {style!r}")
            sys.exit(-1)
        renderable = Styled(renderable, text_style)

    console.print(renderable, justify=align, width=None if width < 0 else width)


def run():
    main()


if __name__ == "__main__":
    run()
