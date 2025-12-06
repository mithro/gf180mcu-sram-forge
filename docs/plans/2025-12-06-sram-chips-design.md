# SRAM Chip Generation Design

Date: 2025-12-06

## Overview

Generate three SRAM chips for the upcoming wafer.space MPW run using available slots (1x1, 1x0.5, 0.5x1). Each chip will be a separate GitHub repository forked from `gf180mcu-project-template`.

## Chip Specifications

| Repository Name | Slot | SRAMs | Capacity | Address Bits |
|-----------------|------|-------|----------|--------------|
| `gf180mcu-ic-1x1-sram-u8b24k` | 1x1 | 48 | 24,576 bytes | 15 |
| `gf180mcu-ic-1x0p5-sram-u8b9k` | 1x0.5 | 18 | 9,216 bytes | 14 |
| `gf180mcu-ic-0p5x1-sram-u8b8k` | 0.5x1 | 16 | 8,192 bytes | 13 |

### Naming Convention

`gf180mcu-ic-<slot>-sram-u<width>b<depth>k`

- `gf180mcu` - PDK/foundry
- `ic` - integrated circuit
- `<slot>` - wafer.space slot shape (1x1, 1x0p5, 0p5x1)
- `sram` - memory type
- `u` - unified interface
- `<width>b` - data width in bits (8b)
- `<depth>k` - address depth in K (24k, 9k, 8k)

### Common Parameters

- **SRAM Macro**: `gf180mcu_fd_ip_sram__sram512x8m8wm1` (512 words x 8 bits)
- **Interface**: unified_bus, 8-bit data width, mux output routing
- **Clock**: 25 MHz target frequency
- **Voltage**: 5.0V core

## Repository Workflow

### Creation Order

1. `gf180mcu-ic-1x1-sram-u8b24k` (1x1 slot)
2. `gf180mcu-ic-1x0p5-sram-u8b9k` (1x0.5 slot)
3. `gf180mcu-ic-0p5x1-sram-u8b8k` (0.5x1 slot)

### Per-Repository Steps

1. Fork `mithro/gf180mcu-project-template` to new repository name
2. Clone the forked repository locally
3. Create chip configuration YAML in sram-forge
4. Generate files with `sram-forge gen`
5. Symlink PDK: `ln -s ~/github/wafer-space/gf180mcu-project-template/gf180mcu gf180mcu`
6. Adapt testbench to template format (workaround for [issue #1](https://github.com/mithro/gf180mcu-sram-forge/issues/1))
7. Enter nix-shell
8. Run verification and build pipeline
9. Commit and push results

## Build and Verification Pipeline

All steps inside nix-shell:

```bash
# 1. RTL Simulation
make sim SLOT={slot}

# 2. Full PnR flow with DRC
make librelane SLOT={slot}

# 3. Copy final outputs
make copy-final

# 4. Generate preview image
make render-image
```

### Expected Outputs

After successful build:

```
final/
  gds/chip_top.gds      # Final GDS layout
  def/chip_top.def      # Final DEF
  sdc/chip_top.sdc      # Timing constraints
  ...
img/
  chip_top.png          # Preview image
```

## PDK Handling

To avoid duplicating the ~1GB PDK per repository, symlink to existing PDK:

```bash
ln -s ~/github/wafer-space/gf180mcu-project-template/gf180mcu gf180mcu
```

The symlink should NOT be committed to the repository (add to .gitignore if needed).

## Known Issues

### Testbench Incompatibility (Issue #1)

The sram-forge testbench generator produces files incompatible with the template's `make sim` target. See [GitHub Issue #1](https://github.com/mithro/gf180mcu-sram-forge/issues/1).

**Workaround**: Manually adapt generated testbench to match template's `chip_top_tb.py` format using `cocotb_tools.runner`.

## Success Criteria

- [ ] All 3 repositories created on GitHub under `mithro/`
- [ ] Generated Verilog is syntactically correct
- [ ] RTL simulation passes (`make sim`)
- [ ] GDS generated successfully (`make librelane`)
- [ ] DRC clean (no violations in LibreLane output)
- [ ] Preview images generated (`make render-image`)
- [ ] All results committed and pushed

## Configuration Files

Chip configurations stored in sram-forge repo:

```
chips/
  gf180mcu-ic-1x1-sram-u8b24k.yaml
  gf180mcu-ic-1x0p5-sram-u8b9k.yaml
  gf180mcu-ic-0p5x1-sram-u8b8k.yaml
```
