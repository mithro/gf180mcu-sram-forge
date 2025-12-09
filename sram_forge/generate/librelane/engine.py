"""LibreLane configuration generator for sram-forge."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from sram_forge.calc.fit import FitResult
from sram_forge.models import ChipConfig, SlotSpec, SramSpec


def get_templates_dir() -> Path:
    """Get path to LibreLane templates directory."""
    return Path(__file__).parent / "templates"


class LibreLaneEngine:
    """Jinja2-based LibreLane configuration generator."""

    def __init__(self, templates_dir: Path | None = None):
        """Initialize the LibreLane engine.

        Args:
            templates_dir: Custom templates directory. Uses bundled templates if None.
        """
        if templates_dir is None:
            templates_dir = get_templates_dir()

        self.templates_dir = templates_dir
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(
                disabled_extensions=["yaml", "tcl", "sdc", "j2"]
            ),
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

        # Convert slot name to define format (e.g., "1x1" -> "1X1", "0p5x1" -> "0P5X1")
        slot_define = chip_config.slot.upper().replace(".", "P").replace("X", "X")

        # Calculate placement density based on macro utilization
        # High macro occupancy requires lower target density to avoid placer divergence
        placement_density_pct = self._calculate_placement_density(
            fit_result.utilization
        )

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
            slot_define=slot_define,
            placement_density_pct=placement_density_pct,
        )

    def _calculate_placement_density(self, macro_utilization: float) -> int:
        """Calculate appropriate placement density based on macro utilization.

        When macros occupy a large fraction of the core area, the global placer
        needs a lower target density to avoid numerical instability (GPL-0305).

        For very high macro occupancy (>80%), the remaining space has very few
        standard cells (typically <2% utilization in remaining area). The target
        density must be close to or slightly above actual utilization, otherwise
        the placer's penalty term grows exponentially causing Inf/NaN overflow.

        Args:
            macro_utilization: Fraction of core area occupied by macros (0.0-1.0).

        Returns:
            Target placement density percentage (1-100).
        """
        if macro_utilization > 0.80:
            # Extremely high macro occupancy (>80%)
            # Actual std cell utilization is typically ~1-2% of remaining area
            # Use very low density to avoid GPL-0305 divergence
            return 2
        elif macro_utilization > 0.70:
            # Very high macro occupancy (70-80%)
            return 5
        elif macro_utilization > 0.50:
            # High macro occupancy (50-70%)
            return 10
        elif macro_utilization > 0.30:
            # Moderate macro occupancy (30-50%)
            return 15
        else:
            # Low macro occupancy (<30%) - use standard density
            return 20

    def _generate_placements(
        self,
        sram_spec: SramSpec,
        slot_spec: SlotSpec,
        fit_result: FitResult,
        halo_um: float = 10.0,
    ) -> list[dict]:
        """Generate SRAM placement coordinates, centered in core area.

        The SRAM array is centered within the core area so that there is
        equal spacing on all sides (left/right and top/bottom).

        Args:
            sram_spec: SRAM macro specification.
            slot_spec: Slot specification.
            fit_result: Fit calculation result.
            halo_um: Routing halo between SRAMs in microns.

        Returns:
            List of placement dictionaries with x, y, orientation.
        """
        placements = []

        sram_w = sram_spec.dimensions_um.width
        sram_h = sram_spec.dimensions_um.height

        # Calculate total array dimensions
        # Array width = cols * sram_width + (cols - 1) * 2 * halo (gaps between SRAMs)
        # We also need halo on outer edges, so: cols * sram_w + (cols + 1) * halo on each side
        # Simplified: total array with outer halos = cols * (sram_w + 2*halo)
        array_width = fit_result.cols * (sram_w + 2 * halo_um)
        array_height = fit_result.rows * (sram_h + 2 * halo_um)

        # Core area dimensions
        core_width = slot_spec.core_width
        core_height = slot_spec.core_height

        # Calculate margins to center the array
        margin_x = (core_width - array_width) / 2
        margin_y = (core_height - array_height) / 2

        # Base position: core origin + margin + first halo
        base_x = slot_spec.core.inset.left + margin_x + halo_um
        base_y = slot_spec.core.inset.bottom + margin_y + halo_um

        # Effective cell size with halo
        cell_w = sram_w + (2 * halo_um)
        cell_h = sram_h + (2 * halo_um)

        idx = 0
        for row in range(fit_result.rows):
            for col in range(fit_result.cols):
                if idx >= fit_result.count:
                    break

                x = base_x + (col * cell_w)
                y = base_y + (row * cell_h)

                placements.append(
                    {
                        "name": f"sram_{idx}",
                        "x": round(x, 2),
                        "y": round(y, 2),
                        "orientation": "N",  # North (no rotation)
                    }
                )
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

    def generate_makefile(
        self,
        chip_config: ChipConfig,
    ) -> str:
        """Generate root Makefile with correct DEFAULT_SLOT.

        Args:
            chip_config: Chip configuration.

        Returns:
            Generated Makefile content.
        """
        template = self.get_template("Makefile.j2")

        return template.render(
            slot=chip_config.slot,
            chip_name=chip_config.chip.name,
        )
