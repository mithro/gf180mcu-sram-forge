"""Documentation generator for sram-forge."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sram_forge.models import ChipConfig, SramSpec
from sram_forge.calc.fit import FitResult


def get_templates_dir() -> Path:
    """Get path to documentation templates directory."""
    return Path(__file__).parent / "templates"


class DocumentationEngine:
    """Jinja2-based documentation generator."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the documentation engine.

        Args:
            templates_dir: Custom templates directory. Uses bundled templates if None.
        """
        if templates_dir is None:
            templates_dir = get_templates_dir()

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(disabled_extensions=["md", "j2"]),
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

    def generate_readme(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate README documentation.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated README markdown.
        """
        template = self.get_template("README.md.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            total_bits=fit_result.total_bits,
            total_bytes=fit_result.total_bits // 8,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_datasheet(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate datasheet-style documentation.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated datasheet markdown.
        """
        template = self.get_template("datasheet.md.j2")

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            total_bits=fit_result.total_bits,
            total_bytes=fit_result.total_bits // 8,
            write_mask=chip_config.interface.unified_bus.write_mask,
        )

    def generate_memory_map(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate memory map documentation.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated memory map markdown.
        """
        template = self.get_template("memory_map.md.j2")

        # Calculate memory regions
        regions = []
        for i in range(fit_result.count):
            start = i * sram_spec.size
            end = start + sram_spec.size - 1
            regions.append({
                "index": i,
                "start": start,
                "end": end,
                "size": sram_spec.size,
            })

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            data_width=sram_spec.width,
            addr_bits=fit_result.address_bits,
            sram_count=fit_result.count,
            total_words=fit_result.total_words,
            regions=regions,
        )
