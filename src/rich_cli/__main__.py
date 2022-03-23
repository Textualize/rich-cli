from operator import itemgetter
import sys
from typing import TYPE_CHECKING, List, NoReturn, Optional, Tuple

import click
from pygments.util import ClassNotFound
from rich.console import Console, RenderableType
from rich.markup import escape
from rich.text import Text

console = Console()
error_console = Console(stderr=True)

if TYPE_CHECKING:
    from rich.console import ConsoleOptions, RenderResult
    from rich.measure import Measurement

BOXES = [
    "none",
    "ascii",
    "ascii2",
    "square",
    "rounded",
    "heavy",
    "double",
]

BOX_TEXT = ", ".join(sorted(BOXES))

COMMON_LEXERS = {
    "html": "html",
    "py": "python",
    "md": "markdown",
    "js": "javascript",
    "xml": "xml",
    "json": "json",
    "toml": "toml",
}

VERSION = "1.5.1"


AUTO = 0
SYNTAX = 1
PRINT = 2
MARKDOWN = 3
RST = 4
JSON = 5
RULE = 6
INSPECT = 7
CSV = 8


def on_error(message: str, error: Optional[Exception] = None, code=-1) -> NoReturn:
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


def read_resource(path: str, lexer: Optional[str]) -> Tuple[str, Optional[str]]:
    """Read a resource form a file or stdin."""
    if not path:
        on_error("missing path or URL")

    if path.startswith(("http://", "https://")):
        import requests

        response = requests.get(path)

        text = response.text
        try:
            mime_type: str = response.headers["Content-Type"]
            if ";" in mime_type:
                mime_type = mime_type.split(";", 1)[0]
        except KeyError:
            pass
        else:
            if not lexer:
                _, dot, ext = path.rpartition(".")
                if dot and ext:
                    ext = ext.lower()
                    lexer = COMMON_LEXERS.get(ext, None)
                if lexer is None:
                    from pygments.lexers import get_lexer_for_mimetype

                    try:
                        lexer = get_lexer_for_mimetype(mime_type).name
                    except Exception:
                        pass
        return (text, lexer)
    try:
        if path == "-":
            return (sys.stdin.read(), None)

        with open(path, "rt") as resource_file:
            text = resource_file.read()
        if not lexer:
            _, dot, ext = path.rpartition(".")
            if dot and ext:
                ext = ext.lower()
                lexer = COMMON_LEXERS.get(ext, None)
        if not lexer:
            from pygments.lexers import guess_lexer_for_filename

            try:
                lexer = guess_lexer_for_filename(path, text).name
            except ClassNotFound:
                return (text, "text")
        return (text, lexer)
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


def blend_text(
    message: str, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
) -> Text:
    """Blend text from one color to another."""
    text = Text(message)
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1
    size = len(text)
    for index in range(size):
        blend = index / size
        color = f"#{int(r1 + dr * blend):2X}{int(g1 + dg * blend):2X}{int(b1 + db * blend):2X}"
        text.stylize(color, index, index + 1)
    return text


class RichCommand(click.Command):
    """Override Clicks help with a Richer version."""

    # TODO: Extract this in to a general tool, i.e. rich-click

    def format_help(self, ctx, formatter):

        from rich.highlighter import RegexHighlighter
        from rich.panel import Panel
        from rich.table import Table
        from rich.theme import Theme

        class OptionHighlighter(RegexHighlighter):
            highlights = [
                r"(?P<switch>\-\w)",
                r"(?P<option>\-\-[\w\-]+)",
            ]

        highlighter = OptionHighlighter()

        console = Console(
            theme=Theme(
                {
                    "option": "bold cyan",
                    "switch": "bold green",
                }
            ),
            highlighter=highlighter,
        )

        console.print(
            f"[b]Rich CLI[/b] [magenta]v{VERSION}[/] 🤑\n\n[dim]Rich text and formatting in the terminal\n",
            justify="center",
        )

        console.print(
            "Usage: [b]rich[/b] [b][OPTIONS][/] [b cyan]<PATH,TEXT,URL, or '-'>\n"
        )

        options_table = Table(highlight=True, box=None, show_header=False)

        for param in self.get_params(ctx)[1:]:

            if len(param.opts) == 2:
                opt1 = highlighter(param.opts[1])
                opt2 = highlighter(param.opts[0])
            else:
                opt2 = highlighter(param.opts[0])
                opt1 = Text("")

            if param.metavar:
                opt2 += Text(f" {param.metavar}", style="bold yellow")

            options = Text(" ".join(reversed(param.opts)))
            help_record = param.get_help_record(ctx)
            if help_record is None:
                help = ""
            else:
                help = Text.from_markup(param.get_help_record(ctx)[-1], emoji=False)

            if param.metavar:
                options += f" {param.metavar}"

            options_table.add_row(opt1, opt2, highlighter(help))

        console.print(
            Panel(
                options_table, border_style="dim", title="Options", title_align="left"
            )
        )

        console.print(
            blend_text("♥ https://www.textualize.io", (32, 32, 255), (255, 32, 255)),
            justify="right",
        )


@click.command(cls=RichCommand)
@click.argument("resource", metavar="<PATH or TEXT or '-'>", default="")
@click.option(
    "--print",
    "-p",
    "_print",
    is_flag=True,
    help="Print [u]console markup[/u]. [dim]See https://rich.readthedocs.io/en/latest/markup.html",
)
@click.option("--rule", "-u", is_flag=True, help="Display a horizontal [u]rule[/u].")
@click.option("--json", "-j", is_flag=True, help="Display as [u]JSON[/u].")
@click.option("--markdown", "-m", is_flag=True, help="Display as [u]markdown[/u].")
@click.option("--rst", is_flag=True, help="Display [u]restructured text[/u].")
@click.option("--csv", is_flag=True, help="Display [u]CSV[/u] as a table.")
@click.option("--syntax", is_flag=True, help="[u]Syntax[/u] highlighting.")
@click.option("--inspect", is_flag=True, help="[u]Inspect[/u] a python object.")
@click.option(
    "--head",
    "-h",
    type=click.IntRange(min=1),
    metavar="LINES",
    default=None,
    help="Display first [b]LINES[/] of the file (requires --syntax or --csv).",
)
@click.option(
    "--tail",
    "-t",
    type=click.IntRange(min=1),
    metavar="LINES",
    default=None,
    help="Display last [b]LINES[/] of the file (requires --syntax or --csv).",
)
@click.option(
    "--emoji", "-j", is_flag=True, help="Enable emoji code. [dim]e.g. :sparkle:"
)
@click.option("--left", "-l", is_flag=True, help="Align to left.")
@click.option("--right", "-r", is_flag=True, help="Align to right.")
@click.option("--center", "-c", is_flag=True, help="Align to center.")
@click.option("--text-left", "-L", is_flag=True, help="Justify text to left.")
@click.option("--text-right", "-R", is_flag=True, help="Justify text to right.")
@click.option("--text-center", "-C", is_flag=True, help="Justify text to center.")
@click.option(
    "--text-full", "-F", is_flag=True, help="Justify text to both left and right edges."
)
@click.option(
    "--soft", is_flag=True, help="Enable soft wrapping of text (requires --print)."
)
@click.option(
    "--expand", "-e", is_flag=True, help="Expand to full width (requires --panel)."
)
@click.option(
    "--width",
    "-w",
    metavar="SIZE",
    type=int,
    help="Fit output to [b]SIZE[/] characters.",
    default=-1,
)
@click.option(
    "--max-width",
    "-W",
    metavar="SIZE",
    type=int,
    help="Set maximum width to [b]SIZE[/] characters.",
    default=-1,
)
@click.option(
    "--style", "-s", metavar="STYLE", help="Set text style to [b]STYLE[/b].", default=""
)
@click.option(
    "--rule-style",
    metavar="STYLE",
    help="Set rule style to [b]STYLE[/b].",
    default="bright_green",
)
@click.option(
    "--rule-char",
    metavar="CHARACTER",
    default="─",
    help="Use [b]CHARACTER[/b] to generate a line with --rule.",
)
@click.option(
    "--padding",
    "-d",
    metavar="TOP,RIGHT,BOTTOM,LEFT",
    help="Padding around output. [dim]1, 2 or 4 comma separated integers, e.g. 2,4",
)
@click.option(
    "--panel",
    "-a",
    default="none",
    type=click.Choice(BOXES),
    metavar="BOX",
    help=f"Set panel type to [b]BOX[/b]. [dim]{BOX_TEXT}",
)
@click.option(
    "--panel-style",
    "-S",
    default="",
    metavar="STYLE",
    help="Set the panel style to [b]STYLE[/b] (requires --panel).",
)
@click.option(
    "--theme",
    metavar="THEME",
    help="Set syntax theme to [b]THEME[/b]. [dim]See https://pygments.org/styles/",
    default="ansi_dark",
    envvar="RICH_THEME",
)
@click.option(
    "--line-numbers", "-n", is_flag=True, help="Enable line number in syntax."
)
@click.option(
    "--guides",
    "-g",
    is_flag=True,
    help="Enable indentation guides in syntax highlighting",
)
@click.option(
    "--lexer",
    "-x",
    metavar="LEXER",
    default=None,
    help="Use [b]LEXER[/b] for syntax highlighting. [dim]See https://pygments.org/docs/lexers/",
)
@click.option("--hyperlinks", "-y", is_flag=True, help="Render hyperlinks in markdown.")
@click.option(
    "--no-wrap", is_flag=True, help="Don't word wrap syntax highlighted files."
)
@click.option(
    "--title", metavar="TEXT", default="", help="Set panel title to [b]TEXT[/]."
)
@click.option(
    "--caption", metavar="TEXT", default="", help="Set panel caption to [b]TEXT[/]."
)
@click.option(
    "--force-terminal",
    is_flag=True,
    help="Force terminal output when not writing to a terminal.",
)
@click.option(
    "--export-html",
    "-o",
    metavar="PATH",
    default="",
    help="Write HTML to [b]PATH[/b].",
)
@click.option("--pager", is_flag=True, help="Display in an interactive pager.")
@click.option("--version", "-v", is_flag=True, help="Print version and exit.")
def main(
    resource: str,
    version: bool = False,
    _print: bool = False,
    syntax: bool = False,
    rule: bool = False,
    rule_char: Optional[str] = None,
    json: bool = False,
    markdown: bool = False,
    rst: bool = False,
    csv: bool = False,
    inspect: bool = True,
    emoji: bool = False,
    left: bool = False,
    right: bool = False,
    center: bool = False,
    text_left: bool = False,
    text_right: bool = False,
    text_center: bool = False,
    soft: bool = False,
    head: Optional[int] = None,
    tail: Optional[int] = None,
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
    force_terminal: bool = False,
    export_html: Optional[str] = None,
    pager: bool = False,
):
    """Rich toolbox for console output."""
    if version:
        sys.stdout.write(f"{VERSION}\n")
        return
    console = Console(
        emoji=emoji,
        record=bool(export_html),
        force_terminal=force_terminal if force_terminal else None,
    )

    def print_usage() -> None:
        console.print(
            r"Usage: [b]rich [OPTIONS][/b] [b cyan]<PATH,TEXT,URL, or '-'>[/]"
        )
        console.print("See [bold green]rich --help[/] for options")
        console.print()
        sys.exit(0)

    if width > 0:
        expand = True

    print_padding: List[int] = []
    if padding:
        try:
            print_padding = [int(pad) for pad in padding.split(",")]
        except Exception:
            on_error(f"padding should be 1, 2 or 4 integers separated by commas")
        else:
            if len(print_padding) not in (1, 2, 4):
                on_error(f"padding should be 1, 2 or 4 integers separated by commas")

    renderable: RenderableType = ""

    resource_format = AUTO
    if _print:
        resource_format = PRINT
    elif syntax:
        resource_format = SYNTAX
    elif json:
        resource_format = JSON
    elif markdown:
        resource_format = MARKDOWN
    elif rule:
        resource_format = RULE
    elif inspect:
        resource_format = INSPECT
    elif csv:
        resource_format = CSV
    elif rst:
        resource_format = RST

    if resource_format == AUTO and "." in resource:
        import os.path

        ext = ""
        if resource.startswith(("http://", "https://")):
            from urllib.parse import urlparse

            try:
                path = urlparse(resource).path
            except Exception:
                pass
            else:
                ext = os.path.splitext(path)[-1].lower()
        else:
            ext = os.path.splitext(resource)[-1].lower()

        if ext == ".md":
            resource_format = MARKDOWN
        elif ext == ".json":
            resource_format = JSON
        elif ext in (".csv", ".tsv"):
            resource_format = CSV
        elif ext == ".rst":
            resource_format = RST

    if resource_format == AUTO:
        resource_format = SYNTAX

    if resource_format in (PRINT, RULE):
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

        try:
            if resource == "-":
                renderable = Text.from_markup(
                    sys.stdin.read(), justify=justify, emoji=emoji
                )
            else:
                renderable = Text.from_markup(resource, justify=justify, emoji=emoji)
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
                characters=rule_char or "─",
                align="center" if justify in ("full", "default") else justify,
            )

    elif resource_format == JSON:
        from rich.json import JSON as RichJSON

        json_data, _lexer = read_resource(resource, lexer)
        try:
            renderable = RichJSON(json_data)
        except Exception as error:
            on_error("unable to read json", error)

    elif resource_format == MARKDOWN:
        from .markdown import Markdown

        markdown_data, lexer = read_resource(resource, lexer)
        renderable = Markdown(markdown_data, code_theme=theme, hyperlinks=hyperlinks)

    elif resource_format == RST:
        from rich_rst import RestructuredText

        rst_data, _ = read_resource(resource, lexer)
        renderable = RestructuredText(
            rst_data,
            code_theme=theme,
            default_lexer=lexer or "python",
            show_errors=False,
        )

    elif resource_format == INSPECT:
        try:
            inspect_data = eval(resource)
        except Exception:
            console.print_exception()
            on_error(f"unable to eval {resource!r}")

        from rich._inspect import Inspect

        renderable = Inspect(
            inspect_data, help=False, dunder=False, all=False, methods=True
        )

    elif resource_format == CSV:

        renderable = render_csv(resource, head, tail, title, caption)

    else:
        if not resource:
            print_usage()
        from rich.syntax import Syntax

        try:
            if resource == "-":
                code = sys.stdin.read()
            else:
                code, lexer = read_resource(resource, lexer)

            num_lines = len(code.splitlines())
            line_range = _line_range(head, tail, num_lines)
            renderable = Syntax(
                code,
                lexer,
                theme=theme,
                line_numbers=line_numbers,
                indent_guides=guides,
                word_wrap=not no_wrap,
                line_range=line_range,
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

    if width > 0 and not pager:
        renderable = ForceWidth(renderable, width=width)

    justify = "default"
    if left:
        justify = "left"
    elif right:
        justify = "right"
    elif center:
        justify = "center"

    if pager:
        if justify != "default":
            from rich.align import Align

            renderable = Align(renderable, justify)

        from .pager import PagerApp, PagerRenderable

        if width < 0:
            width = console.width
        render_options = console.options.update(width=width - 1)
        lines = console.render_lines(renderable, render_options, new_lines=True)
        PagerApp.run(title=resource, content=PagerRenderable(lines, width=width))

    else:
        try:
            console.print(
                renderable,
                width=None if max_width <= 0 else max_width,
                soft_wrap=soft,
                justify=justify,
            )
        except Exception as error:
            on_error("failed to print resource", error)

    if export_html:
        try:
            console.save_html(export_html)
        except Exception as error:
            on_error("failed to save HTML", error)


def render_csv(
    resource: str,
    head: Optional[int] = None,
    tail: Optional[int] = None,
    title: Optional[str] = None,
    caption: Optional[str] = None,
) -> RenderableType:
    """Render resource as CSV.

    Args:
        resource (str): Resource string.

    Returns:
        RenderableType: Table renderable.
    """
    import io
    import csv
    import re
    from rich import box
    from rich.table import Table
    from operator import itemgetter

    is_number = re.compile(r"\-?[0-9]*?\.?[0-9]*?").fullmatch

    csv_data, _ = read_resource(resource, "csv")
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(csv_data[:1024], delimiters=",\t|;")
        has_header = sniffer.has_header(csv_data[:1024])
    except csv.Error as error:
        if resource.lower().endswith(".csv"):
            dialect = csv.get_dialect("excel")
            has_header = True
        elif resource.lower().endswith(".tsv"):
            dialect = csv.get_dialect("excel-tab")
            has_header = True
        else:
            on_error(str(error))

    csv_file = io.StringIO(csv_data)
    reader = csv.reader(csv_file, dialect=dialect)

    table = Table(
        show_header=has_header,
        box=box.HEAVY_HEAD if has_header else box.SQUARE,
        border_style="blue",
        title=title,
        caption=caption,
        caption_justify="right",
    )
    rows = iter(reader)
    if has_header:
        header = next(rows)
        for column in header:
            table.add_column(column)

    table_rows = [row for row in rows if row]
    if head is not None:
        table_rows = table_rows[:head]
    elif tail is not None:
        table_rows = table_rows[-tail:]
    for row in table_rows:
        if row:
            table.add_row(*row)

    for index, table_column in enumerate(table.columns):
        get_index = itemgetter(index)

        for row in table_rows:
            try:
                value = get_index(row)
                if value and not is_number(value):
                    break
            except Exception:
                break
        else:
            table_column.justify = "right"
            table_column.style = "bold green"
            table_column.header_style = "bold green"

    return table


def _line_range(
    head: Optional[int], tail: Optional[int], num_lines: int
) -> Optional[Tuple[int, int]]:
    if head and tail:
        on_error("cannot specify both head and tail")
    if head:
        line_range = (1, head)
    elif tail:
        start_line = num_lines - tail + 2
        finish_line = num_lines + 1
        line_range = (start_line, finish_line)
    else:
        line_range = None
    return line_range


def run():
    main()


if __name__ == "__main__":
    run()
