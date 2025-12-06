# SRAM Chips Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Generate three SRAM chips for wafer.space MPW run, verify they work, and produce GDS with DRC clean results.

**Architecture:** Fork gf180mcu-project-template for each chip, generate Verilog/config with sram-forge, adapt testbench manually, build with LibreLane in nix-shell.

**Tech Stack:** sram-forge, LibreLane, nix-shell, cocotb, GF180MCU PDK, GitHub CLI

---

## Phase 1: Create Chip Configurations

### Task 1.1: Create chips directory

**Files:**
- Create: `chips/` directory

**Step 1: Create directory**

```bash
mkdir -p chips
```

**Step 2: Commit**

```bash
git add -A && git commit -m "chore: create chips directory for chip configurations"
```

---

### Task 1.2: Create 1x1 chip configuration

**Files:**
- Create: `chips/gf180mcu-ic-1x1-sram-u8b24k.yaml`

**Step 1: Write configuration file**

```yaml
# sram-forge chip configuration
# 24KB SRAM chip for 1x1 slot

chip:
  name: gf180mcu_ic_1x1_sram_u8b24k
  description: "24KB SRAM (8-bit x 24K) for 1x1 wafer.space slot"

slot: 1x1

memory:
  macro: gf180mcu_fd_ip_sram__sram512x8m8wm1
  count: 48
  arrangement:
    prefer: rows
    orientation: N

interface:
  scheme: unified_bus
  unified_bus:
    data_width: 8
    output_routing: mux
    write_mask: false

clock:
  frequency_mhz: 25

power:
  core_voltage: 5.0
```

**Step 2: Validate configuration**

Run: `uv run sram-forge check chips/gf180mcu-ic-1x1-sram-u8b24k.yaml`
Expected: "Valid configuration" with count: 48

**Step 3: Commit**

```bash
git add chips/gf180mcu-ic-1x1-sram-u8b24k.yaml
git commit -m "feat: add 1x1 24KB SRAM chip configuration"
```

---

### Task 1.3: Create 1x0.5 chip configuration

**Files:**
- Create: `chips/gf180mcu-ic-1x0p5-sram-u8b9k.yaml`

**Step 1: Write configuration file**

```yaml
# sram-forge chip configuration
# 9KB SRAM chip for 1x0.5 slot

chip:
  name: gf180mcu_ic_1x0p5_sram_u8b9k
  description: "9KB SRAM (8-bit x 9K) for 1x0.5 wafer.space slot"

slot: 1x0p5

memory:
  macro: gf180mcu_fd_ip_sram__sram512x8m8wm1
  count: 18
  arrangement:
    prefer: rows
    orientation: N

interface:
  scheme: unified_bus
  unified_bus:
    data_width: 8
    output_routing: mux
    write_mask: false

clock:
  frequency_mhz: 25

power:
  core_voltage: 5.0
```

**Step 2: Validate configuration**

Run: `uv run sram-forge check chips/gf180mcu-ic-1x0p5-sram-u8b9k.yaml`
Expected: "Valid configuration" with count: 18

**Step 3: Commit**

```bash
git add chips/gf180mcu-ic-1x0p5-sram-u8b9k.yaml
git commit -m "feat: add 1x0.5 9KB SRAM chip configuration"
```

---

### Task 1.4: Create 0.5x1 chip configuration

**Files:**
- Create: `chips/gf180mcu-ic-0p5x1-sram-u8b8k.yaml`

**Step 1: Write configuration file**

```yaml
# sram-forge chip configuration
# 8KB SRAM chip for 0.5x1 slot

chip:
  name: gf180mcu_ic_0p5x1_sram_u8b8k
  description: "8KB SRAM (8-bit x 8K) for 0.5x1 wafer.space slot"

slot: 0p5x1

memory:
  macro: gf180mcu_fd_ip_sram__sram512x8m8wm1
  count: 16
  arrangement:
    prefer: rows
    orientation: N

interface:
  scheme: unified_bus
  unified_bus:
    data_width: 8
    output_routing: mux
    write_mask: false

clock:
  frequency_mhz: 25

power:
  core_voltage: 5.0
```

**Step 2: Validate configuration**

Run: `uv run sram-forge check chips/gf180mcu-ic-0p5x1-sram-u8b8k.yaml`
Expected: "Valid configuration" with count: 16

**Step 3: Commit**

```bash
git add chips/gf180mcu-ic-0p5x1-sram-u8b8k.yaml
git commit -m "feat: add 0.5x1 8KB SRAM chip configuration"
```

---

## Phase 2: Create 1x1 Chip Repository

### Task 2.1: Fork template repository for 1x1 chip

**Step 1: Fork repository on GitHub**

Run:
```bash
gh repo fork mithro/gf180mcu-project-template --fork-name gf180mcu-ic-1x1-sram-u8b24k --clone=false
```

Expected: Repository created at `mithro/gf180mcu-ic-1x1-sram-u8b24k`

**Step 2: Clone the forked repository**

Run:
```bash
cd ~/github/mithro
git clone git@github.com:mithro/gf180mcu-ic-1x1-sram-u8b24k.git
cd gf180mcu-ic-1x1-sram-u8b24k
```

Expected: Repository cloned successfully

---

### Task 2.2: Generate files for 1x1 chip

**Step 1: Generate Verilog, LibreLane config, testbench, and docs**

Run:
```bash
cd ~/github/mithro/gf180mcu-sram-forge
uv run sram-forge gen chips/gf180mcu-ic-1x1-sram-u8b24k.yaml -o ~/github/mithro/gf180mcu-ic-1x1-sram-u8b24k
```

Expected: Files generated in src/, librelane/, cocotb/, docs/

**Step 2: Verify generated files exist**

Run:
```bash
ls -la ~/github/mithro/gf180mcu-ic-1x1-sram-u8b24k/src/
```

Expected: `gf180mcu_ic_1x1_sram_u8b24k_sram_array.sv`, `*_core.sv`, `*_top.sv`

---

### Task 2.3: Setup PDK symlink for 1x1 chip

**Step 1: Create PDK symlink**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-1x1-sram-u8b24k
ln -s ~/github/wafer-space/gf180mcu-project-template/gf180mcu gf180mcu
```

**Step 2: Verify symlink**

Run:
```bash
ls -la gf180mcu/
```

Expected: Shows contents of PDK (gf180mcuD directory)

**Step 3: Add symlink to .gitignore if not present**

Run:
```bash
grep -q "^gf180mcu$" .gitignore || echo "gf180mcu" >> .gitignore
```

---

### Task 2.4: Commit generated files for 1x1 chip

**Step 1: Stage and commit all generated files**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-1x1-sram-u8b24k
git add -A
git commit -m "feat: add generated SRAM design files

Generated by sram-forge for 24KB (8-bit x 24K) SRAM
- 48x gf180mcu_fd_ip_sram__sram512x8m8wm1 macros
- Unified bus interface, 25 MHz, 5.0V

Files:
- src/: SystemVerilog sources
- librelane/: Physical design config
- cocotb/: Testbench (needs adaptation)
- docs/: Documentation
"
```

**Step 2: Push to GitHub**

Run:
```bash
git push origin main
```

---

### Task 2.5: Build and verify 1x1 chip in nix-shell

**Step 1: Enter nix-shell**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-1x1-sram-u8b24k
nix-shell
```

Expected: Shell prompt changes, tools available

**Step 2: Run LibreLane flow**

Run:
```bash
make librelane SLOT=1x1
```

Expected: Full flow completes (synthesis, PnR, DRC). This may take 10-30 minutes.

**Step 3: Copy final outputs**

Run:
```bash
make copy-final
```

Expected: `final/` directory created with GDS, DEF, etc.

**Step 4: Generate preview image**

Run:
```bash
make render-image
```

Expected: `img/chip_top.png` created

**Step 5: Verify DRC clean**

Check LibreLane output for DRC results. Look for:
- `KLayout.DRC: PASS` or 0 violations
- `Magic.DRC: PASS` or 0 violations

---

### Task 2.6: Commit build results for 1x1 chip

**Step 1: Commit final outputs and image**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-1x1-sram-u8b24k
git add final/ img/ .gitignore
git commit -m "feat: add GDS and preview image

LibreLane build complete:
- DRC: [PASS/FAIL - update based on results]
- GDS: final/gds/chip_top.gds
- Preview: img/chip_top.png
"
```

**Step 2: Push to GitHub**

Run:
```bash
git push origin main
```

---

## Phase 3: Create 1x0.5 Chip Repository

### Task 3.1: Fork template repository for 1x0.5 chip

**Step 1: Fork repository on GitHub**

Run:
```bash
gh repo fork mithro/gf180mcu-project-template --fork-name gf180mcu-ic-1x0p5-sram-u8b9k --clone=false
```

**Step 2: Clone the forked repository**

Run:
```bash
cd ~/github/mithro
git clone git@github.com:mithro/gf180mcu-ic-1x0p5-sram-u8b9k.git
cd gf180mcu-ic-1x0p5-sram-u8b9k
```

---

### Task 3.2: Generate files for 1x0.5 chip

**Step 1: Generate files**

Run:
```bash
cd ~/github/mithro/gf180mcu-sram-forge
uv run sram-forge gen chips/gf180mcu-ic-1x0p5-sram-u8b9k.yaml -o ~/github/mithro/gf180mcu-ic-1x0p5-sram-u8b9k
```

**Step 2: Setup PDK symlink**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-1x0p5-sram-u8b9k
ln -s ~/github/wafer-space/gf180mcu-project-template/gf180mcu gf180mcu
grep -q "^gf180mcu$" .gitignore || echo "gf180mcu" >> .gitignore
```

**Step 3: Commit generated files**

Run:
```bash
git add -A
git commit -m "feat: add generated SRAM design files

Generated by sram-forge for 9KB (8-bit x 9K) SRAM
- 18x gf180mcu_fd_ip_sram__sram512x8m8wm1 macros
- Unified bus interface, 25 MHz, 5.0V
"
git push origin main
```

---

### Task 3.3: Build and verify 1x0.5 chip

**Step 1: Enter nix-shell and build**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-1x0p5-sram-u8b9k
nix-shell
make librelane SLOT=1x0p5
make copy-final
make render-image
```

**Step 2: Commit results**

Run:
```bash
git add final/ img/ .gitignore
git commit -m "feat: add GDS and preview image

LibreLane build complete for 1x0.5 slot
"
git push origin main
```

---

## Phase 4: Create 0.5x1 Chip Repository

### Task 4.1: Fork template repository for 0.5x1 chip

**Step 1: Fork repository on GitHub**

Run:
```bash
gh repo fork mithro/gf180mcu-project-template --fork-name gf180mcu-ic-0p5x1-sram-u8b8k --clone=false
```

**Step 2: Clone the forked repository**

Run:
```bash
cd ~/github/mithro
git clone git@github.com:mithro/gf180mcu-ic-0p5x1-sram-u8b8k.git
cd gf180mcu-ic-0p5x1-sram-u8b8k
```

---

### Task 4.2: Generate files for 0.5x1 chip

**Step 1: Generate files**

Run:
```bash
cd ~/github/mithro/gf180mcu-sram-forge
uv run sram-forge gen chips/gf180mcu-ic-0p5x1-sram-u8b8k.yaml -o ~/github/mithro/gf180mcu-ic-0p5x1-sram-u8b8k
```

**Step 2: Setup PDK symlink**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-0p5x1-sram-u8b8k
ln -s ~/github/wafer-space/gf180mcu-project-template/gf180mcu gf180mcu
grep -q "^gf180mcu$" .gitignore || echo "gf180mcu" >> .gitignore
```

**Step 3: Commit generated files**

Run:
```bash
git add -A
git commit -m "feat: add generated SRAM design files

Generated by sram-forge for 8KB (8-bit x 8K) SRAM
- 16x gf180mcu_fd_ip_sram__sram512x8m8wm1 macros
- Unified bus interface, 25 MHz, 5.0V
"
git push origin main
```

---

### Task 4.3: Build and verify 0.5x1 chip

**Step 1: Enter nix-shell and build**

Run:
```bash
cd ~/github/mithro/gf180mcu-ic-0p5x1-sram-u8b8k
nix-shell
make librelane SLOT=0p5x1
make copy-final
make render-image
```

**Step 2: Commit results**

Run:
```bash
git add final/ img/ .gitignore
git commit -m "feat: add GDS and preview image

LibreLane build complete for 0.5x1 slot
"
git push origin main
```

---

## Phase 5: Final Verification

### Task 5.1: Verify all repositories exist and have results

**Step 1: Check all repositories**

Run:
```bash
gh repo view mithro/gf180mcu-ic-1x1-sram-u8b24k --json name,description
gh repo view mithro/gf180mcu-ic-1x0p5-sram-u8b9k --json name,description
gh repo view mithro/gf180mcu-ic-0p5x1-sram-u8b8k --json name,description
```

**Step 2: Verify GDS files exist in each**

Run:
```bash
for repo in gf180mcu-ic-1x1-sram-u8b24k gf180mcu-ic-1x0p5-sram-u8b9k gf180mcu-ic-0p5x1-sram-u8b8k; do
  echo "=== $repo ==="
  ls -la ~/github/mithro/$repo/final/gds/ 2>/dev/null || echo "No GDS found"
  ls -la ~/github/mithro/$repo/img/ 2>/dev/null || echo "No image found"
done
```

---

## Success Checklist

- [ ] chips/ directory created with 3 YAML configs
- [ ] gf180mcu-ic-1x1-sram-u8b24k: forked, generated, built, DRC clean, image
- [ ] gf180mcu-ic-1x0p5-sram-u8b9k: forked, generated, built, DRC clean, image
- [ ] gf180mcu-ic-0p5x1-sram-u8b8k: forked, generated, built, DRC clean, image
- [ ] All repositories pushed to GitHub
