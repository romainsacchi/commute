import xarray as xr

from . import DATA_DIR
from .validation import FUELS, get_data

VARIABLES_MAPPING_PATH = DATA_DIR / "variables_mapping.yaml"
VARIABLES_MAP = get_data(VARIABLES_MAPPING_PATH)


def generic_fuel_name(powertrain: str) -> str:
    """
    Returns the generic fuel name for a given powertrain
    :param powertrain: str
    :return: str
    """
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
    elif powertrain == "FCEV":
        return "hydrogen"
    else:
        raise ValueError("Unknown powertrain.")


def fetch_energy_consumption(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the energy consumption for a given leg
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict

    """

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


def fetch_energy_storage_specs(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the energy storage capacity for a given leg vehicle.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict
    """

    # battery capacity, kWh
    electric_energy = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter="electric energy stored",
            value=0,
        )
        .round(2)
        .values.item(0)
    )

    # fuel tank capacity, kWh
    oxidation_energy = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter="oxidation energy stored",
            value=0,
        )
        .round(2)
        .values.item(0)
    )

    leg["battery capacity"] = electric_energy
    leg["fuel tank capacity"] = oxidation_energy

    return leg


def fetch_mass_components(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the mass of components for a given leg vehicle.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict
    """
    # list of the vehicle components
    # to fetch the mass for.
    list_params = [
        "battery mass",
        "curb mass",
        "driving mass",
        "fuel mass",
        "battery mass",
        "payload",
    ]

    for param in list_params:
        leg[param] = (
            arr.sel(
                powertrain=leg["powertrain"],
                size=leg["size"],
                year=leg["year"],
                parameter=VARIABLES_MAP[param],
                value=0,
            )
            .round(1)
            .values.item(0)
        )

    return leg


def fetch_electric_utility_factor(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the electric utility factor for a given leg vehicle.
    Only relevant for PHEVs.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict

    """

    leg["electric utility factor"] = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter="electric utility factor",
            value=0,
        )
        .round(2)
        .values.item(0)
    )

    return leg


def fetch_passenger_details(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the number of passengers for a given leg vehicle.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict

    """

    leg["number of passengers"] = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter="average passengers",
            value=0,
        )
        .round(1)
        .values.item(0)
    )

    return leg


def fetch_power_specs(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the power specs for a given leg vehicle.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict

    """
    list_params = [
        "total power",
        "electric power",
        "combustion power",
    ]

    # power, in kW
    for param in list_params:
        leg[param] = (
            arr.sel(
                powertrain=leg["powertrain"],
                size=leg["size"],
                year=leg["year"],
                parameter=VARIABLES_MAP[param],
                value=0,
            )
            .round(0)
            .values.item(0)
        )

    return leg


def fetch_use_vars(arr: xr.DataArray, leg: dict) -> dict:
    """
    Fetches the use variables for a given leg vehicle.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict

    """

    # vehicle lifetime, in km
    leg["lifetime"] = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter="lifetime kilometers",
            value=0,
        )
        .round(0)
        .values.item(0)
    )

    # annual mileage, in km per year
    leg["annual mileage"] = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter="kilometers per year",
            value=0,
        )
        .round(0)
        .values.item(0)
    )

    # range, in km
    # for trucks and cars,
    # it is the vehicle tange autonomy
    # on a single charge.
    # for buses, it is the range
    # of the vehicle on a single shift.
    if leg["vehicle"] == "Truck":
        param = "target range"
    elif leg["vehicle"] == "Bus":
        param = "daily distance"
    else:
        param = "range"

    leg["range"] = (
        arr.sel(
            powertrain=leg["powertrain"],
            size=leg["size"],
            year=leg["year"],
            parameter=param,
            value=0,
        )
        .round(0)
        .values.item(0)
    )

    return leg


def fetch_vehicle_specs(arr: xr.DataArray, leg: dict) -> dict:
    """
    Run diverse functions to fetch the vehicle specs.
    :param arr: xr.DataArray
    :param leg: dict
    :return: dict
    """

    list_funcs = [
        fetch_energy_consumption,
        fetch_energy_storage_specs,
        fetch_mass_components,
        fetch_passenger_details,
        fetch_electric_utility_factor,
        fetch_power_specs,
        fetch_use_vars,
    ]

    for func in list_funcs:
        leg = func(arr, leg)

    return leg


def adjust_input_parameters(arr: xr.DataArray, leg: dict) -> xr.DataArray:
    """
    Adjusts the input parameters for a given leg vehicle.
    :param arr: xr.DataArray
    :param leg: dict
    :return: xr.DataArray

    """

    list_params = [
        "lifetime",
        "annual mileage",
        "number of passengers",
        "battery mass",
        "fuel mass",
        "payload",
    ]

    for param in list_params:
        if param in leg:
            if leg[param] is not None:
                arr.loc[
                    dict(
                        powertrain=leg["powertrain"],
                        size=leg["size"],
                        year=leg["year"],
                        parameter=VARIABLES_MAP[param],
                    )
                ] = leg[param]

    return arr


def set_battery_type(leg: dict) -> dict:
    """
    Sets the battery type for a given leg vehicle.
    :param leg: dict
    :return: dict
    """

    energy_storage = {
        "electric": {(leg["powertrain"], leg["size"], leg["year"]): leg["battery type"]}
    }

    if "battery capacity" in leg:
        energy_storage.update(
            {
                "capacity": {
                    (leg["powertrain"], leg["size"], leg["year"]): leg[
                        "battery capacity"
                    ]
                }
            }
        )

    return energy_storage


def set_driving_cycle(leg: dict) -> dict:
    """
    Sets the driving cycle for a given leg vehicle.
    Buses and two-wheelers do not have the choice
    between multiple driving cycles.

    :param leg: dict
    :return: dict
    """

    if leg["vehicle"] == "Car":
        return leg.get("driving cycle", "WLTC")

    if leg["vehicle"] == "Truck":
        return leg.get("driving cycle", "Urban delivery")

    return None


def set_energy_consumption(leg):
    fuel_lhv = FUELS[generic_fuel_name(leg["powertrain"])]["lower heating value"] * 1000
    fuel_density = FUELS[generic_fuel_name(leg["powertrain"])]["density"]

    if leg["powertrain"] not in ["PHEV-p", "PHEV-d"]:

        if leg.get("fuel consumption"):
            return {
                (leg["powertrain"], leg["size"], leg["year"]): (
                    leg["fuel consumption"] * fuel_density * fuel_lhv
                )
                / 100
            }

        if leg.get("electricity consumption"):
            return {
                (leg["powertrain"], leg["size"], leg["year"]): (
                    leg["electricity consumption"] * fuel_density * fuel_lhv
                )
                / 100
            }

    else:
        return None


def set_payload_and_annual_mileage(leg: dict) -> dict:
    """
    Sets the payload and annual mileage for a given leg vehicle.
    For trucks only.

    :param leg: dict
    :return: dict
    """
    return {
        "payload": {leg["driving cycle"]: {leg["size"]: leg["payload"]}},
        "annual mileage": {leg["driving cycle"]: {leg["size"]: leg["annual mileage"]}},
    }


def set_target_range(leg):
    if leg["vehicle"] == "Truck" and leg.get("target range"):
        return leg["target range"]
    elif leg["vehicle"] == "Car" and leg.get("target range"):
        if leg["powertrain"] in ["BEV"]:
            return {(leg["powertrain"], leg["size"], leg["year"]): leg["target range"]}
