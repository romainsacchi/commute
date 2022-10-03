import pytest

from commute import process_commute_requests


def test_mandatory_specs():

    requests = [
        [
            {
                "vehicle": "Buss",
            },
        ],
    ]

    with pytest.raises(KeyError) as wrapped_error:
        process_commute_requests(requests)
    assert wrapped_error.type == KeyError


def test_vehicle_type():

    requests = [
        [
            {
                "vehicle": "Buss",
                "size": "13m-city",
                "powertrain": "ICEV-d",
            },
        ],
    ]

    with pytest.raises(AssertionError) as wrapped_error:
        process_commute_requests(requests)
    assert wrapped_error.type == AssertionError


def test_vehicle_size():

    requests = [
        [
            {
                "vehicle": "Car",
                "size": "12m",
                "powertrain": "ICEV-d",
                "driving cycle": "WLTC",
            },
        ],
    ]

    with pytest.raises(AssertionError) as wrapped_error:
        process_commute_requests(requests)
    assert wrapped_error.type == AssertionError

    requests[0][0]["size"] = "Large"
    assert process_commute_requests(requests) is not None


def test_vehicle_powertrain():

    requests = [
        [
            {
                "vehicle": "Car",
                "size": "Large",
                "powertrain": "ICEV",
            },
        ],
    ]

    with pytest.raises(AssertionError) as wrapped_error:
        process_commute_requests(requests)
    assert wrapped_error.type == AssertionError
