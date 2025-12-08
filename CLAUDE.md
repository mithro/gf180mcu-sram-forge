# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sram-forge is a CLI tool that generates SRAM-based chip designs for the GF180MCU PDK. It takes a YAML chip configuration file and produces:
- SystemVerilog sources (chip top, core, SRAM array)
- LibreLane physical design configuration (config.yaml, PDN, SDC)
- cocotb testbench with behavioral model
- Documentation (README, datasheet, memory map)

The generated outputs form a complete buildable project for wafer.space MPW runs.

## Common Commands

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run all tests
uv run pytest

# Run single test file
uv run pytest sram_forge/tests/test_calc_fit.py

# Run specific test
uv run pytest sram_forge/tests/test_calc_fit.py::test_calculate_fit_basic -v

# CLI usage
uv run sram-forge --help
uv run sram-forge list srams
uv run sram-forge list slots
uv run sram-forge calc --slot 1x1 --sram gf180mcu_fd_ip_sram__sram512x8m8wm1
uv run sram-forge check examples/sram_1x1_u8b8k.yaml
uv run sram-forge gen examples/sram_1x1_u8b8k.yaml -o ./output
uv run sram-forge package examples/sram_1x1_u8b8k.yaml --name my-chip -o ./projects
```

## Architecture

### Data Flow
```
YAML config → load_chip_config() → ChipConfig (Pydantic model)
                                          ↓
srams.yaml → load_srams() → dict[str, SramSpec] ─┬─→ calculate_fit() → FitResult
slots.yaml → load_slots() → dict[str, SlotSpec] ─┘
                                                           ↓
                                             Generator Engines (Jinja2)
                                                           ↓
                                              Generated files (sv, yaml, py, md)
```

### Key Modules

- **`models/`** - Pydantic models for all data structures:
  - `SramSpec`: SRAM macro specs (size, ports, timing, files)
  - `SlotSpec`: Die/core dimensions, IO budget
  - `ChipConfig`: Complete chip configuration from YAML

- **`db/`** - Data loading:
  - `loader.py`: YAML parsing into Pydantic models
  - `data/srams.yaml`: GF180MCU PDK SRAM specifications
  - `data/slots.yaml`: wafer.space slot definitions (1x1, 0p5x1, etc.)

- **`calc/fit.py`** - Calculates how many SRAMs fit in a slot given dimensions and halo spacing

- **`generate/`** - Output generators using Jinja2 templates:
  - `verilog/`: SystemVerilog chip top, core, SRAM array
  - `librelane/`: Physical design config for LibreLane flow
  - `testbench/`: cocotb tests and behavioral model
  - `docs/`: README, datasheet, memory map
  - `package/`: Complete buildable project structure

- **`cli/main.py`** - Click-based CLI with subcommands: list, calc, check, gen, package

### Configuration Schema

Chip configurations (e.g., `examples/sram_1x1_u8b8k.yaml`) define:
- `chip`: name, description
- `slot`: target slot (1x1, 0p5x1, 1x0p5, 0p5x0p5)
- `memory`: macro name, count (or "auto"), arrangement
- `interface`: unified_bus config (data_width, output_routing, write_mask)
- `clock`: target frequency
- `power`: core voltage

### SRAM Port Model

Follows Yosys `$mem_v2` conventions. PDK SRAMs have single RW port with:
- CLK, CEN (enable, active-low), GWEN (write enable, active-low)
- WEN[7:0] (per-bit write mask), A[N:0] (address), D[7:0], Q[7:0]
