import pytest
from click.testing import CliRunner


@pytest.mark.parametrize("suffix", ["csv", "tsv"])
def test_empty_delimited_file_renders_without_exception(tmp_path, suffix):
    from rich_cli.__main__ import main

    path = tmp_path / f"empty.{suffix}"
    path.write_text("", encoding="utf-8")
    result = CliRunner().invoke(main, [str(path)])
    assert result.exit_code == 0, repr(result.exception)
    assert result.exception is None
