"""Tests for database loader."""

import pytest
from pathlib import Path
from sram_forge.db.loader import load_srams, load_slots
from sram_forge.models import SramSpec, SlotSpec


def test_load_srams(fixtures_dir):
    """Load SRAM specs from YAML file."""
    srams = load_srams(fixtures_dir / "srams.yaml")

    assert "test_sram_64x8" in srams
    assert "test_sram_512x8" in srams
    assert isinstance(srams["test_sram_64x8"], SramSpec)
    assert srams["test_sram_64x8"].size == 64


def test_load_slots(fixtures_dir):
    """Load slot specs from YAML file."""
    slots = load_slots(fixtures_dir / "slots.yaml")

    assert "1x1" in slots
    assert "0p5x0p5" in slots
    assert isinstance(slots["1x1"], SlotSpec)
    assert slots["1x1"].die.width == 3932


def test_load_srams_file_not_found():
    """Loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_srams(Path("/nonexistent/srams.yaml"))


def test_load_slots_file_not_found():
    """Loading non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_slots(Path("/nonexistent/slots.yaml"))
