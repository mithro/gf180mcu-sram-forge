"""Format status reports for different outputs."""

from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from sram_forge.status.models import StatusReport, WorkflowRun


def _time_ago(dt: datetime) -> str:
    """Format datetime as relative time string."""
    now = datetime.now(timezone.utc)
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        mins = int(seconds / 60)
        return f"{mins}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    else:
        days = int(seconds / 86400)
        return f"{days}d ago"


def _status_emoji(run: WorkflowRun) -> str:
    """Get emoji for run status."""
    if run.status != "completed":
        return "🔄"
    return "✅" if run.is_success else "❌"


def format_terminal(report: StatusReport) -> str:
    """Format report for terminal output with colors."""
    lines = [
        "sram-forge IC Status",
        "=" * 50,
        f"Last updated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
    ]

    for rev in report.revisions:
        sha_short = rev.forge_sha[:7] if len(rev.forge_sha) > 7 else rev.forge_sha
        status_indicator = "✅" if rev.all_passing else "❌"

        lines.append(f"📦 {sha_short} ({_time_ago(rev.timestamp)})  {rev.summary} {status_indicator}")

        # Show SRAMs on one line
        sram_statuses = [f"{_status_emoji(r)} {r.sram}" for r in rev.runs]
        lines.append(f"   {' '.join(sram_statuses)}")
        lines.append("")

    # Summary
    if report.revisions:
        latest = report.revisions[0]
        if latest.all_passing:
            lines.append("Summary: Latest revision passing ✅")
        else:
            lines.append(f"Summary: Latest revision {latest.summary} ❌")

    return "\n".join(lines)


def format_markdown(report: StatusReport) -> str:
    """Format report as markdown table."""
    lines = [
        "## sram-forge IC Status",
        "",
        f"*Last updated: {report.generated_at.strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
    ]

    for rev in report.revisions:
        sha_short = rev.forge_sha[:7] if len(rev.forge_sha) > 7 else rev.forge_sha
        sha_link = f"[`{sha_short}`]({rev.forge_run_url})" if rev.forge_run_url else f"`{sha_short}`"

        status_indicator = "✅" if rev.all_passing else "❌"
        lines.append(f"### Revision {sha_link} ({rev.summary} {status_indicator})")
        lines.append("")
        lines.append("| SRAM | Slot | Status | Workflow | Commit |")
        lines.append("|------|------|--------|----------|--------|")

        for run in rev.runs:
            status = f"{_status_emoji(run)} {run.conclusion or run.status}"
            commit_link = f"[`{run.head_sha[:7]}`]({run.html_url})"
            lines.append(f"| {run.sram} | {run.slot} | {status} | {run.workflow_name} | {commit_link} |")

        lines.append("")

    return "\n".join(lines)


def format_json(report: StatusReport) -> str:
    """Format report as JSON."""
    return report.model_dump_json(indent=2)


def format_html(report: StatusReport) -> str:
    """Format report as self-contained HTML page."""
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,
    )
    env.globals["time_ago"] = _time_ago

    template = env.get_template("status_page.html.j2")
    return template.render(report=report)
