from importlib.metadata import version

import pytest
from click.testing import CliRunner


@pytest.mark.parametrize("option", ["--version", "--help"])
def test_cli_reports_installed_distribution_version(option):
    from rich_cli.__main__ import main

    result = CliRunner().invoke(main, [option])
    assert result.exit_code == 0, repr(result.exception)
    expected = version("rich-cli")
    if option == "--version":
        assert result.output.strip() == expected
    else:
        assert f"v{expected}" in result.output
