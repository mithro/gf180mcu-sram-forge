"""Tests for LibreLane configuration generation."""

import pytest
from pathlib import Path

from sram_forge.generate.librelane.engine import LibreLaneEngine
from sram_forge.models import SramSpec, SlotSpec, ChipConfig
from sram_forge.calc.fit import calculate_fit


@pytest.fixture
def librelane_engine():
    """Create a LibreLane engine instance."""
    return LibreLaneEngine()


@pytest.fixture
def chip_config():
    """Sample chip configuration for testing."""
    return ChipConfig.model_validate({
        "chip": {"name": "test_sram_8k", "description": "8K SRAM test chip"},
        "slot": "1x1",
        "memory": {"macro": "gf180mcu_fd_ip_sram__sram512x8m8wm1", "count": 16},
        "interface": {
            "scheme": "unified_bus",
            "unified_bus": {
                "data_width": 8,
                "output_routing": "mux",
                "write_mask": False,
            },
        },
        "clock": {"frequency_mhz": 25},
    })


@pytest.fixture
def sram_spec(sample_sram_spec):
    """SRAM spec from conftest fixture."""
    return SramSpec.model_validate(sample_sram_spec)


@pytest.fixture
def slot_spec(sample_slot_spec):
    """Slot spec from conftest fixture."""
    return SlotSpec.model_validate(sample_slot_spec)


def test_librelane_engine_init(librelane_engine):
    """LibreLaneEngine initializes correctly."""
    assert librelane_engine.env is not None


def test_generate_config_yaml(librelane_engine, chip_config, sram_spec, slot_spec):
    """Generate LibreLane config.yaml."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = librelane_engine.generate_config(
        chip_config=chip_config,
        sram_spec=sram_spec,
        slot_spec=slot_spec,
        fit_result=fit_result,
    )

    # Should be valid YAML-like content
    assert "DESIGN_NAME" in result or "design_name" in result.lower()

    # Should have die and core areas
    assert "DIE_AREA" in result or "die_area" in result.lower()
    assert "CORE_AREA" in result or "core_area" in result.lower()

    # Should reference SRAM macros
    assert "MACRO" in result.upper() or "macro" in result.lower()


def test_generate_config_has_clock_period(librelane_engine, chip_config, sram_spec, slot_spec):
    """Generated config includes clock period from chip config."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = librelane_engine.generate_config(
        chip_config=chip_config,
        sram_spec=sram_spec,
        slot_spec=slot_spec,
        fit_result=fit_result,
    )

    # 25 MHz = 40ns period
    assert "40" in result or "CLOCK_PERIOD" in result


def test_generate_pdn_tcl(librelane_engine, chip_config, sram_spec, slot_spec):
    """Generate PDN configuration TCL."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = librelane_engine.generate_pdn(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should contain PDN-related content
    assert "pdn" in result.lower() or "power" in result.lower() or "vdd" in result.lower()


def test_generate_sdc(librelane_engine, chip_config, sram_spec, slot_spec):
    """Generate timing constraints SDC."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = librelane_engine.generate_sdc(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should contain clock constraint
    assert "clock" in result.lower() or "clk" in result.lower()
    # Should contain create_clock or similar SDC command
    assert "create_clock" in result.lower() or "set_clock" in result.lower() or "period" in result.lower()
