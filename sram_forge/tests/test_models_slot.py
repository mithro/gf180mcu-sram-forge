"""Tests for slot model."""

from sram_forge.models.slot import SlotSpec


def test_slot_spec_from_dict(sample_slot_spec):
    """SlotSpec can be created from dictionary."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    assert slot.die.width == 3932
    assert slot.die.height == 5122
    assert slot.core.inset.left == 442


def test_slot_core_dimensions(sample_slot_spec):
    """SlotSpec calculates core dimensions correctly."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    assert slot.core_width == 3932 - 442 - 442  # 3048
    assert slot.core_height == 5122 - 442 - 442  # 4238


def test_slot_core_area(sample_slot_spec):
    """SlotSpec calculates core area correctly."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    expected = 3048 * 4238
    assert slot.core_area_um2 == expected


def test_slot_to_librelane_areas(sample_slot_spec):
    """SlotSpec converts to LibreLane coordinate format."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    die_area, core_area = slot.to_librelane_areas()

    assert die_area == [0, 0, 3932, 5122]
    assert core_area == [442, 442, 3490, 4680]


def test_slot_io_budget_total(sample_slot_spec):
    """IoBudget calculates total pins correctly."""
    slot = SlotSpec.model_validate(sample_slot_spec)

    assert slot.io_budget.total_signal_pins == 12 + 40 + 2  # input + bidir + analog
