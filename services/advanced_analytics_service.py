from collections import defaultdict, Counter
from datetime import datetime
import heapq

from services.analytics_service import AnalyticsService


class AdvancedAnalyticsService(AnalyticsService):

    # =====================================================
    # HELPER FUNCTION
    # =====================================================

    def _to_datetime(self, value):

        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        try:
            return datetime.strptime(
                str(value),
                "%Y-%m-%d %H:%M:%S"
            )

        except (ValueError, TypeError):
            return None

    # =====================================================
    # 1. TOP-K DRIVERS USING HEAP
    # =====================================================

    def top_k_drivers_by_fare(self, k=10):

        if k <= 0:
            return []

        heap = []

        for driver in self.drivers:

            driver_trips = self.trips_by_driver.get(
                driver.driver_id,
                []
            )

            total_fare = sum(
                trip.fare
                for trip in driver_trips
                if trip.is_completed()
            )

            item = (
                total_fare,
                driver.driver_id,
                driver
            )

            # Fill heap until K elements
            if len(heap) < k:

                heapq.heappush(
                    heap,
                    item
                )

            # Replace smallest element
            elif total_fare > heap[0][0]:

                heapq.heapreplace(
                    heap,
                    item
                )

        # Highest fare first
        heap.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [
            {
                "driver": item[2],
                "total_fare": item[0]
            }
            for item in heap
        ]

    # =====================================================
    # 2. CONSECUTIVE COMPLETED TRIPS
    # =====================================================

    def consecutive_trip_analysis(self):

        results = []

        for driver in self.drivers:

            driver_trips = self.trips_by_driver.get(
                driver.driver_id,
                []
            )

            completed_trips = [
                trip
                for trip in driver_trips
                if trip.is_completed()
            ]

            completed_trips.sort(
                key=lambda trip: (
                    self._to_datetime(
                        trip.request_time
                    )
                    or datetime.min
                )
            )

            if not completed_trips:

                results.append({
                    "driver_id": driver.driver_id,
                    "driver_name": driver.driver_name,
                    "total_completed_trips": 0,
                    "longest_consecutive_streak": 0
                })

                continue

            current_streak = 1
            longest_streak = 1

            for i in range(
                1,
                len(completed_trips)
            ):

                previous_trip = completed_trips[i - 1]
                current_trip = completed_trips[i]

                previous_drop = self._to_datetime(
                    previous_trip.drop_time
                )

                current_pickup = self._to_datetime(
                    current_trip.pickup_time
                )

                if (
                    previous_drop is not None
                    and current_pickup is not None
                    and current_pickup >= previous_drop
                ):

                    current_streak += 1

                    longest_streak = max(
                        longest_streak,
                        current_streak
                    )

                else:

                    current_streak = 1

            results.append({
                "driver_id": driver.driver_id,
                "driver_name": driver.driver_name,
                "total_completed_trips": len(
                    completed_trips
                ),
                "longest_consecutive_streak": longest_streak
            })

        results.sort(
            key=lambda x: x["longest_consecutive_streak"],
            reverse=True
        )

        return results

    # =====================================================
    # 3. IDLE TIME DETECTION
    # =====================================================

    def idle_time_analysis(self, threshold_minutes=30):

        results = []

        for driver in self.drivers:

            driver_trips = self.trips_by_driver.get(
                driver.driver_id,
                []
            )

            completed_trips = [
                trip
                for trip in driver_trips
                if trip.is_completed()
                and trip.drop_time is not None
                and trip.pickup_time is not None
            ]

            completed_trips.sort(
                key=lambda trip: (
                    self._to_datetime(
                        trip.pickup_time
                    )
                    or datetime.min
                )
            )

            idle_periods = []

            for i in range(
                1,
                len(completed_trips)
            ):

                previous_trip = completed_trips[i - 1]
                current_trip = completed_trips[i]

                previous_drop = self._to_datetime(
                    previous_trip.drop_time
                )

                current_pickup = self._to_datetime(
                    current_trip.pickup_time
                )

                if (
                    previous_drop is None
                    or current_pickup is None
                ):
                    continue

                idle_minutes = (
                    current_pickup - previous_drop
                ).total_seconds() / 60

                # Only consider positive gaps
                if idle_minutes >= threshold_minutes:

                    idle_periods.append({
                        "previous_trip": previous_trip.trip_id,
                        "next_trip": current_trip.trip_id,
                        "idle_minutes": round(
                            idle_minutes,
                            2
                        )
                    })

            total_idle_minutes = sum(
                period["idle_minutes"]
                for period in idle_periods
            )

            longest_idle_minutes = max(
                (
                    period["idle_minutes"]
                    for period in idle_periods
                ),
                default=0
            )

            results.append({
                "driver_id": driver.driver_id,
                "driver_name": driver.driver_name,
                "idle_periods": len(
                    idle_periods
                ),
                "total_idle_minutes": round(
                    total_idle_minutes,
                    2
                ),
                "longest_idle_minutes": round(
                    longest_idle_minutes,
                    2
                )
            })

        results.sort(
            key=lambda x: x["total_idle_minutes"],
            reverse=True
        )

        return results

    # =====================================================
    # 4. PEAK DEMAND ANALYSIS
    # =====================================================

    def peak_demand_analysis(self):

        hourly_demand = Counter()

        for trip in self.trips:

            request_time = self._to_datetime(
                trip.request_time
            )

            if request_time is None:
                continue

            hour = request_time.hour

            hourly_demand[hour] += 1

        results = []

        for hour, count in hourly_demand.items():

            results.append({
                "hour": hour,
                "trip_count": count
            })

        results.sort(
            key=lambda x: (
                -x["trip_count"],
                x["hour"]
            )
        )

        return results

    # =====================================================
    # 5. DRIVER UTILIZATION
    # =====================================================

    def driver_utilization(self):

        activity_by_driver = defaultdict(list)

        for activity in self.activities:

            activity_by_driver[
                activity.driver_id
            ].append(activity)

        results = []

        for driver in self.drivers:

            activities = activity_by_driver.get(
                driver.driver_id,
                []
            )

            activities.sort(
                key=lambda activity: (
                    self._to_datetime(
                        activity.timestamp
                    )
                    or datetime.min
                )
            )

            online_minutes = 0
            busy_minutes = 0

            for i in range(
                1,
                len(activities)
            ):

                previous = activities[i - 1]
                current = activities[i]

                previous_time = self._to_datetime(
                    previous.timestamp
                )

                current_time = self._to_datetime(
                    current.timestamp
                )

                if (
                    previous_time is None
                    or current_time is None
                ):
                    continue

                duration = (
                    current_time - previous_time
                ).total_seconds() / 60

                if duration < 0:
                    continue

                # Driver is available during
                # Online / Busy / Idle states
                if previous.status in {
                    "Online",
                    "Busy",
                    "Idle"
                }:

                    online_minutes += duration

                # Driver is actually working
                if previous.status == "Busy":

                    busy_minutes += duration

            utilization_rate = (
                busy_minutes / online_minutes * 100
                if online_minutes > 0
                else 0
            )

            results.append({
                "driver_id": driver.driver_id,
                "driver_name": driver.driver_name,
                "online_minutes": round(
                    online_minutes,
                    2
                ),
                "busy_minutes": round(
                    busy_minutes,
                    2
                ),
                "utilization_rate": round(
                    utilization_rate,
                    2
                )
            })

        results.sort(
            key=lambda x: x["utilization_rate"],
            reverse=True
        )

        return results

    # =====================================================
    # 6. CANCELLATION INTELLIGENCE
    # =====================================================

    def cancellation_intelligence(self):

        cancelled_trips = [
            trip
            for trip in self.trips
            if trip.is_cancelled()
        ]

        total_trips = len(self.trips)

        total_cancelled = len(
            cancelled_trips
        )

        overall_rate = (
            total_cancelled / total_trips * 100
            if total_trips > 0
            else 0
        )

        # -------------------------------------------------
        # Cancellation by CITY
        # -------------------------------------------------

        city_total = Counter()
        city_cancelled = Counter()

        for trip in self.trips:

            city_total[trip.city] += 1

            if trip.is_cancelled():

                city_cancelled[trip.city] += 1

        by_city = []

        for city in city_total:

            total = city_total[city]
            cancelled = city_cancelled[city]

            rate = (
                cancelled / total * 100
                if total > 0
                else 0
            )

            by_city.append({
                "city": city,
                "total_trips": total,
                "cancelled_trips": cancelled,
                "cancellation_rate": round(
                    rate,
                    2
                )
            })

        by_city.sort(
            key=lambda x: x["cancellation_rate"],
            reverse=True
        )

        # -------------------------------------------------
        # Cancellation by DRIVER
        # -------------------------------------------------

        driver_total = Counter()
        driver_cancelled = Counter()

        for trip in self.trips:

            driver_total[trip.driver_id] += 1

            if trip.is_cancelled():

                driver_cancelled[
                    trip.driver_id
                ] += 1

        by_driver = []

        for driver_id in driver_total:

            total = driver_total[driver_id]
            cancelled = driver_cancelled[driver_id]

            rate = (
                cancelled / total * 100
                if total > 0
                else 0
            )

            driver = self.driver_index.get(
                driver_id
            )

            driver_name = (
                driver.driver_name
                if driver is not None
                else "Unknown"
            )

            by_driver.append({
                "driver_id": driver_id,
                "driver_name": driver_name,
                "total_trips": total,
                "cancelled_trips": cancelled,
                "cancellation_rate": round(
                    rate,
                    2
                )
            })

        by_driver.sort(
            key=lambda x: x["cancellation_rate"],
            reverse=True
        )

        # -------------------------------------------------
        # Cancellation by REASON
        # -------------------------------------------------

        reason_frequency = Counter(
            trip.cancellation_reason
            for trip in cancelled_trips
            if trip.cancellation_reason
        )

        return {
            "total_cancelled": total_cancelled,

            "overall_cancellation_rate": round(
                overall_rate,
                2
            ),

            "by_city": by_city,

            "by_driver": by_driver,

            "by_reason": dict(
                reason_frequency
            )
        }