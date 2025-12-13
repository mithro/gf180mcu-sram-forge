# Research Plan: 5V/3.3V SRAM Parts for Issue #34

## Research Goals

1. **Document historical SRAM parts** popular in retro computing (Z80, 6502, etc.)
2. **Identify currently available 5V and 3.3V SRAMs** from active manufacturers
3. **Analyze RISCBOY compatibility** with Renesas R1RP0416D (256Kx16, 5V)
4. **Investigate DRAM replacement scenarios** for Z80 systems
5. **Extract and standardize interface patterns** (pinouts, signals, timing)
6. **Archive datasheets locally** for future reference
7. **Recommend target interface(s)** for sram-forge to maximize compatibility

## Key Findings from Initial Research

### Target Parts Identified

| Family | Organization | Voltage | Package | Use Case |
|--------|-------------|---------|---------|----------|
| **8-bit** |
| 6264 | 8K x 8 | 5V | 28-pin DIP | Classic NES, small retro |
| 62256 | 32K x 8 | 5V/3.3V | 28-pin DIP | Z80 systems, RC2014 |
| 628128 | 128K x 8 | 5V | 32-pin DIP | Larger Z80/retro systems |
| AS6C1008 | 128K x 8 | 2.7-5.5V | 32-pin DIP | Modern replacement |
| AS6C4008 | 512K x 8 | 2.7-5.5V | 32-pin DIP | Modern replacement |
| **16-bit** |
| R1RP0416D | 256K x 16 | 5V | 44-pin TSOP | RISCBOY target |
| IS61LV25616 | 256K x 16 | 3.3V | 44-pin TSOP | Low voltage alternative |
| **32-bit** |
| 256Kx32 modules | 256K x 32 | 5V | 66-68 pin | DSP applications |
| 512Kx32 modules | 512K x 32 | 5V/3.3V | 68-pin PLCC | High-performance |

### Active Manufacturers
- **Alliance Memory**: Drop-in replacements for legacy parts (AS6C series)
- **ISSI**: x8, x16, x32 configs in 5V/3.3V/1.8V
- **Renesas**: High-speed SRAMs including R1RP0416D
- **Cypress/Infineon**: Legacy parts still available

### RISCBOY Context
- Uses 512 KiB, 16-bit wide external SRAM
- The R1RP0416D (256Kx16) is the likely target part
- 5V operation, 10-12ns access time, 44-pin TSOP/SOJ

### Z80/Retro Computing Context
- **DRAM chips to replace**: 4116 (16Kx1), 4164 (64Kx1), 41256 (256Kx1)
- **SRAM alternatives**: 62256 and 628128 are most common
- **Open-source Z80**: Project targeting silicon-proven drop-in replacement

---

## Research Phases and Execution Plan

### Phase 1: Historical SRAM Discovery
**Goal**: Build comprehensive list of classic SRAM parts and their usage

**Sub-agents to launch**:
1. **solution-researcher**: Research classic SRAM families (6116, 6264, 62256, 628128, 621024) - their history, pin-compatibility families, which systems used them
2. **solution-researcher**: Research DRAM parts used in Z80/6502 systems (4116, 4164, 41256, 44256) and SRAM replacement strategies

**Outputs**:
- Table of classic SRAM parts with specs
- Table of DRAM parts that could be replaced with SRAM
- List of retro systems and their memory configurations

---

### Phase 2: Current Availability Survey
**Goal**: Document what's still being manufactured and sold

**Sub-agents to launch**:
1. **solution-researcher**: Survey current 5V SRAM availability from Alliance Memory, ISSI, Renesas, Cypress/Infineon - focus on DIP and SOIC packages
2. **solution-researcher**: Survey current 3.3V SRAM availability - same manufacturers

**Outputs**:
- Table of currently available parts with:
  - Part numbers
  - Organization (e.g., 32Kx8)
  - Voltage range
  - Access time
  - Package options
  - Distributor availability (DigiKey, Mouser, etc.)
  - Approximate pricing

---

### Phase 3: Datasheet Collection
**Goal**: Download and archive key datasheets locally

**Directory structure**:
```
docs/research/sram-datasheets/
├── alliance-memory/
│   ├── AS6C62256.pdf
│   ├── AS6C1008.pdf
│   └── AS6C4008.pdf
├── renesas/
│   └── R1RP0416D.pdf
├── issi/
│   └── IS62C256.pdf
└── classic/
    ├── HM6264.pdf
    ├── HM62256.pdf
    └── HM628128.pdf
```

**Execution**: Use WebFetch to download PDFs, or document URLs if direct download not possible

---

### Phase 4: Interface Analysis
**Goal**: Extract and compare pinouts and timing from datasheets

**Sub-agents to launch**:
1. **data-scientist**: Analyze 8-bit SRAM pinouts (6264, 62256, 628128) - create normalized pinout table, identify common patterns
2. **data-scientist**: Analyze 16-bit SRAM pinouts (R1RP0416D and similar) - focus on RISCBOY compatibility
3. **data-scientist**: Analyze 32-bit SRAM pinouts (256Kx32, 512Kx32) - identify byte-enable patterns, package constraints

**Key interface parameters to extract**:
- Pin assignments (address, data, control)
- Control signal polarity (active-high vs active-low)
- Chip enable (CE/CS), Output enable (OE), Write enable (WE)
- Byte enables for 16-bit+ parts
- Timing: access time, cycle time, setup/hold

**Outputs**:
- Normalized pinout comparison table
- Signal naming convention summary
- Timing parameter ranges

---

### Phase 5: sram-forge Compatibility Analysis
**Goal**: Map external SRAM interfaces to sram-forge's interface model

**Current sram-forge interface (from exploration)**:
- Unified bus with configurable data_width (8, 10, 12, 16, etc.)
- Control signals: CLK, CE_n (active-low), WE_n (active-low)
- Optional write mask
- Bidirectional data bus

**Analysis needed**:
- How well does sram-forge's interface match standard SRAM pinouts?
- What modifications would enable direct compatibility?
- Pin budget verification for 16-bit and 32-bit interfaces

---

### Phase 6: Synthesis and Recommendations
**Goal**: Produce actionable recommendations for sram-forge

**Deliverables**:
1. Update GitHub issue #34 with research findings
2. Recommend primary target interface(s):
   - **8-bit**: 62256-compatible (28-pin, most common)
   - **16-bit**: R1RP0416D-compatible (RISCBOY compatible)
   - **32-bit**: If feasible within pin budget
3. Document any interface modifications needed
4. Create interface compatibility matrix

---

## Execution Strategy

### Parallelization
- Phases 1 and 2 can run in parallel (historical + current)
- Phase 3 (datasheet collection) can start once part lists are known
- Phase 4 requires datasheets from Phase 3
- Phases 5 and 6 are sequential after Phase 4

### Sub-agent Types to Use
| Phase | Agent Type | Count | Purpose |
|-------|-----------|-------|---------|
| 1 | solution-researcher | 2 | Historical SRAM and DRAM research |
| 2 | solution-researcher | 2 | Current availability survey |
| 3 | general-purpose | 1 | Datasheet downloads |
| 4 | data-scientist | 2 | Pinout and timing analysis |
| 5 | backend-architect | 1 | Interface compatibility analysis |
| 6 | documentation-writer | 1 | Final synthesis and issue update |

### Output Location
All research outputs will be documented in:
- `docs/research/sram-interfaces/` - Detailed findings
- GitHub Issue #34 - Summary and recommendations
- `docs/research/sram-datasheets/` - Archived datasheets

---

## Key Questions to Answer

1. **Is there a de-facto standard 5V SRAM interface?**
   - 8-bit: 62256 (28-pin) appears to be the most common standard
   - 16-bit: R1RP0416D (44-pin) for RISCBOY compatibility
   - 32-bit: 256Kx32 modules (66-68 pin) for DSP applications

2. **What interface would maximize retro computing compatibility?**
   - Z80 systems: 62256/628128 compatible (active-low CE, OE, WE)
   - RISCBOY: R1RP0416D compatible (16-bit, 5V)
   - DSP systems: 32-bit with byte enables

3. **Can sram-forge support multiple interface standards?**
   - Current architecture supports flexible interfaces
   - May need to add interface "profiles" or templates
   - Consider: 62256-mode, R1RP0416D-mode, custom-mode

4. **Pin budget for each data width on 1x1 slot (52 pins available)?**
   | Width | Control | Addr | Data | Byte-EN | Total | Spare |
   |-------|---------|------|------|---------|-------|-------|
   | 8-bit | 3 | 15 | 8 | 0 | 26 | 26 |
   | 16-bit | 3 | 14 | 16 | 0-2 | 33-35 | 17-19 |
   | 32-bit | 3 | 13 | 32 | 0-4 | 48-52 | 0-4 |

   32-bit is feasible but tight; byte-enables may need to be optional

---

## Success Criteria

- [ ] Comprehensive list of historical and current SRAM parts (8-bit, 16-bit, 32-bit)
- [ ] Datasheets archived for key parts in each width category
- [ ] Pinout comparison tables for each width (8/16/32-bit)
- [ ] Interface recommendations documented for:
  - Z80/retro computing compatibility (8-bit)
  - RISCBOY compatibility (16-bit)
  - High-performance applications (32-bit)
- [ ] GitHub issue #34 updated with findings
- [ ] Clear path forward for RISCBOY compatibility
- [ ] Assessment of 32-bit feasibility within 1x1 slot pin budget
