from commute import process_commute_requests
import pytest

requests = [
    [
        {
            "vehicle": "Car",
            "size": "Medium",
            "powertrain": "ICEV-d",
            "driving cycle": "WLTC",
        },
        {
            "vehicle": "Bus",
            "size": "13m-city",
            "powertrain": "ICEV-d",
            "driving cycle": "WLTd",
        },
    ],
    [
        {
            "vehicle": "Car",
            "size": "Medium",
            "powertrain": "ICEV-d",
            "driving cycle": "WLTC",
        },
    ]
]

result = process_commute_requests(requests)

def test_location():
    assert result is not None
    assert result[0][0]["location"] == "CH"

def test_driving_cycle():
    assert result[0][0]["driving cycle"] == "WLTC"
    assert result[0][1]["driving cycle"] is None

def test_battery_type():
    assert result[0][0]["battery type"] == "NMC-622"

def test_requests_ids():
    assert result[0][0]["commute id"] == 0
    assert result[0][0]["leg id"] == 0
    assert result[0][1]["commute id"] == 0
    assert result[0][1]["leg id"] == 1
    assert result[1][0]["commute id"] == 1
    assert result[1][0]["leg id"] == 0