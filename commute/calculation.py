from carculator import (
    CarInputParameters,
    CarModel,
)
from carculator import fill_xarray_from_input_parameters as fill_car_data
from carculator_truck import (
    TruckInputParameters,
    TruckModel,
)
from carculator_truck import fill_xarray_from_input_parameters as fill_truck_data
from carculator_bus import (
    BusInputParameters,
    BusModel,
)
from carculator_bus import fill_xarray_from_input_parameters as fill_bus_data

from .set_fetch_parameters import (
    adjust_input_parameters,
    fetch_vehicle_specs,
    set_battery_type,
    set_driving_cycle,
    set_energy_consumption,
    set_payload_and_annual_mileage,
    set_target_range,
)


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
    arr = adjust_input_parameters(arr, leg)
    car = CarModel(
        arr,
        energy_storage=set_battery_type(leg),
        electric_utility_factor=leg["electric utility factor"],
        cycle=set_driving_cycle(leg),
        energy_consumption=set_energy_consumption(leg),
        target_range=set_target_range(leg),
    )
    car.set_all()
    leg = fetch_vehicle_specs(car.array, leg)

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
    arr = adjust_input_parameters(arr, leg)
    truck = TruckModel(
        arr,
        energy_storage=set_battery_type(leg),
        payload=set_payload_and_annual_mileage(leg),
        cycle=set_driving_cycle(leg),
        energy_consumption=set_energy_consumption(leg),
        target_range=set_target_range(leg),
    )
    truck.set_all()
    leg = fetch_vehicle_specs(truck.array, leg)

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
    arr = adjust_input_parameters(arr, leg)
    bus = BusModel(
        arr,
        energy_storage=set_battery_type(leg),
        energy_consumption=set_energy_consumption(leg),
    )
    bus.set_all()
    leg = fetch_vehicle_specs(bus.array, leg)

    return_list.append(leg)

def two_wheeler_model(leg, return_list):
    return_list.append(leg)