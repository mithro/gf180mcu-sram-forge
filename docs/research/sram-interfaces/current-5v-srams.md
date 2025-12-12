# Current 5V SRAM Parts Survey

**Document Purpose**: Survey of currently available 5V SRAM parts from active manufacturers for SRAM compatibility with retro computing and RISCBOY applications.

**Related Issue**: GitHub Issue #34

**Research Date**: 2024-12-12

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [8-Bit Parts (x8 Organization)](#8-bit-parts-x8-organization)
   - [Alliance Memory AS6C Series](#alliance-memory-as6c-series)
   - [ISSI IS62C/IS61C Series](#issi-is62cis61c-series)
   - [Cypress/Infineon CY62 Series](#cypressinfineon-cy62-series-legacy)
   - [Renesas 5V SRAMs](#renesas-5v-srams-x8)
3. [16-Bit Parts (x16 Organization)](#16-bit-parts-x16-organization)
   - [Renesas R1RP0416D (RISCBOY Target)](#renesas-r1rp0416d-riscboy-target)
   - [Alliance Memory AS6C8016](#alliance-memory-as6c8016)
   - [ISSI 16-Bit Parts](#issi-16-bit-parts)
4. [32-Bit Parts (x32 Organization)](#32-bit-parts-x32-organization)
5. [Comparison Tables](#comparison-tables)
6. [Availability Summary](#availability-summary)
7. [Recommendations](#recommendations)
8. [References](#references)

---

## Executive Summary

This survey covers currently available 5V-compatible parallel SRAM parts suitable for retro computing interfaces and the RISCBOY project. Key findings:

1. **Alliance Memory** is the primary active supplier of drop-in 5V SRAM replacements
2. **ISSI** continues to offer 5V parts but many are transitioning to low-voltage
3. **Cypress/Infineon CY62 series** has been discontinued; Alliance Memory provides replacements
4. **Renesas R1RP0416D** (256Kx16, 5V) is the RISCBOY target SRAM and remains available
5. **32-bit wide 5V parts** are rare and typically only available as modules

Most "5V" SRAM parts today operate across a wide voltage range (typically 2.7V-5.5V), providing flexibility for both legacy 5V systems and modern 3.3V designs.

---

## 8-Bit Parts (x8 Organization)

### Alliance Memory AS6C Series

Alliance Memory is the leading supplier of drop-in replacement SRAMs for legacy parts. All parts operate from 2.7V to 5.5V, making them compatible with 5V systems.

| Part Number | Organization | Density | Access Time | Package Options | Voltage Range | Temp Range |
|-------------|--------------|---------|-------------|-----------------|---------------|------------|
| AS6C62256 | 32K x 8 | 256Kb | 55ns | 28-PDIP, 28-SOP, 28-TSOP I | 2.7V - 5.5V | -40C to +85C |
| AS6C1008 | 128K x 8 | 1Mb | 55ns | 32-PDIP, 32-SOP, 32-TSOP I | 2.7V - 5.5V | -40C to +85C |
| AS6C2008 | 256K x 8 | 2Mb | 55ns | 32-PDIP, 32-SOP, 32-TSOP I | 2.7V - 5.5V | -40C to +85C |
| AS6C4008 | 512K x 8 | 4Mb | 55ns, 70ns | 32-PDIP, 32-SOP, 32-TSOP I, 36-TFBGA | 2.7V - 5.5V | -40C to +125C (auto) |
| AS6C8008 | 1M x 8 | 8Mb | 55ns | 44-TSOP II, 48-TFBGA | 2.7V - 5.5V | -40C to +85C |

**Key Features**:
- Drop-in replacements for Cypress, IDT, and other legacy SRAMs
- Fully static operation (no clock or refresh required)
- TTL compatible inputs and outputs
- Low standby power suitable for battery backup applications
- Data retention voltage as low as 1.5V (min)

**Availability**: All parts actively manufactured and available at DigiKey, Mouser, and other major distributors.

**Sources**:
- [Alliance Memory AS6C62256 Datasheet](https://www.alliancememory.com/datasheets/as6c62256/)
- [Alliance Memory AS6C1008 Product Page](https://www.alliancememory.com/as6c1008/)
- [Alliance Memory AS6C4008 Datasheet](https://www.alliancememory.com/datasheets/as6c4008/)
- [DigiKey AS6C62256-55PCN](https://www.digikey.com/product-detail/en/alliance-memory-inc/AS6C62256-55PCN/1450-1033-ND/4234592)
- [DigiKey AS6C4008-55PCN](https://www.digikey.com/en/products/detail/alliance-memory-inc/AS6C4008-55PCN/4234586)

---

### ISSI IS62C/IS61C Series

ISSI (Integrated Silicon Solution Inc.) offers a range of 5V-compatible SRAM parts.

| Part Number | Organization | Density | Access Time | Package Options | Voltage | Notes |
|-------------|--------------|---------|-------------|-----------------|---------|-------|
| IS62C256 | 32K x 8 | 256Kb | 45ns, 70ns | 28-SOP, 28-TSOP I | 5V (+/-10%) | Active |
| IS61C1024 | 128K x 8 | 1Mb | 12ns, 15ns, 20ns, 25ns | 32-PDIP, 32-SOP, 32-TSOP | 5V (+/-10%) | Some variants obsolete |
| IS61C5128 | 512K x 8 | 4Mb | 10ns, 12ns, 15ns | 44-TSOP II | 5V | High-speed variant |

**IS62C256 Specifications**:
- Low active power: 200 mW (typical)
- Low standby power: 250 uW (typical) CMOS, 28 mW (typical) TTL
- Single 5V power supply
- Two chip enable pins (CE1#, CE2) for easy memory expansion

**IS61C1024 Specifications**:
- High-speed access times down to 12ns
- Low active power: 600 mW (typical)
- Low standby power: 500 uW (typical) CMOS
- Two Chip Enable (CE1 and CE2) inputs

**Important Notes**:
- The "IS62" prefix typically indicates 5V parts
- The "IS62WV" prefix indicates low-voltage (2.5V/3.3V) parts
- Some IS61C1024 variants (e.g., IS61C1024-15JI) are listed as obsolete

**Sources**:
- [ISSI Asynchronous SRAM Product Page](https://www.issi.com/US/product-asynchronous-sram.shtml)
- [IS62C256-70UI at Mouser](https://www.mouser.com/ProductDetail/ISSI/IS62C256-70UI)
- [IS61C1024 Datasheet (PDF)](https://www.eit.lth.se/fileadmin/eit/courses/datablad/Memory/Sram/IS61C1024.pdf)

---

### Cypress/Infineon CY62 Series (Legacy)

**STATUS: DISCONTINUED** - Cypress issued a product discontinuation notification with a last-time buy date of July 4, 2018.

| Part Number | Organization | Density | Access Time | Status | Replacement |
|-------------|--------------|---------|-------------|--------|-------------|
| CY62256 | 32K x 8 | 256Kb | 55ns, 70ns | DISCONTINUED | AS6C62256 |
| CY62256L | 32K x 8 | 256Kb | 70ns | Limited stock | AS6C62256 |
| CY62256NLL | 32K x 8 | 256Kb | 55ns | Limited stock | AS6C62256 |

**Important**: Alliance Memory has an agreement with Cypress Semiconductor to provide ongoing availability. The AS6C62256 family is the direct replacement and is in stock at DigiKey, Mouser, and Future Electronics.

**Sources**:
- [Alliance Memory CY62256 Replacement Announcement](https://www.alliancememory.com/cypress-semiconductor-cy62256-low-power-srams-and-direct-replacement-as6c62256-from-alliance-memory/)
- [CY62256L-70PC at DigiKey](https://www.digikey.com/en/products/detail/infineon-technologies/CY62256L-70PC/464568) - Still shows some stock

---

### Renesas 5V SRAMs (x8)

Renesas (formerly IDT) offers legacy 5V SRAM products. Many are obsolete or NRND (Not Recommended for New Designs).

| Part Number | Organization | Density | Access Time | Package | Status |
|-------------|--------------|---------|-------------|---------|--------|
| 71256 | 32K x 8 | 256Kb | 20-100ns | Various | Obsolete/NRND |
| 71256SA | 32K x 8 | 256Kb | 12-25ns | TSOP | Obsolete/NRND |
| R1LP0408D | 512K x 8 | 4Mb | 55ns | 32-SOP, 32-TSOP | Obsolete/NRND |

**71256SA Specifications**:
- 5.0V CMOS SRAM organized as 32K x 8
- All I/O TTL-compatible
- Access times: 12ns, 15ns, 20ns, 25ns
- Commercial (0C to 70C) and Industrial (-40C to 85C) options

**R1LP0408D Specifications**:
- 4-Mbit static RAM organized as 512-kword x 8-bit
- Voltage range: 4.5V to 5.5V
- 55ns access time
- Low standby current: 0.8uA

**Important**: While these parts are listed as obsolete/NRND, some stock may still be available through authorized distributors or brokers.

**Sources**:
- [Renesas 71256 Product Page](https://www.renesas.com/en/products/memory-logic/srams/asynchronous-srams/71256-50v-32k-x-8-asynchronous-static-ram)
- [Renesas R1LP0408D Product Page](https://www.renesas.com/en/products/r1lp0408d)
- [71256SA12TPG at Mouser](https://www.mouser.com/ProductDetail/Renesas-Electronics/71256SA12TPG)

---

## 16-Bit Parts (x16 Organization)

### Renesas R1RP0416D (RISCBOY Target)

**This is the primary SRAM target for RISCBOY**

| Parameter | Specification |
|-----------|---------------|
| **Part Number** | R1RP0416D Series |
| **Organization** | 256K x 16 |
| **Density** | 4Mbit |
| **Supply Voltage** | 5.0V +/- 10% (4.5V to 5.5V) |
| **Access Time** | 10ns (max), 12ns (max) |
| **Cycle Time** | Equal to access time |
| **Operating Current** | 170mA (10ns), 160mA (12ns) max |
| **TTL Standby Current** | 40mA max |
| **CMOS Standby Current** | 5mA max (standard), 1mA max (L-version), 0.5mA max (S-version) |
| **Data Retention Current** | 0.5mA max (L), 0.2mA max (S) |
| **Data Retention Voltage** | 2V min (L, S versions) |
| **Package Options** | 44-pin SOJ (400 mil), 44-pin TSOP II (400 mil) |
| **Temperature Range** | 0C to 70C (R1RP0416D-R), -40C to 85C (R1RP0416D-I) |

**Available Part Numbers**:
| Part Number | Speed | Standby | Package | Temp |
|-------------|-------|---------|---------|------|
| R1RP0416DSB-2PR | 10ns | 5mA | SOJ | Commercial |
| R1RP0416DSB-2LR | 10ns | 1mA | SOJ | Commercial |
| R1RP0416DSB-2SR | 10ns | 0.5mA | SOJ | Commercial |
| R1RP0416DGE-2PR | 12ns | 5mA | TSOP II | Commercial |
| R1RP0416DGE-2LR | 12ns | 1mA | TSOP II | Commercial |
| R1RP0416DGE-2SR | 12ns | 0.5mA | TSOP II | Commercial |

**Key Features**:
- Completely static memory - no clock or timing strobe required
- Equal access and cycle times (important for simple interfacing)
- Directly TTL compatible - all inputs and outputs
- High-speed access time: 10ns/12ns max
- Suitable for cache and buffer memory applications

**Applications**:
- High-speed, high-density memory systems
- Wide bit width configuration (16-bit data bus)
- Cache and buffer memory
- RISCBOY main memory

**Sources**:
- [Renesas R1RP0416D-R Product Page](https://www.renesas.com/en/products/r1rp0416d-r)
- [Renesas R1RP0416D-I Product Page](https://www.renesas.com/en/products/r1rp0416d-i)
- [R1RP0416D Series Datasheet (PDF)](https://www.renesas.com/en/document/dst/r1rp0416d-series-datasheet)
- [DigiKey R1RP0416D Datasheet](https://media.digikey.com/pdf/Data%20Sheets/Renesas/R1RP0416D_Series.pdf)

---

### Alliance Memory AS6C8016

| Parameter | Specification |
|-----------|---------------|
| **Part Number** | AS6C8016 |
| **Organization** | 512K x 16 |
| **Density** | 8Mbit |
| **Supply Voltage** | 2.7V to 5.5V |
| **Access Time** | 55ns |
| **Package Options** | 44-pin TSOP II (400 mil), 48-ball TFBGA (6mm x 8mm) |
| **Temperature Range** | -40C to +85C |
| **Data Retention Voltage** | 1.5V (min) |

**Key Features**:
- Super low power CMOS SRAM
- Fabricated using high performance, high reliability CMOS technology
- Stable standby current across operating temperature range
- Suitable for battery backup nonvolatile memory applications

**AC Test Conditions**:
- Input Pulse Levels: 0.2V to VCC - 0.2V
- Input Rise and Fall Times: 3ns
- Input/Output Timing Reference: 1.5V
- Output Load: CL = 30pF + 1TTL, IOH/IOL = -1mA/2mA

**Sources**:
- [Alliance Memory AS6C8016 Datasheet](https://www.alliancememory.com/datasheets/as6c8016/)
- [AS6C8016-55ZIN at Mouser](https://www.mouser.com/ProductDetail/Alliance-Memory/AS6C8016-55ZIN)

---

### ISSI 16-Bit Parts

ISSI offers 16-bit wide SRAMs, but most are low-voltage (3.3V). For 5V operation, the IS61C25616 series is the primary option.

| Part Number | Organization | Density | Access Time | Voltage | Package |
|-------------|--------------|---------|-------------|---------|---------|
| IS61C25616 | 256K x 16 | 4Mb | 8ns, 10ns, 12ns, 15ns | 5V | TSOP, SOJ |
| IS61LV25616 | 256K x 16 | 4Mb | 7ns, 8ns, 10ns, 12ns, 15ns | 3.3V | TSOP, SOJ |
| IS61WV102416 | 1M x 16 | 16Mb | 10ns | 2.5V/3.3V | TSOP |

**Note**: The IS61LV25616 and IS61WV102416 are LOW VOLTAGE parts (indicated by "LV" and "WV" in part number). For true 5V operation, use the IS61C25616 series (without "LV" or "WV").

**Sources**:
- [ISSI SRAM Product Brochure (PDF)](https://www.issi.com/WW/pdf/ISSI_SRAM.pdf)
- [IS61LV25616 Datasheet (Columbia University)](https://www.cs.columbia.edu/~sedwards/classes/2008/4840/ISSI-IS61LV25616-SRAM.pdf)

---

### Lyontek 16-Bit Parts

| Part Number | Organization | Density | Access Time | Voltage | Package |
|-------------|--------------|---------|-------------|---------|---------|
| LY62W51216ML-55LLI | 512K x 16 | 8Mb | 55ns | 2.7V - 5.5V | 44-TSOP II |

**Note**: This part operates across the full 2.7V-5.5V range, making it 5V compatible.

**Sources**:
- [LY62W51216ML-55LLI at Newark](https://www.newark.com/lyontek/ly62w51216ml-55lli/sram-8m-512kx16-2-7-5-5v-44tsopii/dp/53W0605)

---

## 32-Bit Parts (x32 Organization)

32-bit wide 5V SRAMs are rare in discrete chip form. Most available options are:

1. **Multi-chip modules** from specialty suppliers (Mercury, EDI)
2. **Combinations of 16-bit parts** (2x R1RP0416D, 2x AS6C8016, etc.)
3. **Legacy/obsolete parts** that may have limited availability

### Mercury/White Electronic Designs Modules

| Product | Organization | Access Time | Features |
|---------|--------------|-------------|----------|
| WSF256K32 | 256K x 32 | 20ns, 25ns, 35ns | SRAM module, user configurable as 512Kx16 |
| WSF512K32 | 512K x 32 | Various | SRAM + NOR Flash module, 5V TTL compatible |

**Features**:
- Hermetic ceramic packaging available
- MIL-STD-883 compliant versions available
- Commercial, industrial, and military temperature ranges
- TTL compatible inputs and outputs

**Package Options**:
- 66-pin PGA (1.185 inch square, Hermetic Ceramic HIP)
- 68-lead, 40mm Hermetic CQFP

**Sources**:
- [Mercury WSF512K32 Datasheet (PDF)](https://www.mrcy.com/legacy_assets/contentassets/0ef68c0ed74349ec871c142b399a570c/4376.12e_wsf512k32-xxx.pdf)
- [Mercury WSF512K16 Datasheet (PDF)](https://www.mrcy.com/legacy_assets/contentassets/99b115524ec940958307ddd4c3c4435d/mercury-documents/4373.11e_wsf512k16-xxx.pdf)

### EDI Multi-Chip Modules

| Product | Organization | Access Time | Features |
|---------|--------------|-------------|----------|
| EDI8L32256C | 256K x 32 | 15ns, 17ns, 20ns, 25ns | 5V, 8Mbit MCM |
| EDI x32 Family | 64K-512K x 32 | Various | MCM-L SRAM for DSPs |

**Note**: These are specialty multi-chip modules primarily designed for Texas Instruments DSP platforms.

**Sources**:
- [EDI x32 MCM-L SRAM Family](https://docplayer.net/7083919-Edi-s-x32-mcm-l-sram-family-integrated-memory-solution-for-tms320c4x-dsps.html)

---

## Comparison Tables

### 8-Bit Parts Comparison (Actively Manufactured)

| Manufacturer | Part Number | Size | Access Time | Voltage | DIP Avail? | Status |
|--------------|-------------|------|-------------|---------|------------|--------|
| Alliance Memory | AS6C62256 | 32Kx8 | 55ns | 2.7-5.5V | Yes (28-pin) | Active |
| Alliance Memory | AS6C1008 | 128Kx8 | 55ns | 2.7-5.5V | Yes (32-pin) | Active |
| Alliance Memory | AS6C2008 | 256Kx8 | 55ns | 2.7-5.5V | Yes (32-pin) | Active |
| Alliance Memory | AS6C4008 | 512Kx8 | 55ns | 2.7-5.5V | Yes (32-pin) | Active |
| ISSI | IS62C256 | 32Kx8 | 45-70ns | 5V | No (SOP/TSOP) | Active |
| ISSI | IS61C1024 | 128Kx8 | 12-25ns | 5V | Yes (32-pin) | Limited |
| Infineon (Cypress) | CY62256L | 32Kx8 | 70ns | 5V | Yes (28-pin) | EOL |

### 16-Bit Parts Comparison

| Manufacturer | Part Number | Size | Access Time | Voltage | Package | Status |
|--------------|-------------|------|-------------|---------|---------|--------|
| Renesas | R1RP0416D | 256Kx16 | 10-12ns | 4.5-5.5V | SOJ, TSOP II | Active |
| Alliance Memory | AS6C8016 | 512Kx16 | 55ns | 2.7-5.5V | TSOP II, TFBGA | Active |
| ISSI | IS61C25616 | 256Kx16 | 8-15ns | 5V | TSOP, SOJ | Active |
| Lyontek | LY62W51216ML | 512Kx16 | 55ns | 2.7-5.5V | TSOP II | Active |

### Speed vs Power Comparison (16-bit, 256Kx16)

| Part | Access Time | Active Current | Standby (CMOS) |
|------|-------------|----------------|----------------|
| R1RP0416D (10ns) | 10ns | 170mA | 5mA (std), 0.5mA (S) |
| R1RP0416D (12ns) | 12ns | 160mA | 5mA (std), 0.5mA (S) |
| IS61C25616 (10ns) | 10ns | ~100mA | ~5mA |
| AS6C8016 | 55ns | ~60mA | ~1mA |

---

## Availability Summary

### DigiKey Availability (as of December 2024)

| Part Number | Status | Notes |
|-------------|--------|-------|
| AS6C62256-55PCN | In Stock | "Order today, ships today" |
| AS6C1008-55PCN | In Stock | "Order today, ships today" |
| AS6C4008-55PCN | In Stock | "Order today, ships today" |
| IS62C256-70UI | In Stock | Available at Mouser |
| CY62256L-70PC | Limited | Some remaining stock |
| R1RP0416D variants | Verify | Check directly with distributor |

### Pricing Guidance (approximate, varies by quantity)

| Part | 1 pc | 10 pc | 100 pc |
|------|------|-------|--------|
| AS6C62256-55PCN (DIP) | ~$2.50 | ~$2.20 | ~$1.80 |
| AS6C1008-55PCN (DIP) | ~$4.00 | ~$3.50 | ~$3.00 |
| AS6C4008-55PCN (DIP) | ~$5.00 | ~$4.50 | ~$3.80 |
| IS62C256-70UI (SOP) | ~$2.00 | ~$1.80 | ~$1.50 |

**Note**: Prices are approximate and subject to change. Always verify current pricing at distributors.

### Recommended Part Search Tools

- [Octopart](https://octopart.com/) - Compare prices across multiple distributors
- [FindChips](https://www.findchips.com/) - Aggregated inventory search
- [DigiKey](https://www.digikey.com/) - Major authorized distributor
- [Mouser](https://www.mouser.com/) - Major authorized distributor

---

## Recommendations

### For Retro Computing (8-bit systems)

1. **Primary Choice**: Alliance Memory AS6C series
   - AS6C62256 for 32Kx8 (6264/62256 replacement)
   - AS6C1008 for 128Kx8
   - AS6C4008 for 512Kx8
   - Widely available in DIP packages
   - Drop-in replacement for legacy parts

2. **Alternative**: ISSI IS62C256 or IS61C1024
   - Higher speed options available (down to 12ns)
   - Surface mount packages primarily

### For RISCBOY (16-bit, 256Kx16)

1. **Primary Choice**: Renesas R1RP0416D
   - Specifically designed for high-speed applications
   - 10ns/12ns access time
   - True 5V operation (4.5V-5.5V)
   - SOJ and TSOP II packages

2. **Alternative**: Alliance Memory AS6C8016 (512Kx16)
   - Larger capacity (512Kx16 vs 256Kx16)
   - Slower (55ns) but lower power
   - 2.7V-5.5V wide voltage range

### For 32-bit Applications

1. **Use Two 16-bit Parts in Parallel**
   - 2x R1RP0416D for 256Kx32 with 10-12ns access
   - 2x AS6C8016 for 512Kx32 with 55ns access

2. **Specialty Modules** (if hermetic/military grade needed)
   - Mercury WSF256K32 or WSF512K32 modules
   - Higher cost, specialty applications

### General Recommendations

1. **For new designs**: Use Alliance Memory AS6C series or Renesas R1RP series
2. **Avoid**: Cypress CY62 series (discontinued, supply uncertain)
3. **Verify**: Check distributor stock before committing to a design
4. **Consider**: Wide-voltage parts (2.7-5.5V) provide flexibility for 3.3V/5V systems

---

## References

### Manufacturer Websites

- [Alliance Memory](https://www.alliancememory.com/)
- [ISSI (Integrated Silicon Solution Inc.)](https://www.issi.com/)
- [Renesas Electronics](https://www.renesas.com/)
- [Infineon (former Cypress)](https://www.infineon.com/)

### Datasheets

- [AS6C62256 Datasheet](https://www.alliancememory.com/datasheets/as6c62256/)
- [AS6C4008 Datasheet](https://www.alliancememory.com/datasheets/as6c4008/)
- [AS6C8016 Datasheet](https://www.alliancememory.com/datasheets/as6c8016/)
- [R1RP0416D Series Datasheet](https://www.renesas.com/en/document/dst/r1rp0416d-series-datasheet)
- [IS61C1024 Datasheet](https://www.eit.lth.se/fileadmin/eit/courses/datablad/Memory/Sram/IS61C1024.pdf)
- [ISSI SRAM Product Overview](https://www.issi.com/WW/pdf/ISSI_SRAM.pdf)

### Distributor Links

- [DigiKey SRAM Search](https://www.digikey.com/)
- [Mouser SRAM Search](https://www.mouser.com/)
- [Octopart Component Search](https://octopart.com/)

---

*This document was generated on 2024-12-12 for GitHub Issue #34.*
