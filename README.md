# sram-forge

A Python framework for generating SRAM-based chip designs for GF180MCU.

sram-forge produces:
- **Verilog RTL** - Fully expanded SRAM arrays with address decoding
- **LibreLane configs** - config.yaml, pdn_cfg.tcl, timing constraints
- **cocotb testbenches** - Verification tests with behavioral models
- **Documentation** - README, datasheet, memory maps
- **Complete project packages** - Ready-to-build projects from template

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

## Quick Start

```bash
# List available SRAM macros and slots
sram-forge list srams
sram-forge list slots

# Calculate how many SRAMs fit in a slot
sram-forge calc --slot 1x1 --sram gf180mcu_fd_ip_sram__sram512x8m8wm1

# Validate a chip configuration
sram-forge check examples/sram_8k_8bit.yaml

# Generate all outputs
sram-forge gen examples/sram_8k_8bit.yaml -o output/

# Create a complete buildable project
sram-forge package examples/sram_8k_8bit.yaml --name my_sram_chip -o projects/
```

## Chip Configuration

Create a YAML file to define your chip:

```yaml
chip:
  name: my_sram_chip
  description: "Custom SRAM chip"

slot: 1x1  # Die size (1x1, 0p5x1, 1x0p5, 0p5x0p5)

memory:
  macro: gf180mcu_fd_ip_sram__sram512x8m8wm1
  count: auto  # or specific number

interface:
  scheme: unified_bus
```

## Available SRAM Macros

| Macro | Size | Width | Dimensions |
|-------|------|-------|------------|
| sram64x8m8wm1 | 64 | 8 | 203.58 x 114.24 um |
| sram128x8m8wm1 | 128 | 8 | 203.58 x 156.24 um |
| sram256x8m8wm1 | 256 | 8 | 286.62 x 198.24 um |
| sram512x8m8wm1 | 512 | 8 | 369.66 x 282.24 um |

## Available Slots

| Slot | Die Size | Core Area |
|------|----------|-----------|
| 1x1 | 3932 x 5122 um | ~13 mm² |
| 0p5x1 | 1966 x 5122 um | ~6.5 mm² |
| 1x0p5 | 3932 x 2561 um | ~6.5 mm² |
| 0p5x0p5 | 1966 x 2561 um | ~3.2 mm² |

## Project Structure

```
sram_forge/
├── models/          # Pydantic data models
├── db/              # Database loaders and bundled data
├── calc/            # Fit calculation
├── generate/        # Code generators
│   ├── verilog/     # Verilog RTL templates
│   ├── librelane/   # LibreLane config templates
│   ├── testbench/   # cocotb templates
│   ├── docs/        # Documentation templates
│   └── package/     # Project package generator
├── cli/             # Click CLI
└── tests/           # pytest tests
```

## Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=sram_forge
```

## License

Apache 2.0 - See [LICENSE](LICENSE) file.
