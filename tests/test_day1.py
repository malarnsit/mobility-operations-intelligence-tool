from datetime import datetime
from models.driver import Driver
from models.trip import Trip
from models.zone import Zone


def test_driver_is_active():
    driver = Driver(
        "D101", "Rahul", "Bangalore",
        "Sedan", 4.5, "Active"
    )

    assert driver.is_active() is True


def test_inactive_driver():
    driver = Driver(
        "D102", "Priya", "Mumbai",
        "SUV", 4.8, "Inactive"
    )

    assert driver.is_active() is False


def test_trip_completed():
    trip = Trip(
        "T1001", "D101", "R1001", "Bangalore",
        "Koramangala", "Indiranagar",
        datetime(2023, 10, 1, 10, 0),
        datetime(2023, 10, 1, 10, 5),
        datetime(2023, 10, 1, 10, 25),
        8.0, 250.0, "Completed", ""
    )

    assert trip.is_completed() is True
    assert trip.is_cancelled() is False


def test_trip_duration():
    trip = Trip(
        "T1001", "D101", "R1001", "Bangalore",
        "Koramangala", "Indiranagar",
        datetime(2023, 10, 1, 10, 0),
        datetime(2023, 10, 1, 10, 5),
        datetime(2023, 10, 1, 10, 25),
        8.0, 250.0, "Completed", ""
    )

    assert trip.calculate_duration().seconds == 20 * 60


def test_trip_fare_per_km():
    trip = Trip(
        "T1001", "D101", "R1001", "Bangalore",
        "Koramangala", "Indiranagar",
        datetime(2023, 10, 1, 10, 0),
        datetime(2023, 10, 1, 10, 5),
        datetime(2023, 10, 1, 10, 25),
        10.0, 250.0, "Completed", ""
    )

    assert trip.calculate_fare_per_km() == 25.0


def test_zone_add_trip():
    zone = Zone("Koramangala", "Bangalore")

    trip = Trip(
        "T1001", "D101", "R1001", "Bangalore",
        "Koramangala", "Indiranagar",
        datetime(2023, 10, 1, 10, 0),
        datetime(2023, 10, 1, 10, 5),
        datetime(2023, 10, 1, 10, 25),
        10.0, 250.0, "Completed", ""
    )

    zone.add_trip(trip)

    assert zone.get_total_requests() == 1
    assert zone.get_completed_trips() == 1


def test_zone_cancelled_trip_count():
    zone = Zone("Koramangala", "Bangalore")

    trip = Trip(
        "T1002", "D101", "R1002", "Bangalore",
        "Koramangala", "Indiranagar",
        datetime(2023, 10, 1, 11, 0),
        None,
        None,
        0.0, 0.0, "Cancelled", "Rider Cancelled"
    )

    zone.add_trip(trip)

    assert zone.get_cancelled_trips() == 1
