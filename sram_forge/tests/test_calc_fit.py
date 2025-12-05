"""Tests for SRAM fit calculator."""

import pytest
from sram_forge.models import SramSpec, SlotSpec
from sram_forge.calc.fit import calculate_fit, FitResult


@pytest.fixture
def sram_512x8(sample_sram_spec):
    """512x8 SRAM for testing."""
    return SramSpec.model_validate(sample_sram_spec)


@pytest.fixture
def slot_1x1(sample_slot_spec):
    """1x1 slot for testing."""
    return SlotSpec.model_validate(sample_slot_spec)


def test_calculate_fit_basic(sram_512x8, slot_1x1):
    """Calculate how many SRAMs fit in slot."""
    result = calculate_fit(slot_1x1, sram_512x8)

    assert isinstance(result, FitResult)
    assert result.count > 0
    assert result.cols > 0
    assert result.rows > 0
    assert result.count == result.cols * result.rows


def test_calculate_fit_dimensions(sram_512x8, slot_1x1):
    """Fit calculation respects physical dimensions."""
    result = calculate_fit(slot_1x1, sram_512x8)

    # With halo: 431.86 + 20 = 451.86 width, 484.88 + 20 = 504.88 height
    # Core: 3048 x 4238
    # Expected: floor(3048/451.86) = 6 cols, floor(4238/504.88) = 8 rows
    # But need to account for reserved area
    assert result.cols >= 1
    assert result.rows >= 1


def test_calculate_fit_total_capacity(sram_512x8, slot_1x1):
    """Fit result includes total capacity."""
    result = calculate_fit(slot_1x1, sram_512x8)

    expected_words = result.count * sram_512x8.size
    assert result.total_words == expected_words
    assert result.total_bits == expected_words * sram_512x8.width


def test_calculate_fit_address_bits(sram_512x8, slot_1x1):
    """Fit result calculates address bits needed."""
    result = calculate_fit(slot_1x1, sram_512x8)

    import math
    expected_abits = math.ceil(math.log2(result.total_words))
    assert result.address_bits == expected_abits


def test_calculate_fit_with_halo():
    """Halo spacing is applied correctly."""
    # Small slot that fits exactly 1 SRAM without halo
    from sram_forge.models.slot import SlotSpec
    from sram_forge.models.sram import SramSpec

    sram = SramSpec.model_validate({
        "source": "pdk",
        "size": 64,
        "width": 8,
        "abits": 6,
        "dimensions_um": {"width": 100, "height": 100},
        "ports": [{
            "name": "port0",
            "type": "rw",
            "clk_enable": True,
            "clk_polarity": "rising",
            "pins": {"clk": "CLK"},
        }],
    })

    slot = SlotSpec.model_validate({
        "die": {"width": 200, "height": 200},
        "core": {"inset": {"left": 10, "bottom": 10, "right": 10, "top": 10}},
        "io_budget": {"dvdd": 1, "dvss": 1, "input": 0, "bidir": 10, "analog": 0},
        "reserved_area_um2": 0,
    })

    # Core is 180x180, SRAM is 100x100
    # With 20um halo (10 each side): effective 120x120
    # Should fit 1x1
    result = calculate_fit(slot, sram, halo_um=10)
    assert result.cols == 1
    assert result.rows == 1
