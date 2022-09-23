from datetime import date
from typing import List, Tuple

import numpy as np
import yaml
from country_converter import CountryConverter
from schema import And, Optional, Schema, Use

from . import DATA_DIR
from .validation import (
    check_curb_mass,
    check_driving_cycle,
    check_electricity_mix,
    check_energy_storage,
    check_fuel_blend,
    check_power,
    check_schema,
    check_value,
    check_vehicle_availability,
    get_average_value,
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
