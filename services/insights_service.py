class InsightsEngine:

    def __init__(
        self,
        analytics,
        advanced_analytics,
        anomaly_detector
    ):

        self.analytics = analytics

        self.advanced = advanced_analytics

        self.anomaly_detector = anomaly_detector

    # ======================================================
    # 1. REVENUE INSIGHT
    # ======================================================

    def revenue_insight(self):

        summary = (
            self.analytics.trip_summary()
        )

        total_fare = summary[
            "total_fare"
        ]

        completed = summary[
            "completed_trips"
        ]

        if completed == 0:

            return (
                "No completed trips are available "
                "to calculate revenue performance."
            )

        average_fare = (
            total_fare / completed
        )

        return (
            f"Completed trips generated total fare "
            f"of ₹{total_fare:,.2f}, with an average "
            f"fare of ₹{average_fare:,.2f} per "
            f"completed trip."
        )

    # ======================================================
    # 2. CANCELLATION INSIGHT
    # ======================================================

    def cancellation_insight(self):

        result = (
            self.advanced
            .cancellation_intelligence()
        )

        rate = result[
            "overall_cancellation_rate"
        ]

        if rate >= 15:

            return (
                f"Overall cancellation rate is "
                f"{rate:.2f}%, which indicates a "
                f"relatively high level of cancellations "
                f"in the loaded dataset."
            )

        return (
            f"Overall cancellation rate is "
            f"{rate:.2f}%."
        )

    # ======================================================
    # 3. PEAK DEMAND INSIGHT
    # ======================================================

    def peak_demand_insight(self):

        peak = (
            self.advanced
            .peak_demand_analysis()
        )

        if not peak:

            return (
                "No demand data is available."
            )

        top = peak[0]

        return (
            f"Peak demand occurs around "
            f"{top['hour']:02d}:00 with "
            f"{top['trip_count']} trip requests."
        )

    # ======================================================
    # 4. DRIVER PERFORMANCE INSIGHT
    # ======================================================

    def driver_insight(self):

        top_drivers = (
            self.advanced
            .top_k_drivers_by_fare(1)
        )

        if not top_drivers:

            return (
                "No driver performance data "
                "is available."
            )

        top = top_drivers[0]

        return (
            f"Driver {top['driver'].driver_name} "
            f"({top['driver'].driver_id}) generated "
            f"the highest completed-trip fare among "
            f"the Top-K results: "
            f"₹{top['total_fare']:,.2f}."
        )

    # ======================================================
    # 5. UTILIZATION INSIGHT
    # ======================================================

    def utilization_insight(self):

        utilization = (
            self.advanced
            .driver_utilization()
        )

        if not utilization:

            return (
                "No driver activity data "
                "is available."
            )

        valid = [

            row

            for row in utilization

            if row["online_minutes"] > 0
        ]

        if not valid:

            return (
                "No driver has sufficient online "
                "activity to calculate utilization."
            )

        average = (
            sum(
                row["utilization_rate"]
                for row in valid
            )
            / len(valid)
        )

        return (
            f"Average driver utilization across "
            f"drivers with online activity is "
            f"{average:.2f}%."
        )

    # ======================================================
    # 6. ANOMALY INSIGHT
    # ======================================================

    def anomaly_insight(self):

        summary = (
            self.anomaly_detector
            .anomaly_summary()
        )

        total = summary[
            "total_anomalies"
        ]

        if total == 0:

            return (
                "No anomalies were detected using "
                "the configured thresholds."
            )

        return (
            f"{total} potential data-quality or "
            f"operational anomalies were detected. "
            f"Review the anomaly table for details."
        )

    # ======================================================
    # GENERATE ALL INSIGHTS
    # ======================================================

    def generate_insights(self):

        return [

            self.revenue_insight(),

            self.cancellation_insight(),

            self.peak_demand_insight(),

            self.driver_insight(),

            self.utilization_insight(),

            self.anomaly_insight()
        ]