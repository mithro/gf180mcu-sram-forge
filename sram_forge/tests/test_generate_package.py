"""Tests for package generator."""

import pytest
import tarfile
from pathlib import Path
import tempfile
import shutil

from sram_forge.models import ChipConfig, SramSpec, SlotSpec
from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.package.engine import PackageEngine


@pytest.fixture
def package_engine():
    """Create a package engine instance."""
    return PackageEngine()


@pytest.fixture
def chip_config():
    """Sample chip configuration for testing."""
    return ChipConfig.model_validate({
        "chip": {"name": "test_pkg", "description": "Test package chip"},
        "slot": "1x1",
        "memory": {"macro": "gf180mcu_fd_ip_sram__sram512x8m8wm1", "count": 16},
        "interface": {"scheme": "unified_bus"},
    })


@pytest.fixture
def sram_spec(sample_sram_spec):
    """SRAM spec from conftest fixture."""
    return SramSpec.model_validate(sample_sram_spec)


@pytest.fixture
def slot_spec(sample_slot_spec):
    """Slot spec from conftest fixture."""
    return SlotSpec.model_validate(sample_slot_spec)


@pytest.fixture
def fit_result(slot_spec, sram_spec, chip_config):
    """Calculate fit result with count override."""
    result = calculate_fit(slot_spec, sram_spec)
    # Override count for testing
    result.count = 16
    result.total_words = 16 * sram_spec.size
    result.total_bits = result.total_words * sram_spec.width
    import math
    result.address_bits = math.ceil(math.log2(result.total_words))
    return result


class TestPackageEngine:
    """Tests for PackageEngine class."""

    def test_engine_instantiation(self, package_engine):
        """Test engine can be instantiated."""
        assert package_engine is not None

    def test_generate_manifest(
        self, package_engine, chip_config, sram_spec, fit_result
    ):
        """Test manifest generation."""
        result = package_engine.generate_manifest(
            chip_config, sram_spec, fit_result, "test_pkg_v1"
        )

        # Should be YAML
        assert "name:" in result
        assert "test_pkg_v1" in result
        assert "test_pkg" in result
        assert "files:" in result

    def test_manifest_includes_checksums(
        self, package_engine, chip_config, sram_spec, fit_result
    ):
        """Test manifest includes file information."""
        result = package_engine.generate_manifest(
            chip_config, sram_spec, fit_result, "test_pkg_v1"
        )

        # Should list expected files
        assert "sram_array.sv" in result
        assert "config.yaml" in result
        assert "README.md" in result

    def test_create_package(
        self, package_engine, chip_config, sram_spec, slot_spec, fit_result
    ):
        """Test full package creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            archive_path = package_engine.create_package(
                chip_config,
                sram_spec,
                slot_spec,
                fit_result,
                "test_pkg_v1",
                output_path,
            )

            # Archive should exist
            assert archive_path.exists()
            assert archive_path.suffix == ".gz"

            # Archive should contain expected files
            with tarfile.open(archive_path, "r:gz") as tar:
                names = tar.getnames()
                assert any("manifest.yaml" in n for n in names)
                assert any("sram_array.sv" in n for n in names)
                assert any("README.md" in n for n in names)

    def test_package_has_correct_structure(
        self, package_engine, chip_config, sram_spec, slot_spec, fit_result
    ):
        """Test package directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            archive_path = package_engine.create_package(
                chip_config,
                sram_spec,
                slot_spec,
                fit_result,
                "test_pkg_v1",
                output_path,
            )

            with tarfile.open(archive_path, "r:gz") as tar:
                names = tar.getnames()
                # Check directory structure
                assert any("src/" in n for n in names)
                assert any("docs/" in n for n in names)
                assert any("cocotb/" in n for n in names)
