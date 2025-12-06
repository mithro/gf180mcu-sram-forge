"""Tests for package generator."""

import pytest
from pathlib import Path
import tempfile

from sram_forge.models import ChipConfig, SramSpec, SlotSpec
from sram_forge.calc.fit import calculate_fit
from sram_forge.generate.package.engine import PackageEngine, get_template_dir


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
        assert package_engine.template_dir.exists()

    def test_template_dir_detection(self):
        """Test template directory is correctly detected."""
        template_dir = get_template_dir()
        assert template_dir.exists()
        # Should have key template files
        assert (template_dir / "flake.nix").exists()
        assert (template_dir / "Makefile").exists()

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

    def test_manifest_includes_file_paths(
        self, package_engine, chip_config, sram_spec, fit_result
    ):
        """Test manifest includes file paths."""
        result = package_engine.generate_manifest(
            chip_config, sram_spec, fit_result, "test_pkg_v1"
        )

        # Should list expected files with correct paths
        assert "src/" in result
        assert "sram_array.sv" in result
        assert "librelane/config.yaml" in result
        assert "docs/README.md" in result

    def test_generate_readme(
        self, package_engine, chip_config, sram_spec, fit_result
    ):
        """Test README generation."""
        result = package_engine.generate_readme(chip_config, sram_spec, fit_result)

        assert "# test_pkg" in result
        assert "nix-shell" in result
        assert "make librelane" in result

    def test_create_package(
        self, package_engine, chip_config, sram_spec, slot_spec, fit_result
    ):
        """Test full package creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            package_dir = package_engine.create_package(
                chip_config,
                sram_spec,
                slot_spec,
                fit_result,
                "test_pkg_v1",
                output_path,
                init_git=False,  # Skip git init in tests
            )

            # Package directory should exist
            assert package_dir.exists()
            assert package_dir.name == "test_pkg_v1"

            # Should have manifest
            assert (package_dir / "manifest.yaml").exists()

            # Should have README
            assert (package_dir / "README.md").exists()

    def test_package_has_correct_structure(
        self, package_engine, chip_config, sram_spec, slot_spec, fit_result
    ):
        """Test package directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            package_dir = package_engine.create_package(
                chip_config,
                sram_spec,
                slot_spec,
                fit_result,
                "test_pkg_v1",
                output_path,
                init_git=False,
            )

            # Check directory structure
            assert (package_dir / "src").is_dir()
            assert (package_dir / "librelane").is_dir()
            assert (package_dir / "cocotb").is_dir()
            assert (package_dir / "docs").is_dir()

            # Check generated files
            assert (package_dir / "src" / "test_pkg_sram_array.sv").exists()
            assert (package_dir / "src" / "test_pkg_core.sv").exists()
            assert (package_dir / "src" / "test_pkg_top.sv").exists()
            assert (package_dir / "librelane" / "config.yaml").exists()
            assert (package_dir / "librelane" / "pdn_cfg.tcl").exists()
            assert (package_dir / "cocotb" / "test_sram.py").exists()
            assert (package_dir / "docs" / "README.md").exists()

    def test_package_copies_infrastructure(
        self, package_engine, chip_config, sram_spec, slot_spec, fit_result
    ):
        """Test that infrastructure files are copied from template."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            package_dir = package_engine.create_package(
                chip_config,
                sram_spec,
                slot_spec,
                fit_result,
                "test_pkg_v1",
                output_path,
                init_git=False,
            )

            # Should have infrastructure files
            assert (package_dir / "flake.nix").exists()
            assert (package_dir / "Makefile").exists()
            assert (package_dir / "LICENSE").exists()
            assert (package_dir / ".gitignore").exists()

    def test_package_rejects_existing_directory(
        self, package_engine, chip_config, sram_spec, slot_spec, fit_result
    ):
        """Test that creating a package in an existing directory fails."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            existing = output_path / "test_pkg_v1"
            existing.mkdir()

            with pytest.raises(ValueError, match="already exists"):
                package_engine.create_package(
                    chip_config,
                    sram_spec,
                    slot_spec,
                    fit_result,
                    "test_pkg_v1",
                    output_path,
                    init_git=False,
                )
