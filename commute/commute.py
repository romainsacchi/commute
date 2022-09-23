from . import DATA_DIR
from schema import And, Optional, Schema, Use
import yaml
from typing import List, Tuple
from country_converter import CountryConverter
import numpy as np
from datetime import date

from .validation import (
    check_vehicle_availability,
    check_fuel_blend,
    check_electricity_mix,
    check_driving_cycle,
    check_value,
    get_average_value,
    check_energy_storage,
    check_curb_mass,
    check_power,
    check_schema
)
def validate_commute_request(commute_request: list) -> None:
    """
    Validate a commute request.
    """

    for commute in commute_request:
        check_schema(commute_request)
        vehicle = commute["vehicle"]
        size = commute["size"]
        powertrain = commute["powertrain"]
        year = commute.get("year", date.today().year)
        driving_cycle = commute.get("driving_cycle")

        check_vehicle_availability(vehicle, size, powertrain, year)

        if "driving cycle" in commute:
            check_driving_cycle(vehicle, commute["driving cycle"])

        if "fuel consumption" in commute:
            check_value(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                "fuel consumption",
                commute["fuel consumption"],
            )
        else:
            commute["fuel consumption"] = get_average_value(
                vehicle, size, powertrain, year, "fuel consumption"
            )

        if "number of passengers" in commute:
            check_value(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                "number of passengers",
                commute["number of passengers"],
            )
        else:
            commute["number of passengers"] = get_average_value(
                vehicle, size, powertrain, year, "number of passengers"
            )

        if "energy storage" in commute:
            check_energy_storage(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                "energy storage",
                commute["energy storage"],
            )
        else:
            commute["energy storage"] = get_average_value(
                vehicle, size, powertrain, year, "energy storage"
            )

        if "curb mass" in commute:
            check_curb_mass(commute["curb mass"])

        if "power" in commute:
            check_power(commute["power"])
