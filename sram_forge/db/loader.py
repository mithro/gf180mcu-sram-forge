"""YAML database loader."""

from pathlib import Path
from typing import Union
import yaml

from sram_forge.models import SramSpec, SlotSpec, ChipConfig
from sram_forge.models.downstream import DownstreamRepo


def load_srams(path: Union[str, Path]) -> dict[str, SramSpec]:
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


def load_slots(path: Union[str, Path]) -> dict[str, SlotSpec]:
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


def load_chip_config(path: Union[str, Path]) -> ChipConfig:
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


def load_downstream_repos(path: Union[str, Path]) -> list[DownstreamRepo]:
    """Load downstream repository configurations from YAML.

    Args:
        path: Path to downstream_repos.yaml file

    Returns:
        List of DownstreamRepo objects

    Raises:
        FileNotFoundError: If file does not exist.
        ValidationError: If YAML content is invalid.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Downstream repos config not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    if not data or "repos" not in data:
        raise ValueError(f"Invalid downstream repos config: missing 'repos' key in {path}")

    return [DownstreamRepo.model_validate(r) for r in data["repos"]]
