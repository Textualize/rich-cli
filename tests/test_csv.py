import os
import subprocess
import sys
from xml.etree import ElementTree

import pytest


@pytest.mark.parametrize("source", ["stdin", "csv", "tsv"])
@pytest.mark.parametrize(
    "rows,expected",
    [
        (
            "[not-a-style],value\n[red]literal[/red],2\n[/bold],3\n",
            ["[not-a-style]", "[red]literal[/red]", "[/bold]"],
        ),
        (
            "[red]one[/red],1\n[red]two[/red],2\n",
            ["[red]one[/red]", "[red]two[/red]"],
        ),
    ],
)
def test_csv_values_are_literal(tmp_path, source, rows, expected):
    if source == "stdin":
        args = ["--csv", "-"]
        stdin = rows
    else:
        path = tmp_path / f"data.{source}"
        path.write_text(rows.replace(",", "\t") if source == "tsv" else rows)
        args = [str(path)]
        stdin = None
    result = subprocess.run(
        [sys.executable, "-m", "rich_cli", *args],
        input=stdin,
        text=True,
        capture_output=True,
        env={**os.environ, "COLUMNS": "120", "NO_COLOR": "1"},
    )
    assert result.returncode == 0, result.stderr
    for value in expected:
        assert value in result.stdout


def test_csv_svg_preserves_literal_cells(tmp_path):
    target = tmp_path / "table.svg"
    result = subprocess.run(
        [sys.executable, "-m", "rich_cli", "--csv", "-", "--export-svg", str(target)],
        input="name,value\n[red]literal[/red],2\n",
        text=True,
        capture_output=True,
        env={**os.environ, "COLUMNS": "120"},
    )
    assert result.returncode == 0, result.stderr
    text = "".join(ElementTree.parse(target).getroot().itertext())
    assert "[red]literal[/red]" in text
