from typing import Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.markdown import Markdown as RichMarkdown, TextElement
from rich.padding import Padding
from rich.syntax import Syntax


class CodeBlock(TextElement):
    """A code block with syntax highlighting."""

    style_name = "markdown.code_block"

    @classmethod
    def create(cls, markdown: "Markdown", node: Any) -> "CodeBlock":
        node_info = node.info or ""
        lexer_name = node_info.partition(" ")[0]
        wrap_code = getattr(markdown, "wrap_code", True)
        return cls(lexer_name or "default", markdown.code_theme, wrap_code)

    def __init__(self, lexer_name: str, theme: str, wrap_code: bool = True) -> None:
        self.lexer_name = lexer_name
        self.theme = theme
        self.wrap_code = wrap_code

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        syntax = Syntax(code, self.lexer_name, theme=self.theme, word_wrap=self.wrap_code)
        yield Padding(syntax, (0, 4))


class Markdown(RichMarkdown):
    """Extended Markdown class with configurable code block wrapping."""
    
    def __init__(self, markup: str, code_theme: str = "monokai", hyperlinks: bool = False, wrap_code: bool = True):
        super().__init__(markup, code_theme=code_theme, hyperlinks=hyperlinks)
        self.wrap_code = wrap_code


Markdown.elements["code_block"] = CodeBlock
