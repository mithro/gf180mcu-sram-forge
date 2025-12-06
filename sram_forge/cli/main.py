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
            librelane_dir = output_path / "librelane"
            librelane_dir.mkdir(exist_ok=True)

            # Config
            ll_config = librelane_engine.generate_config(chip_config, sram_spec, slot_spec, fit_result)
            (librelane_dir / "config.yaml").write_text(ll_config)
            generated.append("librelane/config.yaml")

            # PDN
            pdn_cfg = librelane_engine.generate_pdn(chip_config, sram_spec, slot_spec, fit_result)
            (librelane_dir / "pdn_cfg.tcl").write_text(pdn_cfg)
            generated.append("librelane/pdn_cfg.tcl")

            # SDC
            sdc = librelane_engine.generate_sdc(chip_config, sram_spec, fit_result)
            (librelane_dir / f"{chip_config.chip.name}_top.sdc").write_text(sdc)
            generated.append(f"librelane/{chip_config.chip.name}_top.sdc")

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
@click.option("--no-git", is_flag=True, help="Skip git initialization")
def package(config: str, name: str, output: str, no_git: bool):
    """Create a complete buildable project from template."""
    import math

    data_dir = get_bundled_data_dir()
    output_path = Path(output)

    try:
        # Load chip config
        chip_config = load_chip_config(Path(config))
        click.echo(f"Creating project '{name}' for: {chip_config.chip.name}")

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
        package_dir = package_engine.create_package(
            chip_config,
            sram_spec,
            slot_spec,
            fit_result,
            name,
            output_path,
            init_git=not no_git,
        )

        click.echo(f"Created project: {package_dir}")
        click.echo()
        click.echo("Contents:")
        click.echo(f"  src/           - Verilog sources")
        click.echo(f"  librelane/     - Physical design config")
        click.echo(f"  cocotb/        - Verification testbench")
        click.echo(f"  docs/          - Documentation")
        click.echo(f"  manifest.yaml  - Package manifest")
        click.echo()
        click.echo("To build:")
        click.echo(f"  cd {package_dir}")
        click.echo("  nix-shell")
        click.echo("  make librelane")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@main.command("create-repo")
@click.argument("config", type=click.Path(exists=True))
@click.option("--owner", default="mithro", help="GitHub owner/organization")
@click.option("--template", default="wafer-space/gf180mcu-project-template", help="Template repository")
@click.option("--clone-dir", default=None, help="Local directory to clone into (default: current dir)")
@click.option("--public/--private", default=True, help="Repository visibility")
@click.option("--push/--no-push", default=True, help="Push generated files after creation")
def create_repo(config: str, owner: str, template: str, clone_dir: str | None, public: bool, push: bool):
    """Create a GitHub repository from template and populate with generated files.

    This command:
    1. Creates a new GitHub repo from the gf180mcu-project-template
    2. Clones it locally
    3. Generates SRAM chip files using sram-forge
    4. Commits and pushes the generated files
    """
    import math
    import subprocess
    import shutil

    data_dir = get_bundled_data_dir()

    try:
        # Load chip config
        chip_config = load_chip_config(Path(config))
        click.echo(f"Creating repository for: {chip_config.chip.name}")

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

        # Derive repo name from chip name (replace underscores with dashes)
        repo_name = chip_config.chip.name.replace("_", "-")
        full_repo = f"{owner}/{repo_name}"

        # Check if repo already exists
        result = subprocess.run(
            ["gh", "repo", "view", full_repo],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            click.echo(f"Repository {full_repo} already exists.", err=True)
            raise SystemExit(1)

        click.echo(f"Creating repository: {full_repo}")
        click.echo(f"  Template: {template}")
        click.echo(f"  Visibility: {'public' if public else 'private'}")

        # Create repo from template
        visibility = "--public" if public else "--private"
        result = subprocess.run(
            ["gh", "repo", "create", full_repo, "--template", template, visibility, "--clone=false"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Error creating repository: {result.stderr}", err=True)
            raise SystemExit(1)

        click.echo(f"Created repository: https://github.com/{full_repo}")

        # Determine clone directory
        if clone_dir:
            clone_path = Path(clone_dir) / repo_name
        else:
            clone_path = Path.cwd() / repo_name

        # Clone the repository
        click.echo(f"Cloning to: {clone_path}")
        result = subprocess.run(
            ["gh", "repo", "clone", full_repo, str(clone_path)],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Error cloning repository: {result.stderr}", err=True)
            raise SystemExit(1)

        # Generate files into the cloned repo
        click.echo("Generating SRAM files...")

        # Clean up template placeholder files
        for placeholder in ["src/.gitkeep", "librelane/.gitkeep", "cocotb/.gitkeep"]:
            placeholder_path = clone_path / placeholder
            if placeholder_path.exists():
                placeholder_path.unlink()

        # Generate Verilog
        verilog_engine = VerilogEngine()
        verilog_dir = clone_path / "src"
        verilog_dir.mkdir(exist_ok=True)

        sram_array = verilog_engine.generate_sram_array(chip_config, sram_spec, fit_result)
        (verilog_dir / f"{chip_config.chip.name}_sram_array.sv").write_text(sram_array)

        chip_core = verilog_engine.generate_chip_core(chip_config, sram_spec, fit_result)
        (verilog_dir / f"{chip_config.chip.name}_core.sv").write_text(chip_core)

        chip_top = verilog_engine.generate_chip_top(chip_config, sram_spec, fit_result)
        (verilog_dir / f"{chip_config.chip.name}_top.sv").write_text(chip_top)

        # Generate LibreLane config
        librelane_engine = LibreLaneEngine()
        librelane_dir = clone_path / "librelane"
        librelane_dir.mkdir(exist_ok=True)

        ll_config = librelane_engine.generate_config(chip_config, sram_spec, slot_spec, fit_result)
        (librelane_dir / "config.yaml").write_text(ll_config)

        pdn_cfg = librelane_engine.generate_pdn(chip_config, sram_spec, slot_spec, fit_result)
        (librelane_dir / "pdn_cfg.tcl").write_text(pdn_cfg)

        sdc = librelane_engine.generate_sdc(chip_config, sram_spec, fit_result)
        (librelane_dir / f"{chip_config.chip.name}_top.sdc").write_text(sdc)

        # Generate testbench
        testbench_engine = TestbenchEngine()
        tb_dir = clone_path / "cocotb"
        tb_dir.mkdir(exist_ok=True)

        test_py = testbench_engine.generate_cocotb_test(chip_config, sram_spec, fit_result)
        (tb_dir / "test_sram.py").write_text(test_py)

        makefile = testbench_engine.generate_makefile(chip_config)
        (tb_dir / "Makefile").write_text(makefile)

        model_py = testbench_engine.generate_behavioral_model(chip_config, sram_spec, fit_result)
        (tb_dir / "sram_model.py").write_text(model_py)

        # Generate docs
        docs_engine = DocumentationEngine()
        docs_dir = clone_path / "docs"
        docs_dir.mkdir(exist_ok=True)

        readme = docs_engine.generate_readme(chip_config, sram_spec, fit_result)
        (docs_dir / "README.md").write_text(readme)

        datasheet = docs_engine.generate_datasheet(chip_config, sram_spec, fit_result)
        (docs_dir / "datasheet.md").write_text(datasheet)

        memory_map = docs_engine.generate_memory_map(chip_config, sram_spec, fit_result)
        (docs_dir / "memory_map.md").write_text(memory_map)

        # Store the config file
        config_path = Path(config)
        shutil.copy(config_path, clone_path / "chip_config.yaml")

        click.echo("Generated files:")
        for subdir in ["src", "librelane", "cocotb", "docs"]:
            subdir_path = clone_path / subdir
            if subdir_path.exists():
                for f in subdir_path.iterdir():
                    if f.is_file():
                        click.echo(f"  {subdir}/{f.name}")

        if push:
            click.echo("Committing and pushing generated files...")

            # Git add all
            subprocess.run(["git", "add", "-A"], cwd=clone_path, check=True)

            # Git commit
            commit_msg = f"""feat: add generated SRAM chip files

Chip: {chip_config.chip.name}
Slot: {chip_config.slot}
SRAMs: {fit_result.count} x {chip_config.memory.macro}
Capacity: {fit_result.total_bits // 8:,} bytes

Generated by sram-forge"""

            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=clone_path,
                check=True
            )

            # Git push
            subprocess.run(["git", "push"], cwd=clone_path, check=True)

            click.echo(f"Pushed to: https://github.com/{full_repo}")

        click.echo()
        click.echo("Repository created successfully!")
        click.echo(f"  URL: https://github.com/{full_repo}")
        click.echo(f"  Local: {clone_path}")
        click.echo()
        click.echo("To build:")
        click.echo(f"  cd {clone_path}")
        click.echo("  nix-shell")
        click.echo("  make librelane")

    except subprocess.CalledProcessError as e:
        click.echo(f"Error running command: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
