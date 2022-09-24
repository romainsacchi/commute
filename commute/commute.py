from datetime import date
from .validation import (
    check_driving_cycle,
    check_schema,
    check_value,
    check_vehicle_availability,
    check_country,
    check_battery_type,
)


def validate_commute_request(commute_request: list) -> None:
    """
    Validate a commute request.
    A commute request is a list of trip legs.
    """

    for leg in commute_request:
        vehicle = leg["vehicle"]
        size = leg["size"]
        powertrain = leg["powertrain"]
        year = leg.get("year", date.today().year)

        check_vehicle_availability(vehicle, powertrain, size, year)
        driving_cycle = check_driving_cycle(vehicle, leg.get("driving cycle"))

        leg["distance"] = leg.get("distance", 1.0)
        leg["return trip"] = leg.get("return trip", False)
        leg["location"] = check_country(leg.get("location", "CH"))
        leg["battery type"] = check_battery_type(
            vehicle, powertrain, leg.get("battery type")
        )

        check_schema(leg)

        for var in [
            "fuel consumption",
            "electricity consumption",
            "number of passengers",
            "payload",
            "battery capacity",
            "curb mass",
            "power",
            "electric utility factor",
            "lifetime",
            "annual mileage",
        ]:

            fetch_value = (
                True
                if var in ["number of passengers", "lifetime", "annual mileage"]
                else False
            )

            leg[var] = check_value(
                vehicle,
                size,
                powertrain,
                year,
                driving_cycle,
                var,
                leg.get(var),
                fetch_value,
            )


def process_commute_requests(commute_requests: list) -> list:
    """
    Process a list of commute requests.
    """

    for commute_request in commute_requests:
        validate_commute_request(commute_request)

    return commute_requests
