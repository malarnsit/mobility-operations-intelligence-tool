from collections import Counter


class AnomalyDetector:

    def __init__(
        self,
        drivers,
        trips,
        activities=None,
        fare_threshold=2000,
        min_distance_km=0
    ):

        self.drivers = drivers

        self.trips = trips

        self.activities = activities or []

        self.fare_threshold = fare_threshold

        self.min_distance_km = min_distance_km

        self.driver_ids = {
            driver.driver_id
            for driver in drivers
        }

    # ======================================================
    # 1. NEGATIVE FARE
    # ======================================================

    def negative_fare_anomalies(self):

        anomalies = []

        for trip in self.trips:

            if trip.fare < 0:

                anomalies.append({

                    "type": "NEGATIVE_FARE",

                    "trip_id": trip.trip_id,

                    "driver_id": trip.driver_id,

                    "value": trip.fare,

                    "message": (
                        f"Trip {trip.trip_id} has "
                        f"negative fare {trip.fare}"
                    )
                })

        return anomalies

    # ======================================================
    # 2. HIGH FARE
    # ======================================================

    def high_fare_anomalies(self):

        anomalies = []

        for trip in self.trips:

            if trip.fare > self.fare_threshold:

                anomalies.append({

                    "type": "HIGH_FARE",

                    "trip_id": trip.trip_id,

                    "driver_id": trip.driver_id,

                    "value": trip.fare,

                    "message": (
                        f"Trip {trip.trip_id} has "
                        f"unusually high fare {trip.fare}"
                    )
                })

        return anomalies

    # ======================================================
    # 3. UNKNOWN DRIVER
    # ======================================================

    def unknown_driver_anomalies(self):

        anomalies = []

        for trip in self.trips:

            if trip.driver_id not in self.driver_ids:

                anomalies.append({

                    "type": "UNKNOWN_DRIVER",

                    "trip_id": trip.trip_id,

                    "driver_id": trip.driver_id,

                    "value": trip.driver_id,

                    "message": (
                        f"Trip {trip.trip_id} references "
                        f"unknown driver {trip.driver_id}"
                    )
                })

        return anomalies

    # ======================================================
    # 4. INVALID TIMESTAMP
    # ======================================================

    def invalid_timestamp_anomalies(self):

        anomalies = []

        for trip in self.trips:

            if (
                trip.pickup_time is not None
                and trip.drop_time is not None
                and trip.drop_time < trip.pickup_time
            ):

                anomalies.append({

                    "type": "INVALID_TIMESTAMP",

                    "trip_id": trip.trip_id,

                    "driver_id": trip.driver_id,

                    "value": None,

                    "message": (
                        f"Trip {trip.trip_id} has "
                        f"drop time before pickup time"
                    )
                })

        return anomalies

    # ======================================================
    # 5. MISSING TIMESTAMP
    # ======================================================

    def missing_timestamp_anomalies(self):

        anomalies = []

        for trip in self.trips:

            if trip.is_completed():

                if (
                    trip.pickup_time is None
                    or trip.drop_time is None
                ):

                    anomalies.append({

                        "type": "MISSING_TIMESTAMP",

                        "trip_id": trip.trip_id,

                        "driver_id": trip.driver_id,

                        "value": None,

                        "message": (
                            f"Completed trip {trip.trip_id} "
                            f"is missing pickup/drop timestamp"
                        )
                    })

        return anomalies

    # ======================================================
    # 6. INVALID DISTANCE
    # ======================================================

    def negative_distance_anomalies(self):

        anomalies = []

        for trip in self.trips:

            if trip.distance_km < self.min_distance_km:

                anomalies.append({

                    "type": "INVALID_DISTANCE",

                    "trip_id": trip.trip_id,

                    "driver_id": trip.driver_id,

                    "value": trip.distance_km,

                    "message": (
                        f"Trip {trip.trip_id} has "
                        f"invalid distance "
                        f"{trip.distance_km}"
                    )
                })

        return anomalies

    # ======================================================
    # DETECT EVERYTHING
    # ======================================================

    def detect_all(self):

        anomalies = []

        anomalies.extend(
            self.negative_fare_anomalies()
        )

        anomalies.extend(
            self.high_fare_anomalies()
        )

        anomalies.extend(
            self.unknown_driver_anomalies()
        )

        anomalies.extend(
            self.invalid_timestamp_anomalies()
        )

        anomalies.extend(
            self.missing_timestamp_anomalies()
        )

        anomalies.extend(
            self.negative_distance_anomalies()
        )

        return anomalies

    # ======================================================
    # ANOMALY SUMMARY
    # ======================================================

    def anomaly_summary(self):

        anomalies = self.detect_all()

        counts = Counter(
            anomaly["type"]
            for anomaly in anomalies
        )

        return {

            "total_anomalies": len(
                anomalies
            ),

            "by_type": dict(
                counts
            )
        }

    # ======================================================
    # CHANGE FARE THRESHOLD
    # ======================================================

    def set_fare_threshold(self, threshold):

        if threshold < 0:

            raise ValueError(
                "Fare threshold cannot be negative."
            )

        self.fare_threshold = threshold

    # ======================================================
    # GET CURRENT THRESHOLDS
    # ======================================================

    def get_thresholds(self):

        return {

            "fare_threshold":
                self.fare_threshold,

            "min_distance_km":
                self.min_distance_km
        }