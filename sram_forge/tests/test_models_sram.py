"""Tests for SRAM model."""

import pytest

from sram_forge.models.sram import Port, SramSpec


def test_sram_spec_from_dict(sample_sram_spec):
    """SramSpec can be created from dictionary."""
    sram = SramSpec.model_validate(sample_sram_spec)

    assert sram.source == "pdk"
    assert sram.size == 512
    assert sram.width == 8
    assert sram.abits == 9
    assert sram.dimensions_um.width == 431.86
    assert sram.dimensions_um.height == 484.88


def test_sram_spec_total_bits(sample_sram_spec):
    """SramSpec calculates total bits correctly."""
    sram = SramSpec.model_validate(sample_sram_spec)

    assert sram.total_bits == 512 * 8  # 4096 bits


def test_sram_spec_area_um2(sample_sram_spec):
    """SramSpec calculates area correctly."""
    sram = SramSpec.model_validate(sample_sram_spec)

    expected = 431.86 * 484.88
    assert abs(sram.area_um2 - expected) < 0.01


def test_port_type_validation():
    """Port type must be ro, wo, or rw."""
    with pytest.raises(ValueError):
        Port(
            name="bad",
            type="invalid",
            clk_enable=True,
            clk_polarity="rising",
            pins={"clk": "CLK"},
        )


def test_port_has_write_mask(sample_sram_spec):
    """Port correctly reports write mask availability."""
    sram = SramSpec.model_validate(sample_sram_spec)
    port = sram.ports[0]

    assert port.has_write_mask is True


def test_port_without_write_mask():
    """Port without wem_n reports no write mask."""
    port = Port(
        name="simple",
        type="rw",
        clk_enable=True,
        clk_polarity="rising",
        pins={
            "clk": "CLK",
            "en_n": "CEN",
            "we_n": "WE",
            "addr": "A[7:0]",
            "din": "D[7:0]",
            "dout": "Q[7:0]",
        },
    )

    assert port.has_write_mask is False
