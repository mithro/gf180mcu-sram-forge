"""Main CLI entry point for sram-forge."""

import json
from pathlib import Path

import click

try:
    from sram_forge import __version__
except ImportError:
    # Fallback for when running directly
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from __init__ import __version__

from sram_forge.db.loader import load_srams, load_slots, load_chip_config, load_downstream_repos
from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.verilog.engine import VerilogEngine
from sram_forge.generate.librelane.engine import LibreLaneEngine
from sram_forge.generate.testbench.engine import TestbenchEngine
from sram_forge.generate.docs.engine import DocumentationEngine
from sram_forge.generate.package.engine import PackageEngine
from sram_forge.status.fetcher import fetch_all_status
from sram_forge.status.reporter import format_terminal, format_markdown, format_json, format_html


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
    click.echo("SRAM Fit Calculation")
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

        click.echo("Valid configuration:")
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

            # Root Makefile (with correct DEFAULT_SLOT for this chip)
            makefile_content = librelane_engine.generate_makefile(chip_config)
            (output_path / "Makefile").write_text(makefile_content)
            generated.append("Makefile")

        if only is None or only == "testbench":
            testbench_engine = TestbenchEngine()
            tb_dir = output_path / "cocotb"
            tb_dir.mkdir(exist_ok=True)

            # Chip-level testbench runner (main entry point)
            chip_tb = testbench_engine.generate_chip_top_tb(
                chip_config, sram_spec, fit_result
            )
            (tb_dir / "chip_top_tb.py").write_text(chip_tb)
            generated.append("cocotb/chip_top_tb.py")

            # Shared utilities
            sram_utils = testbench_engine.generate_sram_utils(
                chip_config, sram_spec, fit_result
            )
            (tb_dir / "sram_utils.py").write_text(sram_utils)
            generated.append("cocotb/sram_utils.py")

            # Behavioral model
            model_py = testbench_engine.generate_behavioral_model(
                chip_config, sram_spec, fit_result
            )
            (tb_dir / "sram_model.py").write_text(model_py)
            generated.append("cocotb/sram_model.py")

            # Control signal tests
            test_control = testbench_engine.generate_test_control_signals(
                chip_config, sram_spec, fit_result
            )
            (tb_dir / "test_control_signals.py").write_text(test_control)
            generated.append("cocotb/test_control_signals.py")

            # SRAM selection tests
            test_selection = testbench_engine.generate_test_sram_selection(
                chip_config, sram_spec, fit_result
            )
            (tb_dir / "test_sram_selection.py").write_text(test_selection)
            generated.append("cocotb/test_sram_selection.py")

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
        click.echo("  src/           - Verilog sources")
        click.echo("  librelane/     - Physical design config")
        click.echo("  cocotb/        - Verification testbench")
        click.echo("  docs/          - Documentation")
        click.echo("  manifest.yaml  - Package manifest")
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

        # Generate root Makefile with correct DEFAULT_SLOT for this chip
        makefile_content = librelane_engine.generate_makefile(chip_config)
        (clone_path / "Makefile").write_text(makefile_content)

        # Generate testbench
        testbench_engine = TestbenchEngine()
        tb_dir = clone_path / "cocotb"
        tb_dir.mkdir(exist_ok=True)

        # Chip-level testbench runner (main entry point)
        chip_tb = testbench_engine.generate_chip_top_tb(
            chip_config, sram_spec, fit_result
        )
        (tb_dir / "chip_top_tb.py").write_text(chip_tb)

        # Shared utilities
        sram_utils = testbench_engine.generate_sram_utils(
            chip_config, sram_spec, fit_result
        )
        (tb_dir / "sram_utils.py").write_text(sram_utils)

        # Behavioral model
        model_py = testbench_engine.generate_behavioral_model(
            chip_config, sram_spec, fit_result
        )
        (tb_dir / "sram_model.py").write_text(model_py)

        # Control signal tests
        test_control = testbench_engine.generate_test_control_signals(
            chip_config, sram_spec, fit_result
        )
        (tb_dir / "test_control_signals.py").write_text(test_control)

        # SRAM selection tests
        test_selection = testbench_engine.generate_test_sram_selection(
            chip_config, sram_spec, fit_result
        )
        (tb_dir / "test_sram_selection.py").write_text(test_selection)

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


@main.command("setup-downstream")
@click.argument("downstream_repo")
@click.option("--forge-repo", default="mithro/gf180mcu-sram-forge", help="The sram-forge repo to add the secret to")
@click.option("--key-name", default=None, help="Name for the deploy key (default: derived from repo name)")
@click.option("--secret-name", default=None, help="Name for the secret (default: derived from repo name)")
def setup_downstream(downstream_repo: str, forge_repo: str, key_name: str | None, secret_name: str | None):
    """Set up deploy key access to a downstream chip repository.

    This command:
    1. Generates an SSH key pair
    2. Adds the public key as a deploy key (with write access) to the downstream repo
    3. Adds the private key as a secret to the sram-forge repo

    Example:
        sram-forge setup-downstream mithro/gf180mcu-ic-0p5x0p5-sram-u8b3k
    """
    import subprocess
    import tempfile
    import re

    # Validate repo format
    if "/" not in downstream_repo:
        click.echo(f"Error: Repository must be in 'owner/repo' format, got: {downstream_repo}", err=True)
        raise SystemExit(1)

    # Derive names from repo if not specified
    repo_short = downstream_repo.split("/")[1]
    # Convert repo name to safe identifier (e.g., gf180mcu-ic-0p5x0p5-sram-u8b3k -> 0P5X0P5)
    # Extract the slot part from the repo name
    slot_match = re.search(r'-(0p5x0p5|0p5x1|1x0p5|1x1)-', repo_short)
    if slot_match:
        slot_id = slot_match.group(1).upper().replace("P", "P")
    else:
        # Fallback to sanitized repo name
        slot_id = repo_short.replace("-", "_").upper()

    if key_name is None:
        key_name = f"sram-forge-deploy-{repo_short}"

    if secret_name is None:
        # Create secret name like DEPLOY_KEY_0P5X0P5
        secret_name = f"DEPLOY_KEY_{slot_id.replace('.', 'P')}"

    click.echo(f"Setting up deploy key for downstream repo: {downstream_repo}")
    click.echo(f"  Deploy key name: {key_name}")
    click.echo(f"  Secret name: {secret_name}")
    click.echo(f"  Forge repo: {forge_repo}")
    click.echo()

    # Check if repos exist and we have access
    click.echo("Checking repository access...")

    result = subprocess.run(
        ["gh", "repo", "view", downstream_repo, "--json", "name"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        click.echo(f"Error: Cannot access downstream repo {downstream_repo}", err=True)
        click.echo(f"  {result.stderr}", err=True)
        raise SystemExit(1)

    result = subprocess.run(
        ["gh", "repo", "view", forge_repo, "--json", "name"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        click.echo(f"Error: Cannot access forge repo {forge_repo}", err=True)
        click.echo(f"  {result.stderr}", err=True)
        raise SystemExit(1)

    click.echo("  Both repositories accessible.")

    # Generate SSH key pair in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        key_path = Path(tmpdir) / "deploy_key"
        pub_key_path = Path(tmpdir) / "deploy_key.pub"

        click.echo("Generating SSH key pair...")
        result = subprocess.run(
            [
                "ssh-keygen",
                "-t", "ed25519",
                "-f", str(key_path),
                "-N", "",  # No passphrase
                "-C", f"sram-forge deploy key for {downstream_repo}"
            ],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Error generating SSH key: {result.stderr}", err=True)
            raise SystemExit(1)

        private_key = key_path.read_text()
        _public_key = pub_key_path.read_text().strip()  # Read but not used directly

        click.echo("  Generated ed25519 key pair")

        # Check if deploy key already exists and remove it
        click.echo("Checking for existing deploy key...")
        result = subprocess.run(
            ["gh", "repo", "deploy-key", "list", "--repo", downstream_repo],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            # Parse output to find existing key with same name
            for line in result.stdout.strip().split("\n"):
                if line and key_name in line:
                    # Extract key ID (first column)
                    key_id = line.split()[0]
                    click.echo(f"  Removing existing deploy key: {key_id}")
                    subprocess.run(
                        ["gh", "repo", "deploy-key", "delete", key_id, "--repo", downstream_repo, "--yes"],
                        capture_output=True
                    )

        # Add public key as deploy key to downstream repo
        click.echo(f"Adding deploy key to {downstream_repo}...")
        result = subprocess.run(
            [
                "gh", "repo", "deploy-key", "add",
                str(pub_key_path),
                "--repo", downstream_repo,
                "--title", key_name,
                "--allow-write"
            ],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Error adding deploy key: {result.stderr}", err=True)
            raise SystemExit(1)

        click.echo("  Added deploy key with write access")

        # Add private key as secret to forge repo
        click.echo(f"Adding secret to {forge_repo}...")

        # Use gh secret set with stdin
        result = subprocess.run(
            ["gh", "secret", "set", secret_name, "--repo", forge_repo],
            input=private_key,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            click.echo(f"Error adding secret: {result.stderr}", err=True)
            raise SystemExit(1)

        click.echo(f"  Added secret: {secret_name}")

    click.echo()
    click.echo("Setup complete!")
    click.echo()
    click.echo("To use in GitHub Actions workflow, add:")
    click.echo()
    click.echo(f"    - name: Configure SSH for {downstream_repo}")
    click.echo("      env:")
    click.echo(f"        DEPLOY_KEY: ${{{{ secrets.{secret_name} }}}}")
    click.echo("      run: |")
    click.echo("        mkdir -p ~/.ssh")
    click.echo("        echo \"$DEPLOY_KEY\" > ~/.ssh/deploy_key")
    click.echo("        chmod 600 ~/.ssh/deploy_key")
    click.echo("        ssh-keyscan github.com >> ~/.ssh/known_hosts")
    click.echo("        git config --global core.sshCommand 'ssh -i ~/.ssh/deploy_key'")
    click.echo()
    click.echo("    - name: Clone downstream repo")
    click.echo(f"      run: git clone git@github.com:{downstream_repo}.git downstream")


@main.group()
def downstream():
    """Manage downstream IC repositories."""
    pass


@downstream.command("list")
def downstream_list():
    """List all downstream IC repositories."""
    data_dir = get_bundled_data_dir()
    repos = load_downstream_repos(data_dir / "downstream_repos.yaml")

    click.echo("Downstream IC Repositories:")
    click.echo("-" * 60)
    for repo in repos:
        click.echo(f"  {repo.sram:8} {repo.slot:8} {repo.full_name}")


@downstream.command("matrix")
def downstream_matrix():
    """Output repository list as JSON matrix for GitHub Actions."""
    data_dir = get_bundled_data_dir()
    repos = load_downstream_repos(data_dir / "downstream_repos.yaml")

    matrix = {
        "include": [
            {
                "sram": r.sram,
                "slot": r.slot,
                "config": r.config,
                "repo": r.full_name,
                "secret": r.deploy_key_secret,
            }
            for r in repos
        ]
    }
    click.echo(json.dumps(matrix))


@downstream.command("status")
@click.option("--format", "fmt", type=click.Choice(["terminal", "md", "json", "html"]), default="terminal")
@click.option("--output", "-o", type=click.Path(), help="Output file (required for HTML)")
def downstream_status(fmt: str, output: str | None):
    """Show GitHub Actions status for all downstream repos."""
    data_dir = get_bundled_data_dir()
    repos = load_downstream_repos(data_dir / "downstream_repos.yaml")

    click.echo("Fetching status...", err=True)
    report = fetch_all_status(repos)

    if fmt == "terminal":
        click.echo(format_terminal(report))
    elif fmt == "md":
        click.echo(format_markdown(report))
    elif fmt == "json":
        click.echo(format_json(report))
    elif fmt == "html":
        if not output:
            click.echo("Error: --output required for HTML format", err=True)
            raise SystemExit(1)
        Path(output).write_text(format_html(report))
        click.echo(f"Wrote HTML to {output}", err=True)


if __name__ == "__main__":
    main()
