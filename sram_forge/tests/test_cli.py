"""Tests for CLI."""

import pytest
from click.testing import CliRunner
from sram_forge.cli.main import main


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


def test_cli_help(runner):
    """CLI shows help."""
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "sram-forge" in result.output.lower() or "usage" in result.output.lower()


def test_cli_version(runner):
    """CLI shows version."""
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_list_subcommand(runner):
    """CLI has list subcommand."""
    result = runner.invoke(main, ["list", "--help"])

    assert result.exit_code == 0
    assert "srams" in result.output.lower() or "slots" in result.output.lower()


def test_cli_calc_subcommand(runner):
    """CLI has calc subcommand."""
    result = runner.invoke(main, ["calc", "--help"])

    assert result.exit_code == 0
