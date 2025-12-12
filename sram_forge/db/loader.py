"""YAML database loader."""

from pathlib import Path

import yaml

from sram_forge.models import ChipConfig, SlotSpec, SramSpec


def load_srams(path: str | Path) -> dict[str, SramSpec]:
    """Load SRAM specifications from YAML file.

    Args:
        path: Path to srams.yaml file.

    Returns:
        Dictionary mapping SRAM names to SramSpec objects.

    Raises:
        FileNotFoundError: If file does not exist.
        ValidationError: If YAML content is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"SRAM database not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    srams = {}
    for name, spec in data.get("srams", {}).items():
        srams[name] = SramSpec.model_validate(spec)

    return srams


def load_slots(path: str | Path) -> dict[str, SlotSpec]:
    """Load slot specifications from YAML file.

    Args:
        path: Path to slots.yaml file.

    Returns:
        Dictionary mapping slot names to SlotSpec objects.

    Raises:
        FileNotFoundError: If file does not exist.
        ValidationError: If YAML content is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Slot database not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    slots = {}
    for name, spec in data.get("slots", {}).items():
        slots[name] = SlotSpec.model_validate(spec)

    return slots


def load_chip_config(path: str | Path) -> ChipConfig:
    """Load chip configuration from YAML file.

    Args:
        path: Path to chip.yaml file.

    Returns:
        ChipConfig object.

    Raises:
        FileNotFoundError: If file does not exist.
        ValidationError: If YAML content is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Chip config not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return ChipConfig.model_validate(data)
