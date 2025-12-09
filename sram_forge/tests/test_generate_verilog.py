"""Tests for Verilog generation."""

import pytest

from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.verilog.engine import VerilogEngine
from sram_forge.models import ChipConfig, SlotSpec, SramSpec


@pytest.fixture
def verilog_engine():
    """Create a Verilog engine instance."""
    return VerilogEngine()


@pytest.fixture
def chip_config():
    """Sample chip configuration for testing."""
    return ChipConfig.model_validate(
        {
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
        }
    )


@pytest.fixture
def sram_spec(sample_sram_spec):
    """SRAM spec from conftest fixture."""
    return SramSpec.model_validate(sample_sram_spec)


@pytest.fixture
def slot_spec(sample_slot_spec):
    """Slot spec from conftest fixture."""
    return SlotSpec.model_validate(sample_slot_spec)


def test_verilog_engine_init(verilog_engine):
    """VerilogEngine initializes with Jinja2 environment."""
    assert verilog_engine.env is not None


def test_verilog_engine_has_templates(verilog_engine):
    """VerilogEngine can load templates."""
    # Should have sram_array template
    template = verilog_engine.get_template("sram_array.sv.j2")
    assert template is not None


def test_generate_sram_array_mux(verilog_engine, chip_config, sram_spec, slot_spec):
    """Generate SRAM array with mux output routing."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = verilog_engine.generate_sram_array(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should contain module declaration
    assert "module" in result
    assert chip_config.chip.name in result or "sram_array" in result

    # Should contain SRAM instantiations
    assert "gf180mcu_fd_ip_sram__sram512x8m8wm1" in result or "sram_" in result

    # Should have clock and data ports
    assert "clk" in result.lower()
    assert "din" in result.lower() or "d[" in result.lower()
    assert "dout" in result.lower() or "q[" in result.lower()


def test_generate_sram_array_has_address_decoder(
    verilog_engine, chip_config, sram_spec, slot_spec
):
    """Generated SRAM array includes address decoder."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = verilog_engine.generate_sram_array(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should have address input
    assert "addr" in result.lower()

    # Should have case statement or mux for output selection
    assert (
        "case" in result.lower() or "mux" in result.lower() or "sel" in result.lower()
    )


def test_generate_sram_array_no_parameters(
    verilog_engine, chip_config, sram_spec, slot_spec
):
    """Generated Verilog should be fully expanded (no parameters)."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = verilog_engine.generate_sram_array(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should NOT contain parameter keyword (fully expanded)
    assert "parameter " not in result.lower()
    # Should NOT contain generate blocks (Verilog generate keyword, not "generated")
    # Look for "generate" as a standalone keyword, not part of "generated"
    import re

    assert not re.search(r"\bgenerate\b", result.lower())
    assert "genvar" not in result.lower()


@pytest.fixture
def chip_config_tristate():
    """Chip configuration with tristate output routing."""
    return ChipConfig.model_validate(
        {
            "chip": {"name": "test_sram_tristate", "description": "Tristate SRAM test"},
            "slot": "1x1",
            "memory": {"macro": "gf180mcu_fd_ip_sram__sram512x8m8wm1", "count": 16},
            "interface": {
                "scheme": "unified_bus",
                "unified_bus": {
                    "data_width": 8,
                    "output_routing": "tristate",
                    "write_mask": False,
                },
            },
        }
    )


def test_generate_sram_array_tristate(
    verilog_engine, chip_config_tristate, sram_spec, slot_spec
):
    """Generate SRAM array with tristate output routing."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = verilog_engine.generate_sram_array(
        chip_config=chip_config_tristate,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should contain tristate (high-Z) assignment
    assert "'bz" in result.lower() or "'hz" in result.lower()
    # Should NOT have case statement for output mux
    assert "case (sram_sel)" not in result


@pytest.fixture
def chip_config_write_mask():
    """Chip configuration with write mask enabled."""
    return ChipConfig.model_validate(
        {
            "chip": {"name": "test_sram_wmask", "description": "Write mask SRAM test"},
            "slot": "1x1",
            "memory": {"macro": "gf180mcu_fd_ip_sram__sram512x8m8wm1", "count": 16},
            "interface": {
                "scheme": "unified_bus",
                "unified_bus": {
                    "data_width": 8,
                    "output_routing": "mux",
                    "write_mask": True,
                },
            },
        }
    )


def test_generate_sram_array_write_mask(
    verilog_engine, chip_config_write_mask, sram_spec, slot_spec
):
    """Generate SRAM array with write mask support."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = verilog_engine.generate_sram_array(
        chip_config=chip_config_write_mask,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should have write mask port
    assert "wem_n" in result.lower()
    # Should NOT have hardcoded WEN value
    assert ".wen(8'b0)" not in result.lower()
