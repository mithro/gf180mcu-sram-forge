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

from sram_forge.db.loader import load_srams, load_slots, load_chip_config
from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.verilog.engine import VerilogEngine
from sram_forge.generate.librelane.engine import LibreLaneEngine
from sram_forge.generate.testbench.engine import TestbenchEngine
from sram_forge.generate.docs.engine import DocumentationEngine
from sram_forge.generate.package.engine import PackageEngine


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
    data_dir = get_bundled_data_dir()

    try:
        # Load and validate chip config
        chip_config = load_chip_config(Path(config))
        click.echo(f"Loaded chip config: {chip_config.chip.name}")

        # Load databases
        srams = load_srams(data_dir / "srams.yaml")
        slots = load_slots(data_dir / "slots.yaml")

        # Validate references
        if chip_config.memory.macro not in srams:
            click.echo(f"Error: SRAM '{chip_config.memory.macro}' not found.", err=True)
            raise SystemExit(1)

        if chip_config.slot not in slots:
            click.echo(f"Error: Slot '{chip_config.slot}' not found.", err=True)
            raise SystemExit(1)

        sram_spec = srams[chip_config.memory.macro]
        slot_spec = slots[chip_config.slot]

        # Calculate fit
        fit_result = calculate_fit(slot_spec, sram_spec)

        # Determine actual count
        if chip_config.memory.count == "auto":
            count = fit_result.count
        else:
            count = chip_config.memory.count
            if count > fit_result.count:
                click.echo(f"Warning: Requested {count} SRAMs but only {fit_result.count} fit.", err=True)

        click.echo(f"Valid configuration:")
        click.echo(f"  Slot: {chip_config.slot}")
        click.echo(f"  SRAM: {chip_config.memory.macro}")
        click.echo(f"  Count: {count}")
        click.echo(f"  Interface: {chip_config.interface.scheme}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--only", type=click.Choice(["verilog", "librelane", "testbench", "docs"]), help="Generate only specific output type")
def gen(config: str, output: str, only: str | None):
    """Generate outputs from chip configuration."""
    data_dir = get_bundled_data_dir()
    output_path = Path(output)

    try:
        # Load chip config
        chip_config = load_chip_config(Path(config))
        click.echo(f"Generating outputs for: {chip_config.chip.name}")

        # Load databases
        srams = load_srams(data_dir / "srams.yaml")
        slots = load_slots(data_dir / "slots.yaml")

        # Validate references
        if chip_config.memory.macro not in srams:
            click.echo(f"Error: SRAM '{chip_config.memory.macro}' not found.", err=True)
            raise SystemExit(1)

        if chip_config.slot not in slots:
            click.echo(f"Error: Slot '{chip_config.slot}' not found.", err=True)
            raise SystemExit(1)

        sram_spec = srams[chip_config.memory.macro]
        slot_spec = slots[chip_config.slot]

        # Calculate fit
        fit_result = calculate_fit(slot_spec, sram_spec)

        # Override count if specified
        if chip_config.memory.count != "auto":
            fit_result.count = chip_config.memory.count
            fit_result.total_words = fit_result.count * sram_spec.size
            fit_result.total_bits = fit_result.total_words * sram_spec.width
            import math
            fit_result.address_bits = math.ceil(math.log2(fit_result.total_words))

        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate outputs
        generated = []

        if only is None or only == "verilog":
            verilog_engine = VerilogEngine()
            verilog_dir = output_path / "src"
            verilog_dir.mkdir(exist_ok=True)

            # SRAM array
            sram_array = verilog_engine.generate_sram_array(chip_config, sram_spec, fit_result)
            (verilog_dir / f"{chip_config.chip.name}_sram_array.sv").write_text(sram_array)
            generated.append(f"src/{chip_config.chip.name}_sram_array.sv")

            # Chip core
            chip_core = verilog_engine.generate_chip_core(chip_config, sram_spec, fit_result)
            (verilog_dir / f"{chip_config.chip.name}_core.sv").write_text(chip_core)
            generated.append(f"src/{chip_config.chip.name}_core.sv")

            # Chip top
            chip_top = verilog_engine.generate_chip_top(chip_config, sram_spec, fit_result)
            (verilog_dir / f"{chip_config.chip.name}_top.sv").write_text(chip_top)
            generated.append(f"src/{chip_config.chip.name}_top.sv")

        if only is None or only == "librelane":
            librelane_engine = LibreLaneEngine()

            # Config
            ll_config = librelane_engine.generate_config(chip_config, sram_spec, slot_spec, fit_result)
            (output_path / "config.yaml").write_text(ll_config)
            generated.append("config.yaml")

            # PDN
            pdn_cfg = librelane_engine.generate_pdn(chip_config, sram_spec, fit_result)
            (output_path / "pdn_cfg.tcl").write_text(pdn_cfg)
            generated.append("pdn_cfg.tcl")

            # SDC
            sdc = librelane_engine.generate_sdc(chip_config, sram_spec, fit_result)
            (output_path / f"{chip_config.chip.name}_top.sdc").write_text(sdc)
            generated.append(f"{chip_config.chip.name}_top.sdc")

        if only is None or only == "testbench":
            testbench_engine = TestbenchEngine()
            tb_dir = output_path / "cocotb"
            tb_dir.mkdir(exist_ok=True)

            # cocotb test
            test_py = testbench_engine.generate_cocotb_test(chip_config, sram_spec, fit_result)
            (tb_dir / "test_sram.py").write_text(test_py)
            generated.append("cocotb/test_sram.py")

            # Makefile
            makefile = testbench_engine.generate_makefile(chip_config)
            (tb_dir / "Makefile").write_text(makefile)
            generated.append("cocotb/Makefile")

            # Behavioral model
            model_py = testbench_engine.generate_behavioral_model(chip_config, sram_spec, fit_result)
            (tb_dir / "sram_model.py").write_text(model_py)
            generated.append("cocotb/sram_model.py")

        if only is None or only == "docs":
            docs_engine = DocumentationEngine()
            docs_dir = output_path / "docs"
            docs_dir.mkdir(exist_ok=True)

            # README
            readme = docs_engine.generate_readme(chip_config, sram_spec, fit_result)
            (docs_dir / "README.md").write_text(readme)
            generated.append("docs/README.md")

            # Datasheet
            datasheet = docs_engine.generate_datasheet(chip_config, sram_spec, fit_result)
            (docs_dir / "datasheet.md").write_text(datasheet)
            generated.append("docs/datasheet.md")

            # Memory map
            memory_map = docs_engine.generate_memory_map(chip_config, sram_spec, fit_result)
            (docs_dir / "memory_map.md").write_text(memory_map)
            generated.append("docs/memory_map.md")

        click.echo(f"Generated {len(generated)} files to {output_path}:")
        for f in generated:
            click.echo(f"  {f}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--name", required=True, help="Package name")
@click.option("--output", "-o", default=".", help="Output directory")
def package(config: str, name: str, output: str):
    """Create a complete asset package."""
    import math

    data_dir = get_bundled_data_dir()
    output_path = Path(output)

    try:
        # Load chip config
        chip_config = load_chip_config(Path(config))
        click.echo(f"Creating package '{name}' for: {chip_config.chip.name}")

        # Load databases
        srams = load_srams(data_dir / "srams.yaml")
        slots = load_slots(data_dir / "slots.yaml")

        # Validate references
        if chip_config.memory.macro not in srams:
            click.echo(f"Error: SRAM '{chip_config.memory.macro}' not found.", err=True)
            raise SystemExit(1)

        if chip_config.slot not in slots:
            click.echo(f"Error: Slot '{chip_config.slot}' not found.", err=True)
            raise SystemExit(1)

        sram_spec = srams[chip_config.memory.macro]
        slot_spec = slots[chip_config.slot]

        # Calculate fit
        fit_result = calculate_fit(slot_spec, sram_spec)

        # Override count if specified
        if chip_config.memory.count != "auto":
            fit_result.count = chip_config.memory.count
            fit_result.total_words = fit_result.count * sram_spec.size
            fit_result.total_bits = fit_result.total_words * sram_spec.width
            fit_result.address_bits = math.ceil(math.log2(fit_result.total_words))

        # Create package
        package_engine = PackageEngine()
        archive_path = package_engine.create_package(
            chip_config,
            sram_spec,
            slot_spec,
            fit_result,
            name,
            output_path,
        )

        click.echo(f"Created package: {archive_path}")
        click.echo(f"Contents:")
        click.echo(f"  - Verilog sources (src/)")
        click.echo(f"  - LibreLane config (config.yaml, pdn_cfg.tcl, *.sdc)")
        click.echo(f"  - Testbench (cocotb/)")
        click.echo(f"  - Documentation (docs/)")
        click.echo(f"  - Manifest (manifest.yaml)")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
