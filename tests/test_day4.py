from datetime import datetime

from models.driver import Driver
from models.trip import Trip

from services.anomaly_service import AnomalyDetector
from services.analytics_service import AnalyticsService
from services.advanced_analytics_service import (
    AdvancedAnalyticsService
)
from services.insights_service import InsightsEngine


def create_driver(
    driver_id="D1",
    name="Test Driver"
):

    return Driver(
        driver_id=driver_id,
        driver_name=name,
        city="Bangalore",
        vehicle_type="Sedan",
        rating=4.5,
        status="Active"
    )


def create_trip(
    trip_id="T1",
    driver_id="D1",
    fare=500,
    distance=10,
    status="Completed"
):

    return Trip(
        trip_id=trip_id,
        driver_id=driver_id,
        rider_id="R1",
        city="Bangalore",
        pickup_zone="Zone A",
        drop_zone="Zone B",
        request_time=datetime(
            2026,
            1,
            1,
            9,
            0
        ),
        pickup_time=datetime(
            2026,
            1,
            1,
            9,
            10
        ),
        drop_time=datetime(
            2026,
            1,
            1,
            9,
            30
        ),
        distance_km=distance,
        fare=fare,
        status=status,
        cancellation_reason=None
    )


def test_negative_fare_detection():

    driver = create_driver()

    trip = create_trip(
        fare=-100
    )

    detector = AnomalyDetector(
        [driver],
        [trip]
    )

    result = (
        detector.negative_fare_anomalies()
    )

    assert len(result) == 1

    assert result[0]["type"] == (
        "NEGATIVE_FARE"
    )


def test_high_fare_detection():

    driver = create_driver()

    trip = create_trip(
        fare=5000
    )

    detector = AnomalyDetector(
        [driver],
        [trip],
        fare_threshold=2000
    )

    result = (
        detector.high_fare_anomalies()
    )

    assert len(result) == 1

    assert result[0]["type"] == (
        "HIGH_FARE"
    )


def test_unknown_driver_detection():

    driver = create_driver(
        driver_id="D1"
    )

    trip = create_trip(
        driver_id="D9999"
    )

    detector = AnomalyDetector(
        [driver],
        [trip]
    )

    result = (
        detector.unknown_driver_anomalies()
    )

    assert len(result) == 1

    assert result[0]["driver_id"] == (
        "D9999"
    )


def test_threshold_change():

    driver = create_driver()

    trip = create_trip(
        fare=1500
    )

    detector = AnomalyDetector(
        [driver],
        [trip],
        fare_threshold=2000
    )

    result_before = (
        detector.high_fare_anomalies()
    )

    assert len(result_before) == 0

    detector.set_fare_threshold(
        1000
    )

    result_after = (
        detector.high_fare_anomalies()
    )

    assert len(result_after) == 1


def test_anomaly_summary():

    driver = create_driver()

    trips = [

        create_trip(
            trip_id="T1",
            fare=-100
        ),

        create_trip(
            trip_id="T2",
            fare=5000
        ),

        create_trip(
            trip_id="T3",
            driver_id="D9999"
        )
    ]

    detector = AnomalyDetector(
        [driver],
        trips
    )

    summary = (
        detector.anomaly_summary()
    )

    assert summary["total_anomalies"] == 3

    assert (
        summary["by_type"]["NEGATIVE_FARE"]
        == 1
    )

    assert (
        summary["by_type"]["HIGH_FARE"]
        == 1
    )

    assert (
        summary["by_type"]["UNKNOWN_DRIVER"]
        == 1
    )


def test_insights_engine():

    driver = create_driver()

    trip = create_trip(
        fare=500
    )

    analytics = AdvancedAnalyticsService(
        [driver],
        [trip],
        []
    )

    detector = AnomalyDetector(
        [driver],
        [trip]
    )

    engine = InsightsEngine(
        analytics=analytics,
        advanced_analytics=analytics,
        anomaly_detector=detector
    )

    insights = (
        engine.generate_insights()
    )

    assert len(insights) == 6

    assert all(
        isinstance(insight, str)
        for insight in insights
    )