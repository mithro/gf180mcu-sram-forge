# SRAM Interface Comparison for sram-forge

This document provides a normalized comparison of SRAM interfaces across 8-bit, 16-bit, and 32-bit widths, with analysis of compatibility with sram-forge's target interface model.

**Related Issue**: GitHub Issue #34

---

## Executive Summary

| Data Width | De-facto Standard | Package | Key Parts | sram-forge Feasibility |
|------------|-------------------|---------|-----------|------------------------|
| **8-bit** | 62256 (28-pin) | DIP | AS6C62256, IS62C256 | Excellent (26 pins) |
| **16-bit** | R1RP0416D (44-pin) | TSOP | R1RP0416D, AS6C8016 | Good (35 pins) |
| **32-bit** | 2x16-bit parallel | TSOP/BGA | 2x R1RP0416D | Feasible (48-52 pins) |

**Conclusion**: All three widths are feasible within the 1x1 slot's 52-pin I/O budget.

---

## Interface Signal Standards

### Control Signal Conventions

All standard async SRAMs use **active-low** control signals:

| Signal | Standard Name | Active Level | Function |
|--------|---------------|--------------|----------|
| Chip Enable | CS#, CE#, CE1# | LOW | Enables chip operation |
| Output Enable | OE# | LOW | Enables data output drivers |
| Write Enable | WE# | LOW | Latches write data on rising edge |
| Lower Byte | LB# | LOW | Enables D[7:0] (16-bit parts) |
| Upper Byte | UB# | LOW | Enables D[15:8] (16-bit parts) |

**Exception**: Some parts have a secondary active-high chip enable (CE2) for memory decoding flexibility.

### Timing Model

```
Asynchronous SRAM Timing (Read Cycle):

         _________________
Address  X___VALID_ADDR___X
         _______
CS#      _______|       |______
         _________
OE#      _________|     |______
                  |<-tAA->|
                  |<-tOE-->|
Data Out ---------X__VALID__X----

Key Parameters:
- tAA: Address access time (10-55ns typical)
- tCE: Chip enable access time
- tOE: Output enable to valid data
- tRC: Read cycle time = tAA (asynchronous SRAM)
```

---

## 8-Bit Interface (62256 Standard)

### Pin Assignment

The 62256 28-pin DIP is the de-facto standard for 8-bit async SRAM:

| Pin | Signal | Direction | Description |
|-----|--------|-----------|-------------|
| 1 | A14 | Input | Address bit 14 |
| 2 | A12 | Input | Address bit 12 |
| 3-10 | A7-A0 | Input | Address bits 7-0 |
| 11-15 | D0-D4 | Bidir | Data bits 0-4 |
| 16-19 | D5-D7 | Bidir | Data bits 5-7 |
| 20 | CS# | Input | Chip select (active-low) |
| 21 | A10 | Input | Address bit 10 |
| 22 | OE# | Input | Output enable (active-low) |
| 23 | A11 | Input | Address bit 11 |
| 24-25 | A9-A8 | Input | Address bits 9-8 |
| 26 | A13 | Input | Address bit 13 |
| 27 | WE# | Input | Write enable (active-low) |
| 14 | GND | Power | Ground |
| 28 | VCC | Power | +5V supply |

### Signal Summary

| Category | Signals | Count |
|----------|---------|-------|
| Address | A[14:0] | 15 |
| Data | D[7:0] | 8 |
| Control | CS#, OE#, WE# | 3 |
| **Total I/O** | | **26** |

### sram-forge Mapping (8-bit)

| sram-forge Signal | 62256 Signal | Notes |
|-------------------|--------------|-------|
| CLK | - | Not used (async SRAM) |
| CE_n | CS# | Active-low chip enable |
| WE_n | WE# | Active-low write enable |
| OE_n | OE# | Optional for sync interface |
| ADDR[14:0] | A[14:0] | 15-bit address (32KB) |
| DATA[7:0] | D[7:0] | Bidirectional data |

**Pin Budget (1x1 slot, 52 pins):**
- Used: 26 pins
- Spare: 26 pins

---

## 16-Bit Interface (R1RP0416D Standard)

### Pin Assignment (44-pin TSOP II)

| Category | Signals | Pins |
|----------|---------|------|
| Address | A[17:0] | 18 |
| Data | DQ[15:0] | 16 |
| Chip Enable | CE1#, CE2 | 2 |
| Output Enable | OE# | 1 |
| Write Enable | WE# | 1 |
| Byte Enable | LB#, UB# | 2 |
| Power | VCC, VSS | 4 |
| **Total** | | **44** |

### Control Signals

| Signal | Pin | Active | Function |
|--------|-----|--------|----------|
| CE1# | - | LOW | Chip enable 1 |
| CE2 | - | HIGH | Chip enable 2 |
| OE# | - | LOW | Output enable |
| WE# | - | LOW | Write enable |
| LB# | - | LOW | Lower byte enable (D7-D0) |
| UB# | - | LOW | Upper byte enable (D15-D8) |

**Chip Selection Logic:**
- Chip is selected when: CE1# = LOW AND CE2 = HIGH
- For simple designs: Tie CE2 high, use CE1# as primary enable

### Signal Summary (I/O only, excluding power)

| Category | Signals | Count |
|----------|---------|-------|
| Address | A[17:0] | 18 |
| Data | DQ[15:0] | 16 |
| Control | CE1#, CE2, OE#, WE#, LB#, UB# | 6 |
| **Total I/O** | | **40** |

### sram-forge Mapping (16-bit)

| sram-forge Signal | R1RP0416D Signal | Notes |
|-------------------|------------------|-------|
| CLK | - | Not used (async SRAM) |
| CE_n | CE1# | Active-low chip enable |
| - | CE2 | Tie HIGH |
| WE_n | WE# | Active-low write enable |
| OE_n | OE# | Optional for sync interface |
| LB_n | LB# | Lower byte enable |
| UB_n | UB# | Upper byte enable |
| ADDR[17:0] | A[17:0] | 18-bit address (256K words) |
| DATA[15:0] | DQ[15:0] | Bidirectional data |

**Pin Budget (1x1 slot, 52 pins):**

Minimum configuration (no byte enables, no OE#):
- Address: 18 pins
- Data: 16 pins
- Control: CE_n + WE_n = 2 pins
- **Total: 36 pins** (16 spare)

Full configuration:
- Address: 18 pins
- Data: 16 pins
- Control: CE_n + WE_n + OE_n + LB_n + UB_n = 5 pins
- **Total: 39 pins** (13 spare)

---

## 32-Bit Interface

### Implementation Options

There are no standard 32-bit SRAM chips in common use. Options include:

1. **Two 16-bit SRAMs in parallel** (recommended)
2. **Multi-chip modules** (specialty/military)
3. **BGA parts** (AS7C325632) - 3.3V only

### Parallel 16-bit Configuration

Using 2x R1RP0416D (256Kx16) for 256Kx32:

| Signal | Chip A | Chip B | Total |
|--------|--------|--------|-------|
| A[17:0] | Shared | Shared | 18 |
| D[15:0] | DQ[15:0]_A | - | 16 |
| D[31:16] | - | DQ[31:16]_B | 16 |
| CE1# | Shared | Shared | 1 |
| OE# | Shared | Shared | 1 |
| WE# | Shared | Shared | 1 |
| LB#/UB# | See below | See below | 0-4 |

### Signal Summary (32-bit parallel)

| Category | Signals | Count |
|----------|---------|-------|
| Address | A[17:0] | 18 |
| Data | D[31:0] | 32 |
| Control | CE#, OE#, WE# | 3 |
| **Minimum Total** | | **53** |

**With byte enables:**
- Add LB0#, UB0#, LB1#, UB1# for per-byte masking
- Total: 57 pins (exceeds 52-pin budget)

### sram-forge Mapping (32-bit)

**Minimum configuration (no byte enables):**

| sram-forge Signal | Physical Signal | Count |
|-------------------|-----------------|-------|
| ADDR[17:0] | A[17:0] (shared) | 18 |
| DATA[31:0] | D[31:0] (2 chips) | 32 |
| CE_n | CE1# (both chips) | 1 |
| WE_n | WE# (both chips) | 1 |
| **Total** | | **52** |

**Pin Budget (1x1 slot, 52 pins):**
- Minimum: 52 pins (0 spare) - **TIGHT FIT**
- With OE#: 53 pins - **EXCEEDS BUDGET**
- With byte enables: 57 pins - **NOT FEASIBLE**

### 32-bit Recommendations

1. **Omit OE#**: Tie OE# low on both chips, use WE# timing only
2. **No byte enables**: Full 32-bit writes only (no byte masking)
3. **Alternative**: Use smaller address space (reduce A[17:0])

**With A[15:0] (64K words = 256KB):**
- Address: 16 pins
- Data: 32 pins
- Control: 2 pins
- **Total: 50 pins** (2 spare)

---

## Interface Comparison Matrix

### Control Signals by Width

| Signal | 8-bit | 16-bit | 32-bit | Notes |
|--------|-------|--------|--------|-------|
| CE_n | Required | Required | Required | Always needed |
| OE_n | Standard | Optional | Omit | Can tie low for sync |
| WE_n | Required | Required | Required | Always needed |
| LB_n | N/A | Optional | Omit* | For byte masking |
| UB_n | N/A | Optional | Omit* | For byte masking |

*Byte enables not feasible in 32-bit within 52-pin budget

### Pin Budget Summary

| Width | Address | Data | Control | Total | Spare (52) |
|-------|---------|------|---------|-------|------------|
| 8-bit | 15 | 8 | 3 | 26 | 26 |
| 16-bit (min) | 18 | 16 | 2 | 36 | 16 |
| 16-bit (full) | 18 | 16 | 5 | 39 | 13 |
| 32-bit (min) | 18 | 32 | 2 | 52 | 0 |
| 32-bit (A15:0) | 16 | 32 | 2 | 50 | 2 |

### Voltage Compatibility

| Part | Voltage | 5V OK? | 3.3V OK? | Recommended |
|------|---------|--------|----------|-------------|
| AS6C62256 | 2.7-5.5V | Yes | Yes | Best for mixed |
| IS62C256 | 4.5-5.5V | Yes | No | 5V only |
| R1RP0416D | 4.5-5.5V | Yes | No | 5V only |
| AS6C8016 | 2.7-5.5V | Yes | Yes | Best for mixed |
| IS61WV25616 | 2.5-3.6V | No | Yes | 3.3V only |

---

## sram-forge Interface Model

### Current Interface Definition

From sram-forge exploration, the unified bus interface supports:

```
Interface Signals:
- CLK            : Clock (for synchronous wrapper)
- CE_n           : Chip enable (active-low)
- WE_n           : Write enable (active-low)
- ADDR[N-1:0]    : Address bus
- DATA[M-1:0]    : Bidirectional data bus
- WMASK[M-1:0]   : Optional write mask
```

### Mapping to External SRAM

| sram-forge | 8-bit SRAM | 16-bit SRAM | 32-bit SRAM |
|------------|------------|-------------|-------------|
| CLK | - | - | - |
| CE_n | CS# | CE1# | CE# (shared) |
| WE_n | WE# | WE# | WE# (shared) |
| OE_n | OE# | OE# | OE# (tie low) |
| ADDR | A[14:0] | A[17:0] | A[17:0] |
| DATA | D[7:0] | DQ[15:0] | D[31:0] |
| WMASK | - | LB#/UB# | - |

### Interface Profile Recommendations

Define interface "profiles" for common configurations:

```yaml
interface_profiles:
  # 8-bit retro computing
  profile_62256:
    data_width: 8
    addr_width: 15
    control_signals: [CE_n, OE_n, WE_n]
    target_parts: [AS6C62256, IS62C256, HM62256]

  # 16-bit RISCBOY
  profile_r1rp0416d:
    data_width: 16
    addr_width: 18
    control_signals: [CE_n, OE_n, WE_n, LB_n, UB_n]
    target_parts: [R1RP0416D, AS6C8016, IS61WV25616]

  # 32-bit high-performance
  profile_32bit:
    data_width: 32
    addr_width: 16  # Limited by pin budget
    control_signals: [CE_n, WE_n]
    notes: "No byte enables, OE# tied low"
```

---

## Recommendations for sram-forge

### Primary Target: 62256-Compatible (8-bit)

**Rationale:**
- Most widely used in retro computing
- Excellent pin budget margin (26 of 52 pins)
- Drop-in compatible with decades of systems
- Modern parts available (AS6C62256)

**Implementation:**
- 15-bit address, 8-bit data
- CE_n, OE_n, WE_n control signals
- Synchronous wrapper with async timing parameters

### Secondary Target: R1RP0416D-Compatible (16-bit)

**Rationale:**
- RISCBOY compatibility (key use case)
- Good pin budget (36-39 of 52 pins)
- High-speed (10-12ns) applications
- Byte-write support via LB#/UB#

**Implementation:**
- 18-bit address, 16-bit data
- Full control signals including byte enables
- Consider timing wrapper for 10-12ns parts

### Tertiary Target: 32-bit

**Rationale:**
- DSP and high-bandwidth applications
- Feasible but tight (52 pins exactly)
- No byte masking within budget

**Implementation:**
- 16-18 bit address (16 recommended)
- 32-bit data
- Minimal control (CE_n, WE_n only)
- Document limitations clearly

---

## References

- [Alliance Memory AS6C62256 Datasheet](https://www.alliancememory.com/datasheets/as6c62256/)
- [Renesas R1RP0416D Datasheet](https://www.renesas.com/en/document/dst/r1rp0416d-series-datasheet)
- [ISSI IS62C256 Datasheet](https://www.issi.com/WW/pdf/62-65C256AL.pdf)
- [Classic SRAM Families Research](./classic-sram-families.md)
- [Current 5V SRAMs Survey](./current-5v-srams.md)
- [Current 3.3V SRAMs Survey](./current-3v3-srams.md)

---

*Document created: 2025-12-12 for GitHub Issue #34*
