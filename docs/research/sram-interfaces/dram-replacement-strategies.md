# DRAM Replacement Strategies for Retro Computing

This document surveys DRAM families commonly used in Z80/6502-era systems and documents
strategies for replacing them with SRAM, including commercial solutions and DIY approaches.

## Table of Contents

1. [Overview](#overview)
2. [DRAM Families](#dram-families)
   - [4116 (16K x 1)](#4116-16k-x-1)
   - [4164 (64K x 1)](#4164-64k-x-1)
   - [41256 (256K x 1)](#41256-256k-x-1)
   - [44256 (256K x 4)](#44256-256k-x-4)
3. [Common DRAM Failure Modes](#common-dram-failure-modes)
4. [Why Replace DRAM with SRAM](#why-replace-dram-with-sram)
5. [SRAM Replacement Strategies](#sram-replacement-strategies)
6. [Commercial SRAM Replacement Products](#commercial-sram-replacement-products)
7. [DIY Replacement Approaches](#diy-replacement-approaches)
8. [Trade-offs and Considerations](#trade-offs-and-considerations)

---

## Overview

Early microcomputers of the late 1970s and 1980s relied heavily on Dynamic RAM (DRAM) for
main memory due to its higher density and lower cost per bit compared to Static RAM (SRAM).
However, DRAM has inherent complexities that make it problematic for long-term reliability:

- **Refresh requirements**: DRAM cells must be constantly refreshed to retain data
- **Complex addressing**: Multiplexed row/column addresses require RAS/CAS timing
- **Multi-voltage requirements**: Early DRAMs (especially 4116) needed multiple supply voltages
- **Age-related degradation**: The tiny capacitors that store bits degrade over decades

As these vintage systems age, DRAM failures become increasingly common. Modern SRAM offers
a compelling replacement option due to its simpler interface, single-voltage operation,
no refresh requirements, and excellent reliability.

---

## DRAM Families

### 4116 (16K x 1)

The 4116 was one of the most widely-used memory chips of the late 1970s, providing storage
for computers such as the Apple II, TRS-80, ZX Spectrum, Commodore PET, IBM PC, and Xerox
Alto, as well as arcade games like Defender and Missile Command.

#### Specifications

| Parameter | Value |
|-----------|-------|
| Organisation | 16,384 x 1 bit |
| Package | 16-pin DIP |
| Access Time | 150-250ns (varies by speed grade) |
| Refresh | 128 rows / 2ms |
| Address Lines | 7-bit row, 7-bit column (A0-A6 multiplexed) |

#### Pin Configuration

```
       +---+--+---+
   VBB |1  +--+ 16| VSS (GND)
   DIN |2       15| CAS*
    WE*|3  MK   14| DOUT
  RAS* |4  4116 13| A6
    A0 |5       12| A3
    A2 |6       11| A4
    A1 |7       10| A5
   VDD |8        9| VCC
       +----------+
```

#### Power Requirements (The Notorious Triple-Voltage Problem)

| Pin | Voltage | Function |
|-----|---------|----------|
| Pin 1 (VBB) | -5V | Substrate bias |
| Pin 8 (VDD) | +12V | Main power for internal circuitry |
| Pin 9 (VCC) | +5V | TTL-compatible I/O levels |
| Pin 16 (VSS) | GND | Ground reference |

The triple-voltage requirement is the primary reason 4116 chips are notoriously unreliable.
Almost all the internal circuitry runs on 12 volts. The 5-volt supply is used only to provide
a standard TTL voltage level for the data out pin. The -5 volts is a substrate bias connected
to the underlying silicon die to improve transistor characteristics.

**Critical Warning**: If a 4116 DRAM is powered with +12V and/or +5V present, but with
the -5V missing or very low, this can cause damage to previously working 4116 DRAM chips.
This makes the chips prone to destroy themselves if voltages fall outside tolerance ranges.

#### Systems Using 4116

| System | Configuration | Notes |
|--------|---------------|-------|
| ZX Spectrum 16K/48K | 8 chips (lower 16K) | Issue 2-6A boards |
| Apple II/II+ | 24 chips (48K) | 3 banks of 8 |
| TRS-80 Model I | 8-24 chips (16K-48K) | 3 banks possible |
| TRS-80 Color Computer | 8 chips (16K models) | Early CoCo only |
| Commodore PET | 8 chips | Lower memory |
| IBM PC 5150 | 36 chips (64K) | 4 banks |
| Atari 400/800 | 24 chips (48K) | 3 banks |
| Williams Arcade Games | 8-16 chips | Robotron, Defender, Joust, etc. |

#### References

- [Reverse-engineering the classic MK4116 16-kilobit DRAM chip](http://www.righto.com/2020/11/reverse-engineering-classic-mk4116-16.html) - Ken Shirriff's detailed die analysis
- [Mostek MK4116 Datasheet (PDF)](https://console5.com/techwiki/images/8/85/MK4116.pdf)
- [4116 Examples and Variants](https://minuszerodegrees.net/memory/4116.htm)

---

### 4164 (64K x 1)

The 4164 represented a major advancement over the 4116: quadruple the capacity with only
a single +5V power supply. This made it far more reliable and easier to use in system designs.

#### Specifications

| Parameter | Value |
|-----------|-------|
| Organisation | 65,536 x 1 bit |
| Package | 16-pin DIP |
| Access Time | 100-200ns (varies by speed grade) |
| Refresh | 256 rows / 4ms |
| Address Lines | 8-bit row, 8-bit column (A0-A7 multiplexed) |
| Power | +5V only |

#### Pin Configuration

```
       +---+--+---+
   N/C |1  +--+ 16| VSS (GND)
     D |2       15| CAS*
   WE* |3  4164 14| Q
  RAS* |4       13| A6
    A0 |5       12| A3
    A2 |6       11| A4
    A1 |7       10| A5
   VCC |8        9| A7
       +----------+
```

#### Key Differences from 4116

| Pin | 4116 | 4164 |
|-----|------|------|
| 1 | -5V (VEE) | N/C (No Connection) |
| 8 | +12V (VDD) | +5V (VCC) |
| 9 | +5V (VCC) | A7 (Address Line) |

The addition of A7 on pin 9 enables addressing 256 rows instead of 128, providing 4x the
memory capacity. The elimination of the -5V and +12V supplies dramatically improved reliability.

#### Systems Using 4164

| System | Configuration | Notes |
|--------|---------------|-------|
| Commodore 64 | 8 chips (64K) | Breadbin and early C64C |
| Apple IIe | 8 chips (64K) | Main board |
| Apple IIc | 16 chips (128K) | Main memory |
| Atari 800XL | 8 chips (64K) | Can also use 4264 |
| Amstrad CPC | 8 chips (64K) | CPC 464, 664, 6128 |
| ZX Spectrum 48K | 8 chips (upper 32K) | Upper memory bank |
| IBM PC 5150/5160 | 36 chips (256K) | Later configurations |
| BBC Micro Model B | 8 chips (32K) | Main RAM |

#### References

- [4164 Examples and Variants](https://www.minuszerodegrees.net/memory/4164.htm)
- [4164 Dynamic RAM with Arduino](https://ezcontents.org/4164-dynamic-ram-arduino) - Testing tutorial
- [C64 Wiki - RAM](https://www.c64-wiki.com/wiki/RAM) - Commodore 64 memory details

---

### 41256 (256K x 1)

The 41256 continued the evolution of single-bit-wide DRAM, offering 256K capacity with
a 9-bit multiplexed address bus while maintaining pin-compatibility with the 4164 form factor.

#### Specifications

| Parameter | Value |
|-----------|-------|
| Organisation | 262,144 x 1 bit |
| Package | 16-pin DIP |
| Access Time | 80-150ns |
| Refresh | 256 rows / 4ms |
| Address Lines | 9-bit row, 9-bit column (A0-A8 multiplexed) |
| Power | +5V only |

#### Pin Configuration

```
       +---+--+---+
    A8 |1  +--+ 16| VSS (GND)
     D |2       15| CAS*
   WE* |3 41256 14| Q
  RAS* |4       13| A6
    A0 |5       12| A3
    A2 |6       11| A4
    A1 |7       10| A5
   VCC |8        9| A7
       +----------+
```

**Note**: Pin 1 is now A8 (additional address line), unlike the N/C on 4164.

#### 41256 vs 4164 Compatibility

A 41256 can often be used in place of a 4164 by connecting pins 1 and 16 together with
a short wire. This ties A8 to ground, making the chip appear as a 64K device (wasting the
upper 192K of capacity).

#### Systems Using 41256

| System | Configuration | Notes |
|--------|---------------|-------|
| IBM PC AT | 36 chips (1MB) | Main memory |
| IBM 512KB/2MB Expansion | 72 chips | Memory expansion card |
| Commodore 128 | 8 chips (256K) | Some configurations |
| Amiga 1000 | 8 chips | Expansion memory |
| Apple Macintosh 128K | 16 chips | Main memory |

#### References

- [41256 Examples and Variants](https://minuszerodegrees.net/memory/41256.htm)
- [IBM 5170 Memory Cards](https://minuszerodegrees.net/5170/cards/5170_cards.htm)
- [IBM 5150 RAM Refresh](https://minuszerodegrees.net/5150/ram_refresh/IBM%205150%20motherboard%20-%20RAM%20refresh.htm)

---

### 44256 (256K x 4)

The 44256 (also designated as various part numbers like 514256, 424256, etc.) is a
"nibble-wide" DRAM providing 4 bits of data per access, reducing the number of chips
needed for byte-wide memory from 8 to 2.

#### Specifications

| Parameter | Value |
|-----------|-------|
| Organisation | 262,144 x 4 bits (1 Mbit total) |
| Package | 20-pin DIP |
| Access Time | 70-100ns |
| Refresh | 256 or 512 rows / 4ms or 8ms |
| Address Lines | 9-bit row, 9-bit column (A0-A8 multiplexed) |
| Power | +5V only |

#### Manufacturer Part Numbers

The same basic chip was manufactured by many companies with different part numbers:

| Manufacturer | Part Number |
|--------------|-------------|
| Toshiba | TC514256, TC514258 |
| Sharp | LH64256, LH64258 |
| Oki | MSM514256, MSM514258 |
| Hitachi | HM514256, HM514258 |
| NEC | uPD424256, uPD424258 |
| Texas Instruments | TMS44C256 |
| Fujitsu | MB81C4256 |
| Panasonic | MN414256 |
| Siemens | HYB514256 |
| Samsung | KM44C256 |
| Micron | MT4C4256 |

#### Systems Using 44256 (256K x 4)

| System | Configuration | Notes |
|--------|---------------|-------|
| Amiga 500 | 4 chips (512K) | Rev 5/6 boards |
| Amiga 500+ | 2 chips (1MB Chip RAM) | A500+ |
| Amiga 2000 | 4 chips | Chip RAM |
| Atari ST | 4 chips | Later models |
| Commodore REU 1750 | 4 chips | RAM Expansion Unit |
| Mac Classic | 4 chips | System RAM |
| PC VGA Cards | 2-8 chips | Video RAM |

#### References

- [256Kx4 DRAM in Commodore/Amiga Equipment](https://www.amiga-stuff.com/hardware/256kx4-dram.html)
- [MT4C4256 Datasheet](https://datasheet4u.com/datasheets/Micron-Technology/MT4C4256/504958)

---

## Common DRAM Failure Modes

Understanding why DRAM fails is essential for diagnosing problems and deciding on repair strategies.

### 1. Capacitor Degradation

DRAM stores data as charge on tiny capacitors. Over decades, these capacitors can:
- Lose capacitance (reducing data retention time)
- Develop leakage currents (losing charge faster)
- Experience dielectric breakdown

The result: data corruption, especially in bits that need to hold their charge longest
between refresh cycles.

### 2. Voltage-Related Damage (4116 Specific)

The 4116's triple-voltage design is particularly vulnerable:
- Missing -5V can damage chips even with +12V and +5V present
- Voltage sequencing issues during power-up/down
- Power supply ripple causing voltage excursions outside spec
- Failed voltage regulators in aging systems

### 3. Heat-Related Failures

DRAM is sensitive to temperature:
- Higher temperatures increase leakage current
- Increased leakage requires more frequent refresh
- More refresh generates more heat (thermal runaway)
- Hot-running systems (like ZX Spectrum) accelerate aging

**Diagnostic Tip**: A RAM chip running significantly hotter than its neighbours may
have an internal short. This "hot finger test" can identify failed chips before
more complex diagnosis.

### 4. Mechanical Stress

- Thermal cycling (expansion/contraction) can crack bond wires
- Socket corrosion causes intermittent connections
- PCB trace cracks from flexing
- Oxidised pins from decades of storage

### 5. Manufacturing Defects Emerging with Age

Early DRAM manufacturing had higher defect rates than modern semiconductors.
Marginal cells that worked initially may fail as parameters drift with age.

### Symptoms of DRAM Failure

| Symptom | Likely Cause |
|---------|--------------|
| No boot / black screen | Complete RAM failure in critical region |
| Garbage on screen | Video RAM corruption |
| Random crashes | Intermittent bit errors |
| Specific address failures | Single chip or cell failure |
| Works when cold, fails warm | Marginal timing or leakage |
| Consistent bit pattern errors | Single chip failed in specific bit position |

---

## Why Replace DRAM with SRAM

Retro computing hobbyists increasingly replace DRAM with SRAM for several compelling reasons:

### Advantages of SRAM Replacement

#### 1. Simplified Power Requirements

- **SRAM**: Single +5V supply (or +3.3V for modern chips)
- **4116 DRAM**: Requires +12V, +5V, and -5V
- Eliminates the failure-prone multi-voltage circuitry
- Can potentially simplify or remove portions of power supply

#### 2. No Refresh Required

SRAM maintains data as long as power is applied without any refresh cycles:
- Eliminates refresh timing circuitry complexity
- Reduces bus contention (DRAM refresh "steals" bus cycles)
- Better compatibility with non-standard CPU configurations
- Slightly improved effective performance (no refresh overhead)

#### 3. Superior Reliability

- No tiny capacitors to degrade
- Simpler internal structure
- Longer operational life
- More tolerant of temperature variations
- No data loss from missed refresh cycles

#### 4. Faster Access Times

| Memory Type | Typical Access Time |
|-------------|---------------------|
| 4116 DRAM | 150-250ns |
| 4164 DRAM | 100-200ns |
| Modern SRAM | 10-55ns |

Modern SRAM is vastly faster than vintage DRAM, providing comfortable timing margins.

#### 5. Lower Power Consumption (When Idle)

SRAM consumes minimal power when not being accessed. The original 4116 chips could
draw significant power, contributing to system heating.

Example: Commodore 64 SRAM modules reduce power consumption from ~240mA (8 DRAM chips)
to less than 5mA (single SRAM module).

#### 6. Availability of New Parts

| Memory Type | Availability Status |
|-------------|---------------------|
| 4116 DRAM | Scarce, often fake/recycled |
| 4164 DRAM | Limited, quality uncertain |
| 41256/44256 | Still available but declining |
| 62256 SRAM (32Kx8) | Readily available, new production |
| AS6C62256 | Current production, multiple sources |

New old stock (NOS) DRAM is increasingly rare and often of questionable provenance.
Modern SRAM chips are still manufactured and readily available.

### Disadvantages and Trade-offs

#### 1. Cost Per Bit

SRAM is significantly more expensive per bit than DRAM:
- 62256 (32KB SRAM): ~$1-3 each
- Modern large SRAM (1MB+): $5-15+ each
- Cost is generally acceptable for retro applications with small memory needs

#### 2. Lower Density

SRAM cells require 6 transistors vs DRAM's 1 transistor + 1 capacitor:
- Larger die size per bit
- Fewer bits per package
- May require multiple SRAM chips or larger packages

#### 3. Interface Complexity

DRAM uses multiplexed addressing; SRAM typically does not:
- Replacement boards need address demultiplexing logic
- RAS/CAS timing must be converted to SRAM control signals
- Additional ICs or CPLD/FPGA may be required

#### 4. Form Factor

- SRAM chips have different pinouts than DRAM
- Physical adapters or replacement boards required
- May not fit in original sockets without modification

---

## SRAM Replacement Strategies

### Strategy 1: DRAM-to-DRAM Upgrade (4116 to 4164)

The simplest "replacement" isn't SRAM at all - it's replacing troublesome 4116 chips
with more reliable 4164 chips. This is popular because:

- 4164 is pin-compatible with minor modifications
- Single +5V operation (eliminate -5V and +12V problems)
- Widely documented for many systems
- Minimal modification required

#### 4116 to 4164 Conversion

1. Bend pin 1 and pin 8 of the 4164 upward (don't insert into socket)
2. Connect pin 8 to pin 9 with a short wire (ties VCC to A7)
3. Alternatively, use a small adapter PCB

The unused A7 input is tied high, selecting the upper 16K of the 64K chip.
The lower 48K of capacity is wasted but the chip works as a 16K replacement.

### Strategy 2: Direct SRAM Substitution

For systems where the memory subsystem is simple enough, individual SRAM chips
can replace DRAM with appropriate adapter circuitry.

#### Required Functions

1. **Address Demultiplexing**: Latch row address on RAS, combine with column address on CAS
2. **Control Signal Translation**: Convert RAS/CAS/WE to CE/OE/WE
3. **Data Direction Control**: Handle separate DIN/DOUT pins if present

#### Typical Components

- 74HC574/74ABT574: 8-bit D-type flip-flop for address latching
- 74HC00/74ABT00: NAND gates for control signal generation
- 62256 or similar: 32Kx8 SRAM chip

### Strategy 3: Complete Replacement Modules

Purpose-built PCBs that plug into all DRAM sockets simultaneously, providing
complete memory replacement with a single modern SRAM IC.

This approach:
- Replaces all memory at once
- Uses a single high-density SRAM chip
- Includes all necessary address demultiplexing
- Often includes additional features (VSP bug fixes, etc.)

---

## Commercial SRAM Replacement Products

### ZX Spectrum Lower RAM Modules

Several commercial and open-source options exist for replacing the 8x 4116 chips
in the ZX Spectrum's lower 16K:

| Product | Features | Source |
|---------|----------|--------|
| ZX Spectrum Lower RAM Module | Single SRAM, plug-in replacement | [Retro-Spektro](https://www.retro-spektro.com/projects/zx-spectrum-lower-ram-replacement-module/) |
| Lower RAM Replacement Module | Issue 2-6A compatible | [zx.zigg.net](http://zx.zigg.net/LRR/) |
| 4116 Replacement Board | DIY project | [Evolutional](https://www.evolutional.co.uk/post/zxspectrum-4116-ram-board/) |

**Compatible ZX Spectrum Issues**: 2, 3, 3B, 4A, 4B, 4S, 5, 6A (not compatible with 128K models)

### Commodore 64 SRAM Modules

| Product | Boards Supported | Source |
|---------|------------------|--------|
| C64 SRAM Module | 250407, 250425 (8x 4164) | [DIY Chris](https://diychris.com/index.php/product/commodore-64-sram-module/) |
| SaRuMan-64 | 250466, 250469 (2x 4464) | [AmiBay](https://www.amibay.com/threads/saruman-64k-static-ram-for-dram-replacement-board.109657/) |
| 64K SRAM Replacement | C64C shortboards | [Retro 8bit Shop](https://www.retro8bitshop.com/product/64k-sram-for-c64/) |

**Benefits**: Reduces power consumption from ~240mA to <5mA, fixes VSP bug on some versions.

### Amiga 500/500+ Modules

| Product | Configuration | Source |
|---------|---------------|--------|
| A500-SRAM-Board | Replaces 44256 DRAM with single SRAM | [GitHub - kr239](https://github.com/kr239/A500-SRAM-Board) |
| A500-DRAM-Board | Replaces 44256 with EDO memory | [GitHub - kr239](https://github.com/kr239/A500-DRAM-Board) |
| A500+ DRAM Replacement | PCBWay shared project | [PCBWay](https://www.pcbway.com/project/shareproject/Amiga_500__DRAM_Replacement_Board.html) |

### Williams Arcade Adapters

| Product | Function | Source |
|---------|----------|--------|
| Williams 4116 to 4164 Adapter | Power pinout conversion | [Arcadeshop](https://www.arcadeshop.com/i/894/williams-4116-to-4164-power-adapter.htm) |
| 4116-to-4164 Adapter PCBs | Individual chip adapters | [Etsy](https://www.etsy.com/listing/805900742/4116-ram-socket-to-4164-ram-adapter-8) |

**Compatible Games**: Defender, Robotron, Joust, Stargate, Bubbles, Blaster, Moon Patrol, and more.

### Apple II Products

| Product | Function | Source |
|---------|----------|--------|
| RAM128 (GW4208B) | 128KB SRAM-based Language Card | [Tindie - Garrett's Workshop](https://www.tindie.com/products/garrettswrkshp/ram128-gw4208b-128kb-ram-for-apple-ii/) |
| RamFactor 8M | 8MB SRAM expansion | [a2heaven](https://a2heaven.com/webshop/index.php?manufacturer_id=21&rt=product/manufacturer) |
| RAM2GS II | 8MB SDRAM for IIgs | [Tindie - Garrett's Workshop](https://www.tindie.com/products/garrettswrkshp/ram2gs-ii-gw4201d-8mb-ram-for-apple-iigs/) |

---

## DIY Replacement Approaches

### The Piggyback Method (Diagnostic Only)

A classic diagnostic technique for finding faulty DRAM without desoldering:

1. Obtain a known-good RAM chip of the same type
2. Place it on top of a suspected bad chip, pins aligned
3. Press down firmly to ensure all 16 pins make contact
4. Power on and test

**How it works**: On a chip with an open circuit failure, the good chip completes
the circuit. If the system works, you've identified the faulty chip.

**Limitations**:
- Does not work if the original chip has a short circuit
- Does not work reliably on 4116 (about 50% success rate)
- Not a permanent repair, just diagnostic
- Multiple failed chips require multiple piggybacks

**Safety check**: Use the "hot finger" test first - touch each chip briefly.
A chip with a short will be noticeably hotter than its neighbours.

### Building Your Own Replacement Board

For hobbyists comfortable with electronics, building a custom SRAM replacement
provides an educational project and deep understanding of the memory system.

#### Basic Design Approach

```
DRAM Socket Interface          Logic             SRAM
     A0-A6 ──────────────────────┐
        │                        │
       RAS* ──┬─> 74HC574 ──────>├──> A0-A13 ──> SRAM
              │   (Latch)        │                A0-A14
       CAS* ──┘                  │
        │                        │
       WE* ─────────────────────>├──> WE* ────> SRAM WE
        │                        │
                                 ├──> CE* ────> SRAM CE
                                 │
     DIN/DOUT ──────────────────>└──> I/O ────> SRAM I/O
```

#### Key Components

1. **Address Latch** (74HC574 or similar)
   - Latches A0-A6 on falling edge of RAS
   - These become the high address bits for SRAM
   - A0-A6 during CAS become low address bits

2. **Control Logic** (74HC00, 74HC02, etc.)
   - Generate SRAM CE from RAS/CAS combination
   - Generate SRAM OE from read timing
   - Pass through WE appropriately

3. **SRAM Chip** (62256 or larger)
   - 32Kx8 (62256) provides 32KB
   - For 16K replacement, use only 14 address bits
   - Modern SRAM has 10-55ns access, far faster than needed

#### Example: ZX Spectrum Lower RAM Replacement

One documented design uses:
- IDT71256L or similar 32Kx8 SRAM (using 16K)
- 74HC574 for address latching
- 74F04 (hex inverter) for control signals
- AS7C512-15 64Kx8 SRAM (alternative)

The SRAM's 25ns access time provides enormous margin over the original
150-200ns 4116 timing requirements.

### Tips for DIY Projects

1. **Study the original design first**
   - Understand how RAS/CAS timing works
   - Identify any system-specific quirks
   - Check for separate DIN/DOUT vs bidirectional data

2. **Start with a working system**
   - Verify the system works before modification
   - Document original behaviour
   - Keep original chips in case of problems

3. **Use quality components**
   - Gold-plated header pins for socket connections
   - Decoupling capacitors near SRAM power pins
   - Good quality PCB or careful point-to-point wiring

4. **Test incrementally**
   - Verify power rails first
   - Check address latching with logic analyser or scope
   - Test with memory diagnostic software

---

## Trade-offs and Considerations

### When SRAM Replacement Makes Sense

| Scenario | Recommendation |
|----------|----------------|
| Multiple failed 4116 chips | Strongly recommended - eliminates triple-voltage problems |
| Single failed 4164/41256 | Consider - depends on availability of replacements |
| Preventive maintenance | Worth considering for heavily-used systems |
| Increased reliability needed | Recommended - SRAM is inherently more reliable |
| Reduced power consumption | Recommended - significant reduction possible |
| Historical preservation | Debatable - changes originality |

### When to Keep Original DRAM

| Scenario | Recommendation |
|----------|----------------|
| Working system, collector value | Keep original - maintain authenticity |
| Minor repair needed | Stock 4164/41256 replacements still available |
| Learning experience | DRAM repair teaches valuable troubleshooting |
| Cost-sensitive | DRAM chips cheaper if available |

### Physical Considerations

- **Form factor**: SRAM modules may be taller/larger than original chips
- **Socket compatibility**: Some modules require socket modification
- **Reversibility**: Consider whether the modification can be undone
- **Case fit**: Verify modified system still fits in original enclosure

### Electrical Considerations

- **Power supply capacity**: SRAM may draw different current profile
- **Timing compatibility**: Verify SRAM timing meets system requirements
- **Signal integrity**: Long wires or poor layout can cause problems
- **Ground paths**: Ensure adequate grounding for replacement board

---

## Quick Reference: DRAM Pinout Comparison

### 16-Pin DRAM Family (4116, 4164, 41256)

| Pin | 4116 | 4164 | 41256 |
|-----|------|------|-------|
| 1 | VBB (-5V) | N/C | A8 |
| 2 | DIN | D | D |
| 3 | WE* | WE* | WE* |
| 4 | RAS* | RAS* | RAS* |
| 5 | A0 | A0 | A0 |
| 6 | A2 | A2 | A2 |
| 7 | A1 | A1 | A1 |
| 8 | VDD (+12V) | VCC (+5V) | VCC (+5V) |
| 9 | VCC (+5V) | A7 | A7 |
| 10 | A5 | A5 | A5 |
| 11 | A4 | A4 | A4 |
| 12 | A3 | A3 | A3 |
| 13 | A6 | A6 | A6 |
| 14 | DOUT | Q | Q |
| 15 | CAS* | CAS* | CAS* |
| 16 | VSS (GND) | VSS (GND) | VSS (GND) |

### 20-Pin DRAM (44256 / 256Kx4)

```
       +---+--+---+
    A8 |1  +--+ 20| VSS (GND)
   DQ0 |2       19| DQ3
   DQ1 |3       18| DQ2
   WE* |4  44256 17| CAS*
  RAS* |5       16| OE*
    A0 |6       15| A7
    A1 |7       14| A6
    A2 |8       13| A5
    A3 |9       12| A4
   VCC |10      11| N/C
       +----------+
```

### Common SRAM Pinout (62256 - 32Kx8)

```
        +---+--+---+
    A14 |1  +--+ 28| VCC (+5V)
    A12 |2       27| WE*
     A7 |3       26| A13
     A6 |4  62256 25| A8
     A5 |5       24| A9
     A4 |6       23| A11
     A3 |7       22| OE*
     A2 |8       21| A10
     A1 |9       20| CS*
     A0 |10      19| I/O7
   I/O0 |11      18| I/O6
   I/O1 |12      17| I/O5
   I/O2 |13      16| I/O4
    VSS |14      15| I/O3
        +----------+
```

---

## Conclusion

DRAM replacement with SRAM is a practical and increasingly popular approach to
maintaining vintage computing hardware. The combination of aging DRAM stock,
reliability concerns with multi-voltage designs (especially the 4116), and
readily available modern SRAM makes this an attractive option.

For most retro computing hobbyists, the benefits of SRAM replacement outweigh
the costs and complexity:

- **Reliability**: Eliminates the most failure-prone components
- **Availability**: Modern SRAM is in current production
- **Performance**: Far exceeds original specifications
- **Power**: Often significantly reduced consumption
- **Future-proofing**: Less concern about finding replacement parts

Commercial solutions exist for many popular systems, and DIY approaches are
well-documented for hobbyists who prefer to build their own. Whether choosing
a drop-in commercial module or designing a custom replacement, SRAM provides
a path to keeping vintage computers running for decades to come.

---

## Additional Resources

### General References

- [SRAM vs DRAM Comparison (Diffen)](https://www.diffen.com/difference/Dynamic_random-access_memory_vs_Static_random-access_memory)
- [Static Random-Access Memory (Wikipedia)](https://en.wikipedia.org/wiki/Static_random-access_memory)
- [Dynamic Random-Access Memory (Wikipedia)](https://en.wikipedia.org/wiki/Dynamic_random-access_memory)

### System-Specific Resources

- [6502.org Forum - DRAM Replacement Discussion](http://forum.6502.org/viewtopic.php?f=4&t=5328)
- [Vintage Computer Federation Forums](https://www.vcfed.org/forum/)
- [Lemon64 - Commodore Community](https://www.lemon64.com/forum/)
- [Stardot Forums - BBC/Acorn Community](https://stardot.org.uk/forums/)
- [Arcade-Museum Forums](https://forums.arcade-museum.com/)

### Datasheets and Technical Documentation

- [Alliance Memory AS6C62256 (32Kx8 SRAM)](https://www.alliancememory.com/wp-content/uploads/pdf/AS6C62256.pdf)
- [Infineon CY62256N (32Kx8 SRAM)](https://www.infineon.com/dgdl/Infineon-CY62256N_256-Kbit_(32_K_8)_Static_RAM-DataSheet-v11_00-EN.pdf)

---

*Document created: 2025-12-12*
*For GitHub Issue #34 - sram-forge project*
