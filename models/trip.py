from datetime import datetime


class Trip:
    """Represents one mobility trip."""

    def __init__(
        self,
        trip_id,
        driver_id,
        rider_id,
        city,
        pickup_zone,
        drop_zone,
        request_time,
        pickup_time,
        drop_time,
        distance_km,
        fare,
        status,
        cancellation_reason,
    ):
        self.__trip_id = trip_id
        self.__driver_id = driver_id
        self.__rider_id = rider_id
        self.__city = city
        self.__pickup_zone = pickup_zone
        self.__drop_zone = drop_zone
        self.__request_time = request_time
        self.__pickup_time = pickup_time
        self.__drop_time = drop_time
        self.__distance_km = float(distance_km)
        self.__fare = float(fare)
        self.__status = status
        self.__cancellation_reason = cancellation_reason

    @property
    def trip_id(self):
        return self.__trip_id

    @property
    def driver_id(self):
        return self.__driver_id

    @property
    def rider_id(self):
        return self.__rider_id

    @property
    def city(self):
        return self.__city

    @property
    def pickup_zone(self):
        return self.__pickup_zone

    @property
    def drop_zone(self):
        return self.__drop_zone

    @property
    def request_time(self):
        return self.__request_time

    @property
    def pickup_time(self):
        return self.__pickup_time

    @property
    def drop_time(self):
        return self.__drop_time

    @property
    def distance_km(self):
        return self.__distance_km

    @property
    def fare(self):
        return self.__fare

    @property
    def status(self):
        return self.__status

    @property
    def cancellation_reason(self):
        return self.__cancellation_reason

    def is_completed(self):
        return self.__status.strip().lower() == "completed"

    def is_cancelled(self):
        return self.__status.strip().lower() == "cancelled"

    def calculate_duration(self):
        if not self.__pickup_time or not self.__drop_time:
            return None
        return self.__drop_time - self.__pickup_time

    def calculate_fare_per_km(self):
        if self.__distance_km <= 0:
            return 0.0
        return self.__fare / self.__distance_km
