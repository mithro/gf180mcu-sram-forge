"""Tests for status fetcher."""



from sram_forge.status.fetcher import (
    parse_forge_sha_from_message,
)


def test_parse_forge_sha_from_message():
    """Extract sram-forge SHA from commit message."""
    message = """chore: update generated files from sram-forge

Source commit: abc1234def5678
Workflow run: https://github.com/mithro/gf180mcu-sram-forge/actions/runs/12345"""

    forge_sha, forge_run_id = parse_forge_sha_from_message(message)

    assert forge_sha == "abc1234def5678"
    assert forge_run_id == 12345


def test_parse_forge_sha_from_message_no_match():
    """Handle commit messages without forge info."""
    message = "Initial commit"

    forge_sha, forge_run_id = parse_forge_sha_from_message(message)

    assert forge_sha is None
    assert forge_run_id is None


def test_parse_forge_sha_partial_match():
    """Handle commit messages with only SHA."""
    message = """chore: update

Source commit: deadbeef123"""

    forge_sha, forge_run_id = parse_forge_sha_from_message(message)

    assert forge_sha == "deadbeef123"
    assert forge_run_id is None
