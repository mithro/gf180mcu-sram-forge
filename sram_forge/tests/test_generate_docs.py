"""Tests for documentation generator."""

import pytest

from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.docs.engine import DocumentationEngine
from sram_forge.models import ChipConfig, SlotSpec, SramSpec


@pytest.fixture
def docs_engine():
    """Create a documentation engine instance."""
    return DocumentationEngine()


@pytest.fixture
def chip_config():
    """Sample chip configuration for testing."""
    return ChipConfig.model_validate(
        {
            "chip": {"name": "test_chip", "description": "Test SRAM chip"},
            "slot": "1x1",
            "memory": {"macro": "gf180mcu_fd_ip_sram__sram512x8m8wm1", "count": "auto"},
            "interface": {"scheme": "unified_bus"},
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


@pytest.fixture
def fit_result(slot_spec, sram_spec):
    """Calculate fit result."""
    return calculate_fit(slot_spec, sram_spec)


class TestDocumentationEngine:
    """Tests for DocumentationEngine class."""

    def test_engine_instantiation(self, docs_engine):
        """Test engine can be instantiated."""
        assert docs_engine is not None
        assert docs_engine.templates_dir.exists()

    def test_generate_readme(self, docs_engine, chip_config, sram_spec, fit_result):
        """Test README generation."""
        result = docs_engine.generate_readme(chip_config, sram_spec, fit_result)

        # Should be markdown
        assert "# test_chip" in result
        assert "Test SRAM chip" in result

        # Should include specifications
        assert "512" in result  # SRAM size
        assert str(fit_result.total_words) in result  # Total words
        assert str(fit_result.address_bits) in result  # Address bits

    def test_generate_datasheet(self, docs_engine, chip_config, sram_spec, fit_result):
        """Test datasheet generation."""
        result = docs_engine.generate_datasheet(chip_config, sram_spec, fit_result)

        # Should be markdown
        assert "# test_chip Datasheet" in result

        # Should include pinout
        assert "clk" in result.lower()
        assert "addr" in result.lower()
        assert "din" in result.lower() or "data" in result.lower()

    def test_generate_memory_map(self, docs_engine, chip_config, sram_spec, fit_result):
        """Test memory map generation."""
        result = docs_engine.generate_memory_map(chip_config, sram_spec, fit_result)

        # Should describe memory organization
        assert "Memory Map" in result
        assert "0x0000" in result or "0x0" in result
        assert "SRAM" in result

    def test_readme_includes_usage(
        self, docs_engine, chip_config, sram_spec, fit_result
    ):
        """Test README includes usage instructions."""
        result = docs_engine.generate_readme(chip_config, sram_spec, fit_result)

        # Should include basic usage
        assert "Usage" in result or "Interface" in result
        assert "write" in result.lower()
        assert "read" in result.lower()

    def test_datasheet_includes_timing_section(
        self, docs_engine, chip_config, sram_spec, fit_result
    ):
        """Test datasheet includes timing information."""
        result = docs_engine.generate_datasheet(chip_config, sram_spec, fit_result)

        # Should include timing section
        assert "Timing" in result
        assert "ns" in result

    def test_pinout_table(self, docs_engine, chip_config, sram_spec, fit_result):
        """Test datasheet includes pinout table."""
        result = docs_engine.generate_datasheet(chip_config, sram_spec, fit_result)

        # Should have table structure
        assert "|" in result  # Markdown table
        assert "Signal" in result or "Pin" in result
        assert "Direction" in result or "I/O" in result
