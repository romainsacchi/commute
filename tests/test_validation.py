from commute.validation import (
    LIST_SIZES,
    LIST_VEHICLES,
    LIST_POWERTRAINS,
    check_battery_type
)
import pytest

def test_list_sizes():
    assert "Large" in LIST_SIZES
    assert "Sedan" not in LIST_SIZES

def test_list_vehicles():
    assert "Car" in LIST_VEHICLES
    assert "Bicycle" not in LIST_VEHICLES

def test_list_powertrains():
    assert "BEV" in LIST_POWERTRAINS
    assert "BEV-depot" in LIST_POWERTRAINS
    assert "ICEV-v" not in LIST_POWERTRAINS

def test_check_battery_type():
    vehicle = "Bus"
    powertrain = "BEV-motion"
    battery_type = "NMC-622"

    with pytest.raises(AssertionError) as wrapped_error:
        check_battery_type(vehicle, powertrain, battery_type)
    assert wrapped_error.type == AssertionError

    assert check_battery_type(vehicle, powertrain, None) == "LTO"

    vehicle = "Car"
    powertrain = "ICEV-d"
    battery_type = "NMC-622"

    with pytest.raises(KeyError) as wrapped_error:
        check_battery_type(vehicle, powertrain, battery_type)
    assert wrapped_error.type == KeyError

