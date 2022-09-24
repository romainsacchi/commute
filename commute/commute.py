from collections import defaultdict
from datetime import date
from multiprocessing import Manager, Process

from .calculation import bus_model, car_model, truck_model, two_wheeler_model
from .validation import (
    check_battery_type,
    check_country,
    check_driving_cycle,
    check_schema,
    check_value,
    check_vehicle_availability,
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

        leg["year"] = leg.get("year", date.today().year)
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
                vehicle, size, powertrain, driving_cycle, var, leg.get(var), fetch_value
            )


def process_commute_requests(commute_requests: list) -> list:
    """
    Process a list of commute requests.
    """

    for commute_request in commute_requests:
        validate_commute_request(commute_request)

    commute_requests = dispatch(commute_requests)

    return commute_requests


def dispatch(commute_requests: list) -> dict:
    """
    Dispatch a list of commute requests.
    """

    d_model = {
        "Car": car_model,
        "Two wheeler": two_wheeler_model,
        "Truck": truck_model,
        "Bus": bus_model,
    }

    jobs = []
    manager = Manager()
    return_dict = manager.list()

    for commute_request in commute_requests:
        for leg in commute_request:
            process = Process(
                target=d_model[leg["vehicle"]],
                args=(leg, return_dict),
            )
            jobs.append(process)

    # Start the processes
    for j in jobs:
        j.start()

    # Ensure all processes have finished
    for j in jobs:
        j.join()

    return return_dict
