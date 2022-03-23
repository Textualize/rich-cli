from typing import Any

from rich.console import Console, ConsoleOptions, RenderResult
from rich.markdown import Markdown, TextElement
from rich.padding import Padding
from rich.syntax import Syntax


class CodeBlock(TextElement):
    """A code block with syntax highlighting."""

    style_name = "markdown.code_block"

    @classmethod
    def create(cls, markdown: "Markdown", node: Any) -> "CodeBlock":
        node_info = node.info or ""
        lexer_name = node_info.partition(" ")[0]
        return cls(lexer_name or "default", markdown.code_theme)

    def __init__(self, lexer_name: str, theme: str) -> None:
        self.lexer_name = lexer_name
        self.theme = theme

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> RenderResult:
        code = str(self.text).rstrip()
        syntax = Syntax(code, self.lexer_name, theme=self.theme, word_wrap=True)
        yield Padding(syntax, (0, 4))


Markdown.elements["code_block"] = CodeBlock
