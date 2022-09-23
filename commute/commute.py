from datetime import date

from .validation import (
    check_driving_cycle,
    check_schema,
    check_value,
    check_vehicle_availability,
)


def validate_commute_request(commute_request: list) -> None:
    """
    Validate a commute request.
    """

    for commute in commute_request:
        check_schema(commute)
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

        if "energy storage" in commute:
            check_value(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                "energy storage",
                commute["energy storage"],
            )

        if "curb mass" in commute:
            check_value(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                "curb mass",
                commute["curb mass"],
            )

        if "power" in commute:
            check_value(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                "power",
                commute["power"],
            )
