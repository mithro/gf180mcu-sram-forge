# Classic SRAM Families for Retro Computing

This document surveys the classic 8-bit SRAM families commonly used in retro computing systems, focusing on their history, pinouts, control signals, and voltage compatibility. This research supports GitHub issue #34 regarding 5V/3.3V SRAM compatibility for sram-forge.

---

## Executive Summary

The **62256 (32K x 8)** is the de-facto standard for 8-bit SRAM in retro computing projects today. It offers the best balance of capacity, availability, and compatibility with Z80, 6502, and other 8-bit systems. Modern replacements from Alliance Memory (AS6C62256) support both 5V and 3.3V operation (2.7V to 5.5V), making them ideal for bridging classic and modern systems.

---

## SRAM Family Overview

| Family | Organization | Package | Address Lines | Era | Primary Use Cases |
|--------|-------------|---------|---------------|-----|-------------------|
| **6116** | 2K x 8 | 24-pin DIP | A0-A10 (11) | ~1981-1982 | VIC-20, early arcade |
| **6264** | 8K x 8 | 28-pin DIP | A0-A12 (13) | ~1983-1985 | NES, small systems |
| **62256** | 32K x 8 | 28-pin DIP | A0-A14 (15) | ~1985-1987 | Z80, 6502, most common |
| **628128** | 128K x 8 | 32-pin DIP | A0-A16 (17) | ~1988-1990 | Larger retro systems |
| **621024** | 128K x 8 | 32-pin DIP | A0-A16 (17) | ~1988-1990 | Alternative to 628128 |

---

## 6116 (2K x 8) - The Earliest Common SRAM

### History and Manufacturers

The 6116 represents the transition from NMOS (2016 series) to CMOS technology for 2K x 8 SRAMs. It became popular in early 8-bit microcomputers due to its low power consumption and simple interface.

**Original/Major Manufacturers:**
- Hitachi: HM6116
- Toshiba: TC5517
- NEC: uPD446
- Mitsubishi: M58725P, M5M5116
- Fujitsu: MB8416
- AMD: AM9128
- Texas Instruments: TMS4016
- Fairchild: MB8128-15
- RCA/GE: CDM6116
- Cypress: CY6116, CY6117
- IDT: IDT6116

**Year Introduced:** Approximately 1981-1982 (CMOS variants)

### 24-Pin DIP Pinout

```
              .----\/----.
        A7 - |01      24| - Vcc (+5V)
        A6 - |02      23| - A8
        A5 - |03      22| - A9
        A4 - |04      21| - /WE
        A3 - |05      20| - /OE
        A2 - |06      19| - A10
        A1 - |07      18| - /CS
        A0 - |08      17| - I/O7
      I/O0 - |09      16| - I/O6
      I/O1 - |10      15| - I/O5
      I/O2 - |11      14| - I/O4
       GND - |12      13| - I/O3
              `----------'
```

### Control Signals

| Signal | Pin | Polarity | Function |
|--------|-----|----------|----------|
| /CS | 18 | Active LOW | Chip Select - enables the device |
| /OE | 20 | Active LOW | Output Enable - enables data output |
| /WE | 21 | Active LOW | Write Enable - enables write operation |

### Systems Using 6116

- **Commodore VIC-20**: Used 2x 6116 SRAMs (positions U14, U15) for main RAM in CR board revision
- **Early arcade machines**: Video RAM, work RAM
- **Vintage synthesizers and drum machines**: Parameter storage
- **Pinball machines**: Score and settings storage

### Voltage Specifications

| Parameter | Standard | Low Power (LP) |
|-----------|----------|----------------|
| Vcc | 5V +/- 5% | 5V +/- 5% |
| Standby Current | 10-100mA | 1-4 uW @ 2V (battery retention) |
| Data Retention | N/A | 2V minimum |

---

## 6264 (8K x 8) - The NES Standard

### History and Manufacturers

The 6264 became the JEDEC standard for 8K x 8 static RAM, widely used in Nintendo Entertainment System (NES) cartridges for work RAM (WRAM) and save RAM.

**Major Manufacturers:**
- Hitachi: HM6264
- Hynix (formerly Hyundai): HY6264
- Cypress: CY6264
- Samsung: KM6264
- Alliance Memory: AS6C6264 (current production)

### 28-Pin DIP Pinout

```
              .----\/----.
        nc - |01      28| - Vcc (+5V)
       A12 - |02      27| - /WE
        A7 - |03      26| - CS2
        A6 - |04      25| - A8
        A5 - |05      24| - A9
        A4 - |06      23| - A11
        A3 - |07      22| - /OE
        A2 - |08      21| - A10
        A1 - |09      20| - /CS1
        A0 - |10      19| - D7
        D0 - |11      18| - D6
        D1 - |12      17| - D5
        D2 - |13      16| - D4
       GND - |14      15| - D3
              `----------'
```

### Control Signals

| Signal | Pin | Polarity | Function |
|--------|-----|----------|----------|
| /CS1 | 20 | Active LOW | Chip Select 1 |
| CS2 | 26 | Active HIGH | Chip Select 2 |
| /OE | 22 | Active LOW | Output Enable |
| /WE | 27 | Active LOW | Write Enable |

**Note:** The 6264 has dual chip selects - the chip is selected when /CS1 is LOW **and** CS2 is HIGH. This allows flexible memory decoding.

### Systems Using 6264

- **Nintendo NES/Famicom**: Work RAM and battery-backed save RAM at $6000-$7FFF
- **Small Z80 systems**: RC2014 and similar homebrew computers
- **Arcade machines**: Various video and work RAM applications

### Battery Backup Notes

The 6264 is commonly used with CR2032 batteries for save game storage. Key considerations:
- Battery life typically 10-25+ years with proper circuit design
- Use CMOS variant (6264, not 2464) for lowest standby current
- Proper chip enable decoding is important to minimize leakage

---

## 62256 (32K x 8) - The Most Popular Standard

### History and Manufacturers

The 62256 is the most widely used SRAM for retro computing projects. Its 32KB capacity matches common memory map requirements (e.g., 32KB RAM + 32KB ROM = 64KB address space).

**Major Manufacturers:**
- Hitachi: HM62256
- Samsung: KM62256
- Cypress/Infineon: CY62256 (discontinued 2018, last-time buy)
- Alliance Memory: AS6C62256 (current production, recommended replacement)
- ISSI: IS61C256, IS62C256

**Samsung KM62256 Datasheet Timeline:**
- February 1993: Advance information draft
- November 1993: Initial draft
- September 1994: Finalized
- December 1997: Revision 4.0

### 28-Pin DIP Pinout

```
              .----\/----.
       A14 - |01      28| - Vcc (+5V)
       A12 - |02      27| - /WE
        A7 - |03      26| - A13
        A6 - |04      25| - A8
        A5 - |05      24| - A9
        A4 - |06      23| - A11
        A3 - |07      22| - /OE
        A2 - |08      21| - A10
        A1 - |09      20| - /CS
        A0 - |10      19| - D7
        D0 - |11      18| - D6
        D1 - |12      17| - D5
        D2 - |13      16| - D4
       GND - |14      15| - D3
              `----------'
```

### Control Signals

| Signal | Pin | Polarity | Function |
|--------|-----|----------|----------|
| /CS | 20 | Active LOW | Chip Select |
| /OE | 22 | Active LOW | Output Enable |
| /WE | 27 | Active LOW | Write Enable |

### 6264 vs 62256 Pinout Comparison

The 62256 and 6264 share the same 28-pin package with nearly identical pinouts. Key difference:

| Pin | 6264 | 62256 |
|-----|------|-------|
| 1 | NC | A14 |
| 26 | CS2 (active high) | A13 |

This means:
- A 62256 can replace a 6264 if you tie A13 and A14 appropriately
- Pin 26 changes from active-high chip enable to address line

### Systems Using 62256

- **Z80 systems**: Sinclair ZX Spectrum, RC2014, Amstrad CPC (expansions)
- **6502 systems**: Apple II (expansions), Replica 1 (Apple 1 clone)
- **Commodore systems**: C64, VIC-20 (memory expansions)
- **Atari systems**: Memory expansions
- **Nintendo NES/Famicom**: Some games (RacerMate Challenge II, Romance of the Three Kingdoms II)
- **68000 projects**: Combined with EPROMs for simple systems

### Voltage Specifications and 3.3V Variants

| Part Number | Voltage Range | Manufacturer | Notes |
|-------------|---------------|--------------|-------|
| HM62256 | 5V +/- 10% | Hitachi | Original 5V part |
| CY62256 | 4.5V - 5.5V | Cypress | Discontinued 2018 |
| AS6C62256 | 2.7V - 5.5V | Alliance Memory | **Recommended** - works at both 3.3V and 5V |
| IS61C256 | 4.5V - 5.5V | ISSI | 5V only |
| IS61LV256 | 2.7V - 3.6V | ISSI | 3.3V only, lower absolute max (4.6V) |

**Critical Note:** The IS61C256 (5V) has absolute max of 7.0V, while IS61LV256 (3.3V) has absolute max of 4.6V. Do not use 3.3V parts with 5V signals without level shifting.

---

## 628128 (128K x 8) - Larger Retro Systems

### History and Manufacturers

The 628128 provides 128KB in a 32-pin package, used in larger retro systems and gaming cartridges requiring more RAM.

**Major Manufacturers:**
- Hitachi: HM628128
- Wing Shing: WS628128
- Alliance Memory: AS6C1008 (modern 128K x 8 replacement)

### 32-Pin DIP Pinout

```
              .----\/----.
  nc (A18) - |01      32| - Vcc (+5V)
       A16 - |02      31| - A15
       A14 - |03      30| - CS2 (or A17)
       A12 - |04      29| - /WE
        A7 - |05      28| - A13
        A6 - |06      27| - A8
        A5 - |07      26| - A9
        A4 - |08      25| - A11
        A3 - |09      24| - /OE
        A2 - |10      23| - A10
        A1 - |11      22| - /CS1
        A0 - |12      21| - D7
        D0 - |13      20| - D6
        D1 - |14      19| - D5
        D2 - |15      18| - D4
       GND - |16      17| - D3
              `----------'
```

### Control Signals

| Signal | Pin | Polarity | Function |
|--------|-----|----------|----------|
| /CS1 | 22 | Active LOW | Chip Select 1 |
| CS2 | 30 | Active HIGH | Chip Select 2 (or A17 on some variants) |
| /OE | 24 | Active LOW | Output Enable |
| /WE | 29 | Active LOW | Write Enable |

### Systems Using 628128

- **Sega Genesis/Mega Drive**: Cartridge SRAM for save games
- **Neo Geo**: Cartridge memory
- **Larger Z80 projects**: Extended memory configurations
- **DSP development boards**: Data storage

---

## 621024 (128K x 8) - Alternative to 628128

### Overview

The 621024 is an alternative 128K x 8 SRAM with a slightly different pinout than the 628128. Manufactured by companies like AMIC Technology (LP621024) and Utron Technology (UT621024).

### 32-Pin Pinout

The 621024 shares the same general pinout as the 628128 with pin 1 designated as NC (or A18 for larger variants) and pin 30 as CS2/A17.

### Key Specifications

| Parameter | Value |
|-----------|-------|
| Organization | 128K x 8 (131,072 words x 8 bits) |
| Supply Voltage | 5V single supply |
| Access Time | 35-70 ns typical |
| Standby Current | 2 uA typical |
| Data Retention Voltage | 2V minimum |

---

## De-Facto Standard Interface Summary

### The 62256/6264 Standard

The 28-pin 62256 pinout has become the de-facto standard for 8-bit asynchronous SRAM:

**Standard Control Signals:**
- All control signals are **active LOW**
- Single chip select (/CS) or dual (/CS1 + CS2)
- Separate /OE and /WE for 8080-style bus
- Can also work with 6502-style bus (tie /OE low, use /WE as R/W)

**Standard Timing (Asynchronous):**
- Address setup before chip select
- Data valid after OE asserted (read)
- Write pulse determines write timing
- No clock required

### Interface Compatibility with Modern FPGAs/ASICs

| Signal | 62256 Name | Typical FPGA Name | Polarity |
|--------|------------|-------------------|----------|
| Chip Enable | /CS | CE_n or CSn | Active LOW |
| Output Enable | /OE | OE_n | Active LOW |
| Write Enable | /WE | WE_n | Active LOW |
| Address | A[14:0] | ADDR[14:0] | - |
| Data | D[7:0] | DATA[7:0] | Bidirectional |

---

## Modern Replacement Parts

### Currently Available (2025)

| Part Number | Organization | Voltage | Package | Manufacturer | Status |
|-------------|-------------|---------|---------|--------------|--------|
| AS6C6264 | 8K x 8 | 2.7-5.5V | 28-DIP, SOP | Alliance Memory | **In Production** |
| AS6C62256 | 32K x 8 | 2.7-5.5V | 28-DIP, SOP | Alliance Memory | **In Production** |
| AS6C1008 | 128K x 8 | 2.7-5.5V | 32-DIP, SOP | Alliance Memory | **In Production** |
| AS6C4008 | 512K x 8 | 2.7-5.5V | 32-DIP, SOP | Alliance Memory | **In Production** |
| IS61C256 | 32K x 8 | 4.5-5.5V | 28-DIP, SOP | ISSI | **In Production** |
| IS61LV256 | 32K x 8 | 2.7-3.6V | 28-DIP, SOP | ISSI | **In Production** |

### Recommended Parts for New Designs

**For 5V-only systems:**
- Any 62256-compatible part will work
- IS61C256 if you need exact 5V operation

**For 3.3V-only systems:**
- AS6C62256 (2.7-5.5V) - safest choice
- IS61LV256 - dedicated 3.3V part

**For mixed 5V/3.3V systems:**
- **AS6C62256** is the best choice - operates reliably at both voltages
- Allows same part to be used across multiple designs

---

## Pinout Comparison Tables

### 28-Pin SRAM Comparison (6264 vs 62256)

| Pin | 6116 (24-pin) | 6264 (28-pin) | 62256 (28-pin) |
|-----|---------------|---------------|----------------|
| 1 | A7 | NC | A14 |
| 2 | A6 | A12 | A12 |
| 3 | A5 | A7 | A7 |
| 4 | A4 | A6 | A6 |
| 5 | A3 | A5 | A5 |
| 6 | A2 | A4 | A4 |
| 7 | A1 | A3 | A3 |
| 8 | A0 | A2 | A2 |
| 9 | I/O0 | A1 | A1 |
| 10 | I/O1 | A0 | A0 |
| 11 | I/O2 | D0 | D0 |
| 12 | GND | D1 | D1 |
| 13 | I/O3 | D2 | D2 |
| 14 | I/O4 | GND | GND |
| 15 | I/O5 | D3 | D3 |
| 16 | I/O6 | D4 | D4 |
| 17 | I/O7 | D5 | D5 |
| 18 | /CS | D6 | D6 |
| 19 | A10 | D7 | D7 |
| 20 | /OE | /CS1 | /CS |
| 21 | /WE | A10 | A10 |
| 22 | A9 | /OE | /OE |
| 23 | A8 | A11 | A11 |
| 24 | Vcc | A9 | A9 |
| 25 | - | A8 | A8 |
| 26 | - | **CS2** | **A13** |
| 27 | - | /WE | /WE |
| 28 | - | Vcc | Vcc |

### 32-Pin SRAM (628128/621024)

| Pin | Function | Pin | Function |
|-----|----------|-----|----------|
| 1 | NC (A18) | 17 | D3 |
| 2 | A16 | 18 | D4 |
| 3 | A14 | 19 | D5 |
| 4 | A12 | 20 | D6 |
| 5 | A7 | 21 | D7 |
| 6 | A6 | 22 | /CS1 |
| 7 | A5 | 23 | A10 |
| 8 | A4 | 24 | /OE |
| 9 | A3 | 25 | A11 |
| 10 | A2 | 26 | A9 |
| 11 | A1 | 27 | A8 |
| 12 | A0 | 28 | A13 |
| 13 | D0 | 29 | /WE |
| 14 | D1 | 30 | CS2 (A17) |
| 15 | D2 | 31 | A15 |
| 16 | GND | 32 | Vcc |

---

## Read/Write Cycle Timing

### Asynchronous Read Cycle

```
            ___________________________________________
Address    X___________VALID_ADDRESS___________________X
            ___________________________________________
/CS        __________|                    |____________
            _______________________________
/OE        __________|                    |____________
            ___________________________________________
Data Out   ----------X--------VALID_DATA--------------X
                      |<---tAA--->|
                      |<----tCE--->|
                      |<----tOE---->|
```

**Key Timing Parameters:**
- tAA: Address access time (55-70ns typical for modern parts)
- tCE: Chip enable access time
- tOE: Output enable access time

### Asynchronous Write Cycle

```
            ___________________________________________
Address    X___________VALID_ADDRESS___________________X
            ___________________________________________
/CS        __________|                    |____________
            _______________________________
/WE        __________|                    |____________
            ___________________________________________
Data In    ----------X--------VALID_DATA--------------X
                      |<--tWP-->|
                      |<--tDW-->|
```

**Key Timing Parameters:**
- tWP: Write pulse width (45-55ns typical)
- tDW: Data valid to write end

---

## Recommendations for sram-forge

### Primary Target Interface

Based on this research, the **62256-compatible interface** should be the primary target for 8-bit SRAM compatibility in sram-forge:

1. **Most widely used** in retro computing projects
2. **Still in production** from multiple manufacturers
3. **Voltage flexible** (2.7V - 5.5V with AS6C62256)
4. **Simple interface** - 3 control signals, all active-low
5. **28-pin standard** - well-established JEDEC pinout

### Interface Mapping

| sram-forge Signal | 62256 Signal | Notes |
|-------------------|--------------|-------|
| CE_n | /CS | Active LOW chip enable |
| WE_n | /WE | Active LOW write enable |
| OE_n | /OE | Active LOW output enable (optional for synchronous) |
| ADDR[14:0] | A[14:0] | 15-bit address for 32KB |
| DATA[7:0] | D[7:0] | Bidirectional 8-bit data |

### Future Considerations

- **16-bit variants**: Consider 62256 x 2 for 16-bit width
- **Larger capacities**: 628128/AS6C1008 for 128KB
- **Synchronous wrapper**: Add clock domain crossing if needed

---

## References

### Verified Sources

- [NESdev Wiki - 6264 static RAM](https://www.nesdev.org/wiki/6264_static_RAM)
- [Wikipedia - 6264](https://en.wikipedia.org/wiki/6264)
- [Alliance Memory AS6C62256 Product Page](https://www.alliancememory.com/datasheets/as6c62256/)
- [Alliance Memory AS6C62256 Datasheet (PDF)](https://www.alliancememory.com/wp-content/uploads/pdf/AS6C62256.pdf)
- [Alliance Memory AS6C6264 Product Page](https://www.alliancememory.com/datasheets/as6c6264/)
- [Renesas 6116 Product Page](https://www.renesas.com/us/en/products/memory-logic/srams/asynchronous-srams/6116-50v-2k-x-8-asynchronous-static-ram)
- [Futurlec 6116 Datasheet](https://www.futurlec.com/Memory/HT6116-70S.shtml)
- [Futurlec 62256 Datasheet](https://www.futurlec.com/Memory/62256-70S.shtml)
- [Futurlec 628128 Datasheet](https://www.futurlec.com/Memory/628128.shtml)
- [MIT 6264 Datasheet (PDF)](https://web.mit.edu/6.115/www/document/6264.pdf)
- [MIT HM62256 Datasheet (PDF)](https://web.mit.edu/6.115/www/document/62256.pdf)
- [Samsung KM62256 Datasheet (PDF)](https://www.futurlec.com/Datasheet/Memory/62256.pdf)
- [ISSI IS61C256 Datasheet (PDF)](https://www.issi.com/WW/pdf/61c256ah.pdf)
- [Alldatasheet - HM628128](https://www.alldatasheet.com/datasheet-pdf/pdf/82433/HITACHI/HM628128.html)
- [Datasheetspdf - UT621024](https://datasheetspdf.com/datasheet/UT621024.html)
- [Cypress CY62256 Replacement - Alliance Memory](https://www.alliancememory.com/cypress-semiconductor-cy62256-replacement/)

### Retro Computing Resources

- [Reactive Micro - 6116 SRAM Pins and Cross Reference](https://downloads.reactivemicro.com/Electronics/Static%20RAM/6116%20SRAM%20Pins%20and%20Cross%20Referance.txt)
- [NESdev Forums - SRAM replacement/cross reference](https://forums.nesdev.org/viewtopic.php?t=8722)
- [Arcade Components - Vintage Memory Parts](https://www.arcadecomponents.com/)

---

*Document created: 12 December 2025*
*For GitHub Issue #34: 5V/3.3V SRAM Compatibility*
