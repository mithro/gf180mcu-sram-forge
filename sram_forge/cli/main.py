"""Main CLI entry point for sram-forge."""

from pathlib import Path

import click

try:
    from sram_forge import __version__
except ImportError:
    # Fallback for when running directly
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from __init__ import __version__

from sram_forge.db.loader import load_srams, load_slots


def get_bundled_data_dir() -> Path:
    """Get path to bundled data directory."""
    return Path(__file__).parent.parent / "db" / "data"


@click.group()
@click.version_option(version=__version__, prog_name="sram-forge")
def main():
    """sram-forge: Generate SRAM-based chip designs for GF180MCU."""
    pass


@main.command("list")
@click.argument("what", type=click.Choice(["srams", "slots"]))
def list_cmd(what: str):
    """List available SRAMs or slots."""
    data_dir = get_bundled_data_dir()

    if what == "srams":
        srams = load_srams(data_dir / "srams.yaml")
        click.echo("Available SRAMs:")
        click.echo("-" * 70)
        for name, spec in sorted(srams.items()):
            bits = spec.size * spec.width
            click.echo(
                f"  {name}\n"
                f"    Capacity: {spec.size} x {spec.width}-bit = {bits} bits ({bits // 8} bytes)\n"
                f"    Size: {spec.dimensions_um.width:.2f} x {spec.dimensions_um.height:.2f} um\n"
                f"    Source: {spec.source}"
            )
            click.echo()
    else:
        slots = load_slots(data_dir / "slots.yaml")
        click.echo("Available Slots:")
        click.echo("-" * 70)
        for name, spec in sorted(slots.items()):
            die_area, core_area = spec.to_librelane_areas()
            click.echo(
                f"  {name}\n"
                f"    Die: {spec.die.width:.0f} x {spec.die.height:.0f} um\n"
                f"    Core: {spec.core_width:.0f} x {spec.core_height:.0f} um\n"
                f"    Core Area: {spec.core_area_um2 / 1e6:.3f} mm^2\n"
                f"    IO Budget: {spec.io_budget.bidir} bidir, {spec.io_budget.input} input"
            )
            click.echo()


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
