"""SRAM fit calculator."""

import math
from dataclasses import dataclass

from sram_forge.models import SramSpec, SlotSpec


@dataclass
class FitResult:
    """Result of SRAM fit calculation."""

    cols: int
    rows: int
    count: int
    total_words: int
    total_bits: int
    address_bits: int
    utilization: float

    @property
    def total_bytes(self) -> int:
        """Total capacity in bytes."""
        return self.total_bits // 8


def calculate_fit(
    slot: SlotSpec,
    sram: SramSpec,
    halo_um: float = 10.0,
    reserved_um2: float | None = None,
) -> FitResult:
    """Calculate how many SRAMs fit in a slot.

    Args:
        slot: Target slot specification.
        sram: SRAM macro specification.
        halo_um: Routing halo around each SRAM in microns (each side).
        reserved_um2: Override reserved area. If None, uses slot's value.

    Returns:
        FitResult with placement information.
    """
    if reserved_um2 is None:
        reserved_um2 = slot.reserved_area_um2

    core_w = slot.core_width
    core_h = slot.core_height

    # Effective SRAM size with halo
    sram_w = sram.dimensions_um.width + (2 * halo_um)
    sram_h = sram.dimensions_um.height + (2 * halo_um)

    # Calculate grid
    cols = int(core_w // sram_w)
    rows = int(core_h // sram_h)

    # Ensure at least 1x1 if anything fits
    if cols < 1 or rows < 1:
        cols = max(0, cols)
        rows = max(0, rows)

    # Check if we need to reduce for reserved area
    if cols > 0 and rows > 0:
        used_area = cols * rows * sram_w * sram_h
        available_area = core_w * core_h

        while (available_area - used_area) < reserved_um2 and (cols > 1 or rows > 1):
            # Reduce the larger dimension
            if cols >= rows and cols > 1:
                cols -= 1
            elif rows > 1:
                rows -= 1
            else:
                break
            used_area = cols * rows * sram_w * sram_h

    count = cols * rows
    total_words = count * sram.size
    total_bits = total_words * sram.width

    # Calculate address bits needed
    if total_words > 0:
        address_bits = math.ceil(math.log2(total_words))
    else:
        address_bits = 0

    # Calculate utilization
    if core_w * core_h > 0:
        utilization = (count * sram.dimensions_um.width * sram.dimensions_um.height) / (core_w * core_h)
    else:
        utilization = 0.0

    return FitResult(
        cols=cols,
        rows=rows,
        count=count,
        total_words=total_words,
        total_bits=total_bits,
        address_bits=address_bits,
        utilization=utilization,
    )
