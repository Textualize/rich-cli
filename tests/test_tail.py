import pytest
from click.testing import CliRunner


@pytest.mark.parametrize("tail", [1, 2, 3, 5])
@pytest.mark.parametrize("newline", ["", "\n"])
def test_syntax_tail_keeps_requested_last_lines(tmp_path, tail, newline):
    from rich_cli.__main__ import main

    lines = ["FIRST_LINE", "MIDDLE_LINE", "LAST_LINE"]
    path = tmp_path / "lines.txt"
    path.write_text("\n".join(lines) + newline, encoding="utf-8")
    result = CliRunner().invoke(
        main, [str(path), "--syntax", "--lexer", "text", "--tail", str(tail)]
    )
    assert result.exit_code == 0, repr(result.exception)
    expected = lines[-tail:]
    assert [line for line in lines if line in result.output] == expected
