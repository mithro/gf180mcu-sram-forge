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


def test_cli_list_srams(runner):
    """List command shows available SRAMs."""
    result = runner.invoke(main, ["list", "srams"])

    assert result.exit_code == 0
    # Should show PDK SRAMs
    assert "sram512x8" in result.output.lower()
    assert "sram256x8" in result.output.lower()
    assert "sram128x8" in result.output.lower()
    assert "sram64x8" in result.output.lower()


def test_cli_list_slots(runner):
    """List command shows available slots."""
    result = runner.invoke(main, ["list", "slots"])

    assert result.exit_code == 0
    # Should show template slots
    assert "1x1" in result.output
    assert "0p5x0p5" in result.output


def test_cli_list_srams_shows_capacity(runner):
    """List SRAMs shows capacity information."""
    result = runner.invoke(main, ["list", "srams"])

    assert result.exit_code == 0
    # Should show words and bits
    assert "512" in result.output  # 512 words
    assert "8" in result.output    # 8-bit width


def test_cli_list_slots_shows_dimensions(runner):
    """List slots shows dimension information."""
    result = runner.invoke(main, ["list", "slots"])

    assert result.exit_code == 0
    # Should show die dimensions
    assert "3932" in result.output  # 1x1 width
    assert "5122" in result.output  # 1x1 height


def test_cli_calc_basic(runner):
    """Calc command calculates SRAM fit."""
    result = runner.invoke(main, ["calc", "--slot", "1x1", "--sram", "gf180mcu_fd_ip_sram__sram512x8m8wm1"])

    assert result.exit_code == 0
    # Should show fit results
    assert "col" in result.output.lower() or "row" in result.output.lower()
    assert "total" in result.output.lower() or "count" in result.output.lower()


def test_cli_calc_shows_capacity(runner):
    """Calc command shows total capacity."""
    result = runner.invoke(main, ["calc", "--slot", "1x1", "--sram", "gf180mcu_fd_ip_sram__sram512x8m8wm1"])

    assert result.exit_code == 0
    # Should show capacity information
    assert "word" in result.output.lower() or "bit" in result.output.lower() or "byte" in result.output.lower()


def test_cli_calc_shows_address_bits(runner):
    """Calc command shows address bits needed."""
    result = runner.invoke(main, ["calc", "--slot", "1x1", "--sram", "gf180mcu_fd_ip_sram__sram512x8m8wm1"])

    assert result.exit_code == 0
    # Should show address bits
    assert "address" in result.output.lower()


def test_cli_calc_invalid_sram(runner):
    """Calc command reports error for invalid SRAM."""
    result = runner.invoke(main, ["calc", "--slot", "1x1", "--sram", "nonexistent_sram"])

    assert result.exit_code != 0 or "error" in result.output.lower() or "not found" in result.output.lower()


def test_cli_calc_invalid_slot(runner):
    """Calc command reports error for invalid slot."""
    result = runner.invoke(main, ["calc", "--slot", "invalid_slot", "--sram", "gf180mcu_fd_ip_sram__sram512x8m8wm1"])

    assert result.exit_code != 0 or "error" in result.output.lower() or "not found" in result.output.lower()


def test_cli_gen_subcommand(runner):
    """CLI has gen subcommand."""
    result = runner.invoke(main, ["gen", "--help"])

    assert result.exit_code == 0
    assert "output" in result.output.lower()


def test_cli_check_subcommand(runner):
    """CLI has check subcommand."""
    result = runner.invoke(main, ["check", "--help"])

    assert result.exit_code == 0


def test_downstream_list(runner):
    """downstream list shows all repos."""
    result = runner.invoke(main, ["downstream", "list"])

    assert result.exit_code == 0
    assert "u8b24k" in result.output
    assert "u8b3k" in result.output


def test_downstream_matrix(runner):
    """downstream matrix outputs JSON."""
    import json

    result = runner.invoke(main, ["downstream", "matrix"])

    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "include" in data
    assert len(data["include"]) == 4
