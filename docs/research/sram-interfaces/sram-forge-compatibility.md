# sram-forge External SRAM Compatibility Analysis

This document analyzes how sram-forge's current interface model maps to standard external SRAM interfaces, identifying gaps and recommending modifications.

**Related Issue**: GitHub Issue #34

---

## Current sram-forge Interface Model

### Interface Configuration (from `models/chip.py`)

```python
class UnifiedBus(BaseModel):
    data_width: int = Field(default=8, gt=0)
    registered_output: bool = Field(default=False)
    output_routing: Literal["mux", "tristate", "tristate_registered"]
    write_mask: bool = Field(default=False)

class Interface(BaseModel):
    scheme: Literal["unified_bus", "banked", "multi_port"]
    unified_bus: UnifiedBus
```

### Current Signal Model

The current sram-forge generates these external signals:

| Signal | Direction | Description |
|--------|-----------|-------------|
| CLK | Input | System clock |
| CE_n | Input | Chip enable (active-low) |
| WE_n | Input | Write enable (active-low) |
| ADDR[N-1:0] | Input | Address bus |
| DATA[M-1:0] | Bidir | Data bus (configurable width) |
| WMASK[M-1:0] | Input | Optional write mask |

### Slot I/O Budgets

From `db/data/slots.yaml`:

| Slot | Input | Bidir | Total Signal |
|------|-------|-------|--------------|
| 1x1 | 12 | 40 | 52 |
| 0p5x1 | 4 | 44 | 48 |
| 1x0p5 | 4 | 46 | 50 |
| 0p5x0p5 | 4 | 38 | 42 |

---

## Gap Analysis

### What sram-forge Has vs. What External SRAMs Need

| Feature | sram-forge | 8-bit SRAM | 16-bit SRAM | 32-bit SRAM |
|---------|------------|------------|-------------|-------------|
| Chip enable (CE_n) | Yes | Yes (CS#) | Yes (CE1#) | Yes |
| Write enable (WE_n) | Yes | Yes (WE#) | Yes (WE#) | Yes |
| Output enable (OE_n) | **No** | Yes (OE#) | Yes (OE#) | Optional |
| Byte enables (LB_n, UB_n) | **No** | N/A | Yes | Optional |
| Secondary CE (CE2) | **No** | Some | Yes | N/A |
| Address width | Flexible | 15 | 18 | 16-18 |
| Data width | 8,10,12,16 | 8 | 16 | 32 |

### Missing Features

1. **OE_n (Output Enable)**: Standard async SRAMs have this signal. Can be:
   - Tied low for always-on output (common in sync designs)
   - Exposed for async compatibility

2. **Byte enables (LB_n, UB_n)**: Required for 16-bit parts with byte-write capability
   - Current `write_mask` is per-bit, not per-byte
   - Need byte-granularity option

3. **CE2 (Active-high chip enable)**: Some SRAMs use dual enables
   - Usually can tie high for simple designs
   - May want option to expose

---

## Interface Profile Proposal

### Add Interface Profiles to ChipConfig

```python
class ExternalSramProfile(BaseModel):
    """Pre-defined interface profiles for standard external SRAMs."""

    profile: Literal[
        "62256",        # 8-bit, 28-pin, 32KB
        "628128",       # 8-bit, 32-pin, 128KB
        "r1rp0416d",    # 16-bit, 44-pin, 256Kx16
        "as6c8016",     # 16-bit, 44-pin, 512Kx16
        "32bit_min",    # 32-bit minimal (no byte enables)
        "custom",       # User-defined
    ]

    # Override defaults if needed
    has_oe_n: bool = True
    has_byte_enables: bool = False
    has_ce2: bool = False
```

### Profile Definitions

#### 62256 Profile (8-bit standard)
```yaml
profile_62256:
  data_width: 8
  address_width: 15
  signals:
    - CE_n   # Pin 20 (CS#)
    - OE_n   # Pin 22 (OE#)
    - WE_n   # Pin 27 (WE#)
  total_pins: 26
```

#### R1RP0416D Profile (16-bit RISCBOY)
```yaml
profile_r1rp0416d:
  data_width: 16
  address_width: 18
  signals:
    - CE_n   # CE1# (tie CE2 high)
    - OE_n   # OE#
    - WE_n   # WE#
    - LB_n   # Lower byte enable
    - UB_n   # Upper byte enable
  total_pins: 39
```

#### 32-bit Minimal Profile
```yaml
profile_32bit_min:
  data_width: 32
  address_width: 16  # Limited to fit budget
  signals:
    - CE_n
    - WE_n
  notes: "OE# tied low, no byte enables"
  total_pins: 50
```

---

## Pin Budget Verification

### 1x1 Slot Analysis

| Profile | Address | Data | Control | Total | Spare |
|---------|---------|------|---------|-------|-------|
| 62256 | 15 | 8 | 3 | 26 | 26 |
| R1RP0416D | 18 | 16 | 5 | 39 | 13 |
| 32-bit min | 16 | 32 | 2 | 50 | 2 |

All profiles fit within the 52-pin budget of the 1x1 slot.

### Smaller Slots

| Profile | Pins Needed | 0p5x1 (48) | 1x0p5 (50) | 0p5x0p5 (42) |
|---------|-------------|------------|------------|--------------|
| 62256 | 26 | OK | OK | OK |
| R1RP0416D | 39 | OK | OK | **NO** |
| 32-bit | 50 | **NO** | OK | **NO** |

---

## Recommended Model Changes

### 1. Add OE_n Signal Option

```python
class UnifiedBus(BaseModel):
    # Existing fields...
    has_output_enable: bool = Field(
        default=True,
        description="Expose OE_n signal (tie low if False)"
    )
```

### 2. Add Byte Enable Option

```python
class UnifiedBus(BaseModel):
    # Existing fields...
    byte_enable: bool = Field(
        default=False,
        description="Expose LB_n/UB_n for 16-bit parts"
    )
```

### 3. Add Interface Profile Selection

```python
class ExternalInterface(BaseModel):
    """Configuration for external SRAM compatibility."""

    profile: Literal["62256", "r1rp0416d", "32bit", "custom"] = "custom"
    data_width: int = 8
    address_width: int = 15
    has_output_enable: bool = True
    has_byte_enables: bool = False

    def pin_count(self) -> int:
        """Calculate total pin count."""
        pins = self.address_width + self.data_width + 2  # CE_n, WE_n
        if self.has_output_enable:
            pins += 1
        if self.has_byte_enables:
            pins += 2
        return pins
```

### 4. Update Power Model for Voltage Range

```python
class Power(BaseModel):
    core_voltage: Literal[5.0, 3.3, 1.8] = Field(default=5.0)
    io_voltage: Literal[5.0, 3.3, 2.5, 1.8] = Field(default=5.0)
    notes: str = Field(
        default="",
        description="Voltage compatibility notes"
    )
```

---

## Verilog Template Changes

### Current chip_core.sv Interface

```systemverilog
module chip_core (
    input  logic        CLK,
    input  logic        CE_n,
    input  logic        WE_n,
    input  logic [ADDR_WIDTH-1:0] ADDR,
    inout  wire  [DATA_WIDTH-1:0] DATA
);
```

### Proposed chip_core.sv Interface

```systemverilog
module chip_core #(
    parameter DATA_WIDTH = 8,
    parameter ADDR_WIDTH = 15,
    parameter HAS_OE_N = 1,
    parameter HAS_BYTE_EN = 0
) (
    input  logic        CLK,
    input  logic        CE_n,
    input  logic        WE_n,

    // Optional OE_n
    {% if interface.has_output_enable %}
    input  logic        OE_n,
    {% endif %}

    // Optional byte enables (16-bit only)
    {% if interface.has_byte_enables %}
    input  logic        LB_n,
    input  logic        UB_n,
    {% endif %}

    input  logic [ADDR_WIDTH-1:0] ADDR,
    inout  wire  [DATA_WIDTH-1:0] DATA
);

    // Internal OE handling
    {% if not interface.has_output_enable %}
    wire OE_n = 1'b0;  // Always enabled
    {% endif %}

    // Byte enable to write mask conversion
    {% if interface.has_byte_enables %}
    wire [DATA_WIDTH-1:0] write_mask;
    assign write_mask[7:0]  = {8{~LB_n}};
    assign write_mask[15:8] = {8{~UB_n}};
    {% endif %}

endmodule
```

---

## Compatibility Matrix

### sram-forge vs External SRAM Features

| Feature | Current | With Changes | Notes |
|---------|---------|--------------|-------|
| 8-bit data | Yes | Yes | Works today |
| 16-bit data | Yes | Yes | data_width=16 |
| 32-bit data | **No** | Yes | Need to add |
| CE_n | Yes | Yes | Works today |
| WE_n | Yes | Yes | Works today |
| OE_n | **No** | Yes | Add option |
| LB_n/UB_n | **No** | Yes | Add for 16-bit |
| 5V operation | Yes | Yes | core_voltage=5.0 |
| 3.3V operation | Yes | Yes | core_voltage=3.3 |
| Per-bit mask | Yes | Yes | write_mask=true |
| Per-byte mask | **No** | Yes | byte_enable=true |

### Target Compatibility

| SRAM Part | Current | With Changes |
|-----------|---------|--------------|
| AS6C62256 | Partial | Full |
| IS62C256 | Partial | Full |
| R1RP0416D | **No** | Full |
| AS6C8016 | **No** | Full |
| 2x R1RP0416D (32-bit) | **No** | Limited* |

*32-bit: No byte enables within pin budget

---

## Implementation Priority

### High Priority (RISCBOY Compatibility)

1. **Add OE_n signal option** - Required for async SRAM compatibility
2. **Add byte enables (LB_n/UB_n)** - Required for R1RP0416D
3. **Support data_width=16** - Verify existing support works

### Medium Priority (Retro Computing)

4. **Add 62256 profile** - Pre-configured for 8-bit retro
5. **Document pin mappings** - Show how sram-forge pins map to DIP packages
6. **Test 5V and 3.3V generation** - Verify voltage settings work

### Lower Priority (Advanced)

7. **Add 32-bit support** - data_width=32
8. **Document pin budget calculator** - Show feasibility for each slot
9. **Add CE2 support** - For parts with dual chip enable

---

## Example Configurations

### 8-bit Retro (62256-compatible)

```yaml
chip:
  name: retro_sram_32k
  description: "62256-compatible 32KB SRAM"

interface:
  scheme: unified_bus
  external_profile: 62256
  unified_bus:
    data_width: 8
    has_output_enable: true

power:
  core_voltage: 5.0
```

### 16-bit RISCBOY (R1RP0416D-compatible)

```yaml
chip:
  name: riscboy_sram
  description: "R1RP0416D-compatible 512KB SRAM"

interface:
  scheme: unified_bus
  external_profile: r1rp0416d
  unified_bus:
    data_width: 16
    has_output_enable: true
    has_byte_enables: true

power:
  core_voltage: 5.0
```

### 32-bit High-Performance

```yaml
chip:
  name: highperf_sram
  description: "256KB x 32-bit SRAM"

interface:
  scheme: unified_bus
  external_profile: 32bit_min
  unified_bus:
    data_width: 32
    has_output_enable: false  # Tied low to save pins

power:
  core_voltage: 5.0
```

---

## Conclusion

sram-forge's current architecture is well-suited for external SRAM compatibility with minor additions:

1. **OE_n signal**: Add as optional, default true for async compatibility
2. **Byte enables**: Add for 16-bit parts (LB_n, UB_n)
3. **32-bit data**: Extend data_width support
4. **Interface profiles**: Pre-defined configurations for common parts

The modular design with Pydantic models and Jinja2 templates makes these changes straightforward. All target interfaces (8-bit, 16-bit, 32-bit) fit within the 1x1 slot's 52-pin I/O budget.

---

## References

- [Interface Comparison Document](./interface-comparison.md)
- [Classic SRAM Families](./classic-sram-families.md)
- [Current 5V SRAMs](./current-5v-srams.md)
- [Current 3.3V SRAMs](./current-3v3-srams.md)
- [sram-forge models/chip.py](../../sram_forge/models/chip.py)
- [sram-forge db/data/slots.yaml](../../sram_forge/db/data/slots.yaml)

---

*Document created: 2025-12-12 for GitHub Issue #34*
