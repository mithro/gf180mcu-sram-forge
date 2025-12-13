# SRAM Datasheet Archive Index

This directory contains references to key datasheets for SRAM parts relevant to sram-forge compatibility research (Issue #34).

## 8-bit SRAMs (x8)

### Alliance Memory AS6C Series (Modern Replacements)

| Part | Organization | Datasheet URL |
|------|-------------|---------------|
| AS6C6264 | 8K x 8 | https://www.alliancememory.com/datasheets/AS6C6264.pdf |
| AS6C62256 | 32K x 8 | https://www.alliancememory.com/datasheets/AS6C62256.pdf |
| AS6C1008 | 128K x 8 | https://www.alliancememory.com/datasheets/AS6C1008.pdf |
| AS6C4008 | 512K x 8 | https://www.alliancememory.com/datasheets/AS6C4008.pdf |
| AS6C8008 | 1M x 8 | https://www.alliancememory.com/datasheets/AS6C8008.pdf |

### ISSI IS62/IS61 Series

| Part | Organization | Datasheet URL |
|------|-------------|---------------|
| IS62C256 | 32K x 8 | https://www.issi.com/WW/pdf/62-65C256AL.pdf |
| IS61C1024 | 128K x 8 | https://www.issi.com/WW/pdf/61C1024.pdf |

### Classic References

| Part | Organization | Source | Notes |
|------|-------------|--------|-------|
| HM6264 | 8K x 8 | Hitachi | Original manufacturer datasheet |
| HM62256 | 32K x 8 | Hitachi | Original manufacturer datasheet |
| TMM2064 | 8K x 8 | Toshiba | NES compatible variant |

## 16-bit SRAMs (x16)

### Renesas R1RP Series (RISCBOY Target)

| Part | Organization | Datasheet URL |
|------|-------------|---------------|
| R1RP0416D | 256K x 16 | https://www.renesas.com/en/document/dst/r1rp0416d-series-datasheet |
| R1RP0416D-I | 256K x 16 | Same as above (industrial temp range) |

**Key specs for R1RP0416D:**
- 5V operation (4.5V - 5.5V)
- 10ns or 12ns access time
- 44-pin SOJ or TSOP II
- Control signals: CE1#, CE2, OE#, WE#, LB#, UB#

### ISSI IS61/IS62 16-bit Series

| Part | Organization | Datasheet URL |
|------|-------------|---------------|
| IS61WV25616BLL | 256K x 16 | https://www.issi.com/WW/pdf/61WV25616.pdf |
| IS61WV51216BLL | 512K x 16 | https://www.issi.com/WW/pdf/61WV51216.pdf |

### Alliance Memory 16-bit

| Part | Organization | Datasheet URL |
|------|-------------|---------------|
| AS6C8016 | 512K x 16 | https://www.alliancememory.com/datasheets/AS6C8016.pdf |

## 32-bit SRAMs (x32)

### Alliance Memory 32-bit

| Part | Organization | Datasheet URL |
|------|-------------|---------------|
| AS7C325632 | 256K x 32 | https://www.alliancememory.com/datasheets/AS7C325632.pdf |
| AS7C351232 | 512K x 32 | https://www.alliancememory.com/datasheets/AS7C351232.pdf |

**Note:** 32-bit parts are typically only available in BGA packages.

## Historical DRAM References

For DRAM-to-SRAM replacement research:

| Part | Organization | Notes |
|------|-------------|-------|
| 4116 | 16K x 1 | Triple-voltage DRAM, widely documented online |
| 4164 | 64K x 1 | Single 5V DRAM |
| 41256 | 256K x 1 | Higher capacity DRAM |
| 44256 | 256K x 4 | Nibble-wide variant |

## Pinout Quick Reference

### 28-pin DIP (6264/62256)

Standard JEDEC pinout used by 6264 (8Kx8) and 62256 (32Kx8):

```
        ┌────────┐
 A14 ─┤1     28├─ VCC
 A12 ─┤2     27├─ WE#
  A7 ─┤3     26├─ A13/CS2
  A6 ─┤4     25├─ A8
  A5 ─┤5     24├─ A9
  A4 ─┤6     23├─ A11
  A3 ─┤7     22├─ OE#
  A2 ─┤8     21├─ A10
  A1 ─┤9     20├─ CS1#
  A0 ─┤10    19├─ D7
  D0 ─┤11    18├─ D6
  D1 ─┤12    17├─ D5
  D2 ─┤13    16├─ D4
 GND ─┤14    15├─ D3
        └────────┘
```

**Note:** Pin 1 is NC on 6264, A14 on 62256. Pin 26 is active-high CS2 on 6264, A13 on 62256.

### 32-pin DIP (628128/1008/4008)

Standard JEDEC pinout for larger 8-bit SRAMs:

```
        ┌────────┐
 A18 ─┤1     32├─ VCC
 A16 ─┤2     31├─ A15
 A14 ─┤3     30├─ A17
 A12 ─┤4     29├─ WE#
  A7 ─┤5     28├─ A13
  A6 ─┤6     27├─ A8
  A5 ─┤7     26├─ A9
  A4 ─┤8     25├─ A11
  A3 ─┤9     24├─ OE#
  A2 ─┤10    23├─ A10
  A1 ─┤11    22├─ CS#
  A0 ─┤12    21├─ D7
  D0 ─┤13    20├─ D6
  D1 ─┤14    19├─ D5
  D2 ─┤15    18├─ D4
 GND ─┤16    17├─ D3
        └────────┘
```

**Note:** Pin 1 is NC on 128Kx8, A18 on 512Kx8. Some pins vary by size.

### 44-pin TSOP II (16-bit SRAMs)

Pin layout for 256Kx16 and 512Kx16 parts (e.g., R1RP0416D):

| Signal | Pin(s) | Function |
|--------|--------|----------|
| A0-A17 | Various | Address inputs |
| DQ0-DQ15 | Various | Data I/O |
| CE1# | Active-low chip enable |
| CE2 | Active-high chip enable |
| OE# | Output enable (active-low) |
| WE# | Write enable (active-low) |
| LB# | Lower byte enable (DQ0-7) |
| UB# | Upper byte enable (DQ8-15) |
| VCC | Power (5V or 3.3V) |
| VSS | Ground |

## Control Signal Summary

All standard SRAMs use active-low control signals:

| Signal | Active | Function |
|--------|--------|----------|
| CS#/CE# | LOW | Chip select/enable |
| OE# | LOW | Output enable (tristate when high) |
| WE# | LOW | Write enable |
| LB# | LOW | Lower byte enable (16-bit parts) |
| UB# | LOW | Upper byte enable (16-bit parts) |

**Exception:** Some parts have a secondary CE2 that is active-high.

## Downloading Datasheets

Most datasheets can be downloaded directly from manufacturer websites:

1. **Alliance Memory**: https://www.alliancememory.com/products/sram/
2. **ISSI**: https://www.issi.com/products/sram.shtml
3. **Renesas**: https://www.renesas.com/products/memory-logic/srams
4. **Infineon/Cypress**: https://www.infineon.com/products/memory-sram
