import csv
import io

import pytest
from click.testing import CliRunner


def make_csv(delimiter, field_length, newline="\n", count=5):
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=delimiter, lineterminator=newline)
    writer.writerow(["description", "amount"])
    writer.writerows(["x" * field_length, number] for number in range(count))
    return output.getvalue()


@pytest.mark.parametrize("delimiter", [",", "\t", ";", "|"])
@pytest.mark.parametrize("field_length", [300, 1500])
def test_csv_sniffing_preserves_complete_lines(monkeypatch, delimiter, field_length):
    from rich_cli import __main__ as cli

    data = make_csv(delimiter, field_length)
    monkeypatch.setattr(cli, "read_resource", lambda *args: (data, None))

    table = cli.render_csv("-")

    assert table.show_header
    assert [column.header for column in table.columns] == ["description", "amount"]
    assert table.row_count == 5
    assert table.columns[0]._cells == ["x" * field_length] * 5
    assert table.columns[1]._cells == [str(number) for number in range(5)]


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_piped_tsv_with_long_rows(newline):
    from rich_cli.__main__ import main

    result = CliRunner().invoke(
        main, ["-", "--csv"], input=make_csv("\t", 300, newline)
    )

    assert result.exit_code == 0, result.output
    assert "description" in result.output
    assert "amount" in result.output


@pytest.mark.parametrize(
    "options, expected", [({}, 150), ({"head": 2}, 2), ({"tail": 3}, 3)]
)
def test_csv_sampling_does_not_truncate_output(monkeypatch, options, expected):
    from rich_cli import __main__ as cli

    data = make_csv("\t", 300, count=150).rstrip("\n")
    monkeypatch.setattr(cli, "read_resource", lambda *args: (data, None))

    table = cli.render_csv("-", **options)

    assert table.row_count == expected
    assert table.columns[1]._cells[-1] == ("1" if "head" in options else "149")


@pytest.mark.parametrize("resource, delimiter", [("data.csv", ","), ("data.tsv", "\t")])
def test_csv_extension_fallback(monkeypatch, resource, delimiter):
    from rich_cli import __main__ as cli

    data = f"name{delimiter}amount\napple{delimiter}1{delimiter}extra\n"
    monkeypatch.setattr(cli, "read_resource", lambda *args: (data, None))

    table = cli.render_csv(resource)

    assert table.show_header
    assert table.columns[0].header == "name"
    assert table.columns[0]._cells == ["apple"]
