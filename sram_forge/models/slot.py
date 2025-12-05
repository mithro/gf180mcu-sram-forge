"""Slot specification models."""

from pydantic import BaseModel, Field


class Die(BaseModel):
    """Die dimensions in microns."""

    width: float = Field(gt=0, description="Die width in microns")
    height: float = Field(gt=0, description="Die height in microns")


class Inset(BaseModel):
    """Inset from die edge to core boundary."""

    left: float = Field(ge=0, description="Left inset in microns")
    bottom: float = Field(ge=0, description="Bottom inset in microns")
    right: float = Field(ge=0, description="Right inset in microns")
    top: float = Field(ge=0, description="Top inset in microns")


class Core(BaseModel):
    """Core area definition via insets."""

    inset: Inset = Field(description="Insets from die edges")


class IoBudget(BaseModel):
    """Available IO pads by type."""

    dvdd: int = Field(ge=0, description="VDD power pads")
    dvss: int = Field(ge=0, description="VSS ground pads")
    input: int = Field(ge=0, description="Input-only pads")
    bidir: int = Field(ge=0, description="Bidirectional pads")
    analog: int = Field(ge=0, description="Analog pads")

    @property
    def total_signal_pins(self) -> int:
        """Total signal pins (excluding power)."""
        return self.input + self.bidir + self.analog


class SlotSpec(BaseModel):
    """Complete slot specification."""

    die: Die = Field(description="Die dimensions")
    core: Core = Field(description="Core area definition")
    io_budget: IoBudget = Field(description="Available IO pads")
    reserved_area_um2: float = Field(ge=0, description="Reserved area for logo, ID, etc.")

    @property
    def core_width(self) -> float:
        """Usable core width in microns."""
        return self.die.width - self.core.inset.left - self.core.inset.right

    @property
    def core_height(self) -> float:
        """Usable core height in microns."""
        return self.die.height - self.core.inset.bottom - self.core.inset.top

    @property
    def core_area_um2(self) -> float:
        """Usable core area in square microns."""
        return self.core_width * self.core_height

    def to_librelane_areas(self) -> tuple[list[float], list[float]]:
        """Convert to LibreLane [x_min, y_min, x_max, y_max] format.

        Returns:
            Tuple of (die_area, core_area) in LibreLane format.
        """
        die_area = [0, 0, self.die.width, self.die.height]
        core_area = [
            self.core.inset.left,
            self.core.inset.bottom,
            self.die.width - self.core.inset.right,
            self.die.height - self.core.inset.top,
        ]
        return die_area, core_area
