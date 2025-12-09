"""Tests for status reporter."""

from datetime import datetime, timezone

import pytest

from sram_forge.status.models import WorkflowRun, ForgeRevision, StatusReport
from sram_forge.status.reporter import format_terminal, format_markdown, format_json, format_html


@pytest.fixture
def sample_report():
    """Create a sample status report for testing."""
    now = datetime.now(timezone.utc)
    runs = [
        WorkflowRun(
            repo="mithro/gf180mcu-ic-1x1-sram-u8b24k",
            sram="u8b24k", slot="1x1", workflow_name="CI",
            status="completed", conclusion="success", run_id=1, head_sha="aaa",
            updated_at=now, html_url="http://example.com/1",
            forge_sha="abc123", forge_run_id=100
        ),
        WorkflowRun(
            repo="mithro/gf180mcu-ic-0p5x0p5-sram-u8b3k",
            sram="u8b3k", slot="0p5x0p5", workflow_name="CI",
            status="completed", conclusion="failure", run_id=2, head_sha="bbb",
            updated_at=now, html_url="http://example.com/2",
            forge_sha="abc123", forge_run_id=100
        ),
    ]
    revision = ForgeRevision(
        forge_sha="abc123",
        forge_run_url="http://example.com/runs/100",
        timestamp=now,
        runs=runs
    )
    return StatusReport(generated_at=now, revisions=[revision])


def test_format_terminal(sample_report):
    """Terminal output contains key info."""
    result = format_terminal(sample_report)

    assert "abc123" in result  # Forge SHA
    assert "u8b24k" in result  # SRAM name
    assert "u8b3k" in result
    assert "1/2" in result  # Summary


def test_format_markdown(sample_report):
    """Markdown output is valid table format."""
    result = format_markdown(sample_report)

    assert "|" in result  # Table format
    assert "abc123" in result
    assert "u8b24k" in result


def test_format_json(sample_report):
    """JSON output is valid JSON."""
    import json

    result = format_json(sample_report)
    parsed = json.loads(result)

    assert "generated_at" in parsed
    assert "revisions" in parsed
    assert len(parsed["revisions"]) == 1


def test_format_html(sample_report):
    """HTML output is valid HTML."""
    result = format_html(sample_report)

    assert "<!DOCTYPE html>" in result
    assert "abc123" in result
    assert "u8b24k" in result
    assert "<script>" in result  # Has JS
    assert "<style>" in result   # Has CSS
