"""Chip configuration models."""

from typing import Literal

from pydantic import BaseModel, Field


class ChipInfo(BaseModel):
    """Basic chip identification."""

    name: str = Field(description="Design name")
    description: str | None = Field(default=None, description="Chip description")


class Arrangement(BaseModel):
    """SRAM arrangement preferences."""

    prefer: Literal["rows", "columns", "square"] = Field(
        default="rows", description="Preferred arrangement"
    )
    orientation: Literal["N", "E", "S", "W", "mixed"] = Field(
        default="mixed", description="SRAM orientation"
    )


class Memory(BaseModel):
    """SRAM array configuration."""

    macro: str = Field(description="SRAM macro name from srams.yaml")
    count: Literal["auto"] | int = Field(
        default="auto", description="Number of SRAMs: 'auto' or integer"
    )
    arrangement: Arrangement = Field(
        default_factory=Arrangement, description="Arrangement preferences"
    )


class UnifiedBus(BaseModel):
    """Unified bus interface configuration."""

    data_width: int = Field(default=8, gt=0, description="Data bus width")
    registered_output: bool = Field(default=False, description="Add output register")
    output_routing: Literal["mux", "tristate", "tristate_registered"] = Field(
        default="mux", description="Output routing strategy"
    )
    write_mask: bool = Field(
        default=False, description="Expose per-bit write mask pins"
    )


class Interface(BaseModel):
    """External interface configuration."""

    scheme: Literal["unified_bus", "banked", "multi_port"] = Field(
        default="unified_bus", description="Interface scheme"
    )
    unified_bus: UnifiedBus = Field(
        default_factory=UnifiedBus, description="Unified bus config"
    )


class IoConfig(BaseModel):
    """IO configuration."""

    base: Literal["template", "minimal", "custom"] = Field(
        default="template", description="IO base configuration"
    )
    pins: dict[str, str] = Field(default_factory=dict, description="Pin assignments")


class Features(BaseModel):
    """Optional feature flags."""

    parity: bool = Field(default=False, description="Add parity bits")
    ecc: bool = Field(default=False, description="Add ECC")
    bist: bool = Field(default=False, description="Add built-in self-test")


class Clock(BaseModel):
    """Clock configuration."""

    frequency_mhz: float = Field(
        default=25, gt=0, description="Target clock frequency in MHz"
    )


class Power(BaseModel):
    """Power configuration."""

    core_voltage: Literal[5.0, 3.3, 1.8] = Field(
        default=5.0, description="Core voltage"
    )


class ChipConfig(BaseModel):
    """Complete chip configuration."""

    chip: ChipInfo = Field(description="Chip identification")
    slot: str = Field(description="Target slot name")
    memory: Memory = Field(description="SRAM array configuration")
    interface: Interface = Field(
        default_factory=Interface, description="External interface"
    )
    io: IoConfig = Field(default_factory=IoConfig, description="IO configuration")
    features: Features = Field(
        default_factory=Features, description="Optional features"
    )
    clock: Clock = Field(default_factory=Clock, description="Clock configuration")
    power: Power = Field(default_factory=Power, description="Power configuration")
