"""Package generator for sram-forge."""

from datetime import datetime
from pathlib import Path
import tarfile
import tempfile
import shutil

from jinja2 import Environment, BaseLoader

from sram_forge.models import ChipConfig, SramSpec, SlotSpec
from sram_forge.calc.fit import FitResult
from sram_forge.generate.verilog.engine import VerilogEngine
from sram_forge.generate.librelane.engine import LibreLaneEngine
from sram_forge.generate.testbench.engine import TestbenchEngine
from sram_forge.generate.docs.engine import DocumentationEngine


MANIFEST_TEMPLATE = """\
# sram-forge Package Manifest
# Generated: {{ timestamp }}

package:
  name: {{ package_name }}
  version: "1.0.0"
  generator: sram-forge

chip:
  name: {{ chip.name }}
  description: {{ chip.description | default('') }}

memory:
  macro: {{ config.memory.macro }}
  count: {{ sram_count }}
  total_words: {{ total_words }}
  total_bits: {{ total_bits }}
  address_bits: {{ addr_bits }}
  data_width: {{ data_width }}

slot: {{ config.slot }}
interface: {{ config.interface.scheme }}

files:
  verilog:
    - src/{{ chip.name }}_sram_array.sv
    - src/{{ chip.name }}_core.sv
    - src/{{ chip.name }}_top.sv
  librelane:
    - config.yaml
    - pdn_cfg.tcl
    - {{ chip.name }}_top.sdc
  testbench:
    - cocotb/test_sram.py
    - cocotb/Makefile
    - cocotb/sram_model.py
  docs:
    - docs/README.md
    - docs/datasheet.md
    - docs/memory_map.md
"""


class PackageEngine:
    """Asset package generator."""

    def __init__(self):
        """Initialize the package engine."""
        self.verilog_engine = VerilogEngine()
        self.librelane_engine = LibreLaneEngine()
        self.testbench_engine = TestbenchEngine()
        self.docs_engine = DocumentationEngine()

        self.env = Environment(loader=BaseLoader())
        self.manifest_template = self.env.from_string(MANIFEST_TEMPLATE)

    def generate_manifest(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
        package_name: str,
    ) -> str:
        """Generate package manifest.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.
            package_name: Name for the package.

        Returns:
            Generated manifest YAML.
        """
        return self.manifest_template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            package_name=package_name,
            timestamp=datetime.now().isoformat(),
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            total_bits=fit_result.total_bits,
        )

    def create_package(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        slot_spec: SlotSpec,
        fit_result: FitResult,
        package_name: str,
        output_dir: Path,
    ) -> Path:
        """Create a complete asset package.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            slot_spec: Slot specification.
            fit_result: Fit calculation result.
            package_name: Name for the package.
            output_dir: Directory to write package to.

        Returns:
            Path to created archive.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create staging directory
        with tempfile.TemporaryDirectory() as tmpdir:
            staging = Path(tmpdir) / package_name
            staging.mkdir()

            # Generate all files
            self._generate_verilog(staging, chip_config, sram_spec, fit_result)
            self._generate_librelane(staging, chip_config, sram_spec, slot_spec, fit_result)
            self._generate_testbench(staging, chip_config, sram_spec, fit_result)
            self._generate_docs(staging, chip_config, sram_spec, fit_result)

            # Generate manifest
            manifest = self.generate_manifest(chip_config, sram_spec, fit_result, package_name)
            (staging / "manifest.yaml").write_text(manifest)

            # Create archive
            archive_name = f"{package_name}.tar.gz"
            archive_path = output_dir / archive_name

            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(staging, arcname=package_name)

            return archive_path

    def _generate_verilog(
        self,
        staging: Path,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> None:
        """Generate Verilog files."""
        src_dir = staging / "src"
        src_dir.mkdir(exist_ok=True)

        sram_array = self.verilog_engine.generate_sram_array(chip_config, sram_spec, fit_result)
        (src_dir / f"{chip_config.chip.name}_sram_array.sv").write_text(sram_array)

        chip_core = self.verilog_engine.generate_chip_core(chip_config, sram_spec, fit_result)
        (src_dir / f"{chip_config.chip.name}_core.sv").write_text(chip_core)

        chip_top = self.verilog_engine.generate_chip_top(chip_config, sram_spec, fit_result)
        (src_dir / f"{chip_config.chip.name}_top.sv").write_text(chip_top)

    def _generate_librelane(
        self,
        staging: Path,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        slot_spec: SlotSpec,
        fit_result: FitResult,
    ) -> None:
        """Generate LibreLane files."""
        ll_config = self.librelane_engine.generate_config(
            chip_config, sram_spec, slot_spec, fit_result
        )
        (staging / "config.yaml").write_text(ll_config)

        pdn_cfg = self.librelane_engine.generate_pdn(chip_config, sram_spec, fit_result)
        (staging / "pdn_cfg.tcl").write_text(pdn_cfg)

        sdc = self.librelane_engine.generate_sdc(chip_config, sram_spec, fit_result)
        (staging / f"{chip_config.chip.name}_top.sdc").write_text(sdc)

    def _generate_testbench(
        self,
        staging: Path,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> None:
        """Generate testbench files."""
        tb_dir = staging / "cocotb"
        tb_dir.mkdir(exist_ok=True)

        test_py = self.testbench_engine.generate_cocotb_test(chip_config, sram_spec, fit_result)
        (tb_dir / "test_sram.py").write_text(test_py)

        makefile = self.testbench_engine.generate_makefile(chip_config)
        (tb_dir / "Makefile").write_text(makefile)

        model_py = self.testbench_engine.generate_behavioral_model(chip_config, sram_spec, fit_result)
        (tb_dir / "sram_model.py").write_text(model_py)

    def _generate_docs(
        self,
        staging: Path,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> None:
        """Generate documentation files."""
        docs_dir = staging / "docs"
        docs_dir.mkdir(exist_ok=True)

        readme = self.docs_engine.generate_readme(chip_config, sram_spec, fit_result)
        (docs_dir / "README.md").write_text(readme)

        datasheet = self.docs_engine.generate_datasheet(chip_config, sram_spec, fit_result)
        (docs_dir / "datasheet.md").write_text(datasheet)

        memory_map = self.docs_engine.generate_memory_map(chip_config, sram_spec, fit_result)
        (docs_dir / "memory_map.md").write_text(memory_map)
