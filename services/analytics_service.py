from collections import Counter, defaultdict
from statistics import mean


class AnalyticsService:

    def __init__(self, drivers, trips, activities):

        self.drivers = drivers
        self.trips = trips
        self.activities = activities

        self.driver_index = {
            driver.driver_id: driver
            for driver in drivers
        }

        self.trip_index = {
            trip.trip_id: trip
            for trip in trips
        }

        self.trips_by_driver = defaultdict(list)
        self.trips_by_city = defaultdict(list)
        self.trips_by_zone = defaultdict(list)

        for trip in trips:

            self.trips_by_driver[
                trip.driver_id
            ].append(trip)

            self.trips_by_city[
                trip.city
            ].append(trip)

            zone_key = (
                trip.city,
                trip.pickup_zone
            )

            self.trips_by_zone[
                zone_key
            ].append(trip)

    # -----------------------------------------
    # DRIVER ANALYTICS
    # -----------------------------------------

    def driver_summary(self, driver_id):

        driver = self.driver_index.get(driver_id)

        if driver is None:
            return None

        driver_trips = self.trips_by_driver.get(
            driver_id,
            []
        )

        completed = [
            trip
            for trip in driver_trips
            if trip.is_completed()
        ]

        cancelled = [
            trip
            for trip in driver_trips
            if trip.is_cancelled()
        ]

        total_fare = sum(
            trip.fare
            for trip in completed
        )

        average_fare = (
            mean(trip.fare for trip in completed)
            if completed
            else 0
        )

        return {
            "driver_id": driver.driver_id,
            "driver_name": driver.driver_name,
            "city": driver.city,
            "vehicle_type": driver.vehicle_type,
            "rating": driver.rating,
            "status": driver.status,
            "total_trips": len(driver_trips),
            "completed_trips": len(completed),
            "cancelled_trips": len(cancelled),
            "total_fare": total_fare,
            "average_fare": average_fare
        }

    def all_driver_summaries(self):

        summaries = []

        for driver in self.drivers:

            summary = self.driver_summary(
                driver.driver_id
            )

            if summary is not None:
                summaries.append(summary)

        return summaries

    def rank_drivers_by_fare(self, top_k=10):

        ranked = []

        for driver in self.drivers:

            trips = self.trips_by_driver.get(
                driver.driver_id,
                []
            )

            total_fare = sum(
                trip.fare
                for trip in trips
                if trip.is_completed()
            )

            ranked.append({
                "driver": driver,
                "total_fare": total_fare
            })

        ranked.sort(
            key=lambda x: x["total_fare"],
            reverse=True
        )

        return ranked[:top_k]

    def search_drivers(self, keyword):

        keyword = keyword.lower()

        results = []

        for driver in self.drivers:

            if (
                keyword in driver.driver_id.lower()
                or keyword in driver.driver_name.lower()
                or keyword in driver.city.lower()
            ):

                results.append(driver)

        return results

    # -----------------------------------------
    # TRIP ANALYTICS
    # -----------------------------------------

    def trip_summary(self):

        total = len(self.trips)

        completed = sum(
            1
            for trip in self.trips
            if trip.is_completed()
        )

        cancelled = sum(
            1
            for trip in self.trips
            if trip.is_cancelled()
        )

        total_fare = sum(
            trip.fare
            for trip in self.trips
            if trip.is_completed()
        )

        return {
            "total_trips": total,
            "completed_trips": completed,
            "cancelled_trips": cancelled,
            "total_fare": total_fare
        }

    def trip_status_frequency(self):

        return dict(
            Counter(
                trip.status
                for trip in self.trips
            )
        )

    def cancellation_reason_frequency(self):

        return dict(
            Counter(
                trip.cancellation_reason
                for trip in self.trips
                if trip.is_cancelled()
                and trip.cancellation_reason
            )
        )

    def search_trips(self, keyword):

        keyword = keyword.lower()

        results = []

        for trip in self.trips:

            searchable_values = [
                trip.trip_id,
                trip.driver_id,
                trip.rider_id,
                trip.city,
                trip.pickup_zone,
                trip.drop_zone,
                trip.status
            ]

            if any(
                keyword in str(value).lower()
                for value in searchable_values
                if value is not None
            ):

                results.append(trip)

        return results

    # -----------------------------------------
    # ZONE ANALYTICS
    # -----------------------------------------

    def zone_summaries(self):

        results = []

        for (city, zone), trips in self.trips_by_zone.items():

            completed = sum(
                1
                for trip in trips
                if trip.is_completed()
            )

            cancelled = sum(
                1
                for trip in trips
                if trip.is_cancelled()
            )

            total_fare = sum(
                trip.fare
                for trip in trips
                if trip.is_completed()
            )

            results.append({
                "city": city,
                "zone": zone,
                "total_trips": len(trips),
                "completed_trips": completed,
                "cancelled_trips": cancelled,
                "total_fare": total_fare
            })

        return results

    def rank_zones_by_trips(self, top_k=10):

        zones = self.zone_summaries()

        return sorted(
            zones,
            key=lambda x: x["total_trips"],
            reverse=True
        )[:top_k]

    # -----------------------------------------
    # CITY ANALYTICS
    # -----------------------------------------

    def city_summaries(self):

        results = []

        for city, trips in self.trips_by_city.items():

            completed = sum(
                1
                for trip in trips
                if trip.is_completed()
            )

            cancelled = sum(
                1
                for trip in trips
                if trip.is_cancelled()
            )

            total_fare = sum(
                trip.fare
                for trip in trips
                if trip.is_completed()
            )

            results.append({
                "city": city,
                "total_trips": len(trips),
                "completed_trips": completed,
                "cancelled_trips": cancelled,
                "total_fare": total_fare
            })

        return results
