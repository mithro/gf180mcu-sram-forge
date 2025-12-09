"""Tests for cocotb testbench generation."""

import pytest

from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.testbench.engine import TestbenchEngine
from sram_forge.models import ChipConfig, SlotSpec, SramSpec


@pytest.fixture
def testbench_engine():
    """Create a testbench engine instance."""
    return TestbenchEngine()


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
            "clock": {"frequency_mhz": 25},
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


def test_testbench_engine_init(testbench_engine):
    """TestbenchEngine initializes correctly."""
    assert testbench_engine.env is not None


def test_generate_cocotb_test(testbench_engine, chip_config, sram_spec, slot_spec):
    """Generate cocotb testbench."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = testbench_engine.generate_cocotb_test(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should be valid Python
    assert "import cocotb" in result
    assert "from cocotb" in result

    # Should have test functions
    assert "@cocotb.test" in result or "async def test_" in result


def test_generate_cocotb_test_has_write_read(
    testbench_engine, chip_config, sram_spec, slot_spec
):
    """Generated testbench includes write/read tests."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = testbench_engine.generate_cocotb_test(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should test basic read/write operations
    assert "write" in result.lower()
    assert "read" in result.lower()


def test_generate_cocotb_test_has_address_boundary(
    testbench_engine, chip_config, sram_spec, slot_spec
):
    """Generated testbench includes address boundary tests."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = testbench_engine.generate_cocotb_test(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should test address boundaries
    assert "boundary" in result.lower() or "address" in result.lower()


def test_generate_makefile(testbench_engine, chip_config):
    """Generate cocotb Makefile."""
    result = testbench_engine.generate_makefile(chip_config)

    # Should be a valid Makefile
    assert "TOPLEVEL" in result or "toplevel" in result.lower()
    assert "MODULE" in result or "module" in result.lower()


def test_generate_behavioral_model(testbench_engine, chip_config, sram_spec, slot_spec):
    """Generate Python behavioral model."""
    fit_result = calculate_fit(slot_spec, sram_spec)

    result = testbench_engine.generate_behavioral_model(
        chip_config=chip_config,
        sram_spec=sram_spec,
        fit_result=fit_result,
    )

    # Should be a Python class
    assert "class" in result
    # Should have write and read methods
    assert "def write" in result or "def read" in result or "memory" in result.lower()
