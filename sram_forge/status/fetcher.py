"""Fetch workflow status from GitHub via gh CLI."""

import json
import re
import subprocess
from datetime import datetime, timezone

from sram_forge.models.downstream import DownstreamRepo
from sram_forge.status.models import WorkflowRun, ForgeRevision, StatusReport


def parse_forge_sha_from_message(message: str) -> tuple[str | None, int | None]:
    """Extract sram-forge source commit SHA and run ID from commit message.

    Looks for patterns like:
        Source commit: abc1234
        Workflow run: https://github.com/.../actions/runs/12345

    Args:
        message: Git commit message

    Returns:
        Tuple of (forge_sha, forge_run_id), either can be None
    """
    sha_match = re.search(r"Source commit:\s*([a-f0-9]+)", message)
    run_match = re.search(r"/actions/runs/(\d+)", message)

    return (
        sha_match.group(1) if sha_match else None,
        int(run_match.group(1)) if run_match else None,
    )


def fetch_workflow_runs(repo: str, limit: int = 5) -> list[dict]:
    """Fetch latest workflow runs for a repo using gh CLI.

    Args:
        repo: Full repository name (owner/repo)
        limit: Maximum number of runs to fetch

    Returns:
        List of workflow run dicts from gh CLI
    """
    result = subprocess.run(
        [
            "gh", "run", "list",
            "--repo", repo,
            "--limit", str(limit),
            "--json", "workflowName,status,conclusion,databaseId,headSha,updatedAt,url",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def fetch_commit_message(repo: str, sha: str) -> str | None:
    """Fetch commit message for a SHA using gh CLI.

    Args:
        repo: Full repository name (owner/repo)
        sha: Commit SHA

    Returns:
        Commit message or None if fetch fails
    """
    result = subprocess.run(
        [
            "gh", "api",
            f"repos/{repo}/commits/{sha}",
            "--jq", ".commit.message",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def fetch_repo_status(
    repo: DownstreamRepo,
    limit: int = 5,
) -> list[WorkflowRun]:
    """Fetch workflow status for a single downstream repo.

    Args:
        repo: Downstream repository config
        limit: Max runs to fetch

    Returns:
        List of WorkflowRun objects
    """
    full_name = repo.full_name
    raw_runs = fetch_workflow_runs(full_name, limit)

    runs = []
    for raw in raw_runs:
        # Get commit message to extract forge SHA
        commit_msg = fetch_commit_message(full_name, raw["headSha"])
        forge_sha, forge_run_id = (None, None)
        if commit_msg:
            forge_sha, forge_run_id = parse_forge_sha_from_message(commit_msg)

        runs.append(WorkflowRun(
            repo=full_name,
            sram=repo.sram,
            slot=repo.slot,
            workflow_name=raw["workflowName"],
            status=raw["status"],
            conclusion=raw.get("conclusion"),
            run_id=raw["databaseId"],
            head_sha=raw["headSha"],
            updated_at=datetime.fromisoformat(raw["updatedAt"].replace("Z", "+00:00")),
            html_url=raw["url"],
            forge_sha=forge_sha,
            forge_run_id=forge_run_id,
        ))

    return runs


def group_by_forge_revision(runs: list[WorkflowRun]) -> list[ForgeRevision]:
    """Group workflow runs by their sram-forge source revision.

    Args:
        runs: List of all workflow runs

    Returns:
        List of ForgeRevision objects, most recent first
    """
    # Group by forge_sha
    by_sha: dict[str | None, list[WorkflowRun]] = {}
    for run in runs:
        key = run.forge_sha or f"unknown-{run.head_sha[:7]}"
        if key not in by_sha:
            by_sha[key] = []
        by_sha[key].append(run)

    # Convert to ForgeRevision objects
    revisions = []
    for sha, sha_runs in by_sha.items():
        # Find latest timestamp and run URL
        latest = max(sha_runs, key=lambda r: r.updated_at)
        forge_run_url = None
        if latest.forge_run_id:
            forge_run_url = f"https://github.com/mithro/gf180mcu-sram-forge/actions/runs/{latest.forge_run_id}"

        revisions.append(ForgeRevision(
            forge_sha=sha if not sha.startswith("unknown-") else sha,
            forge_run_url=forge_run_url,
            timestamp=latest.updated_at,
            runs=sha_runs,
        ))

    # Sort by timestamp, most recent first
    revisions.sort(key=lambda r: r.timestamp, reverse=True)
    return revisions


def fetch_all_status(repos: list[DownstreamRepo], limit: int = 5) -> StatusReport:
    """Fetch status for all downstream repos and create report.

    Args:
        repos: List of downstream repo configs
        limit: Max runs per repo

    Returns:
        Complete StatusReport
    """
    all_runs = []
    for repo in repos:
        try:
            runs = fetch_repo_status(repo, limit)
            all_runs.extend(runs)
        except subprocess.CalledProcessError as e:
            # Log error but continue with other repos
            print(f"Warning: Failed to fetch status for {repo.full_name}: {e}")

    revisions = group_by_forge_revision(all_runs)

    return StatusReport(
        generated_at=datetime.now(timezone.utc),
        revisions=revisions,
    )
