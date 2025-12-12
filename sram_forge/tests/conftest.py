"""Shared pytest fixtures for sram-forge tests."""

from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_sram_spec() -> dict:
    """Sample SRAM specification for testing."""
    return {
        "source": "pdk",
        "size": 512,
        "width": 8,
        "abits": 9,
        "dimensions_um": {
            "width": 431.86,
            "height": 484.88,
        },
        "ports": [
            {
                "name": "port0",
                "type": "rw",
                "clk_enable": True,
                "clk_polarity": "rising",
                "pins": {
                    "clk": "CLK",
                    "en_n": "CEN",
                    "we_n": "GWEN",
                    "wem_n": "WEN[7:0]",
                    "addr": "A[8:0]",
                    "din": "D[7:0]",
                    "dout": "Q[7:0]",
                },
            }
        ],
        "timing_ns": {
            "min_cycle": 6.077,
            "clk_to_q": 5.008,
            "setup": {"addr": 0.947, "din": 0.458, "en": 0.406},
            "hold": {"addr": 0.549, "din": 0.674},
        },
        "files": {
            "gds": "pdk_dir::libs.ref/gf180mcu_fd_ip_sram/gds/sram.gds",
            "lef": "pdk_dir::libs.ref/gf180mcu_fd_ip_sram/lef/sram.lef",
        },
    }


@pytest.fixture
def sample_slot_spec() -> dict:
    """Sample slot specification for testing."""
    return {
        "die": {"width": 3932, "height": 5122},
        "core": {"inset": {"left": 442, "bottom": 442, "right": 442, "top": 442}},
        "io_budget": {
            "dvdd": 8,
            "dvss": 10,
            "input": 12,
            "bidir": 40,
            "analog": 2,
        },
        "reserved_area_um2": 50000,
    }
