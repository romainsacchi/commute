from typing import Any, Dict, List, Tuple

import numpy as np
import yaml
from country_converter import CountryConverter
from schema import And, Optional, Or, Schema, Use

from . import DATA_DIR

BUSES_VALIDATION_PATH = DATA_DIR / "buses_validation.yaml"
TRUCKS_VALIDATION_PATH = DATA_DIR / "trucks_validation.yaml"
CARS_VALIDATION_PATH = DATA_DIR / "cars_validation.yaml"
TWO_WHEELERS_VALIDATION_PATH = DATA_DIR / "two_wheelers_validation.yaml"
VEHICLE_ARCHETYPES_PATH = DATA_DIR / "vehicle_archetypes.yaml"
FUELS_SPECS_PATH = DATA_DIR / "fuels_specs.yaml"
ELECTRICITY_TECHS_PATH = DATA_DIR / "electricity_specs.yaml"

coco = CountryConverter()


def get_data(filepath) -> dict:
    """
    Return a dictionary of vehicle archetypes.
    """
    with open(filepath, "r", encoding="utf-8") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data


VEHICLE_ARCHETYPES = get_data(VEHICLE_ARCHETYPES_PATH)
FUELS = get_data(FUELS_SPECS_PATH)
ELECTRICITY = get_data(ELECTRICITY_TECHS_PATH)


def check_vehicle_availability(
    vehicle_type: str, powertrain: str, size: str, year: int
) -> None:
    """
    Given a vehicle type, powertrain, size and year,
    we determine whether the vehicle is available or not.
    """
    assert (
        vehicle_type in VEHICLE_ARCHETYPES
    ), f"Vehicle type {vehicle_type} not available."

    assert (
        size in VEHICLE_ARCHETYPES[vehicle_type]
    ), f"Size {size} not available for {vehicle_type}."

    assert (
        powertrain in VEHICLE_ARCHETYPES[vehicle_type][size]
    ), f"Powertrain {powertrain} not available for {size} {vehicle_type}."

    min_year = VEHICLE_ARCHETYPES[vehicle_type][size][powertrain]["year"]["min"]
    max_year = VEHICLE_ARCHETYPES[vehicle_type][size][powertrain]["year"]["max"]

    assert (
        min_year <= year <= max_year
    ), f"Year {year} not available for {powertrain} {size} {vehicle_type}."


def get_archetypes_from_variable(
    var: str, val: [str, int]
) -> List[Tuple[str, str, str, int]]:
    """
    :param var: variable to filter on, e.g., vehicle type, size, powertrain, year
    :param val: value of the variable to filter on, e.g., car, small, ICEV-d, 2020
    Return a list of tuples of vehicle archetypes given a value for a variable.
    """

    list_available_archetypes = []

    if var not in ["vehicle type", "size", "powertrain", "year"]:
        raise ValueError(f"Variable {var} not available.")

    if var == "year":
        for vehicle in VEHICLE_ARCHETYPES:
            for size in VEHICLE_ARCHETYPES[vehicle]:
                for powertrain in VEHICLE_ARCHETYPES[vehicle][size].values():
                    min_year = powertrain["year"]["min"]
                    max_year = powertrain["year"]["max"]

                    if min_year <= val <= max_year:
                        list_available_archetypes.append(
                            (vehicle, size, powertrain, val)
                        )

    if var == "vehicle type":
        for vehicle in VEHICLE_ARCHETYPES:
            if vehicle == val:
                for size in VEHICLE_ARCHETYPES[vehicle]:
                    for powertrain in VEHICLE_ARCHETYPES[vehicle][size].values():
                        min_year = powertrain["year"]["min"]
                        max_year = powertrain["year"]["max"]
                        list_available_archetypes.extend(
                            [
                                (vehicle, size, powertrain, year)
                                for year in range(min_year, max_year + 1)
                            ]
                        )

    if var == "size":
        for vehicle in VEHICLE_ARCHETYPES:
            for size in VEHICLE_ARCHETYPES[vehicle]:
                if size == val:
                    for powertrain in VEHICLE_ARCHETYPES[vehicle][size].values():
                        min_year = powertrain["year"]["min"]
                        max_year = powertrain["year"]["max"]

                        list_available_archetypes.extend(
                            [
                                (vehicle, size, powertrain, year)
                                for year in range(min_year, max_year + 1)
                            ]
                        )

    return list_available_archetypes


def get_list_vehicles() -> List[str]:
    """
    Return a list of vehicle types.
    """
    return list(VEHICLE_ARCHETYPES.keys())


def get_list_sizes() -> List[str]:
    """
    Return a list of vehicle sizes.
    """
    list_sizes = []
    for vehicle in VEHICLE_ARCHETYPES:
        for size in VEHICLE_ARCHETYPES[vehicle]:
            list_sizes.append(size)
    return list(set(list_sizes))


def get_list_powertrains() -> List[str]:
    """
    Return a list of powertrains.
    """
    list_powertrains = []
    for vehicle in VEHICLE_ARCHETYPES:
        for size in VEHICLE_ARCHETYPES[vehicle]:
            for powertrain in VEHICLE_ARCHETYPES[vehicle][size]:
                list_powertrains.append(powertrain)
    return list(set(list_powertrains))


LIST_VEHICLES = get_list_vehicles()
LIST_SIZES = get_list_sizes()
LIST_POWERTRAINS = get_list_powertrains()


def check_battery_type(
    vehicle_type: str, powertrain: str, battery_type: str
) -> [str, None]:
    """
    Check whether the battery type is available for a given vehicle type.
    """

    if battery_type:
        try:
            battery_types = get_vehicle_specs(vehicle_type)[vehicle_type][
                "battery type"
            ][powertrain]
        except KeyError as exc:
            raise KeyError(f"Powertrain {powertrain} does not have a battery.") from exc

        assert (
            battery_type in battery_types
        ), f"Battery type {battery_type} not available for {powertrain} {vehicle_type}."

    else:
        if powertrain in ["BEV-opp", "BEV-motion"]:
            battery_type = "LTO"
        else:
            battery_type = "NMC-622"

    return battery_type


def check_fuel_blend(blend) -> None:
    """
    Check if the fuel blend is valid.
    """

    assert isinstance(blend, dict), "Fuel blend must be a dictionary."
    assert len(blend) > 0, "Fuel blend must not be empty."
    assert np.isclose(sum(blend.values()), 1), "Fuel blend must sum to 1."
    assert all((f in FUELS for f in blend)), "Fuel blend contains unknown fuel."
    assert all((f >= 0 for f in blend.values())), "Fuel blend contains negative values."


def check_electricity_mix(mix) -> None:
    """
    The electricity mix is a dictionary of length 21.
    Keys are technologies names, and values are the corresponding supply shares.
    The sum of the values must equal 1.

    """
    assert isinstance(mix, dict), "Electricity mix must be a dictionary."
    assert len(mix) == 21, "Electricity mix must be of length 21."
    assert np.isclose(sum(mix.values()), 1), "Electricity mix must sum to 1."
    assert all(
        (f >= 0 for f in mix.values())
    ), "Electricity mix contains negative values."
    assert all(
        (f in ELECTRICITY for f in mix)
    ), "Electricity mix contains unknown technology."


def get_vehicle_specs(vehicle_type: str) -> Dict[str, Any]:
    """
    Return the specifications of a vehicle type.
    """
    d_specs = {
        "Two wheeler": TWO_WHEELERS_VALIDATION_PATH,
        "Car": CARS_VALIDATION_PATH,
        "Bus": BUSES_VALIDATION_PATH,
        "Truck": TRUCKS_VALIDATION_PATH,
    }

    return get_data(d_specs[vehicle_type])


def check_value(
    vehicle, size, powertrain, driving_cycle, variable, value, fetch_value=False
) -> float:
    """
    Check if the value is valid, given a variable.
    """

    specs = get_vehicle_specs(vehicle)[vehicle]

    if variable not in specs:
        return value

    if powertrain in specs[variable]:
        if driving_cycle in specs[variable][powertrain][size]:
            min_value = specs[variable][powertrain][size][driving_cycle]["min"]
            max_value = specs[variable][powertrain][size][driving_cycle]["max"]
            avg_value = specs[variable][powertrain][size][driving_cycle]["average"]
        else:
            min_value = specs[variable][powertrain][size]["min"]
            max_value = specs[variable][powertrain][size]["max"]
            avg_value = specs[variable][powertrain][size]["average"]

    elif size in specs[variable]:
        if driving_cycle in specs[variable][size]:
            min_value = specs[variable][size][driving_cycle]["min"]
            max_value = specs[variable][size][driving_cycle]["max"]
            avg_value = specs[variable][size][driving_cycle]["average"]
        else:
            min_value = specs[variable][size]["min"]
            max_value = specs[variable][size]["max"]
            avg_value = specs[variable][size]["average"]

    else:
        return value

    if value:
        assert (
            min_value <= value <= max_value
        ), f"{variable} {value} outside of bounds: {min_value}-{max_value}."
        return value

    if fetch_value:
        return avg_value
    return value


def check_country(country: str) -> str:
    """
    Check if the country is valid.
    """

    if country in coco.ISO2.ISO2.values.tolist():
        return country
    if country in coco.ISO3.ISO3.values.tolist():
        return coco.convert(country, src="ISO3", to="ISO2")

    if country.lower() in [
        c.lower() for c in coco.name_official.name_short.values.tolist()
    ]:
        return coco.convert(country, src="name_short", to="ISO2")

    raise ValueError(f"Country {country} not available.")


def check_driving_cycle(vehicle_type: str, driving_cycle: [str, None]) -> [str, None]:
    """
    Check if the driving cycle is valid.
    :param vehicle_type: vehicle type, e.g., Car, Bus, Truck
    :param driving_cycle: driving cycle, e.g., WLTC, NEDC, Long haul
    """

    specs = get_vehicle_specs(vehicle_type)

    if driving_cycle:
        if "driving cycle" in specs[vehicle_type]:
            assert (
                driving_cycle in specs[vehicle_type]["driving cycle"]
            ), f"Driving cycle {driving_cycle} incorrect or not available for {vehicle_type}."
            return driving_cycle

        print(f"Driving cycle for {vehicle_type} specified, but will be ignored.")
        return None
    else:
        if vehicle_type in ["Car", "Truck"]:
            raise ValueError(f"Driving cycle must be specified for {vehicle_type}.")
        return None


def check_schema(commute_request: dict) -> None:
    """
    Check if the schema of the commute request is valid.
    :param commute_request: commute request

    """

    request_schema = Schema(
        {
            "vehicle": And(str, lambda s: s in LIST_VEHICLES),
            "size": And(str, lambda s: s in LIST_SIZES),
            "powertrain": And(str, lambda s: s in LIST_POWERTRAINS),
            "distance": And(float, lambda n: 0 <= n <= 10000),
            "location": str,
            "return trip": bool,
            "commute id": int,
            "leg id": int,
            Optional("year"): And(int, lambda n: 2000 <= n <= 2050),
            Optional("fuel blend"): And(
                dict,
                lambda s: check_fuel_blend(s),
            ),
            Optional("electricity mix"): And(list, lambda s: check_electricity_mix(s)),
            Optional("driving cycle"): Or(str, None),
            Optional("fuel consumption"): And(Use(float), lambda n: 0 <= n <= 200),
            Optional("electricity consumption"): And(
                Use(float), lambda n: 0 <= n <= 500
            ),
            Optional("number of passengers"): And(int, lambda n: 0 <= n <= 200),
            Optional("battery type"): Or(str, None),
            Optional("battery capacity"): Or(
                And(Use(float), lambda n: 0 <= n <= 1000), None
            ),
            Optional("battery mass"): Or(
                And(Use(float), lambda n: 0 <= n <= 10000), None
            ),
            Optional("energy storage replacement"): Or(
                And(Use(int), lambda n: 0 <= n <= 2), None
            ),
            Optional("curb mass"): Or(And(Use(float), lambda n: 0 <= n <= 50000), None),
            Optional("payload"): Or(And(Use(float), lambda n: 0 <= n <= 28000), None),
            Optional("electric power"): Or(
                And(Use(float), lambda n: 0 <= n <= 1000), None
            ),
            Optional("combustion power"): Or(
                And(Use(float), lambda n: 0 <= n <= 1000), None
            ),
            Optional("electric utility factor"): Or(
                And(float, lambda n: 0 <= n <= 1), None
            ),
            Optional("lifetime"): Or(And(Use(int), lambda n: 0 <= n <= 1500000), None),
            Optional("annual mileage"): Or(
                And(Use(int), lambda n: 0 <= n <= 150000), None
            ),
            Optional("target range"): Or(And(Use(int), lambda n: 0 <= n <= 1500), None),
        }
    )

    request_schema.validate(commute_request)
