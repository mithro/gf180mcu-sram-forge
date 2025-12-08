#!/usr/bin/env python3
"""Create a thumbnail from an image file, preserving relative scale."""
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow"]
# ///

import sys
from pathlib import Path

from PIL import Image


def create_thumbnail(input_path: str, output_path: str, scale: float = 0.2) -> None:
    """Create a thumbnail by scaling the image by a fixed factor.

    This preserves the relative size between images that have been
    normalized to consistent pixel/mm scale.

    Args:
        input_path: Path to input image
        output_path: Path for output thumbnail
        scale: Scale factor (0.2 = 20% of original size)
    """
    img = Image.open(input_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    w, h = img.size
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Ensure minimum size
    if new_w < 50:
        new_w = 50
        new_h = int(h * 50 / w)

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    img.save(output_path, "JPEG", quality=85)

    print(f"{Path(input_path).name}: {w}x{h} -> {new_w}x{new_h}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <input_image> <output_thumbnail> [scale]", file=sys.stderr)
        sys.exit(1)

    scale = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
    create_thumbnail(sys.argv[1], sys.argv[2], scale)
