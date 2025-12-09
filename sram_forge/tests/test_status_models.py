"""Tests for status report models."""

from datetime import datetime, timezone


from sram_forge.status.models import WorkflowRun, ForgeRevision


def test_workflow_run_from_dict():
    """WorkflowRun can be created from dict."""
    data = {
        "repo": "mithro/gf180mcu-ic-1x1-sram-u8b24k",
        "sram": "u8b24k",
        "slot": "1x1",
        "workflow_name": "CI",
        "status": "completed",
        "conclusion": "success",
        "run_id": 12345,
        "head_sha": "abc1234",
        "updated_at": "2025-12-08T10:00:00Z",
        "html_url": "https://github.com/mithro/gf180mcu-ic-1x1-sram-u8b24k/actions/runs/12345",
        "forge_sha": "def5678",
        "forge_run_id": 67890,
    }
    run = WorkflowRun.model_validate(data)

    assert run.repo == "mithro/gf180mcu-ic-1x1-sram-u8b24k"
    assert run.conclusion == "success"
    assert run.is_success


def test_workflow_run_is_success():
    """WorkflowRun.is_success reflects conclusion."""
    success_run = WorkflowRun(
        repo="owner/repo", sram="u8b1k", slot="1x1", workflow_name="CI",
        status="completed", conclusion="success", run_id=1, head_sha="abc",
        updated_at=datetime.now(timezone.utc), html_url="http://example.com",
        forge_sha=None, forge_run_id=None
    )
    failure_run = WorkflowRun(
        repo="owner/repo", sram="u8b1k", slot="1x1", workflow_name="CI",
        status="completed", conclusion="failure", run_id=2, head_sha="def",
        updated_at=datetime.now(timezone.utc), html_url="http://example.com",
        forge_sha=None, forge_run_id=None
    )

    assert success_run.is_success is True
    assert failure_run.is_success is False


def test_forge_revision_summary():
    """ForgeRevision computes summary correctly."""
    now = datetime.now(timezone.utc)
    runs = [
        WorkflowRun(
            repo="owner/repo1", sram="u8b1k", slot="1x1", workflow_name="CI",
            status="completed", conclusion="success", run_id=1, head_sha="a",
            updated_at=now, html_url="http://example.com",
            forge_sha="abc123", forge_run_id=100
        ),
        WorkflowRun(
            repo="owner/repo2", sram="u8b2k", slot="1x1", workflow_name="CI",
            status="completed", conclusion="failure", run_id=2, head_sha="b",
            updated_at=now, html_url="http://example.com",
            forge_sha="abc123", forge_run_id=100
        ),
    ]

    revision = ForgeRevision(
        forge_sha="abc123",
        forge_run_url="http://example.com/runs/100",
        timestamp=now,
        runs=runs
    )

    assert revision.summary == "1/2"
    assert revision.all_passing is False
    assert revision.passing_count == 1
    assert revision.total_count == 2
