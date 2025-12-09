"""Models for workflow status reporting."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, computed_field


class WorkflowRun(BaseModel):
    """A single GitHub Actions workflow run."""

    repo: str
    """Full repository name (owner/repo)."""

    sram: str
    """SRAM identifier for display."""

    slot: str
    """Slot size."""

    workflow_name: str
    """Name of the workflow."""

    status: Literal["queued", "in_progress", "completed"]
    """Current status of the run."""

    conclusion: Literal[
        "success", "failure", "cancelled", "skipped",
        "neutral", "timed_out", "action_required", "stale"
    ] | None
    """Final conclusion (only set when completed)."""

    run_id: int
    """GitHub Actions run ID."""

    head_sha: str
    """Commit SHA in the downstream repo."""

    updated_at: datetime
    """When the run was last updated."""

    html_url: str
    """URL to the workflow run page."""

    forge_sha: str | None
    """sram-forge commit that generated this build (from commit message)."""

    forge_run_id: int | None
    """sram-forge workflow run ID (from commit message)."""

    @computed_field
    @property
    def is_success(self) -> bool:
        """Whether this run succeeded."""
        return self.conclusion == "success"


class ForgeRevision(BaseModel):
    """Workflow runs grouped by sram-forge revision."""

    forge_sha: str
    """The sram-forge commit SHA."""

    forge_run_url: str | None
    """URL to the sram-forge workflow run."""

    timestamp: datetime
    """When this revision was built."""

    runs: list[WorkflowRun]
    """Workflow runs for each downstream repo."""

    @computed_field
    @property
    def passing_count(self) -> int:
        """Number of passing runs."""
        return sum(1 for r in self.runs if r.is_success)

    @computed_field
    @property
    def total_count(self) -> int:
        """Total number of runs."""
        return len(self.runs)

    @computed_field
    @property
    def summary(self) -> str:
        """Summary string like '3/4'."""
        return f"{self.passing_count}/{self.total_count}"

    @computed_field
    @property
    def all_passing(self) -> bool:
        """Whether all runs passed."""
        return self.passing_count == self.total_count


class StatusReport(BaseModel):
    """Complete status report across all downstream repos."""

    generated_at: datetime
    """When this report was generated."""

    revisions: list[ForgeRevision]
    """Revisions, most recent first."""
