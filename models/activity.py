class DriverActivity:
    """Represents one driver activity/status event."""

    def __init__(self, driver_id, timestamp, status):
        self.__driver_id = driver_id
        self.__timestamp = timestamp
        self.__status = status

    @property
    def driver_id(self):
        return self.__driver_id

    @property
    def timestamp(self):
        return self.__timestamp

    @property
    def status(self):
        return self.__status
