"""Main CLI entry point for sram-forge."""

import click

try:
    from sram_forge import __version__
except ImportError:
    # Fallback for when running directly
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from __init__ import __version__


@click.group()
@click.version_option(version=__version__, prog_name="sram-forge")
def main():
    """sram-forge: Generate SRAM-based chip designs for GF180MCU."""
    pass


@main.command()
@click.argument("what", type=click.Choice(["srams", "slots"]))
def list(what: str):
    """List available SRAMs or slots."""
    click.echo(f"Listing {what}...")
    # TODO: Implement actual listing


@main.command()
@click.option("--slot", required=True, help="Slot name (e.g., 1x1)")
@click.option("--sram", required=True, help="SRAM macro name")
def calc(slot: str, sram: str):
    """Calculate SRAM capacity for a slot."""
    click.echo(f"Calculating fit for {sram} in slot {slot}...")
    # TODO: Implement actual calculation


@main.command()
@click.argument("config", type=click.Path(exists=True))
def check(config: str):
    """Validate a chip configuration file."""
    click.echo(f"Checking {config}...")
    # TODO: Implement validation


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--only", type=click.Choice(["verilog", "librelane", "testbench", "docs"]))
def gen(config: str, output: str, only: str | None):
    """Generate outputs from chip configuration."""
    click.echo(f"Generating from {config} to {output}...")
    if only:
        click.echo(f"Only generating: {only}")
    # TODO: Implement generation


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--name", required=True, help="Package name")
@click.option("--output", "-o", default=".", help="Output directory")
def package(config: str, name: str, output: str):
    """Create a complete asset package."""
    click.echo(f"Creating package '{name}' from {config}...")
    # TODO: Implement package generation


if __name__ == "__main__":
    main()
