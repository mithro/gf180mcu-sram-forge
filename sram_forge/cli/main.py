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
from sram_forge.calc.fit import calculate_fit


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
@click.option("--halo", default=10.0, help="Routing halo in microns (default: 10)")
def calc(slot: str, sram: str, halo: float):
    """Calculate SRAM capacity for a slot."""
    data_dir = get_bundled_data_dir()

    # Load databases
    try:
        srams = load_srams(data_dir / "srams.yaml")
        slots = load_slots(data_dir / "slots.yaml")
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)

    # Validate SRAM name
    if sram not in srams:
        click.echo(f"Error: SRAM '{sram}' not found.", err=True)
        click.echo(f"Available SRAMs: {', '.join(sorted(srams.keys()))}", err=True)
        raise SystemExit(1)

    # Validate slot name
    if slot not in slots:
        click.echo(f"Error: Slot '{slot}' not found.", err=True)
        click.echo(f"Available slots: {', '.join(sorted(slots.keys()))}", err=True)
        raise SystemExit(1)

    sram_spec = srams[sram]
    slot_spec = slots[slot]

    # Calculate fit
    result = calculate_fit(slot_spec, sram_spec, halo_um=halo)

    # Display results
    click.echo(f"SRAM Fit Calculation")
    click.echo("=" * 60)
    click.echo(f"Slot: {slot}")
    click.echo(f"SRAM: {sram}")
    click.echo(f"Halo: {halo} um")
    click.echo()
    click.echo("Results:")
    click.echo("-" * 60)
    click.echo(f"  Grid: {result.cols} columns x {result.rows} rows")
    click.echo(f"  Total SRAMs: {result.count}")
    click.echo()
    click.echo(f"  Total Words: {result.total_words:,}")
    click.echo(f"  Total Bits: {result.total_bits:,}")
    click.echo(f"  Total Bytes: {result.total_bits // 8:,}")
    click.echo()
    click.echo(f"  Address Bits: {result.address_bits}")
    click.echo(f"  Core Utilization: {result.utilization * 100:.1f}%")


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
