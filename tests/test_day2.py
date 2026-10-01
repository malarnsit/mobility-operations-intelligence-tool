from models.driver import Driver
from models.trip import Trip

from services.analytics_service import AnalyticsService


# =========================================================
# SAMPLE TEST DATA
# =========================================================

def create_test_data():

    drivers = [

        Driver(
            "D1",
            "Asha",
            "Bangalore",
            "Sedan",
            4.8,
            "Active"
        ),

        Driver(
            "D2",
            "Ravi",
            "Mumbai",
            "SUV",
            4.5,
            "Active"
        )
    ]


    trips = [

        Trip(

            "T1",

            "D1",

            "R1",

            "Bangalore",

            "Indiranagar",

            "Koramangala",

            "2026-01-01 08:00:00",

            "2026-01-01 08:05:00",

            "2026-01-01 08:25:00",

            10,

            200,

            "Completed",

            ""
        ),


        Trip(

            "T2",

            "D1",

            "R2",

            "Bangalore",

            "Indiranagar",

            "Whitefield",

            "2026-01-01 09:00:00",

            "2026-01-01 09:05:00",

            "2026-01-01 09:35:00",

            15,

            300,

            "Completed",

            ""
        ),


        Trip(

            "T3",

            "D2",

            "R3",

            "Mumbai",

            "Andheri",

            "Bandra",

            "2026-01-01 10:00:00",

            "",

            "",

            8,

            0,

            "Cancelled",

            "Rider"
        )
    ]


    return drivers, trips


# =========================================================
# TEST 1
# =========================================================

def test_driver_index_lookup():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    assert (
        service.driver_index["D1"].driver_name
        == "Asha"
    )


# =========================================================
# TEST 2
# =========================================================

def test_driver_summary():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = service.driver_summary("D1")

    assert result["total_trips"] == 2

    assert result["completed_trips"] == 2

    assert result["total_fare"] == 500


# =========================================================
# TEST 3
# =========================================================

def test_unknown_driver():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = service.driver_summary(
        "D999"
    )

    assert result is None


# =========================================================
# TEST 4
# =========================================================

def test_trip_summary():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = service.trip_summary()

    assert result["total_trips"] == 3

    assert result["completed_trips"] == 2

    assert result["cancelled_trips"] == 1


# =========================================================
# TEST 5
# =========================================================

def test_status_frequency():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.trip_status_frequency()
    )

    assert result["Completed"] == 2

    assert result["Cancelled"] == 1


# =========================================================
# TEST 6
# =========================================================

def test_cancellation_frequency():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.cancellation_reason_frequency()
    )

    assert result["Rider"] == 1


# =========================================================
# TEST 7
# =========================================================

def test_driver_search():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.search_drivers("asha")
    )

    assert len(result) == 1

    assert result[0].driver_id == "D1"


# =========================================================
# TEST 8
# =========================================================

def test_city_search():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.search_drivers("mumbai")
    )

    assert len(result) == 1

    assert result[0].driver_id == "D2"


# =========================================================
# TEST 9
# =========================================================

def test_trip_search():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.search_trips(
            "indiranagar"
        )
    )

    assert len(result) == 2


# =========================================================
# TEST 10
# =========================================================

def test_top_driver():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.rank_drivers_by_fare(1)
    )

    assert len(result) == 1

    assert (
        result[0]["driver"].driver_id
        == "D1"
    )


# =========================================================
# TEST 11
# =========================================================

def test_zone_summary():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.zone_summaries()
    )

    assert len(result) == 2


# =========================================================
# TEST 12
# =========================================================

def test_city_summary():

    drivers, trips = create_test_data()

    service = AnalyticsService(
        drivers,
        trips,
        []
    )

    result = (
        service.city_summaries()
    )

    assert len(result) == 2