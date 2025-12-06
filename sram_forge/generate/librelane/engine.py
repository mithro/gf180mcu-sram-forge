"""LibreLane configuration generator for sram-forge."""

from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sram_forge.models import ChipConfig, SramSpec, SlotSpec
from sram_forge.calc.fit import FitResult


def get_templates_dir() -> Path:
    """Get path to LibreLane templates directory."""
    return Path(__file__).parent / "templates"


class LibreLaneEngine:
    """Jinja2-based LibreLane configuration generator."""

    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize the LibreLane engine.

        Args:
            templates_dir: Custom templates directory. Uses bundled templates if None.
        """
        if templates_dir is None:
            templates_dir = get_templates_dir()

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(disabled_extensions=["yaml", "tcl", "sdc", "j2"]),
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

    def generate_config(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        slot_spec: SlotSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate LibreLane config.yaml.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            slot_spec: Slot specification.
            fit_result: Fit calculation result.

        Returns:
            Generated YAML configuration.
        """
        template = self.get_template("config.yaml.j2")

        # Calculate areas
        die_area, core_area = slot_spec.to_librelane_areas()

        # Calculate clock period in ns
        clock_period_ns = 1000.0 / chip_config.clock.frequency_mhz

        # Generate SRAM placement coordinates
        placements = self._generate_placements(sram_spec, slot_spec, fit_result)

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            slot=slot_spec,
            fit=fit_result,
            die_area=die_area,
            core_area=core_area,
            clock_period_ns=clock_period_ns,
            macro_name=chip_config.memory.macro,
            placements=placements,
        )

    def _generate_placements(
        self,
        sram_spec: SramSpec,
        slot_spec: SlotSpec,
        fit_result: FitResult,
        halo_um: float = 10.0,
    ) -> list[dict]:
        """Generate SRAM placement coordinates.

        Args:
            sram_spec: SRAM macro specification.
            slot_spec: Slot specification.
            fit_result: Fit calculation result.
            halo_um: Routing halo in microns.

        Returns:
            List of placement dictionaries with x, y, orientation.
        """
        placements = []

        sram_w = sram_spec.dimensions_um.width
        sram_h = sram_spec.dimensions_um.height

        # Effective cell size with halo
        cell_w = sram_w + (2 * halo_um)
        cell_h = sram_h + (2 * halo_um)

        # Start from core origin
        base_x = slot_spec.core.inset.left + halo_um
        base_y = slot_spec.core.inset.bottom + halo_um

        idx = 0
        for row in range(fit_result.rows):
            for col in range(fit_result.cols):
                if idx >= fit_result.count:
                    break

                x = base_x + (col * cell_w)
                y = base_y + (row * cell_h)

                placements.append({
                    "name": f"sram_{idx}",
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "orientation": "N",  # North (no rotation)
                })
                idx += 1

        return placements

    def generate_pdn(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        slot_spec: SlotSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate PDN configuration TCL.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            slot_spec: Slot specification.
            fit_result: Fit calculation result.

        Returns:
            Generated TCL configuration.
        """
        template = self.get_template("pdn_cfg.tcl.j2")

        # Generate SRAM placement coordinates
        placements = self._generate_placements(sram_spec, slot_spec, fit_result)

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            macro_name=chip_config.memory.macro,
            placements=placements,
        )

    def generate_sdc(
        self,
        chip_config: ChipConfig,
        sram_spec: SramSpec,
        fit_result: FitResult,
    ) -> str:
        """Generate timing constraints SDC.

        Args:
            chip_config: Chip configuration.
            sram_spec: SRAM macro specification.
            fit_result: Fit calculation result.

        Returns:
            Generated SDC file.
        """
        template = self.get_template("chip_top.sdc.j2")

        # Calculate clock period in ns
        clock_period_ns = 1000.0 / chip_config.clock.frequency_mhz

        return template.render(
            chip=chip_config.chip,
            config=chip_config,
            sram=sram_spec,
            fit=fit_result,
            clock_period_ns=clock_period_ns,
            macro_name=chip_config.memory.macro,
        )
