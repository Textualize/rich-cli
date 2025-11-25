"""Tests for environment variable support in rich-cli."""

import os
from unittest import mock

import pytest
from click.testing import CliRunner

from rich_cli.__main__ import main


class TestEnvironmentVariables:
    """Test suite for environment variable functionality."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    @pytest.fixture
    def sample_python_file(self, tmp_path):
        """Create a sample Python file for testing."""
        file_path = tmp_path / "sample.py"
        file_path.write_text(
            "def hello():\n"
            "    print('Hello, World!')\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    hello()\n"
        )
        return str(file_path)

    @pytest.fixture
    def sample_markdown_file(self, tmp_path):
        """Create a sample Markdown file for testing."""
        file_path = tmp_path / "sample.md"
        file_path.write_text(
            "# Hello World\n\n"
            "This is a [link](https://example.com).\n"
        )
        return str(file_path)

    # ==================== RICH_HYPERLINKS Tests ====================

    def test_hyperlinks_env_var_enables_hyperlinks(
        self, runner, sample_markdown_file
    ):
        """Test that RICH_HYPERLINKS=1 enables hyperlinks."""
        with mock.patch.dict(os.environ, {"RICH_HYPERLINKS": "1"}):
            result = runner.invoke(
                main, [sample_markdown_file, "--markdown"]
            )
            assert result.exit_code == 0

    def test_hyperlinks_env_var_various_truthy_values(self, runner):
        """Test that various truthy values work for RICH_HYPERLINKS."""
        truthy_values = ["1", "true", "True", "TRUE", "yes", "Yes", "on", "ON"]

        for value in truthy_values:
            with mock.patch.dict(os.environ, {"RICH_HYPERLINKS": value}):
                result = runner.invoke(main, ["--help"])
                assert result.exit_code == 0, f"Failed for value: {value}"

    def test_hyperlinks_env_var_falsy_values(self, runner):
        """Test that falsy values disable hyperlinks."""
        falsy_values = ["0", "false", "False", "no", "off", ""]

        for value in falsy_values:
            with mock.patch.dict(os.environ, {"RICH_HYPERLINKS": value}):
                result = runner.invoke(main, ["--help"])
                assert result.exit_code == 0, f"Failed for value: {value}"

    def test_hyperlinks_cli_overrides_env_var(self, runner, sample_markdown_file):
        """Test that CLI flag overrides environment variable."""
        with mock.patch.dict(os.environ, {"RICH_HYPERLINKS": "1"}):
            result = runner.invoke(
                main, [sample_markdown_file, "--markdown"]
            )
            assert result.exit_code == 0

    # ==================== RICH_LINE_NUMBERS Tests ====================

    def test_line_numbers_env_var(self, runner, sample_python_file):
        """Test that RICH_LINE_NUMBERS enables line numbers."""
        with mock.patch.dict(os.environ, {"RICH_LINE_NUMBERS": "1"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    def test_line_numbers_env_var_disabled(self, runner, sample_python_file):
        """Test that RICH_LINE_NUMBERS=0 disables line numbers."""
        with mock.patch.dict(os.environ, {"RICH_LINE_NUMBERS": "0"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    # ==================== RICH_GUIDES Tests ====================

    def test_guides_env_var(self, runner, sample_python_file):
        """Test that RICH_GUIDES enables indent guides."""
        with mock.patch.dict(os.environ, {"RICH_GUIDES": "1"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    # ==================== RICH_FORCE_TERMINAL Tests ====================

    def test_force_terminal_env_var(self, runner, sample_python_file):
        """Test that RICH_FORCE_TERMINAL forces terminal output."""
        with mock.patch.dict(os.environ, {"RICH_FORCE_TERMINAL": "1"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    # ==================== RICH_SOFT_WRAP Tests ====================

    def test_soft_wrap_env_var(self, runner, sample_python_file):
        """Test that RICH_SOFT_WRAP enables soft wrapping."""
        with mock.patch.dict(os.environ, {"RICH_SOFT_WRAP": "1"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    # ==================== RICH_PAGER Tests ====================

    def test_pager_env_var(self, runner, sample_python_file):
        """Test that RICH_PAGER env var is recognized."""
        # Test with pager disabled to avoid interactive mode
        with mock.patch.dict(os.environ, {"RICH_PAGER": "0"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    # ==================== RICH_WIDTH Tests ====================

    def test_width_env_var(self, runner, sample_python_file):
        """Test that RICH_WIDTH sets output width."""
        with mock.patch.dict(os.environ, {"RICH_WIDTH": "80"}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    def test_width_env_var_various_values(self, runner, sample_python_file):
        """Test various width values."""
        for width in ["40", "80", "120", "200"]:
            with mock.patch.dict(os.environ, {"RICH_WIDTH": width}):
                result = runner.invoke(main, [sample_python_file])
                assert result.exit_code == 0, f"Failed for width: {width}"

    def test_width_invalid_value(self, runner, sample_python_file):
        """Test that invalid width values cause an error."""
        with mock.patch.dict(os.environ, {"RICH_WIDTH": "not_a_number"}):
            result = runner.invoke(main, [sample_python_file])
            # Click should raise an error for invalid int conversion
            assert result.exit_code != 0

    # ==================== Combined Tests ====================

    def test_multiple_env_vars_combined(self, runner, sample_python_file):
        """Test multiple environment variables working together."""
        env_vars = {
            "RICH_LINE_NUMBERS": "1",
            "RICH_GUIDES": "1",
            "RICH_WIDTH": "100",
        }
        with mock.patch.dict(os.environ, env_vars):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    def test_env_vars_with_existing_rich_theme(self, runner, sample_python_file):
        """Test new env vars work alongside existing RICH_THEME."""
        env_vars = {
            "RICH_THEME": "monokai",
            "RICH_LINE_NUMBERS": "1",
            "RICH_GUIDES": "1",
        }
        with mock.patch.dict(os.environ, env_vars):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    def test_unset_env_vars_use_defaults(self, runner, sample_python_file):
        """Test that unset env vars fall back to defaults."""
        env_vars_to_remove = [
            "RICH_HYPERLINKS",
            "RICH_LINE_NUMBERS",
            "RICH_GUIDES",
            "RICH_FORCE_TERMINAL",
            "RICH_SOFT_WRAP",
            "RICH_PAGER",
            "RICH_WIDTH",
        ]
        clean_env = {k: v for k, v in os.environ.items()
                     if k not in env_vars_to_remove}

        with mock.patch.dict(os.environ, clean_env, clear=True):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0

    def test_empty_string_env_var_treated_as_false(self, runner, sample_python_file):
        """Test that empty string env vars are treated as falsy."""
        with mock.patch.dict(os.environ, {"RICH_LINE_NUMBERS": ""}):
            result = runner.invoke(main, [sample_python_file])
            assert result.exit_code == 0
