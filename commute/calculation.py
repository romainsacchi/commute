from collections import defaultdict

from carculator import CarInputParameters, CarModel
from carculator import fill_xarray_from_input_parameters as fill_car_data
from carculator_bus import BusInputParameters, BusModel
from carculator_bus import fill_xarray_from_input_parameters as fill_bus_data
from carculator_truck import TruckInputParameters, TruckModel
from carculator_truck import fill_xarray_from_input_parameters as fill_truck_data

from .validation import FUELS


def generic_fuel_name(powertrain):
    if powertrain in ["ICEV-d", "HEV-d", "PHEV-d"]:
        return "diesel"
    elif powertrain in ["ICEV-p", "HEV-p", "PHEV-p"]:
        return "gasoline"
    elif powertrain == "ICEV-g":
        return "CNG"
    elif powertrain in [
        "BEV",
        "BEV-depot",
        "BEV-opp",
        "BEV-motion",
        "PHEV-d",
        "PHEV-p",
    ]:
        return "electricity"
    else:
        return "hydrogen"


def fetch_energy_consumption(arr, leg):

    fuel_lhv = FUELS[generic_fuel_name(leg["powertrain"])]["lower heating value"] * 1000
    fuel_density = FUELS[generic_fuel_name(leg["powertrain"])]["density"]

    if leg["powertrain"] not in ["PHEV-d", "PHEV-p"]:
        energy_use = (
            (
                arr.sel(
                    powertrain=leg["powertrain"],
                    size=leg["size"],
                    year=leg["year"],
                    parameter="TtW energy",
                    value=0,
                )
                / fuel_lhv
                / fuel_density
                * 100
            )
            .round(2)
            .values.item(0)
        )

        if leg["powertrain"] in ["BEV", "BEV-depot", "BEV-opp", "BEV-motion"]:
            leg["electricity consumption"] = energy_use
        else:
            leg["fuel consumption"] = energy_use
    else:

        electricity_use = (
            (
                arr.sel(
                    powertrain=leg["powertrain"],
                    size=leg["size"],
                    year=leg["year"],
                    parameter="TtW energy, electric mode",
                    value=0,
                )
                * arr.sel(
                    powertrain=leg["powertrain"],
                    size=leg["size"],
                    year=leg["year"],
                    parameter="electric utility factor",
                    value=0,
                )
                / 3600
                / 1
                * 100
            )
            .round(2)
            .values.item(0)
        )

        fuel_use = (
            (
                arr.sel(
                    powertrain=leg["powertrain"],
                    size=leg["size"],
                    year=leg["year"],
                    parameter="TtW energy, combustion mode",
                    value=0,
                )
                * arr.sel(
                    powertrain=leg["powertrain"],
                    size=leg["size"],
                    year=leg["year"],
                    parameter="electric utility factor",
                    value=0,
                )
                / fuel_lhv
                / fuel_density
                * 100
            )
            .round(2)
            .values.item(0)
        )

        leg["electricity consumption"] = electricity_use
        leg["fuel consumption"] = fuel_use

    return leg


def two_wheeler_model(leg, return_list):
    return_list.append(leg)


def car_model(leg, return_list):

    cip = CarInputParameters()
    cip.static()
    _, arr = fill_car_data(
        cip,
        scope={
            "size": [leg["size"]],
            "powertrain": [leg["powertrain"]],
        },
    )
    arr = arr.interp(year=[leg["year"]])
    car = CarModel(arr, cycle="WLTC")
    car.set_all()

    leg = fetch_energy_consumption(car.array, leg)

    return_list.append(leg)


def truck_model(leg, return_list):

    tip = TruckInputParameters()
    tip.static()
    _, arr = fill_truck_data(
        tip,
        scope={
            "size": [leg["size"]],
            "powertrain": [leg["powertrain"]],
        },
    )
    arr = arr.interp(year=[leg["year"]])
    truck = TruckModel(arr, cycle="Long haul")
    truck.set_all()

    leg = fetch_energy_consumption(truck.array, leg)

    return_list.append(leg)


def bus_model(leg, return_list):

    bip = BusInputParameters()
    bip.static()
    _, arr = fill_bus_data(
        bip,
        scope={
            "size": [leg["size"]],
            "powertrain": [leg["powertrain"]],
        },
    )
    arr = arr.interp(year=[leg["year"]])
    bus = BusModel(arr)
    bus.set_all()

    leg = fetch_energy_consumption(bus.array, leg)

    return_list.append(leg)
