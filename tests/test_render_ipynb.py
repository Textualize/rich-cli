import json

import pytest
from click.testing import CliRunner


@pytest.mark.parametrize("output_type", ["display_data", "execute_result"])
@pytest.mark.parametrize(
    "plain_text", ["DISPLAY_FIRST\nDISPLAY_LAST", ["DISPLAY_FIRST\n", "DISPLAY_LAST"]]
)
def test_notebook_plain_text_outputs_are_rendered(tmp_path, output_type, plain_text):
    from rich_cli.__main__ import main

    output = {
        "output_type": output_type,
        "data": {"text/plain": plain_text},
        "metadata": {},
    }
    if output_type == "execute_result":
        output["execution_count"] = 7
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "name": "python3",
                "display_name": "Python",
                "language": "python",
            }
        },
        "cells": [
            {
                "cell_type": "code",
                "id": "display-output",
                "metadata": {},
                "execution_count": 7,
                "source": ["pass\n"],
                "outputs": [output],
            }
        ],
    }
    path = tmp_path / "display.ipynb"
    path.write_text(json.dumps(notebook), encoding="utf-8")
    result = CliRunner().invoke(main, [str(path)])
    assert result.exit_code == 0, repr(result.exception)
    assert "DISPLAY_FIRST" in result.output
    assert "DISPLAY_LAST" in result.output
    assert result.output.index("DISPLAY_FIRST") < result.output.index("DISPLAY_LAST")
    assert ("Out[" in result.output) == (output_type == "execute_result")
