"""Tests for chip configuration model."""

import pytest
from sram_forge.models.chip import ChipConfig, Memory, Interface, UnifiedBus


def test_chip_config_minimal():
    """ChipConfig with minimal required fields."""
    config = ChipConfig(
        chip={"name": "test_sram", "description": "Test chip"},
        slot="1x1",
        memory={"macro": "sram512x8m8wm1"},
    )

    assert config.chip.name == "test_sram"
    assert config.slot == "1x1"
    assert config.memory.macro == "sram512x8m8wm1"
    assert config.memory.count == "auto"


def test_chip_config_with_interface():
    """ChipConfig with interface configuration."""
    config = ChipConfig(
        chip={"name": "test_sram"},
        slot="1x1",
        memory={"macro": "sram512x8m8wm1", "count": 14},
        interface={
            "scheme": "unified_bus",
            "unified_bus": {
                "data_width": 8,
                "output_routing": "tristate",
                "write_mask": True,
            },
        },
    )

    assert config.interface.scheme == "unified_bus"
    assert config.interface.unified_bus.output_routing == "tristate"
    assert config.interface.unified_bus.write_mask is True


def test_chip_config_defaults():
    """ChipConfig has sensible defaults."""
    config = ChipConfig(
        chip={"name": "test"},
        slot="1x1",
        memory={"macro": "sram512x8m8wm1"},
    )

    assert config.interface.scheme == "unified_bus"
    assert config.interface.unified_bus.output_routing == "mux"
    assert config.interface.unified_bus.write_mask is False
    assert config.interface.unified_bus.registered_output is False
    assert config.clock.frequency_mhz == 25
    assert config.power.core_voltage == 5.0


def test_memory_count_auto():
    """Memory count can be 'auto' or integer."""
    mem1 = Memory(macro="test", count="auto")
    assert mem1.count == "auto"

    mem2 = Memory(macro="test", count=10)
    assert mem2.count == 10
