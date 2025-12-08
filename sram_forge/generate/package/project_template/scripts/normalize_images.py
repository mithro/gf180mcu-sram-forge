#!/usr/bin/env python3
"""Normalize slot images to consistent pixel/mm scale.

All images are scaled so they have the same pixel density (pixels per mm),
making physical sizes visually comparable across different slots.

Usage:
    uv run scripts/normalize_images.py <images_dir> <slots_dir>
"""
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow", "pyyaml"]
# ///

import argparse
import sys
from pathlib import Path

import yaml
from PIL import Image


def get_slot_dimensions(slots_dir: Path) -> dict[str, tuple[int, int]]:
    """Get die dimensions (width, height in µm) for each slot from YAML files."""
    dimensions = {}
    for yaml_file in slots_dir.glob("slot_*.yaml"):
        slot_name = yaml_file.stem.replace("slot_", "")
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
        die_area = data.get("DIE_AREA", [0, 0, 0, 0])
        width_um = die_area[2] - die_area[0]
        height_um = die_area[3] - die_area[1]
        dimensions[slot_name] = (width_um, height_um)

    # Map 'default' to '1x1' for forks that use default slot naming
    if "1x1" in dimensions and "default" not in dimensions:
        dimensions["default"] = dimensions["1x1"]

    return dimensions


def normalize_images(images_dir: Path, slots_dir: Path, target_ppmm: float | None = None) -> None:
    """Normalize all slot images to consistent pixel/mm scale.

    Args:
        images_dir: Directory containing slot images (e.g., 1x1_white.png)
        slots_dir: Directory containing slot YAML files
        target_ppmm: Target pixels per mm. If None, calculated from largest slot.
    """
    dimensions = get_slot_dimensions(slots_dir)
    if not dimensions:
        print("No slot configurations found")
        return

    # Find all image files
    image_files = list(images_dir.glob("*_white.png")) + list(images_dir.glob("*_black.png"))
    if not image_files:
        print(f"No images found in {images_dir}")
        return

    # Determine target pixels/mm from the largest slot (1x1)
    # The 1x1 slot is the reference - all others will be scaled relative to it
    if target_ppmm is None:
        # Find the 1x1 image to get current rendering scale
        ref_image_path = images_dir / "1x1_white.png"
        if not ref_image_path.exists():
            # Fallback: use first available image and its slot dimensions
            ref_image_path = image_files[0]
            slot_name = ref_image_path.stem.split("_")[0]
        else:
            slot_name = "1x1"

        if slot_name not in dimensions:
            print(f"Cannot find dimensions for reference slot: {slot_name}")
            return

        with Image.open(ref_image_path) as img:
            ref_width_px = img.width

        ref_width_um = dimensions[slot_name][0]
        target_ppmm = ref_width_px / (ref_width_um / 1000)  # pixels per mm
        print(f"Reference: {slot_name} at {ref_width_px}px width, {ref_width_um}µm")
        print(f"Target scale: {target_ppmm:.1f} pixels/mm")

    # Process each image
    for image_path in image_files:
        # Extract slot name from filename (e.g., "1x1" from "1x1_white.png")
        parts = image_path.stem.split("_")
        slot_name = parts[0]
        variant = parts[1] if len(parts) > 1 else "white"

        if slot_name not in dimensions:
            print(f"Skipping {image_path.name}: no dimensions for slot '{slot_name}'")
            continue

        width_um, height_um = dimensions[slot_name]

        # Calculate target dimensions at consistent scale
        target_width = int((width_um / 1000) * target_ppmm)
        target_height = int((height_um / 1000) * target_ppmm)

        with Image.open(image_path) as img:
            current_width, current_height = img.size

            if current_width == target_width and current_height == target_height:
                print(f"{image_path.name}: already at target size ({target_width}x{target_height})")
                continue

            # Resize to target dimensions
            print(f"{image_path.name}: {current_width}x{current_height} -> {target_width}x{target_height}")
            resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            resized.save(image_path)


def main():
    parser = argparse.ArgumentParser(
        description="Normalize slot images to consistent pixel/mm scale"
    )
    parser.add_argument("images_dir", type=Path, help="Directory containing slot images")
    parser.add_argument("slots_dir", type=Path, help="Directory containing slot YAML files")
    parser.add_argument(
        "--ppmm", type=float, default=None,
        help="Target pixels per mm (default: calculated from 1x1 slot)"
    )

    args = parser.parse_args()

    if not args.images_dir.exists():
        print(f"Images directory not found: {args.images_dir}")
        sys.exit(1)

    if not args.slots_dir.exists():
        print(f"Slots directory not found: {args.slots_dir}")
        sys.exit(1)

    normalize_images(args.images_dir, args.slots_dir, args.ppmm)


if __name__ == "__main__":
    main()
