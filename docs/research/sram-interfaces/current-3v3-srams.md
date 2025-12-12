# Current 3.3V SRAM Parts Survey

This document surveys currently available 3.3V SRAM parts from active manufacturers,
focusing on parts relevant to embedded systems, retro computing, and FPGA applications.

*Research conducted for GitHub Issue #34*
*Date: 12 December 2025*

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [8-bit Parts (x8 Organization)](#8-bit-parts-x8-organization)
   - [32Kx8 (256Kbit) - 62256 Equivalents](#32kx8-256kbit---62256-equivalents)
   - [128Kx8 (1Mbit) - 628128 Equivalents](#128kx8-1mbit---628128-equivalents)
   - [512Kx8 (4Mbit) and Larger](#512kx8-4mbit-and-larger)
3. [16-bit Parts (x16 Organization)](#16-bit-parts-x16-organization)
   - [256Kx16 (4Mbit) - IS61LV25616 and Similar](#256kx16-4mbit---is61lv25616-and-similar)
   - [512Kx16 (8Mbit) and Larger](#512kx16-8mbit-and-larger)
4. [32-bit Parts (x32 Organization)](#32-bit-parts-x32-organization)
5. [Voltage Compatibility Notes](#voltage-compatibility-notes)
   - [Wide Voltage Parts (2.7-5.5V)](#wide-voltage-parts-27-55v)
   - [5V Tolerant I/O](#5v-tolerant-io)
   - [3.3V vs 5V Trade-offs](#33v-vs-5v-trade-offs)
6. [Manufacturer Overview](#manufacturer-overview)
7. [Availability and Pricing Summary](#availability-and-pricing-summary)
8. [References](#references)

---

## Executive Summary

The 3.3V SRAM market is well-served by three primary manufacturers:

| Manufacturer | Series | Key Strengths |
|-------------|--------|---------------|
| **Alliance Memory** | AS6C, AS7C | Wide voltage (2.7-5.5V), drop-in 5V replacements, DIP packages |
| **ISSI** | IS61LV, IS62LV, IS61WV, IS62WV | Broad selection, high speed (10ns), industrial temp |
| **Infineon (Cypress)** | CY62, CY7C | Ultra-low power (MoBL), automotive grade, ECC options |

**Key Findings:**

1. **Wide voltage parts (2.7-5.5V)** from Alliance Memory are excellent for mixed 3.3V/5V systems
2. **IS61LV25616** is the primary 3.3V alternative to the 5V R1RP0416D for RISCBOY-like applications
3. **32-bit parts** are scarce in commodity forms; most applications use two 16-bit devices
4. **Through-hole (DIP) packages** are still available for 8-bit parts up to 512Kx8
5. **Access times** range from 10ns (high-speed) to 55ns (low-power)

---

## 8-bit Parts (x8 Organization)

### 32Kx8 (256Kbit) - 62256 Equivalents

These are direct replacements for the classic 62256 SRAM used in Z80, 6502, and other retro systems.

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| AS6C62256-55PCN | Alliance | 2.7-5.5V | 55ns | 28-DIP | In Stock | ~$5.85 |
| AS6C62256-55SIN | Alliance | 2.7-5.5V | 55ns | 28-SOP | In Stock | ~$5.64 |
| AS6C62256-55STIN | Alliance | 2.7-5.5V | 55ns | 28-sTSOP | In Stock | ~$4.50 |
| IS61LV256AL-10TLI | ISSI | 3.0-3.6V | 10ns | 28-TSOP | In Stock | ~$3.50 |
| IS62C256AL-45ULI | ISSI | 3.0-3.6V | 45ns | 28-SOP | In Stock | ~$2.80 |
| CY62256LL-70PC | Infineon | 4.5-5.5V | 70ns | 28-DIP | In Stock | ~$4.00 |

**Notes:**
- Alliance AS6C62256 is the most versatile with 2.7-5.5V range (works at both 3.3V and 5V)
- All inputs and outputs are TTL compatible
- 28-pin DIP is the standard for retro computing applications
- ISSI IS61LV256AL offers faster access (10ns) but narrower voltage range

**Package Pinout (28-pin DIP):**
```
        +----v----+
   A14 -|1     28|- VCC
   A12 -|2     27|- WE#
    A7 -|3     26|- A13
    A6 -|4     25|- A8
    A5 -|5     24|- A9
    A4 -|6     23|- A11
    A3 -|7     22|- OE#
    A2 -|8     21|- A10
    A1 -|9     20|- CS#
    A0 -|10    19|- D7
   D0  -|11    18|- D6
   D1  -|12    17|- D5
   D2  -|13    16|- D4
   GND -|14    15|- D3
        +---------+
```

---

### 128Kx8 (1Mbit) - 628128 Equivalents

Larger capacity 8-bit SRAMs for systems requiring more memory.

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| AS6C1008-55PCN | Alliance | 2.7-5.5V | 55ns | 32-DIP | In Stock | ~$5.43 |
| AS6C1008-55SIN | Alliance | 2.7-5.5V | 55ns | 32-SOP | In Stock | ~$5.20 |
| IS62WV1288DBLL-45TLI | ISSI | 2.5-3.6V | 45ns | 32-TSOP | In Stock | ~$4.20 |
| CY62128ELL-45ZXI | Infineon | 4.5-5.5V | 45ns | 32-TSOP | In Stock | ~$5.50 |

**Notes:**
- 32-pin DIP packages still available from Alliance Memory
- ISSI IS62WV1288 offers lower voltage (2.5V min) for battery applications
- Address bus is 17 bits (A0-A16)

---

### 512Kx8 (4Mbit) and Larger

Higher density 8-bit parts for modern applications.

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| AS6C4008-55PCN | Alliance | 2.7-5.5V | 55ns | 32-DIP | In Stock | ~$7.50 |
| AS6C4008-55SIN | Alliance | 2.7-5.5V | 55ns | 32-SOP | In Stock | ~$5.64 |
| AS6C4008A-55ZIN | Alliance | 2.7-5.5V | 55ns | 32-TSOP-I | In Stock | ~$5.00 |
| IS62WV5128BLL-55HLI | ISSI | 2.5-3.6V | 55ns | 32-sTSOP-I | In Stock | ~$4.80 |
| IS61LV5128AL-10KI | ISSI | 3.0-3.6V | 10ns | 32-SOP | In Stock | ~$6.50 |
| CY62148EV30LL-45ZSXI | Infineon | 2.2-3.6V | 45ns | 32-TSOP-II | In Stock | ~$7.00 |

**1Mx8 (8Mbit) Parts:**

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| AS6C8008-55ZIN | Alliance | 2.7-5.5V | 55ns | 44-TSOP-II | In Stock | ~$9.00 |
| AS6C8008A-55BIN | Alliance | 2.7-3.6V | 55ns | 48-TFBGA | In Stock | ~$8.50 |

**Notes:**
- AS6C4008 is available in 32-DIP (through-hole) - rare for 4Mbit density
- ISSI IS62WV5128BLL features ultra-low power (15mA active, <5uA standby)
- Infineon CY62148EV30 has MoBL (More Battery Life) technology
- 512Kx8 uses 19-bit address (A0-A18), 1Mx8 uses 20-bit address (A0-A19)

---

## 16-bit Parts (x16 Organization)

### 256Kx16 (4Mbit) - IS61LV25616 and Similar

These are alternatives to the Renesas R1RP0416D used in RISCBOY.

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| IS61LV25616AL-10TLI | ISSI | 3.0-3.6V | 10ns | 44-TSOP-II | **Obsolete** | N/A |
| IS61WV25616BLL-10TLI | ISSI | 2.5-3.6V | 10ns | 44-TSOP-II | In Stock | ~$8.50 |
| AS6C3216-55TIN | Alliance | 2.7-3.6V | 55ns | 48-TSOP-I | In Stock | ~$12.00 |
| CY62146EV30LL-45ZSXI | Infineon | 2.2-3.6V | 45ns | 44-TSOP-II | In Stock | ~$9.00 |

**IMPORTANT:** The IS61LV25616AL is marked **obsolete** at DigiKey. The replacement is the IS61WV25616BLL.

**Key Features of IS61WV25616BLL:**
- 256K words x 16 bits (4,194,304 bits)
- High-speed access: 10ns, 12ns, 15ns options
- Single 3.3V power supply (2.5V to 3.6V range)
- **Byte write capability** via UB# and LB# pins
- TTL-compatible I/O
- CMOS low power: <5mA typical standby
- Fully static - no clock or refresh required

**Byte Write Operation:**
| UB# | LB# | Operation |
|-----|-----|-----------|
| L | L | Write full 16-bit word |
| L | H | Write upper byte (D15-D8) only |
| H | L | Write lower byte (D7-D0) only |
| H | H | No write (outputs high-Z during write) |

**Package Pinout (44-pin TSOP-II):**
```
Control signals: CE#, OE#, WE#, LB#, UB#
Address: A0-A17 (18 bits for 256K words)
Data: D0-D15 (16 bits bidirectional)
Power: VCC, VSS
```

---

### 512Kx16 (8Mbit) and Larger

Higher density 16-bit parts.

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| AS6C8016-55ZIN | Alliance | 2.7-5.5V | 55ns | 44-TSOP-II | In Stock | ~$11.00 |
| AS6C8016A-55BIN | Alliance | 2.7-3.6V | 55ns | 48-TFBGA | In Stock | ~$10.50 |
| CY62157EV30LL-45ZSXI | Infineon | 2.2-3.6V | 45ns | 44-TSOP-II | In Stock | ~$10.00 |
| IS61WV51216BLL-10TLI | ISSI | 2.5-3.6V | 10ns | 44-TSOP-II | In Stock | ~$12.00 |

**1Mx16 (16Mbit) Parts:**

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| AS6C3216-55TIN | Alliance | 2.7-3.6V | 55ns | 48-TSOP-I | In Stock | ~$15.00 |
| CY62167EV30LL-45ZXI | Infineon | 2.2-3.6V | 45ns | 48-TSOP-I | In Stock | ~$14.00 |
| IS61WV102416BLL-10TLI | ISSI | 2.5-3.6V | 10ns | 48-TSOP-I | In Stock | ~$16.00 |

**2Mx16 (32Mbit) Parts:**

| Part Number | Mfr | Voltage | Access Time | Package | Stock Status | Price (qty 1) |
|------------|-----|---------|-------------|---------|--------------|---------------|
| IS61WV204816BLL-10TLI | ISSI | 2.5-3.6V | 10ns | 48-TSOP-I | In Stock | ~$25.00 |
| CY62167EV30LL-45BVXI | Infineon | 2.2-3.6V | 45ns | 48-VFBGA | In Stock | ~$18.00 |

**Notes:**
- AS6C8016 has wide voltage (2.7-5.5V) for mixed systems
- All 16-bit parts have byte-write capability (LB#/UB# pins)
- Infineon MoBL devices offer ultra-low active current
- Higher densities (32Mb+) available primarily in BGA packages

---

## 32-bit Parts (x32 Organization)

32-bit parallel asynchronous SRAMs are relatively rare in commodity form. Most high-performance applications use:
- Two 16-bit SRAMs in parallel
- Synchronous SRAMs (which have better 32-bit options)

### Available 32-bit Asynchronous SRAMs

| Part Number | Mfr | Organization | Voltage | Access Time | Package | Stock Status | Price |
|------------|-----|--------------|---------|-------------|---------|--------------|-------|
| AS7C325632-10BIN | Alliance | 256Kx32 | 3.0-3.6V | 10ns | 90-TFBGA | In Stock | ~$12.00 |
| AS7C351232-10BIN | Alliance | 512Kx32 | 3.0-3.6V | 10ns | 90-TFBGA | In Stock | ~$15.00 |

**Package Constraints:**
- 32-bit parts require high pin counts (90-100+ pins)
- Available only in BGA packages (not through-hole)
- Pin budget: 32 data + 18-19 address + 4 byte-enables + 3 control + power = ~60+ pins minimum

**Features of AS7C325632/AS7C351232:**
- 256Kx32 (8Mb) or 512Kx32 (16Mb) organization
- Fast 10ns access time
- Data retention voltage: 1.5V minimum
- 90-ball TFBGA package
- Four byte-enable pins (BE0#, BE1#, BE2#, BE3#) for individual byte writes

**Alternative: Dual 16-bit Configuration**

For applications requiring 32-bit data width, using two 16-bit SRAMs is often more practical:

```
                    +-------------+
Address A[17:0] --> | IS61WV25616 | --> D[15:0]
Control CE#,OE#,WE# | (256Kx16)   |
Byte LB#, UB#       +-------------+

                    +-------------+
Address A[17:0] --> | IS61WV25616 | --> D[31:16]
Control CE#,OE#,WE# | (256Kx16)   |
Byte LB#, UB#       +-------------+
```

This approach:
- Uses more common, cheaper parts
- Allows through-hole or common SMD packages
- Provides 4-byte granularity (one LB/UB per chip)

---

## Voltage Compatibility Notes

### Wide Voltage Parts (2.7-5.5V)

Alliance Memory's AS6C series parts operate from **2.7V to 5.5V**, making them ideal for:
- Mixed 3.3V/5V systems
- Legacy system upgrades
- Systems with varying supply voltages

| Part | Voltage Range | Notes |
|------|---------------|-------|
| AS6C62256 | 2.7-5.5V | Drop-in 62256 replacement |
| AS6C1008 | 2.7-5.5V | Drop-in 628128 replacement |
| AS6C4008 | 2.7-5.5V | 512Kx8 with wide voltage |
| AS6C8016 | 2.7-5.5V | 512Kx16 with wide voltage |

**Key Specification:**
- All inputs and outputs are **TTL compatible**
- Compatible with both 5V and 3.3V logic levels
- No level shifters required in mixed-voltage systems

### 5V Tolerant I/O

True "5V tolerant I/O" means the part can accept 5V input signals without damage while operating at 3.3V VCC.

| Category | Behavior |
|----------|----------|
| **5V Tolerant** | Can accept 5V inputs while VCC=3.3V; output remains 3.3V |
| **Wide Voltage** | Operates at any voltage in range; output follows VCC |
| **Absolute Max** | 5V on inputs allowed only as transient/ESD protection |

**Parts with Wide Voltage (functionally 5V compatible):**
- Alliance Memory AS6C series (2.7-5.5V VCC)

**Parts with 3.3V only operation:**
- ISSI IS61LV/IS62LV series (typically 3.0-3.6V)
- Infineon CY62 "EV" series (typically 2.2-3.6V)

For interfacing 3.3V-only SRAMs with 5V systems, use:
- Level translators (74LVX4245, 74LVC245)
- FPGAs with 5V-tolerant I/O
- MCUs with 5V-tolerant GPIO

### 3.3V vs 5V Trade-offs

| Characteristic | 3.3V SRAM | 5V SRAM | Wide Voltage (2.7-5.5V) |
|---------------|-----------|---------|-------------------------|
| **Power Consumption** | Lower | Higher | Varies with VCC |
| **Speed** | Often faster | Traditional | Comparable |
| **Noise Immunity** | Lower | Higher | Depends on VCC |
| **Battery Life** | Better | Worse | Excellent |
| **Modern MCU Compatibility** | Native | May need level shift | Native to both |
| **Legacy System Compatibility** | May need level shift | Native | Native |
| **Availability** | Excellent (new designs) | Declining | Excellent |
| **Package Options** | SMD focus | DIP still available | Both available |

**Recommendation:**
- For new designs: Use 3.3V parts with wide voltage range (AS6C series)
- For retro computing: Wide voltage AS6C series works directly in 5V systems
- For battery applications: Low-voltage ISSI IS62WV series (2.5V min)
- For automotive/harsh environments: Infineon MoBL series with ECC

---

## Manufacturer Overview

### Alliance Memory

**Website:** [alliancememory.com](https://www.alliancememory.com/)

**Product Lines:**
- **AS6C series**: Low-power asynchronous SRAM, 2.7-5.5V, wide temp range
- **AS7C series**: Fast asynchronous SRAM, 3.3V
- Focus on drop-in legacy replacements

**Key Strengths:**
- Wide voltage range (2.7-5.5V) on most parts
- Through-hole DIP packages still available
- Long product lifecycle commitment
- Excellent for retro computing applications

**Datasheet Links:**
- [AS6C62256 Datasheet](https://www.alliancememory.com/datasheets/as6c62256/)
- [AS6C4008 Datasheet](https://www.alliancememory.com/datasheets/as6c4008/)
- [AS6C8016 Datasheet](https://www.alliancememory.com/datasheets/as6c8016/)

---

### ISSI (Integrated Silicon Solution Inc.)

**Website:** [issi.com](https://www.issi.com/)

**Product Lines:**
- **IS61LV series**: 3.3V low-voltage SRAM (being phased out)
- **IS62LV series**: 3.3V low-voltage SRAM
- **IS61WV/IS62WV series**: Current generation, ultra-low power

**Key Strengths:**
- High-speed options (10ns access time)
- Very low power consumption
- Broad density range (256Kb to 32Mb+)
- Industrial and automotive temperature grades

**Note:** IS61LV series is being replaced by IS61WV series. Check for "AL" suffix parts as obsolete.

**Datasheet Links:**
- [ISSI SRAM Part Decoder](https://www.issi.com/WW/pdf/SRAM_Part_Decoder.pdf)
- [IS61WV25616BLL Datasheet](https://www.issi.com/ww/pdf/61WV25616BLL.pdf) (replacement for IS61LV25616)

---

### Infineon (formerly Cypress Semiconductor)

**Website:** [infineon.com](https://www.infineon.com/)

**Product Lines:**
- **CY62xxx series**: Standard asynchronous SRAM
- **CY62xxxEV series**: MoBL (More Battery Life) ultra-low power
- **CY62xxxG series**: 65nm with on-chip ECC

**Key Strengths:**
- Ultra-low power MoBL technology
- On-chip ECC for improved reliability (65nm parts)
- Automotive qualification (AEC-Q100)
- Wide temperature range (-40 to +125C)

**Datasheet Links:**
- [CY62148EV30 Product Page](https://www.infineon.com/part/CY62148EV30LL-45ZSXI)
- [CY62167EV30 Product Page](https://www.infineon.com/part/CY62167EV30LL-45ZXI)

---

## Availability and Pricing Summary

*Prices are approximate and based on single-unit quantities from major distributors (DigiKey, Mouser) as of December 2025. Volume pricing can be significantly lower.*

### 8-bit Parts Quick Reference

| Density | Best Value | Best Speed | Wide Voltage |
|---------|------------|------------|--------------|
| 32Kx8 | IS62C256AL (~$2.80) | IS61LV256AL-10 (~$3.50) | AS6C62256 (~$5.85) |
| 128Kx8 | IS62WV1288DBLL (~$4.20) | IS62WV1288DBLL-45 (~$4.20) | AS6C1008 (~$5.43) |
| 512Kx8 | IS62WV5128BLL (~$4.80) | IS61LV5128AL-10 (~$6.50) | AS6C4008 (~$5.64) |
| 1Mx8 | - | - | AS6C8008 (~$9.00) |

### 16-bit Parts Quick Reference

| Density | Best Value | Best Speed | Byte-Write |
|---------|------------|------------|------------|
| 256Kx16 | CY62146EV30 (~$9.00) | IS61WV25616BLL-10 (~$8.50) | All parts |
| 512Kx16 | CY62157EV30 (~$10.00) | IS61WV51216BLL-10 (~$12.00) | All parts |
| 1Mx16 | CY62167EV30 (~$14.00) | IS61WV102416BLL-10 (~$16.00) | All parts |

### Where to Buy

| Distributor | Notes |
|-------------|-------|
| [DigiKey](https://www.digikey.com) | Excellent stock, fast shipping, good parametric search |
| [Mouser](https://www.mouser.com) | Wide selection, competitive pricing |
| [Newark/element14](https://www.newark.com) | Good for industrial quantities |
| [Octopart](https://www.octopart.com) | Price comparison across distributors |
| [LCSC](https://www.lcsc.com) | Lower prices, good for Chinese-sourced ISSI parts |

---

## References

### Datasheets (Verified Links)

**Alliance Memory:**
- [AS6C62256](https://www.alliancememory.com/datasheets/as6c62256/) - 32Kx8 SRAM
- [AS6C4008](https://www.alliancememory.com/datasheets/as6c4008/) - 512Kx8 SRAM
- [AS6C8008](https://www.alliancememory.com/datasheets/as6c8008/) - 1Mx8 SRAM
- [AS6C8016](https://www.alliancememory.com/datasheets/as6c8016/) - 512Kx16 SRAM
- [AS6C3216](https://www.alliancememory.com/datasheets/as6c3216/) - 2Mx16 SRAM
- [Low Power Asynchronous SRAM Overview](https://www.alliancememory.com/product/low-power-asynchronous-sram/)

**ISSI:**
- [ISSI SRAM Part Decoder](https://www.issi.com/WW/pdf/SRAM_Part_Decoder.pdf) - Part numbering guide
- [Asynchronous SRAM Product Page](https://www.issi.com/US/product-asynchronous-sram.shtml)

**Infineon:**
- [CY62148EV30LL-45ZSXI](https://www.infineon.com/part/CY62148EV30LL-45ZSXI) - 512Kx8 SRAM
- [CY62167EV30LL-45ZXI](https://www.infineon.com/cms/en/product/memories/sram-static-ram/asynchronous-sram/cy62167ev30ll-45zxi/) - 1Mx16 SRAM
- [CY62157EV30LL-45ZSXI](https://www.infineon.com/cms/en/product/memories/sram-static-ram/asynchronous-sram/cy62157ev30ll-45zsxi/) - 512Kx16 SRAM

### Distributor Links

- [DigiKey SRAM Category](https://www.digikey.com/en/products/filter/sram/702)
- [Mouser SRAM Category](https://www.mouser.com/c/semiconductors/memory-ics/sram/)
- [Octopart AS6C4008-55PCN](https://octopart.com/as6c4008-55pcn-alliance+memory-7865078)
- [Octopart IS62WV5128BLL-55HLI](https://octopart.com/part/issi/IS62WV5128BLL-55HLI)

### Technical References

- [DigiKey: Alliance Memory AS6C1008-55SIN](https://www.digikey.com/en/products/detail/alliance-memory-inc/AS6C1008-55SIN/4234577)
- [DigiKey: IS62WV5128BLL-55HLI](https://www.digikey.com/en/products/detail/issi-integrated-silicon-solution-inc/IS62WV5128BLL-55HLI/1557564)
- [DigiKey: CY62148EV30LL-45ZSXI](https://www.digikey.com/en/products/detail/infineon-technologies/CY62148EV30LL-45ZSXI/1205259)
- [DigiKey: CY62167EV30LL-45ZXI](https://www.digikey.com/en/products/detail/infineon-technologies/CY62167EV30LL-45ZXI/1644410)

---

## Appendix: Part Number Decoder

### Alliance Memory AS6Cxxxx

```
AS6C 4008 - 55 S IN
│    │      │  │ │
│    │      │  │ └─ Temperature: blank=Commercial, I=Industrial (-40 to +85C)
│    │      │  └─── Package: P=PDIP, S=SOP, ST=sTSOP, Z=TSOP-I, T=TSOP-I (48), B=TFBGA
│    │      └────── Speed: 55=55ns access time
│    └───────────── Density/Organization (e.g., 4008=512Kx8, 8016=512Kx16)
└────────────────── Family: AS6C=Low Power Asynchronous SRAM
```

### ISSI IS61/62WVxxxx

```
IS61 WV 5128 B LL - 55 H L I
│    │   │    │ │    │  │ │ │
│    │   │    │ │    │  │ │ └─ Temperature: blank=Commercial, I=Industrial
│    │   │    │ │    │  │ └─── Package: L=TSOP, H=sTSOP, Q=SOP, B=BGA
│    │   │    │ │    │  └───── Power: blank=Standard, L=Low Power
│    │   │    │ │    └───────── Speed: 55=55ns, 45=45ns, 10=10ns
│    │   │    │ └────────────── Generation: B=2nd gen, blank=1st gen
│    │   │    └──────────────── Power mode: LL=Ultra Low Power, L=Low Power
│    │   └───────────────────── Density (5128=512Kx8, 25616=256Kx16)
│    └───────────────────────── Series: WV=Wide Voltage, LV=Low Voltage
└────────────────────────────── Type: 61=SRAM, 62=Ultra Low Power SRAM
```

### Infineon CY62xxx

```
CY62 167 EV 30 LL - 45 ZS X I
│    │   │  │  │    │  │  │ │
│    │   │  │  │    │  │  │ └─ Temperature: I=Industrial, A=Automotive
│    │   │  │  │    │  │  └─── Voltage: X=2.2-3.6V, S=4.5-5.5V
│    │   │  │  │    │  └────── Package: Z=TSOP-I, B=BGA, S=SOP
│    │   │  │  │    └────────── Speed: 45=45ns, 55=55ns
│    │   │  │  └─────────────── Power: LL=Ultra Low Leakage, L=Low Power
│    │   │  └──────────────── Process: 30=0.30um, 18=0.18um (newer, lower power)
│    │   └─────────────────── Feature: EV=MoBL (ultra low power), G=with ECC
│    └─────────────────────── Density (146=256Kx16, 157=512Kx16, 167=1Mx16, 148=512Kx8)
└──────────────────────────── Family: CY62=Asynchronous SRAM
```

---

*Document version: 1.0*
*Last updated: 12 December 2025*
*Related issue: GitHub #34*
