class Driver:
    """Represents one driver in the mobility system."""

    def __init__(self, driver_id, driver_name, city, vehicle_type, rating, status):
        self.__driver_id = driver_id
        self.__driver_name = driver_name
        self.__city = city
        self.__vehicle_type = vehicle_type
        self.__rating = float(rating)
        self.__status = status

    @property
    def driver_id(self):
        return self.__driver_id

    @property
    def driver_name(self):
        return self.__driver_name

    @property
    def city(self):
        return self.__city

    @property
    def vehicle_type(self):
        return self.__vehicle_type

    @property
    def rating(self):
        return self.__rating

    @property
    def status(self):
        return self.__status

    def is_active(self):
        return self.__status.strip().lower() == "active"

    def get_profile(self):
        return {
            "driver_id": self.__driver_id,
            "driver_name": self.__driver_name,
            "city": self.__city,
            "vehicle_type": self.__vehicle_type,
            "rating": self.__rating,
            "status": self.__status,
        }
