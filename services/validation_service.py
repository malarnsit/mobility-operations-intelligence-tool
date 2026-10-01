
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class ValidationResult:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)


class DataValidator:

    def __init__(
        self,
        drivers=None,
        trips=None,
        activities=None
    ):
        """
        Store the loaded Python objects.

        drivers    -> list of Driver objects
        trips      -> list of Trip objects
        activities -> list of DriverActivity objects
        """

        self.drivers = drivers or []
        self.trips = trips or []
        self.activities = activities or []


    # ---------------------------------------------------------
    # MAIN VALIDATION
    # ---------------------------------------------------------

    def validate_all(self):

        result = ValidationResult()

        # Validate each dataset
        driver_errors, driver_warnings = (
            self._validate_drivers()
        )

        trip_errors, trip_warnings = (
            self._validate_trips()
        )

        activity_errors, activity_warnings = (
            self._validate_activities()
        )

        # Combine errors
        result.errors.extend(driver_errors)
        result.errors.extend(trip_errors)
        result.errors.extend(activity_errors)

        # Combine warnings
        result.warnings.extend(driver_warnings)
        result.warnings.extend(trip_warnings)
        result.warnings.extend(activity_warnings)

        # Summary
        result.summary = {
            "drivers": len(self.drivers),
            "trips": len(self.trips),
            "activities": len(self.activities),
            "errors": len(result.errors),
            "warnings": len(result.warnings)
        }

        return result


    # ---------------------------------------------------------
    # DRIVER VALIDATION
    # ---------------------------------------------------------

    def _validate_drivers(self):

        errors = []
        warnings = []

        driver_ids = []

        for driver in self.drivers:

            # Check driver ID
            if not driver.driver_id:
                errors.append(
                    "Driver has missing driver_id."
                )
            else:
                driver_ids.append(
                    driver.driver_id
                )

            # Check driver name
            if not driver.driver_name:
                warnings.append(
                    f"Driver {driver.driver_id} "
                    f"has missing driver_name."
                )

            # Check city
            if not driver.city:
                warnings.append(
                    f"Driver {driver.driver_id} "
                    f"has missing city."
                )

            # Check rating
            if driver.rating is not None:

                try:

                    rating = float(
                        driver.rating
                    )

                    if rating < 0 or rating > 5:
                        errors.append(
                            f"Driver {driver.driver_id} "
                            f"has invalid rating: {rating}"
                        )

                except (ValueError, TypeError):

                    errors.append(
                        f"Driver {driver.driver_id} "
                        f"has invalid rating."
                    )

        # Duplicate driver IDs
        counts = Counter(driver_ids)

        for driver_id, count in counts.items():

            if count > 1:

                errors.append(
                    f"Duplicate driver_id found: "
                    f"{driver_id}"
                )

        return errors, warnings


    # ---------------------------------------------------------
    # TRIP VALIDATION
    # ---------------------------------------------------------

    def _validate_trips(self):

        errors = []
        warnings = []

        trip_ids = []

        driver_ids = {
            driver.driver_id
            for driver in self.drivers
        }

        for trip in self.trips:

            # Trip ID
            if not trip.trip_id:

                errors.append(
                    "Trip has missing trip_id."
                )

            else:

                trip_ids.append(
                    trip.trip_id
                )

            # Driver ID
            if not trip.driver_id:

                errors.append(
                    f"Trip {trip.trip_id} "
                    f"has missing driver_id."
                )

            elif trip.driver_id not in driver_ids:

                errors.append(
                    f"Trip {trip.trip_id} "
                    f"references unknown driver "
                    f"{trip.driver_id}."
                )

            # Distance
            if trip.distance_km is not None:

                try:

                    distance = float(
                        trip.distance_km
                    )

                    if distance < 0:

                        errors.append(
                            f"Trip {trip.trip_id} "
                            f"has negative distance: "
                            f"{distance}"
                        )

                except (ValueError, TypeError):

                    errors.append(
                        f"Trip {trip.trip_id} "
                        f"has invalid distance."
                    )

            # Fare
            if trip.fare is not None:

                try:

                    fare = float(
                        trip.fare
                    )

                    if fare < 0:

                        errors.append(
                            f"Trip {trip.trip_id} "
                            f"has negative fare: "
                            f"{fare}"
                        )

                except (ValueError, TypeError):

                    errors.append(
                        f"Trip {trip.trip_id} "
                        f"has invalid fare."
                    )

            # Pickup / drop time
            if (
                trip.pickup_time is not None
                and
                trip.drop_time is not None
            ):

                if trip.drop_time < trip.pickup_time:

                    errors.append(
                        f"Trip {trip.trip_id} "
                        f"has drop_time before "
                        f"pickup_time."
                    )

            # Completed trip timestamps
            if trip.is_completed():

                if trip.pickup_time is None:

                    warnings.append(
                        f"Completed trip "
                        f"{trip.trip_id} has no "
                        f"pickup_time."
                    )

                if trip.drop_time is None:

                    warnings.append(
                        f"Completed trip "
                        f"{trip.trip_id} has no "
                        f"drop_time."
                    )

            # Cancelled trip reason
            if trip.is_cancelled():

                if not trip.cancellation_reason:

                    warnings.append(
                        f"Cancelled trip "
                        f"{trip.trip_id} has no "
                        f"cancellation_reason."
                    )

        # Duplicate trip IDs
        counts = Counter(trip_ids)

        for trip_id, count in counts.items():

            if count > 1:

                errors.append(
                    f"Duplicate trip_id found: "
                    f"{trip_id}"
                )

        return errors, warnings


    # ---------------------------------------------------------
    # ACTIVITY VALIDATION
    # ---------------------------------------------------------

    def _validate_activities(self):

        errors = []
        warnings = []

        driver_ids = {
            driver.driver_id
            for driver in self.drivers
        }

        for activity in self.activities:

            if not activity.driver_id:

                errors.append(
                    "Activity has missing driver_id."
                )

            elif activity.driver_id not in driver_ids:

                errors.append(
                    f"Activity references unknown "
                    f"driver {activity.driver_id}."
                )

            if not activity.timestamp:

                errors.append(
                    f"Activity for driver "
                    f"{activity.driver_id} "
                    f"has missing timestamp."
                )

            if not activity.status:

                warnings.append(
                    f"Activity for driver "
                    f"{activity.driver_id} "
                    f"has missing status."
                )

        return errors, warnings
