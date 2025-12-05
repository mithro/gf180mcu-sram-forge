"""Verilog template engine for sram-forge."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sram_forge.models import ChipConfig, SramSpec
from sram_forge.calc.fit import FitResult


def get_templates_dir() -> Path:
    """Get path to Verilog templates directory."""
    return Path(__file__).parent / "templates"


class VerilogEngine:
    """Jinja2-based Verilog code generator."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the Verilog engine.

        Args:
            templates_dir: Custom templates directory. Uses bundled templates if None.
        """
        if templates_dir is None:
            templates_dir = get_templates_dir()

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(disabled_extensions=["sv", "v", "j2"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self.env.filters["bits_for"] = self._bits_for
        self.env.filters["hex_width"] = self._hex_width

    @staticmethod
    def _bits_for(value: int) -> int:
        """Calculate bits needed to represent a value."""
        if value <= 1:
            return 1
        import math
        return math.ceil(math.log2(value))

    @staticmethod
    def _hex_width(bits: int) -> int:
        """Calculate hex digits needed for given bit width."""
        return (bits + 3) // 4

    def get_template(self, name: str):
        """Get a template by name.

        Args:
            name: Template filename.

        Returns:
            Jinja2 Template object.
        """
        return self.env.get_template(name)

    def generate_sram_array(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate SRAM array module.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated SystemVerilog code.
        """
        template = self.get_template("sram_array.sv.j2")

        # Get port information from SRAM spec
        port = sram_spec.ports[0]  # Use first port

        # Calculate select bits needed
        select_bits = self._bits_for(fit_result.count)

        # Determine output routing from config
        output_routing = chip_config.interface.unified_bus.output_routing
        write_mask = chip_config.interface.unified_bus.write_mask

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            port=port,
            fit=fit_result,
            sram_count=fit_result.count,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_addr_bits=sram_spec.abits,
            select_bits=select_bits,
            output_routing=output_routing,
            write_mask=write_mask,
            macro_name=chip_config.memory.macro,
        )

    def generate_chip_core(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate chip core module (wraps SRAM array).

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated SystemVerilog code.
        """
        template = self.get_template("chip_core.sv.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
        )

    def generate_chip_top(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate chip top module (with IO pads).

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated SystemVerilog code.
        """
        template = self.get_template("chip_top.sv.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
        )
