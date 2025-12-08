#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml", "Pillow"]
# ///
"""
Generate slot documentation with usable area calculations.

Usage:
    uv run scripts/generate_slot_docs.py --output-dir gh-pages/
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import yaml

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# Seal ring width in microns (26µm on each side)
SEAL_RING_UM = 26


@dataclass
class SlotInfo:
    """Information about a slot size."""

    name: str  # "1x1", "0p5x1", etc.
    label: str  # "1×1 (Full)"

    # Die area (total silicon size including seal ring) in microns
    die_width_um: int
    die_height_um: int

    # Core area (usable area inside IO ring) in microns
    core_width_um: int
    core_height_um: int

    # IO counts
    io_bidir: int = 0
    io_inputs: int = 0
    io_analog: int = 0
    io_power_pairs: int = 0

    # === Die size (total silicon) ===
    @property
    def die_width_mm(self) -> float:
        return self.die_width_um / 1000

    @property
    def die_height_mm(self) -> float:
        return self.die_height_um / 1000

    @property
    def die_area_mm2(self) -> float:
        return self.die_width_mm * self.die_height_mm

    # === Usable silicon area (die minus seal ring) ===
    @property
    def slot_width_um(self) -> int:
        return self.die_width_um - (2 * SEAL_RING_UM)

    @property
    def slot_height_um(self) -> int:
        return self.die_height_um - (2 * SEAL_RING_UM)

    @property
    def slot_width_mm(self) -> float:
        return self.slot_width_um / 1000

    @property
    def slot_height_mm(self) -> float:
        return self.slot_height_um / 1000

    @property
    def slot_area_mm2(self) -> float:
        return self.slot_width_mm * self.slot_height_mm

    # === Core area (inside IO ring) ===
    @property
    def core_width_mm(self) -> float:
        return self.core_width_um / 1000

    @property
    def core_height_mm(self) -> float:
        return self.core_height_um / 1000

    @property
    def core_area_mm2(self) -> float:
        return self.core_width_mm * self.core_height_mm

    # === Overhead calculations ===
    @property
    def io_overhead_pct(self) -> float:
        """Percentage of die area used by IO ring, seal ring, etc."""
        if self.die_area_mm2 == 0:
            return 0.0
        return ((self.die_area_mm2 - self.core_area_mm2) / self.die_area_mm2) * 100

    @property
    def seal_ring_area_mm2(self) -> float:
        """Area consumed by seal ring."""
        return self.die_area_mm2 - self.slot_area_mm2

    @property
    def io_ring_area_mm2(self) -> float:
        """Area consumed by IO ring (slot area minus core area)."""
        return self.slot_area_mm2 - self.core_area_mm2

    @property
    def io_signal_total(self) -> int:
        """Total signal IO pins (bidir + inputs + analog)."""
        return self.io_bidir + self.io_inputs + self.io_analog

    @property
    def io_power_total(self) -> int:
        """Total power pads (DVDD + DVSS)."""
        return self.io_power_pairs * 2

    @property
    def pad_total(self) -> int:
        """Total number of pads (signal IOs + power pads)."""
        return self.io_signal_total + self.io_power_total


# Slot labels mapping
SLOT_LABELS = {
    "1x1": "1×1 (Full)",
    "0p5x1": "0.5×1 (Half Width)",
    "1x0p5": "1×0.5 (Half Height)",
    "0p5x0p5": "0.5×0.5 (Quarter)",
}


def parse_pad_lef(lef_dir: Path) -> dict[str, tuple[float, float]]:
    """Parse LEF files to get pad cell dimensions."""
    pad_sizes = {}

    for lef_file in lef_dir.glob("*.lef"):
        with open(lef_file) as f:
            content = f.read()

        # Extract SIZE X BY Y
        match = re.search(r"SIZE\s+([\d.]+)\s+BY\s+([\d.]+)", content)
        if match:
            width = float(match.group(1))
            height = float(match.group(2))
            cell_name = lef_file.stem
            pad_sizes[cell_name] = (width, height)

    return pad_sizes


def validate_geometry(slots: dict[str, SlotInfo], pad_sizes: dict[str, tuple[float, float]]) -> list[str]:
    """Validate slot dimensions against pad geometry."""
    warnings = []

    # Get typical IO pad height (use bi_t as reference)
    io_pad_height = None
    for name, (w, h) in pad_sizes.items():
        if "bi_t" in name or "bi_24t" in name:
            io_pad_height = h
            break

    if io_pad_height is None:
        warnings.append("Could not find IO pad dimensions for validation")
        return warnings

    # Expected core offset = pad height + margin
    # We expect ~350µm pad + ~92µm margin = ~442µm
    expected_min_offset = io_pad_height  # At minimum, pad height

    for name, slot in slots.items():
        # Calculate actual offset from YAML
        # CORE_AREA starts at [442, 442, ...] meaning 442µm offset
        # This is derived from DIE - CORE
        die_width = slot.die_width_um
        core_width = slot.core_width_um
        offset = (die_width - core_width) / 2

        if offset < expected_min_offset:
            warnings.append(
                f"{name}: Core offset ({offset:.0f}µm) is less than pad height ({io_pad_height:.0f}µm)"
            )

    return warnings


# Use GITHUB_REPOSITORY env var when running in GitHub Actions, fallback to upstream
REPO = os.environ.get("GITHUB_REPOSITORY", "wafer-space/gf180mcu-project-template")
IMAGE_ARTIFACT_SUFFIX = "_image"
THUMBNAIL_WIDTH = 400
JPEG_QUALITY = 85


def download_images(output_dir: Path) -> bool:
    """Download slot images from latest GitHub Actions run."""
    if not HAS_PIL:
        print("Warning: Pillow not installed, skipping image download")
        return False

    images_dir = output_dir / "images"
    thumbnails_dir = output_dir / "thumbnails"
    images_dir.mkdir(parents=True, exist_ok=True)
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Get latest successful run
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO}/actions/runs?branch=main&status=success&per_page=1",
             "-q", ".workflow_runs[0].id"],
            capture_output=True, text=True, check=True
        )
        run_id = result.stdout.strip()
        if not run_id:
            print("No successful runs found")
            return False

        print(f"Downloading images from run {run_id}...")

        # Get artifacts
        result = subprocess.run(
            ["gh", "api", f"repos/{REPO}/actions/runs/{run_id}/artifacts",
             "-q", ".artifacts[].name"],
            capture_output=True, text=True, check=True
        )
        artifacts = [a for a in result.stdout.strip().split("\n") if a.endswith(IMAGE_ARTIFACT_SUFFIX)]

        for artifact_name in artifacts:
            slot_name = artifact_name.replace(IMAGE_ARTIFACT_SUFFIX, "")
            print(f"  Downloading {slot_name}...")

            with tempfile.TemporaryDirectory() as tmp_dir:
                subprocess.run(
                    ["gh", "run", "download", run_id, "-R", REPO, "-n", artifact_name, "-D", tmp_dir],
                    check=True, capture_output=True
                )

                for png_file in Path(tmp_dir).glob("*.png"):
                    variant = "black" if "black" in png_file.name.lower() else "white"
                    new_name = f"{slot_name}_{variant}.png"

                    # Copy full image
                    final_path = images_dir / new_name
                    shutil.move(str(png_file), str(final_path))

                    # Create thumbnail
                    thumb_path = thumbnails_dir / f"{slot_name}_{variant}.jpg"
                    with Image.open(final_path) as img:
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        width, height = img.size
                        if width > THUMBNAIL_WIDTH:
                            ratio = THUMBNAIL_WIDTH / width
                            img = img.resize((THUMBNAIL_WIDTH, int(height * ratio)), Image.Resampling.LANCZOS)
                        img.save(thumb_path, "JPEG", quality=JPEG_QUALITY, optimize=True)

        return True

    except subprocess.CalledProcessError as e:
        print(f"Error downloading images: {e}")
        return False
    except FileNotFoundError:
        print("Error: 'gh' CLI not found. Install GitHub CLI to download images.")
        return False


def parse_slot_yaml(yaml_path: Path) -> SlotInfo:
    """Parse a slot YAML file and extract slot information."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    # Extract slot name from filename (e.g., "slot_1x1.yaml" -> "1x1")
    name = yaml_path.stem.replace("slot_", "")
    label = SLOT_LABELS.get(name, name)

    # Parse DIE_AREA: [x1, y1, x2, y2]
    die_area = data.get("DIE_AREA", [0, 0, 0, 0])
    die_width_um = die_area[2] - die_area[0]
    die_height_um = die_area[3] - die_area[1]

    # Parse CORE_AREA: [x1, y1, x2, y2]
    core_area = data.get("CORE_AREA", [0, 0, 0, 0])
    core_width_um = core_area[2] - core_area[0]
    core_height_um = core_area[3] - core_area[1]

    # Count IOs from pad lists
    io_bidir = 0
    io_inputs = 0
    io_analog = 0
    io_power_pairs = 0

    for direction in ["PAD_SOUTH", "PAD_EAST", "PAD_NORTH", "PAD_WEST"]:
        pads = data.get(direction, [])
        for pad in pads:
            pad_str = str(pad)
            if "bidir" in pad_str:
                io_bidir += 1
            elif "inputs" in pad_str or pad_str in ("clk_pad", "rst_n_pad"):
                io_inputs += 1
            elif "analog" in pad_str:
                io_analog += 1
            elif "dvdd_pads" in pad_str:
                io_power_pairs += 1
            # dvss_pads are counted with dvdd as pairs

    return SlotInfo(
        name=name,
        label=label,
        die_width_um=die_width_um,
        die_height_um=die_height_um,
        core_width_um=core_width_um,
        core_height_um=core_height_um,
        io_bidir=io_bidir,
        io_inputs=io_inputs,
        io_analog=io_analog,
        io_power_pairs=io_power_pairs,
    )


def load_all_slots(slots_dir: Path) -> dict[str, SlotInfo]:
    """Load all slot configurations from a directory."""
    slots = {}
    for yaml_file in sorted(slots_dir.glob("slot_*.yaml")):
        slot = parse_slot_yaml(yaml_file)
        slots[slot.name] = slot
    return slots


def generate_json(slots: dict[str, SlotInfo], output_path: Path) -> None:
    """Generate JSON file with slot information."""
    data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "slots": {},
    }

    # Sort by slot order: 1x1 first
    slot_order = ["1x1", "0p5x1", "1x0p5", "0p5x0p5"]
    sorted_names = sorted(slots.keys(), key=lambda x: slot_order.index(x) if x in slot_order else 99)

    for name in sorted_names:
        slot = slots[name]
        data["slots"][name] = {
            "label": slot.label,
            "die": {
                "width_um": slot.die_width_um,
                "height_um": slot.die_height_um,
                "width_mm": round(slot.die_width_mm, 3),
                "height_mm": round(slot.die_height_mm, 3),
                "area_mm2": round(slot.die_area_mm2, 2),
            },
            "slot": {
                "width_um": slot.slot_width_um,
                "height_um": slot.slot_height_um,
                "width_mm": round(slot.slot_width_mm, 3),
                "height_mm": round(slot.slot_height_mm, 3),
                "area_mm2": round(slot.slot_area_mm2, 2),
            },
            "core": {
                "width_um": slot.core_width_um,
                "height_um": slot.core_height_um,
                "width_mm": round(slot.core_width_mm, 3),
                "height_mm": round(slot.core_height_mm, 3),
                "area_mm2": round(slot.core_area_mm2, 2),
            },
            "io_overhead_pct": round(slot.io_overhead_pct, 1),
            "io": {
                "bidir": slot.io_bidir,
                "inputs": slot.io_inputs,
                "analog": slot.io_analog,
                "power_pairs": slot.io_power_pairs,
                "power_total": slot.io_power_total,
                "signal_total": slot.io_signal_total,
                "pad_total": slot.pad_total,
            },
        }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Generated: {output_path}")


def generate_markdown(slots: dict[str, SlotInfo], output_path: Path) -> None:
    """Generate Markdown file with slot information."""
    lines = [
        "# GF180MCU Slot Sizes",
        "",
        "This document describes the available slot sizes for wafer.space projects.",
        "",
        "## Understanding Slot Dimensions",
        "",
        "Each slot has three important size measurements:",
        "",
        "```",
        "┌─────────────────────────────────────────┐",
        "│             SEAL RING (26µm)            │",
        "│  ┌───────────────────────────────────┐  │",
        "│  │           IO RING                 │  │",
        "│  │  ┌─────────────────────────────┐  │  │",
        "│  │  │                             │  │  │",
        "│  │  │        CORE AREA            │  │  │",
        "│  │  │    (Your Design Area)       │  │  │",
        "│  │  │                             │  │  │",
        "│  │  └─────────────────────────────┘  │  │",
        "│  │                                   │  │",
        "│  └───────────────────────────────────┘  │",
        "│                                         │",
        "└─────────────────────────────────────────┘",
        " ◄─────────── DIE SIZE ──────────────────►",
        "   ◄────── USABLE SILICON ────────────►",
        "      ◄────── CORE SIZE ───────────►",
        "```",
        "",
        "- **Die Size**: The actual physical silicon dimensions, including all peripheral structures.",
        "- **Usable Silicon**: Die size minus the seal ring (26µm on each edge). The seal ring protects the chip from damage during dicing.",
        "- **Core Area**: The usable design area inside the IO ring where your logic is placed.",
        "",
        "## Slot Dimensions",
        "",
        "| Slot | Die Size | Usable Silicon | Core Area | IO Overhead |",
        "|------|----------|-----------|-----------|-------------|",
    ]

    slot_order = ["1x1", "0p5x1", "1x0p5", "0p5x0p5"]
    sorted_names = sorted(slots.keys(), key=lambda x: slot_order.index(x) if x in slot_order else 99)

    for name in sorted_names:
        slot = slots[name]
        die_size = f"{slot.die_width_mm:.2f} × {slot.die_height_mm:.2f}mm ({slot.die_area_mm2:.2f}mm²)"
        slot_size = f"{slot.slot_width_mm:.2f} × {slot.slot_height_mm:.2f}mm ({slot.slot_area_mm2:.2f}mm²)"
        core_size = f"{slot.core_width_mm:.2f} × {slot.core_height_mm:.2f}mm ({slot.core_area_mm2:.2f}mm²)"
        overhead = f"{slot.io_overhead_pct:.0f}%"
        lines.append(f"| {slot.label} | {die_size} | {slot_size} | {core_size} | {overhead} |")

    lines.extend([
        "",
        "## IO Breakdown",
        "",
        "| Slot | Bidirectional | Inputs | Analog | Total IOs | Power Pairs | Total Pads |",
        "|------|---------------|--------|--------|-----------|-------------|------------|",
    ])

    for name in sorted_names:
        slot = slots[name]
        lines.append(
            f"| {slot.label} | {slot.io_bidir} | {slot.io_inputs} | {slot.io_analog} | {slot.io_signal_total} | {slot.io_power_pairs} | {slot.pad_total} |"
        )

    lines.extend([
        "",
        "## Notes",
        "",
        "- **IO Overhead**: Percentage of die area consumed by seal ring and IO ring",
        "- **Power Pairs**: Each pair consists of one DVDD and one DVSS pad",
        "",
        f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
    ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Generated: {output_path}")


def generate_html(
    slots: dict[str, SlotInfo],
    output_path: Path,
    images_dir: Path | None = None,
) -> None:
    """Generate HTML file with slot information for GitHub Pages."""
    slot_order = ["1x1", "0p5x1", "1x0p5", "0p5x0p5"]
    sorted_names = sorted(slots.keys(), key=lambda x: slot_order.index(x) if x in slot_order else 99)

    # Check which images exist
    def get_image_path(name: str, variant: str) -> str | None:
        if images_dir is None:
            return None
        thumb = images_dir / "thumbnails" / f"{name}_{variant}.jpg"
        if thumb.exists():
            return f"thumbnails/{name}_{variant}.jpg"
        return None

    generated_time = datetime.now(timezone.utc).strftime("%d %b %Y %H:%M UTC")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GF180MCU Slot Sizes - wafer.space</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        h1 {{ text-align: center; margin-bottom: 10px; }}
        .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; }}
        .subtitle a {{ color: #0066cc; text-decoration: none; }}
        .section {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 0 auto 20px auto;
            max-width: 1200px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{ margin: 0 0 20px 0; text-align: center; }}
        .section > p {{ text-align: center; color: #555; margin-bottom: 20px; }}
        .size-diagram {{
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin: 0 auto 20px auto;
            max-width: 500px;
            overflow-x: auto;
        }}
        .size-diagram pre {{
            margin: 0;
            font-family: monospace;
            font-size: 12px;
            line-height: 1.3;
            white-space: pre;
            color: #333;
        }}
        .size-definitions {{
            max-width: 800px;
            margin: 0 auto;
            text-align: left;
        }}
        .size-definitions dt {{
            font-weight: bold;
            color: #333;
            margin-top: 15px;
        }}
        .size-definitions dd {{
            margin: 5px 0 0 0;
            color: #555;
            line-height: 1.5;
        }}
        .slots-grid {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            align-items: flex-start;
            gap: 20px;
            margin: 0 auto;
        }}
        .slot-card {{
            background: #fafafa;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            flex-shrink: 0;
        }}
        .slot-card h3 {{ margin: 0 0 8px 0; font-size: 1.15em; text-align: center; }}
        .slot-card .dims {{ font-size: 0.9em; color: #666; margin-bottom: 15px; text-align: center; white-space: nowrap; }}
        .slot-card .specs {{ font-size: 0.85em; }}
        .slot-card .specs dt {{ font-weight: bold; color: #444; margin-top: 12px; }}
        .slot-card .specs dd {{ margin: 3px 0 0 0; color: #555; }}
        .slot-card img {{
            display: block;
            margin: 15px auto;
            border-radius: 4px;
            cursor: pointer;
            /* No max-width - display at natural thumbnail size for consistent scale */
        }}
        .slot-card img:hover {{ opacity: 0.9; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{ background: #f5f5f5; font-weight: 600; }}
        .download-link {{
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        .download-link:hover {{ background: #0055aa; }}
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0; top: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.9);
        }}
        .modal img {{
            max-width: 95%; max-height: 95%;
            margin: auto;
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
        }}
        .modal .close {{
            position: absolute;
            top: 20px; right: 35px;
            color: white;
            font-size: 40px;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <h1>GF180MCU Slot Sizes</h1>
    <p class="subtitle">
        wafer.space Project Template |
        <a href="https://github.com/wafer-space/gf180mcu-project-template">GitHub</a> |
        Generated: {generated_time}
    </p>

    <div class="section">
        <h2>Understanding Slot Dimensions</h2>
        <p>Each slot has three important size measurements:</p>
        <div class="size-diagram">
            <pre>
┌─────────────────────────────────────────┐
│             SEAL RING (26µm)            │
│  ┌───────────────────────────────────┐  │
│  │           IO RING                 │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │                             │  │  │
│  │  │        CORE AREA            │  │  │
│  │  │    (Your Design Area)       │  │  │
│  │  │                             │  │  │
│  │  └─────────────────────────────┘  │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
 ◄─────────── DIE SIZE ──────────────────►
   ◄────── USABLE SILICON ────────────►
      ◄────── CORE SIZE ───────────►
            </pre>
        </div>
        <dl class="size-definitions">
            <dt>Die Size</dt>
            <dd>The actual physical silicon dimensions. This is the total area of the chip including all peripheral structures.</dd>
            <dt>Usable Silicon</dt>
            <dd>The die size minus the seal ring (26µm on each edge). The seal ring protects the chip from damage during dicing and provides a moisture barrier. This is the area available inside the seal ring.</dd>
            <dt>Core Area</dt>
            <dd>The usable design area inside the IO ring. This is where your digital logic, analog circuits, and other design elements are placed. The IO ring contains the pad cells that connect your design to the outside world.</dd>
        </dl>
    </div>

    <div class="section">
        <h2>Available Slots</h2>
        <div class="slots-grid">
"""

    for name in sorted_names:
        slot = slots[name]

        img_html = ""
        img_path = get_image_path(name, "white")
        if img_path:
            full_img = f"images/{name}_white.png"
            img_html = f'<img src="{img_path}" alt="{slot.label}" onclick="openModal(\'{full_img}\')">'

        html += f"""            <div class="slot-card">
                <h3>{slot.label}</h3>
                {img_html}
                <dl class="specs">
                    <dt>Die Size</dt>
                    <dd>{slot.die_width_mm:.2f}mm × {slot.die_height_mm:.2f}mm ({slot.die_area_mm2:.2f}mm²)</dd>
                    <dt>Usable Silicon</dt>
                    <dd>{slot.slot_width_mm:.2f}mm × {slot.slot_height_mm:.2f}mm ({slot.slot_area_mm2:.2f}mm²)</dd>
                    <dt>Core Area</dt>
                    <dd>{slot.core_width_mm:.2f}mm × {slot.core_height_mm:.2f}mm ({slot.core_area_mm2:.2f}mm²)</dd>
                    <dt>IO Overhead</dt>
                    <dd>{slot.io_overhead_pct:.0f}%</dd>
                    <dt>Total IOs</dt>
                    <dd>{slot.io_signal_total} (bidir: {slot.io_bidir}, in: {slot.io_inputs}, analog: {slot.io_analog})</dd>
                    <dt>Total Pads</dt>
                    <dd>{slot.pad_total} ({slot.io_signal_total} IO + {slot.io_power_total} power)</dd>
                </dl>
            </div>
"""

    html += """        </div>
    </div>

    <div class="section">
        <h2>Detailed Specifications</h2>
        <table>
            <thead>
                <tr>
                    <th>Slot</th>
                    <th>Die Size</th>
                    <th>Usable Silicon</th>
                    <th>Core Area</th>
                    <th>IO Overhead</th>
                    <th>Bidir</th>
                    <th>Inputs</th>
                    <th>Analog</th>
                    <th>Total IOs</th>
                    <th>Power</th>
                    <th>Total Pads</th>
                </tr>
            </thead>
            <tbody>
"""

    for name in sorted_names:
        slot = slots[name]
        html += f"""                <tr>
                    <td>{slot.label}</td>
                    <td>{slot.die_width_mm:.2f} × {slot.die_height_mm:.2f}mm<br><small>({slot.die_area_mm2:.2f}mm²)</small></td>
                    <td>{slot.slot_width_mm:.2f} × {slot.slot_height_mm:.2f}mm<br><small>({slot.slot_area_mm2:.2f}mm²)</small></td>
                    <td>{slot.core_width_mm:.2f} × {slot.core_height_mm:.2f}mm<br><small>({slot.core_area_mm2:.2f}mm²)</small></td>
                    <td>{slot.io_overhead_pct:.0f}%</td>
                    <td>{slot.io_bidir}</td>
                    <td>{slot.io_inputs}</td>
                    <td>{slot.io_analog}</td>
                    <td>{slot.io_signal_total}</td>
                    <td>{slot.io_power_pairs} pairs</td>
                    <td>{slot.pad_total}</td>
                </tr>
"""

    html += """            </tbody>
        </table>
        <div style="text-align: center;">
            <a href="slots.json" class="download-link">Download JSON</a>
        </div>
    </div>

    <div id="imageModal" class="modal" onclick="closeModal()">
        <span class="close">&times;</span>
        <img id="modalImage">
    </div>

    <script>
        function openModal(src) {
            document.getElementById('imageModal').style.display = 'block';
            document.getElementById('modalImage').src = src;
        }
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
    </script>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate slot documentation with usable area calculations"
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("gh-pages"),
        help="Output directory for generated files (default: gh-pages)",
    )
    parser.add_argument(
        "--slots-dir",
        type=Path,
        default=None,
        help="Directory containing slot YAML files (default: librelane/slots)",
    )
    parser.add_argument(
        "--download-images",
        action="store_true",
        help="Download slot images from latest GitHub Actions run",
    )

    args = parser.parse_args()

    # Determine paths
    script_dir = Path(__file__).parent.parent
    slots_dir = args.slots_dir or (script_dir / "librelane" / "slots")
    output_dir = args.output_dir

    if not slots_dir.exists():
        print(f"Error: Slots directory not found: {slots_dir}")
        return 1

    # Load and generate
    print(f"Loading slots from: {slots_dir}")
    slots = load_all_slots(slots_dir)

    if not slots:
        print("Error: No slot configurations found")
        return 1

    print(f"Found {len(slots)} slot configurations")

    # Validate against pad geometry if available
    pdk_io_dir = script_dir / "gf180mcu" / "gf180mcuD" / "libs.ref" / "gf180mcu_fd_io" / "lef"
    if pdk_io_dir.exists():
        print(f"Validating against pad geometry from: {pdk_io_dir}")
        pad_sizes = parse_pad_lef(pdk_io_dir)
        warnings = validate_geometry(slots, pad_sizes)
        for warning in warnings:
            print(f"  WARNING: {warning}")
        if not warnings:
            print("  Validation passed: geometry consistent")
    else:
        print("Note: PDK not found, skipping geometry validation")

    # Download images if requested
    if args.download_images:
        print("Downloading images from GitHub Actions...")
        if download_images(output_dir):
            print("Images downloaded successfully")
        else:
            print("Image download failed or skipped")

    # Generate outputs
    generate_json(slots, output_dir / "slots.json")
    generate_markdown(slots, output_dir / "SLOTS.md")
    generate_html(slots, output_dir / "index.html", images_dir=output_dir)

    print(f"\nAll outputs written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
