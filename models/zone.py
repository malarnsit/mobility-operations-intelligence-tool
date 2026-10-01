class Zone:
    """Represents a pickup zone and its trips."""

    def __init__(self, zone_id, city):
        self.__zone_id = zone_id
        self.__city = city
        self.__trips = []

    @property
    def zone_id(self):
        return self.__zone_id

    @property
    def city(self):
        return self.__city

    @property
    def trips(self):
        return list(self.__trips)

    def add_trip(self, trip):
        self.__trips.append(trip)

    def get_total_requests(self):
        return len(self.__trips)

    def get_completed_trips(self):
        return sum(1 for trip in self.__trips if trip.is_completed())

    def get_cancelled_trips(self):
        return sum(1 for trip in self.__trips if trip.is_cancelled())
