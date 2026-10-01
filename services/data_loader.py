import csv
from datetime import datetime

from models.driver import Driver
from models.trip import Trip
from models.zone import Zone
from models.activity import DriverActivity


DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class DataLoader:
    """Loads CSV files and converts rows into domain objects."""

    def _read_csv(self, filepath, required_columns):
        with open(filepath, "r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError(f"{filepath} is empty or has no header row.")

            actual = {column.strip() for column in reader.fieldnames}
            missing = required_columns - actual

            if missing:
                missing_text = ", ".join(sorted(missing))
                raise ValueError(
                    f"Missing required columns in {filepath}: {missing_text}"
                )

            return list(reader)

    def parse_datetime(self, value, allow_blank=False):
        value = (value or "").strip()

        if allow_blank and not value:
            return None

        return datetime.strptime(value, DATE_FORMAT)

    def load_drivers(self, filepath):
        drivers = []

        rows = self._read_csv(
            filepath,
            {
                "driver_id", "driver_name", "city",
                "vehicle_type", "rating", "status"
            },
        )

        for row in rows:
                drivers.append(
                    Driver(
                        driver_id=row["driver_id"].strip(),
                        driver_name=row["driver_name"].strip(),
                        city=row["city"].strip(),
                        vehicle_type=row["vehicle_type"].strip(),
                        rating=row["rating"],
                        status=row["status"].strip(),
                    )
                )

        return drivers

    def load_trips(self, filepath):
        trips = []

        rows = self._read_csv(
            filepath,
            {
                "trip_id", "driver_id", "rider_id", "city",
                "pickup_zone", "drop_zone", "request_time",
                "pickup_time", "drop_time", "distance_km",
                "fare", "status", "cancellation_reason"
            },
        )

        for row in rows:
                trips.append(
                    Trip(
                        trip_id=row["trip_id"].strip(),
                        driver_id=row["driver_id"].strip(),
                        rider_id=row["rider_id"].strip(),
                        city=row["city"].strip(),
                        pickup_zone=row["pickup_zone"].strip(),
                        drop_zone=row["drop_zone"].strip(),
                        request_time=self.parse_datetime(row["request_time"]),
                        pickup_time=self.parse_datetime(row["pickup_time"], allow_blank=True),
                        drop_time=self.parse_datetime(row["drop_time"], allow_blank=True),
                        distance_km=row["distance_km"],
                        fare=row["fare"],
                        status=row["status"].strip(),
                        cancellation_reason=row["cancellation_reason"].strip(),
                    )
                )

        return trips

    def load_activities(self, filepath):
        activities = []

        rows = self._read_csv(
            filepath,
            {"driver_id", "timestamp", "status"},
        )

        for row in rows:
                activities.append(
                    DriverActivity(
                        driver_id=row["driver_id"].strip(),
                        timestamp=self.parse_datetime(row["timestamp"]),
                        status=row["status"].strip(),
                    )
                )

        return activities

    def create_zones(self, trips):
        zones = {}

        for trip in trips:
            key = (trip.city, trip.pickup_zone)

            if key not in zones:
                zones[key] = Zone(trip.pickup_zone, trip.city)

            zones[key].add_trip(trip)

        return list(zones.values())
