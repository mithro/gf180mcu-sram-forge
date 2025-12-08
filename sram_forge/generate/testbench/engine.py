"""Testbench generator for sram-forge."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sram_forge.models import ChipConfig, SramSpec
from sram_forge.calc.fit import FitResult


def get_templates_dir() -> Path:
    """Get path to testbench templates directory."""
    return Path(__file__).parent / "templates"


class TestbenchEngine:
    """Jinja2-based cocotb testbench generator."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the testbench engine.

        Args:
            templates_dir: Custom templates directory. Uses bundled templates if None.
        """
        if templates_dir is None:
            templates_dir = get_templates_dir()

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(disabled_extensions=["py", "j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template(self, name: str):
        """Get a template by name.

        Args:
            name: Template filename.

        Returns:
            Jinja2 Template object.
        """
        return self.env.get_template(name)

    def generate_cocotb_test(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate cocotb testbench.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated Python test file.
        """
        template = self.get_template("test_sram.py.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_makefile(
        self,
        chip_config: ChipConfig,
    ) -> str:
        """Generate cocotb Makefile.

        Args:
            chip_config: Chip configuration.

        Returns:
            Generated Makefile content.
        """
        template = self.get_template("Makefile.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
        )

    def generate_behavioral_model(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate Python behavioral model for verification.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated Python model file.
        """
        template = self.get_template("sram_model.py.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_chip_top_tb(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate chip-level cocotb testbench runner.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated Python testbench file.
        """
        template = self.get_template("chip_top_tb.py.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            slot=chip_config.slot,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_sram_utils(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate shared SRAM testbench utilities.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated Python utilities file.
        """
        template = self.get_template("sram_utils.py.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_test_control_signals(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate control signal protocol tests.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated Python test file.
        """
        template = self.get_template("test_control_signals.py.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_test_sram_selection(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate SRAM selection and isolation tests.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated Python test file.
        """
        template = self.get_template("test_sram_selection.py.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )
