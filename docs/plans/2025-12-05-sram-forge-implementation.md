# sram-forge Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python framework that generates SRAM-based chip designs for GF180MCU, producing LibreLane configs, Verilog, testbenches, and documentation from YAML specifications.

**Architecture:** Template engine (Jinja2) with YAML database of SRAM/slot specs. Core library with calculation, placement, and generation modules. Thin CLI wrappers using Click. Outputs LibreLane-compatible configurations.

**Tech Stack:** Python 3.11+, uv, Click (CLI), Jinja2 (templates), PyYAML, Pydantic (models)

---

## Phase 1: Project Setup

### Task 1: Initialize Python Project

**Files:**
- Create: `sram_forge/pyproject.toml`
- Create: `sram_forge/__init__.py`
- Create: `sram_forge/py.typed`

**Step 1: Create project directory**

```bash
mkdir -p sram_forge
```

**Step 2: Create pyproject.toml**

Create `sram_forge/pyproject.toml`:

```toml
[project]
name = "sram-forge"
version = "0.1.0"
description = "Generate SRAM-based chip designs for GF180MCU"
readme = "README.md"
license = {text = "Apache-2.0"}
requires-python = ">=3.11"
dependencies = [
    "click>=8.1.0",
    "jinja2>=3.1.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
]

[project.scripts]
sram-forge = "sram_forge.cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

**Step 3: Create package init**

Create `sram_forge/__init__.py`:

```python
"""sram-forge: Generate SRAM-based chip designs for GF180MCU."""

__version__ = "0.1.0"
```

**Step 4: Create py.typed marker**

```bash
touch sram_forge/py.typed
```

**Step 5: Verify uv can see the project**

Run: `cd sram_forge && uv pip install -e ".[dev]" --dry-run`
Expected: Shows what would be installed without errors

**Step 6: Commit**

```bash
git add sram_forge/
git commit -m "feat: initialize sram-forge Python project structure"
```

---

### Task 2: Create Test Infrastructure

**Files:**
- Create: `sram_forge/tests/__init__.py`
- Create: `sram_forge/tests/conftest.py`

**Step 1: Create tests directory**

```bash
mkdir -p sram_forge/tests
```

**Step 2: Create tests/__init__.py**

Create `sram_forge/tests/__init__.py`:

```python
"""sram-forge test suite."""
```

**Step 3: Create conftest.py with fixtures**

Create `sram_forge/tests/conftest.py`:

```python
"""Shared pytest fixtures for sram-forge tests."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_sram_spec() -> dict:
    """Sample SRAM specification for testing."""
    return {
        "source": "pdk",
        "size": 512,
        "width": 8,
        "abits": 9,
        "dimensions_um": {
            "width": 431.86,
            "height": 484.88,
        },
        "ports": [
            {
                "name": "port0",
                "type": "rw",
                "clk_enable": True,
                "clk_polarity": "rising",
                "pins": {
                    "clk": "CLK",
                    "en_n": "CEN",
                    "we_n": "GWEN",
                    "wem_n": "WEN[7:0]",
                    "addr": "A[8:0]",
                    "din": "D[7:0]",
                    "dout": "Q[7:0]",
                },
            }
        ],
        "timing_ns": {
            "min_cycle": 6.077,
            "clk_to_q": 5.008,
            "setup": {"addr": 0.947, "din": 0.458, "en": 0.406},
            "hold": {"addr": 0.549, "din": 0.674},
        },
        "files": {
            "gds": "pdk_dir::libs.ref/gf180mcu_fd_ip_sram/gds/sram.gds",
            "lef": "pdk_dir::libs.ref/gf180mcu_fd_ip_sram/lef/sram.lef",
        },
    }


@pytest.fixture
def sample_slot_spec() -> dict:
    """Sample slot specification for testing."""
    return {
        "die": {"width": 3932, "height": 5122},
        "core": {
            "inset": {"left": 442, "bottom": 442, "right": 442, "top": 442}
        },
        "io_budget": {
            "dvdd": 8,
            "dvss": 10,
            "input": 12,
            "bidir": 40,
            "analog": 2,
        },
        "reserved_area_um2": 50000,
    }
```

**Step 4: Create fixtures directory**

```bash
mkdir -p sram_forge/tests/fixtures
touch sram_forge/tests/fixtures/.gitkeep
```

**Step 5: Verify pytest runs**

Run: `cd sram_forge && uv run pytest --collect-only`
Expected: Shows "no tests ran" (collection works, just no tests yet)

**Step 6: Commit**

```bash
git add sram_forge/tests/
git commit -m "feat: add pytest infrastructure and fixtures"
```

---

## Phase 2: Data Models

### Task 3: Create SRAM Model

**Files:**
- Create: `sram_forge/sram_forge/models/__init__.py`
- Create: `sram_forge/sram_forge/models/sram.py`
- Create: `sram_forge/tests/test_models_sram.py`

**Step 1: Create models directory**

```bash
mkdir -p sram_forge/sram_forge/models
```

**Step 2: Write failing test for SramSpec**

Create `sram_forge/tests/test_models_sram.py`:

```python
"""Tests for SRAM model."""

import pytest
from sram_forge.models.sram import SramSpec, Port, Timing


def test_sram_spec_from_dict(sample_sram_spec):
    """SramSpec can be created from dictionary."""
    sram = SramSpec.model_validate(sample_sram_spec)

    assert sram.source == "pdk"
    assert sram.size == 512
    assert sram.width == 8
    assert sram.abits == 9
    assert sram.dimensions_um.width == 431.86
    assert sram.dimensions_um.height == 484.88


def test_sram_spec_total_bits(sample_sram_spec):
    """SramSpec calculates total bits correctly."""
    sram = SramSpec.model_validate(sample_sram_spec)

    assert sram.total_bits == 512 * 8  # 4096 bits


def test_sram_spec_area_um2(sample_sram_spec):
    """SramSpec calculates area correctly."""
    sram = SramSpec.model_validate(sample_sram_spec)

    expected = 431.86 * 484.88
    assert abs(sram.area_um2 - expected) < 0.01


def test_port_type_validation():
    """Port type must be ro, wo, or rw."""
    with pytest.raises(ValueError):
        Port(
            name="bad",
            type="invalid",
            clk_enable=True,
            clk_polarity="rising",
            pins={"clk": "CLK"},
        )


def test_port_has_write_mask(sample_sram_spec):
    """Port correctly reports write mask availability."""
    sram = SramSpec.model_validate(sample_sram_spec)
    port = sram.ports[0]

    assert port.has_write_mask is True


def test_port_without_write_mask():
    """Port without wem_n reports no write mask."""
    port = Port(
        name="simple",
        type="rw",
        clk_enable=True,
        clk_polarity="rising",
        pins={"clk": "CLK", "en_n": "CEN", "we_n": "WE", "addr": "A[7:0]", "din": "D[7:0]", "dout": "Q[7:0]"},
    )

    assert port.has_write_mask is False
```

**Step 3: Run test to verify it fails**

Run: `cd sram_forge && uv run pytest tests/test_models_sram.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'sram_forge.models'"

**Step 4: Create models/__init__.py**

Create `sram_forge/sram_forge/models/__init__.py`:

```python
"""Data models for sram-forge."""

from sram_forge.models.sram import SramSpec, Port, Timing, Dimensions, Pins

__all__ = ["SramSpec", "Port", "Timing", "Dimensions", "Pins"]
```

**Step 5: Implement SramSpec model**

Create `sram_forge/sram_forge/models/sram.py`:

```python
"""SRAM specification models."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class Dimensions(BaseModel):
    """Physical dimensions in microns."""

    width: float = Field(gt=0, description="Width in microns")
    height: float = Field(gt=0, description="Height in microns")


class Pins(BaseModel):
    """Pin mapping for an SRAM port."""

    clk: str = Field(description="Clock pin name")
    en_n: Optional[str] = Field(default=None, description="Enable pin (active low)")
    we_n: Optional[str] = Field(default=None, description="Write enable pin (active low)")
    wem_n: Optional[str] = Field(default=None, description="Write mask pin (active low)")
    addr: Optional[str] = Field(default=None, description="Address bus")
    din: Optional[str] = Field(default=None, description="Data input bus")
    dout: Optional[str] = Field(default=None, description="Data output bus")


class SetupHold(BaseModel):
    """Setup and hold timing parameters."""

    addr: float = Field(ge=0, description="Address setup/hold time in ns")
    din: Optional[float] = Field(default=None, ge=0, description="Data input setup/hold time in ns")
    en: Optional[float] = Field(default=None, ge=0, description="Enable setup/hold time in ns")


class Timing(BaseModel):
    """Timing parameters in nanoseconds."""

    min_cycle: float = Field(gt=0, description="Minimum clock period")
    clk_to_q: float = Field(gt=0, description="Clock to output delay")
    setup: SetupHold = Field(description="Setup times")
    hold: SetupHold = Field(description="Hold times")


class Port(BaseModel):
    """SRAM port definition."""

    name: str = Field(description="Port identifier")
    type: Literal["ro", "wo", "rw"] = Field(description="Port type: read-only, write-only, read-write")
    clk_enable: bool = Field(description="Whether port is synchronous")
    clk_polarity: Literal["rising", "falling"] = Field(description="Clock edge")
    pins: Pins = Field(description="Pin mapping")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("ro", "wo", "rw"):
            raise ValueError(f"Port type must be 'ro', 'wo', or 'rw', got '{v}'")
        return v

    @property
    def has_write_mask(self) -> bool:
        """Whether this port has per-bit write mask capability."""
        return self.pins.wem_n is not None


class Files(BaseModel):
    """File paths for SRAM macro."""

    gds: str = Field(description="GDS file path")
    lef: str = Field(description="LEF file path")
    lib: Optional[str] = Field(default=None, description="Liberty timing file path")
    verilog: Optional[str] = Field(default=None, description="Verilog model path")


class SramSpec(BaseModel):
    """Complete SRAM macro specification."""

    source: Literal["pdk", "openram", "custom"] = Field(description="SRAM source")
    size: int = Field(gt=0, description="Number of words")
    width: int = Field(gt=0, description="Bits per word")
    abits: int = Field(gt=0, description="Address bus width")
    dimensions_um: Dimensions = Field(description="Physical dimensions")
    ports: list[Port] = Field(min_length=1, description="Port definitions")
    timing_ns: Optional[Timing] = Field(default=None, description="Timing parameters")
    files: Optional[Files] = Field(default=None, description="File paths")

    @property
    def total_bits(self) -> int:
        """Total storage capacity in bits."""
        return self.size * self.width

    @property
    def area_um2(self) -> float:
        """Area in square microns."""
        return self.dimensions_um.width * self.dimensions_um.height
```

**Step 6: Fix the import path issue**

The package structure needs adjustment. Update `sram_forge/sram_forge/` to just `sram_forge/`:

```bash
# We created nested sram_forge/sram_forge by mistake
# The structure should be sram_forge/models/ directly
mv sram_forge/sram_forge/models sram_forge/models
rmdir sram_forge/sram_forge 2>/dev/null || true
```

**Step 7: Run tests to verify they pass**

Run: `cd sram_forge && uv run pytest tests/test_models_sram.py -v`
Expected: All 6 tests PASS

**Step 8: Commit**

```bash
git add sram_forge/
git commit -m "feat: add SramSpec model with Pydantic validation"
```

---

### Task 4: Create Slot Model

**Files:**
- Create: `sram_forge/sram_forge/models/slot.py`
- Create: `sram_forge/tests/test_models_slot.py`
- Modify: `sram_forge/sram_forge/models/__init__.py`

**Step 1: Write failing test for SlotSpec**

Create `sram_forge/tests/test_models_slot.py`:

```python
"""Tests for slot model."""

import pytest
from sram_forge.models.slot import SlotSpec, Die, Core, Inset, IoBudget


def test_slot_spec_from_dict(sample_slot_spec):
    """SlotSpec can be created from dictionary."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    assert slot.die.width == 3932
    assert slot.die.height == 5122
    assert slot.core.inset.left == 442


def test_slot_core_dimensions(sample_slot_spec):
    """SlotSpec calculates core dimensions correctly."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    assert slot.core_width == 3932 - 442 - 442  # 3048
    assert slot.core_height == 5122 - 442 - 442  # 4238


def test_slot_core_area(sample_slot_spec):
    """SlotSpec calculates core area correctly."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    expected = 3048 * 4238
    assert slot.core_area_um2 == expected


def test_slot_to_librelane_areas(sample_slot_spec):
    """SlotSpec converts to LibreLane coordinate format."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    die_area, core_area = slot.to_librelane_areas()

    assert die_area == [0, 0, 3932, 5122]
    assert core_area == [442, 442, 3490, 4680]


def test_slot_io_budget_total(sample_slot_spec):
    """IoBudget calculates total pins correctly."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    assert slot.io_budget.total_signal_pins == 12 + 40 + 2  # input + bidir + analog
```

**Step 2: Run test to verify it fails**

Run: `cd sram_forge && uv run pytest tests/test_models_slot.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement SlotSpec model**

Create `sram_forge/models/slot.py`:

```python
"""Slot specification models."""

from pydantic import BaseModel, Field


class Die(BaseModel):
    """Die dimensions in microns."""

    width: float = Field(gt=0, description="Die width in microns")
    height: float = Field(gt=0, description="Die height in microns")


class Inset(BaseModel):
    """Inset from die edge to core boundary."""

    left: float = Field(ge=0, description="Left inset in microns")
    bottom: float = Field(ge=0, description="Bottom inset in microns")
    right: float = Field(ge=0, description="Right inset in microns")
    top: float = Field(ge=0, description="Top inset in microns")


class Core(BaseModel):
    """Core area definition via insets."""

    inset: Inset = Field(description="Insets from die edges")


class IoBudget(BaseModel):
    """Available IO pads by type."""

    dvdd: int = Field(ge=0, description="VDD power pads")
    dvss: int = Field(ge=0, description="VSS ground pads")
    input: int = Field(ge=0, description="Input-only pads")
    bidir: int = Field(ge=0, description="Bidirectional pads")
    analog: int = Field(ge=0, description="Analog pads")

    @property
    def total_signal_pins(self) -> int:
        """Total signal pins (excluding power)."""
        return self.input + self.bidir + self.analog


class SlotSpec(BaseModel):
    """Complete slot specification."""

    die: Die = Field(description="Die dimensions")
    core: Core = Field(description="Core area definition")
    io_budget: IoBudget = Field(description="Available IO pads")
    reserved_area_um2: float = Field(ge=0, description="Reserved area for logo, ID, etc.")

    @property
    def core_width(self) -> float:
        """Usable core width in microns."""
        return self.die.width - self.core.inset.left - self.core.inset.right

    @property
    def core_height(self) -> float:
        """Usable core height in microns."""
        return self.die.height - self.core.inset.bottom - self.core.inset.top

    @property
    def core_area_um2(self) -> float:
        """Usable core area in square microns."""
        return self.core_width * self.core_height

    def to_librelane_areas(self) -> tuple[list[float], list[float]]:
        """Convert to LibreLane [x_min, y_min, x_max, y_max] format.

        Returns:
            Tuple of (die_area, core_area) in LibreLane format.
        """
        die_area = [0, 0, self.die.width, self.die.height]
        core_area = [
            self.core.inset.left,
            self.core.inset.bottom,
            self.die.width - self.core.inset.right,
            self.die.height - self.core.inset.top,
        ]
        return die_area, core_area
```

**Step 4: Update models/__init__.py**

Update `sram_forge/models/__init__.py`:

```python
"""Data models for sram-forge."""

from sram_forge.models.sram import SramSpec, Port, Timing, Dimensions, Pins
from sram_forge.models.slot import SlotSpec, Die, Core, Inset, IoBudget

__all__ = [
    "SramSpec", "Port", "Timing", "Dimensions", "Pins",
    "SlotSpec", "Die", "Core", "Inset", "IoBudget",
]
```

**Step 5: Run tests to verify they pass**

Run: `cd sram_forge && uv run pytest tests/test_models_slot.py -v`
Expected: All 5 tests PASS

**Step 6: Commit**

```bash
git add sram_forge/
git commit -m "feat: add SlotSpec model with LibreLane conversion"
```

---

### Task 5: Create Chip Configuration Model

**Files:**
- Create: `sram_forge/models/chip.py`
- Create: `sram_forge/tests/test_models_chip.py`
- Modify: `sram_forge/models/__init__.py`

**Step 1: Write failing test for ChipConfig**

Create `sram_forge/tests/test_models_chip.py`:

```python
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
```

**Step 2: Run test to verify it fails**

Run: `cd sram_forge && uv run pytest tests/test_models_chip.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Implement ChipConfig model**

Create `sram_forge/models/chip.py`:

```python
"""Chip configuration models."""

from typing import Literal, Optional, Union
from pydantic import BaseModel, Field


class ChipInfo(BaseModel):
    """Basic chip identification."""

    name: str = Field(description="Design name")
    description: Optional[str] = Field(default=None, description="Chip description")


class Arrangement(BaseModel):
    """SRAM arrangement preferences."""

    prefer: Literal["rows", "columns", "square"] = Field(
        default="rows", description="Preferred arrangement"
    )
    orientation: Literal["N", "E", "S", "W", "mixed"] = Field(
        default="mixed", description="SRAM orientation"
    )


class Memory(BaseModel):
    """SRAM array configuration."""

    macro: str = Field(description="SRAM macro name from srams.yaml")
    count: Union[Literal["auto"], int] = Field(
        default="auto", description="Number of SRAMs: 'auto' or integer"
    )
    arrangement: Arrangement = Field(
        default_factory=Arrangement, description="Arrangement preferences"
    )


class UnifiedBus(BaseModel):
    """Unified bus interface configuration."""

    data_width: int = Field(default=8, gt=0, description="Data bus width")
    registered_output: bool = Field(
        default=False, description="Add output register"
    )
    output_routing: Literal["mux", "tristate", "tristate_registered"] = Field(
        default="mux", description="Output routing strategy"
    )
    write_mask: bool = Field(
        default=False, description="Expose per-bit write mask pins"
    )


class Interface(BaseModel):
    """External interface configuration."""

    scheme: Literal["unified_bus", "banked", "multi_port"] = Field(
        default="unified_bus", description="Interface scheme"
    )
    unified_bus: UnifiedBus = Field(
        default_factory=UnifiedBus, description="Unified bus config"
    )


class IoConfig(BaseModel):
    """IO configuration."""

    base: Literal["template", "minimal", "custom"] = Field(
        default="template", description="IO base configuration"
    )
    pins: dict[str, str] = Field(
        default_factory=dict, description="Pin assignments"
    )


class Features(BaseModel):
    """Optional feature flags."""

    parity: bool = Field(default=False, description="Add parity bits")
    ecc: bool = Field(default=False, description="Add ECC")
    bist: bool = Field(default=False, description="Add built-in self-test")


class Clock(BaseModel):
    """Clock configuration."""

    frequency_mhz: float = Field(
        default=25, gt=0, description="Target clock frequency in MHz"
    )


class Power(BaseModel):
    """Power configuration."""

    core_voltage: Literal[5.0, 3.3, 1.8] = Field(
        default=5.0, description="Core voltage"
    )


class ChipConfig(BaseModel):
    """Complete chip configuration."""

    chip: ChipInfo = Field(description="Chip identification")
    slot: str = Field(description="Target slot name")
    memory: Memory = Field(description="SRAM array configuration")
    interface: Interface = Field(
        default_factory=Interface, description="External interface"
    )
    io: IoConfig = Field(default_factory=IoConfig, description="IO configuration")
    features: Features = Field(
        default_factory=Features, description="Optional features"
    )
    clock: Clock = Field(default_factory=Clock, description="Clock configuration")
    power: Power = Field(default_factory=Power, description="Power configuration")
```

**Step 4: Update models/__init__.py**

Update `sram_forge/models/__init__.py`:

```python
"""Data models for sram-forge."""

from sram_forge.models.sram import SramSpec, Port, Timing, Dimensions, Pins
from sram_forge.models.slot import SlotSpec, Die, Core, Inset, IoBudget
from sram_forge.models.chip import ChipConfig, Memory, Interface, UnifiedBus

__all__ = [
    "SramSpec", "Port", "Timing", "Dimensions", "Pins",
    "SlotSpec", "Die", "Core", "Inset", "IoBudget",
    "ChipConfig", "Memory", "Interface", "UnifiedBus",
]
```

**Step 5: Run tests to verify they pass**

Run: `cd sram_forge && uv run pytest tests/test_models_chip.py -v`
Expected: All 4 tests PASS

**Step 6: Commit**

```bash
git add sram_forge/
git commit -m "feat: add ChipConfig model with interface options"
```

---

## Phase 3: Database Loading

### Task 6: Create YAML Database Loader

**Files:**
- Create: `sram_forge/db/__init__.py`
- Create: `sram_forge/db/loader.py`
- Create: `sram_forge/tests/test_db_loader.py`
- Create: `sram_forge/tests/fixtures/srams.yaml`
- Create: `sram_forge/tests/fixtures/slots.yaml`

**Step 1: Create test fixtures**

Create `sram_forge/tests/fixtures/srams.yaml`:

```yaml
# Test SRAM specifications
srams:
  test_sram_64x8:
    source: pdk
    size: 64
    width: 8
    abits: 6
    dimensions_um:
      width: 431.86
      height: 232.88
    ports:
      - name: port0
        type: rw
        clk_enable: true
        clk_polarity: rising
        pins:
          clk: CLK
          en_n: CEN
          we_n: GWEN
          addr: A[5:0]
          din: D[7:0]
          dout: Q[7:0]
    timing_ns:
      min_cycle: 5.75
      clk_to_q: 4.48
      setup:
        addr: 0.68
      hold:
        addr: 0.54
    files:
      gds: pdk_dir::test.gds
      lef: pdk_dir::test.lef

  test_sram_512x8:
    source: pdk
    size: 512
    width: 8
    abits: 9
    dimensions_um:
      width: 431.86
      height: 484.88
    ports:
      - name: port0
        type: rw
        clk_enable: true
        clk_polarity: rising
        pins:
          clk: CLK
          en_n: CEN
          we_n: GWEN
          wem_n: WEN[7:0]
          addr: A[8:0]
          din: D[7:0]
          dout: Q[7:0]
    timing_ns:
      min_cycle: 6.077
      clk_to_q: 5.008
      setup:
        addr: 0.947
        din: 0.458
        en: 0.406
      hold:
        addr: 0.549
        din: 0.674
    files:
      gds: pdk_dir::sram512.gds
      lef: pdk_dir::sram512.lef
```

Create `sram_forge/tests/fixtures/slots.yaml`:

```yaml
# Test slot specifications
slots:
  1x1:
    die:
      width: 3932
      height: 5122
    core:
      inset:
        left: 442
        bottom: 442
        right: 442
        top: 442
    io_budget:
      dvdd: 8
      dvss: 10
      input: 12
      bidir: 40
      analog: 2
    reserved_area_um2: 50000

  0p5x0p5:
    die:
      width: 1936
      height: 2531
    core:
      inset:
        left: 442
        bottom: 442
        right: 442
        top: 442
    io_budget:
      dvdd: 4
      dvss: 4
      input: 4
      bidir: 38
      analog: 4
    reserved_area_um2: 30000
```

**Step 2: Write failing test for loader**

Create `sram_forge/tests/test_db_loader.py`:

```python
"""Tests for database loader."""

import pytest
from pathlib import Path
from sram_forge.db.loader import load_srams, load_slots, load_chip_config
from sram_forge.models import SramSpec, SlotSpec, ChipConfig


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
```

**Step 3: Run test to verify it fails**

Run: `cd sram_forge && uv run pytest tests/test_db_loader.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 4: Create db module**

```bash
mkdir -p sram_forge/db
```

Create `sram_forge/db/__init__.py`:

```python
"""Database loading utilities."""

from sram_forge.db.loader import load_srams, load_slots, load_chip_config

__all__ = ["load_srams", "load_slots", "load_chip_config"]
```

**Step 5: Implement loader**

Create `sram_forge/db/loader.py`:

```python
"""YAML database loader."""

from pathlib import Path
from typing import Union
import yaml

from sram_forge.models import SramSpec, SlotSpec, ChipConfig


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
```

**Step 6: Run tests to verify they pass**

Run: `cd sram_forge && uv run pytest tests/test_db_loader.py -v`
Expected: All 4 tests PASS

**Step 7: Commit**

```bash
git add sram_forge/
git commit -m "feat: add YAML database loader for srams and slots"
```

---

## Phase 4: Calculation Engine

### Task 7: Create Fit Calculator

**Files:**
- Create: `sram_forge/calc/__init__.py`
- Create: `sram_forge/calc/fit.py`
- Create: `sram_forge/tests/test_calc_fit.py`

**Step 1: Write failing test**

Create `sram_forge/tests/test_calc_fit.py`:

```python
"""Tests for SRAM fit calculator."""

import pytest
from sram_forge.models import SramSpec, SlotSpec
from sram_forge.calc.fit import calculate_fit, FitResult


@pytest.fixture
def sram_512x8(sample_sram_spec):
    """512x8 SRAM for testing."""
    return SramSpec.model_validate(sample_sram_spec)


@pytest.fixture
def slot_1x1(sample_slot_spec):
    """1x1 slot for testing."""
    return SlotSpec.model_validate(sample_slot_spec)


def test_calculate_fit_basic(sram_512x8, slot_1x1):
    """Calculate how many SRAMs fit in slot."""
    result = calculate_fit(slot_1x1, sram_512x8)

    assert isinstance(result, FitResult)
    assert result.count > 0
    assert result.cols > 0
    assert result.rows > 0
    assert result.count == result.cols * result.rows


def test_calculate_fit_dimensions(sram_512x8, slot_1x1):
    """Fit calculation respects physical dimensions."""
    result = calculate_fit(slot_1x1, sram_512x8)

    # With halo: 431.86 + 20 = 451.86 width, 484.88 + 20 = 504.88 height
    # Core: 3048 x 4238
    # Expected: floor(3048/451.86) = 6 cols, floor(4238/504.88) = 8 rows
    # But need to account for reserved area
    assert result.cols >= 1
    assert result.rows >= 1


def test_calculate_fit_total_capacity(sram_512x8, slot_1x1):
    """Fit result includes total capacity."""
    result = calculate_fit(slot_1x1, sram_512x8)

    expected_words = result.count * sram_512x8.size
    assert result.total_words == expected_words
    assert result.total_bits == expected_words * sram_512x8.width


def test_calculate_fit_address_bits(sram_512x8, slot_1x1):
    """Fit result calculates address bits needed."""
    result = calculate_fit(slot_1x1, sram_512x8)

    import math
    expected_abits = math.ceil(math.log2(result.total_words))
    assert result.address_bits == expected_abits


def test_calculate_fit_with_halo():
    """Halo spacing is applied correctly."""
    # Small slot that fits exactly 1 SRAM without halo
    from sram_forge.models.slot import SlotSpec
    from sram_forge.models.sram import SramSpec

    sram = SramSpec.model_validate({
        "source": "pdk",
        "size": 64,
        "width": 8,
        "abits": 6,
        "dimensions_um": {"width": 100, "height": 100},
        "ports": [{
            "name": "port0",
            "type": "rw",
            "clk_enable": True,
            "clk_polarity": "rising",
            "pins": {"clk": "CLK"},
        }],
    })

    slot = SlotSpec.model_validate({
        "die": {"width": 200, "height": 200},
        "core": {"inset": {"left": 10, "bottom": 10, "right": 10, "top": 10}},
        "io_budget": {"dvdd": 1, "dvss": 1, "input": 0, "bidir": 10, "analog": 0},
        "reserved_area_um2": 0,
    })

    # Core is 180x180, SRAM is 100x100
    # With 20um halo (10 each side): effective 120x120
    # Should fit 1x1
    result = calculate_fit(slot, sram, halo_um=10)
    assert result.cols == 1
    assert result.rows == 1
```

**Step 2: Run test to verify it fails**

Run: `cd sram_forge && uv run pytest tests/test_calc_fit.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create calc module**

```bash
mkdir -p sram_forge/calc
```

Create `sram_forge/calc/__init__.py`:

```python
"""Calculation utilities for sram-forge."""

from sram_forge.calc.fit import calculate_fit, FitResult

__all__ = ["calculate_fit", "FitResult"]
```

**Step 4: Implement fit calculator**

Create `sram_forge/calc/fit.py`:

```python
"""SRAM fit calculator."""

import math
from dataclasses import dataclass

from sram_forge.models import SramSpec, SlotSpec


@dataclass
class FitResult:
    """Result of SRAM fit calculation."""

    cols: int
    rows: int
    count: int
    total_words: int
    total_bits: int
    address_bits: int
    utilization: float

    @property
    def total_bytes(self) -> int:
        """Total capacity in bytes."""
        return self.total_bits // 8


def calculate_fit(
    slot: SlotSpec,
    sram: SramSpec,
    halo_um: float = 10.0,
    reserved_um2: float | None = None,
) -> FitResult:
    """Calculate how many SRAMs fit in a slot.

    Args:
        slot: Target slot specification.
        sram: SRAM macro specification.
        halo_um: Routing halo around each SRAM in microns (each side).
        reserved_um2: Override reserved area. If None, uses slot's value.

    Returns:
        FitResult with placement information.
    """
    if reserved_um2 is None:
        reserved_um2 = slot.reserved_area_um2

    core_w = slot.core_width
    core_h = slot.core_height

    # Effective SRAM size with halo
    sram_w = sram.dimensions_um.width + (2 * halo_um)
    sram_h = sram.dimensions_um.height + (2 * halo_um)

    # Calculate grid
    cols = int(core_w // sram_w)
    rows = int(core_h // sram_h)

    # Ensure at least 1x1 if anything fits
    if cols < 1 or rows < 1:
        cols = max(0, cols)
        rows = max(0, rows)

    # Check if we need to reduce for reserved area
    if cols > 0 and rows > 0:
        used_area = cols * rows * sram_w * sram_h
        available_area = core_w * core_h

        while (available_area - used_area) < reserved_um2 and (cols > 1 or rows > 1):
            # Reduce the larger dimension
            if cols >= rows and cols > 1:
                cols -= 1
            elif rows > 1:
                rows -= 1
            else:
                break
            used_area = cols * rows * sram_w * sram_h

    count = cols * rows
    total_words = count * sram.size
    total_bits = total_words * sram.width

    # Calculate address bits needed
    if total_words > 0:
        address_bits = math.ceil(math.log2(total_words))
    else:
        address_bits = 0

    # Calculate utilization
    if core_w * core_h > 0:
        utilization = (count * sram.dimensions_um.width * sram.dimensions_um.height) / (core_w * core_h)
    else:
        utilization = 0.0

    return FitResult(
        cols=cols,
        rows=rows,
        count=count,
        total_words=total_words,
        total_bits=total_bits,
        address_bits=address_bits,
        utilization=utilization,
    )
```

**Step 5: Run tests to verify they pass**

Run: `cd sram_forge && uv run pytest tests/test_calc_fit.py -v`
Expected: All 5 tests PASS

**Step 6: Commit**

```bash
git add sram_forge/
git commit -m "feat: add SRAM fit calculator"
```

---

## Phase 5: CLI Foundation

### Task 8: Create Main CLI Entry Point

**Files:**
- Create: `sram_forge/cli/__init__.py`
- Create: `sram_forge/cli/main.py`
- Create: `sram_forge/tests/test_cli.py`

**Step 1: Write failing test**

Create `sram_forge/tests/test_cli.py`:

```python
"""Tests for CLI."""

import pytest
from click.testing import CliRunner
from sram_forge.cli.main import main


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


def test_cli_help(runner):
    """CLI shows help."""
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "sram-forge" in result.output.lower() or "usage" in result.output.lower()


def test_cli_version(runner):
    """CLI shows version."""
    result = runner.invoke(main, ["--version"])

    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_list_subcommand(runner):
    """CLI has list subcommand."""
    result = runner.invoke(main, ["list", "--help"])

    assert result.exit_code == 0
    assert "srams" in result.output.lower() or "slots" in result.output.lower()


def test_cli_calc_subcommand(runner):
    """CLI has calc subcommand."""
    result = runner.invoke(main, ["calc", "--help"])

    assert result.exit_code == 0
```

**Step 2: Run test to verify it fails**

Run: `cd sram_forge && uv run pytest tests/test_cli.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 3: Create CLI module**

```bash
mkdir -p sram_forge/cli
```

Create `sram_forge/cli/__init__.py`:

```python
"""CLI for sram-forge."""

from sram_forge.cli.main import main

__all__ = ["main"]
```

**Step 4: Implement main CLI**

Create `sram_forge/cli/main.py`:

```python
"""Main CLI entry point for sram-forge."""

import click

from sram_forge import __version__


@click.group()
@click.version_option(version=__version__, prog_name="sram-forge")
def main():
    """sram-forge: Generate SRAM-based chip designs for GF180MCU."""
    pass


@main.command()
@click.argument("what", type=click.Choice(["srams", "slots"]))
def list(what: str):
    """List available SRAMs or slots."""
    click.echo(f"Listing {what}...")
    # TODO: Implement actual listing


@main.command()
@click.option("--slot", required=True, help="Slot name (e.g., 1x1)")
@click.option("--sram", required=True, help="SRAM macro name")
def calc(slot: str, sram: str):
    """Calculate SRAM capacity for a slot."""
    click.echo(f"Calculating fit for {sram} in slot {slot}...")
    # TODO: Implement actual calculation


@main.command()
@click.argument("config", type=click.Path(exists=True))
def check(config: str):
    """Validate a chip configuration file."""
    click.echo(f"Checking {config}...")
    # TODO: Implement validation


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--only", type=click.Choice(["verilog", "librelane", "testbench", "docs"]))
def gen(config: str, output: str, only: str | None):
    """Generate outputs from chip configuration."""
    click.echo(f"Generating from {config} to {output}...")
    if only:
        click.echo(f"Only generating: {only}")
    # TODO: Implement generation


@main.command()
@click.argument("config", type=click.Path(exists=True))
@click.option("--name", required=True, help="Package name")
@click.option("--output", "-o", default=".", help="Output directory")
def package(config: str, name: str, output: str):
    """Create a complete asset package."""
    click.echo(f"Creating package '{name}' from {config}...")
    # TODO: Implement package generation


if __name__ == "__main__":
    main()
```

**Step 5: Run tests to verify they pass**

Run: `cd sram_forge && uv run pytest tests/test_cli.py -v`
Expected: All 4 tests PASS

**Step 6: Test CLI directly**

Run: `cd sram_forge && uv run sram-forge --help`
Expected: Shows help with all subcommands

**Step 7: Commit**

```bash
git add sram_forge/
git commit -m "feat: add Click CLI with subcommand structure"
```

---

## Remaining Tasks (Summary)

The following tasks follow the same TDD pattern:

### Phase 5 (continued):
- **Task 9:** Implement `sram-forge list` command with actual database loading
- **Task 10:** Implement `sram-forge calc` command with formatted output

### Phase 6: Verilog Generation
- **Task 11:** Create Verilog template engine
- **Task 12:** Implement `sram_array.sv` generation (mux routing)
- **Task 13:** Implement `sram_array.sv` generation (tristate routing)
- **Task 14:** Implement `chip_core.sv` generation
- **Task 15:** Implement `chip_top.sv` generation

### Phase 7: LibreLane Generation
- **Task 16:** Create LibreLane `config.yaml` generator
- **Task 17:** Create `pdn_cfg.tcl` generator
- **Task 18:** Create `chip_top.sdc` generator

### Phase 8: Testbench Generation
- **Task 19:** Create cocotb testbench template
- **Task 20:** Generate test cases based on chip config

### Phase 9: Documentation Generation
- **Task 21:** Create Sphinx documentation structure
- **Task 22:** Generate Wavedrom timing diagrams
- **Task 23:** Generate datasheet RST files

### Phase 10: Package Generation
- **Task 24:** Implement template cloning
- **Task 25:** Implement file population
- **Task 26:** Create README generator

### Phase 11: Integration
- **Task 27:** Add bundled `srams.yaml` with PDK SRAMs
- **Task 28:** Add bundled `slots.yaml` with template slots
- **Task 29:** End-to-end integration test

---

## Execution Notes

- Each task is designed for ~5-15 minutes of focused work
- Run tests after every change
- Commit after every passing task
- If tests fail, fix before proceeding
- Use `uv run` for all Python commands
