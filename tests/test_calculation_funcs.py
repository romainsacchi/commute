import numpy as np
import pytest
import xarray as xr

from commute.set_fetch_parameters import (
    adjust_input_parameters,
    fetch_energy_consumption,
    generic_fuel_name,
)


def test_generic_fuel_name():
    assert generic_fuel_name("ICEV-d") == "diesel"
    assert generic_fuel_name("HEV-d") == "diesel"
    assert generic_fuel_name("PHEV-p") == "gasoline"
    assert generic_fuel_name("ICEV-p") == "gasoline"
    assert generic_fuel_name("ICEV-g") == "CNG"
    assert generic_fuel_name("ICEV-p") != "CNG"
    assert generic_fuel_name("FCEV") == "hydrogen"
    assert generic_fuel_name("BEV-motion") == "electricity"

    with pytest.raises(ValueError) as wrapped_error:
        generic_fuel_name("foo")
    assert wrapped_error.type == ValueError


def test_fetch_energy_consumption():

    # test diesel
    arr = xr.DataArray(
        data=np.array([[[[[1500]]]]]),
        coords={
            "powertrain": ["ICEV-d"],
            "size": ["Large"],
            "year": [2020],
            "parameter": ["TtW energy"],
            "value": [0],
        },
        dims=["powertrain", "size", "year", "parameter", "value"],
    )
    leg = {
        "powertrain": "ICEV-d",
        "size": "Large",
        "year": 2020,
    }

    returned_leg = fetch_energy_consumption(arr, leg)

    assert "electricity consumption" not in returned_leg
    assert returned_leg["fuel consumption"] == round(1500 / 43000 / 0.83 * 100, 2)

    # test electric
    arr = xr.DataArray(
        data=np.array([[[[[1200]]]]]),
        coords={
            "powertrain": ["BEV"],
            "size": ["Large"],
            "year": [2020],
            "parameter": ["TtW energy"],
            "value": [0],
        },
        dims=["powertrain", "size", "year", "parameter", "value"],
    )
    leg = {
        "powertrain": "BEV",
        "size": "Large",
        "year": 2020,
    }

    returned_leg = fetch_energy_consumption(arr, leg)

    assert "fuel consumption" not in returned_leg
    assert returned_leg["electricity consumption"] == round(1200 / 3600 * 100, 2)

    # test plugin hybrid
    arr = xr.DataArray(
        data=np.array([[[[[1200], [1800], [0.5]]]]]),
        coords={
            "powertrain": ["PHEV-d"],
            "size": ["Large"],
            "year": [2020],
            "parameter": [
                "TtW energy, electric mode",
                "TtW energy, combustion mode",
                "electric utility factor",
            ],
            "value": [0],
        },
        dims=["powertrain", "size", "year", "parameter", "value"],
    )
    leg = {
        "powertrain": "PHEV-d",
        "size": "Large",
        "year": 2020,
    }

    returned_leg = fetch_energy_consumption(arr, leg)

    assert (
        "fuel consumption" in returned_leg and "electricity consumption" in returned_leg
    )
    assert returned_leg["electricity consumption"] == round(1200 / 3600 * 100 * 0.5, 2)
    assert returned_leg["fuel consumption"] == round(1800 / 43000 / 0.83 * 100 * 0.5, 2)


def test_adjust_input_parameters():
    arr = xr.DataArray(
        data=np.array([[[[[1200], [200000], [10000]]]]]),
        coords={
            "powertrain": ["BEV"],
            "size": ["Large"],
            "year": [2020],
            "parameter": ["TtW energy", "lifetimes", "kilometers per year"],
            "value": [0],
        },
        dims=["powertrain", "size", "year", "parameter", "value"],
    )
    leg = {
        "powertrain": "BEV",
        "size": "Large",
        "year": 2020,
        "lifetimes": 150000,
        "annual mileage": 15000,
    }

    returned_arr = adjust_input_parameters(arr, leg)

    assert returned_arr.sel(parameter="lifetimes").values == 200000
    assert returned_arr.sel(parameter="kilometers per year").values == 15000
