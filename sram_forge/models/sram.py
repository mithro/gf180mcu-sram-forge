"""SRAM specification models."""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


class Dimensions(BaseModel):
    """Physical dimensions in microns."""

    width: float = Field(gt=0, description="Width in microns")
    height: float = Field(gt=0, description="Height in microns")


class Pins(BaseModel):
    """Pin mapping for an SRAM port."""

    clk: str = Field(description="Clock pin name")
    en_n: Optional[str] = Field(default=None, description="Enable pin (active low)")
    we_n: Optional[str] = Field(default=None, description="Write enable pin (active low)")
    wem_n: Optional[str] = Field(default=None, description="Write mask pin (active low)")
    addr: Optional[str] = Field(default=None, description="Address bus")
    din: Optional[str] = Field(default=None, description="Data input bus")
    dout: Optional[str] = Field(default=None, description="Data output bus")


class SetupHold(BaseModel):
    """Setup and hold timing parameters."""

    addr: float = Field(ge=0, description="Address setup/hold time in ns")
    din: Optional[float] = Field(default=None, ge=0, description="Data input setup/hold time in ns")
    en: Optional[float] = Field(default=None, ge=0, description="Enable setup/hold time in ns")


class Timing(BaseModel):
    """Timing parameters in nanoseconds."""

    min_cycle: float = Field(gt=0, description="Minimum clock period")
    clk_to_q: float = Field(gt=0, description="Clock to output delay")
    setup: SetupHold = Field(description="Setup times")
    hold: SetupHold = Field(description="Hold times")


class Port(BaseModel):
    """SRAM port definition."""

    name: str = Field(description="Port identifier")
    type: Literal["ro", "wo", "rw"] = Field(description="Port type: read-only, write-only, read-write")
    clk_enable: bool = Field(description="Whether port is synchronous")
    clk_polarity: Literal["rising", "falling"] = Field(description="Clock edge")
    pins: Pins = Field(description="Pin mapping")

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        if v not in ("ro", "wo", "rw"):
            raise ValueError(f"Port type must be 'ro', 'wo', or 'rw', got '{v}'")
        return v

    @property
    def has_write_mask(self) -> bool:
        """Whether this port has per-bit write mask capability."""
        return self.pins.wem_n is not None


class Files(BaseModel):
    """File paths for SRAM macro."""

    gds: str = Field(description="GDS file path")
    lef: str = Field(description="LEF file path")
    lib: Optional[str] = Field(default=None, description="Liberty timing file path")
    verilog: Optional[str] = Field(default=None, description="Verilog model path")


class SramSpec(BaseModel):
    """Complete SRAM macro specification."""

    source: Literal["pdk", "openram", "custom"] = Field(description="SRAM source")
    size: int = Field(gt=0, description="Number of words")
    width: int = Field(gt=0, description="Bits per word")
    abits: int = Field(gt=0, description="Address bus width")
    dimensions_um: Dimensions = Field(description="Physical dimensions")
    ports: list[Port] = Field(min_length=1, description="Port definitions")
    timing_ns: Optional[Timing] = Field(default=None, description="Timing parameters")
    files: Optional[Files] = Field(default=None, description="File paths")

    @property
    def total_bits(self) -> int:
        """Total storage capacity in bits."""
        return self.size * self.width

    @property
    def area_um2(self) -> float:
        """Area in square microns."""
        return self.dimensions_um.width * self.dimensions_um.height
