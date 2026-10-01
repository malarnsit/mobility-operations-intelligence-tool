from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from werkzeug.utils import secure_filename

import os

from services.anomaly_service import AnomalyDetector
from services.insights_service import InsightsEngine
from services.data_loader import DataLoader
from services.validation_service import DataValidator
from services.analytics_service import AnalyticsService
from services.advanced_analytics_service import AdvancedAnalyticsService


app = Flask(__name__)

app.secret_key = "mobility-operations-secret-key"

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "data",
    "uploads"
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


ALLOWED_EXTENSIONS = {"csv"}


# ==========================================================
# APPLICATION STATE
# ==========================================================

app_state = {
    "drivers": [],
    "trips": [],
    "activities": [],
    "zones": [],
    "validation": None,
    "analytics": None,

    # DAY 4
    "anomaly_detector": None,
    "insights": []
}


# ==========================================================
# FILE HELPERS
# ==========================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_uploaded_file(file):

    if file is None:
        return None

    if file.filename == "":
        return None

    if not allowed_file(file.filename):

        raise ValueError(
            "Only CSV files are allowed."
        )

    filename = secure_filename(
        file.filename
    )

    filepath = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    file.save(filepath)

    return filepath


# ==========================================================
# LOAD DATASET
# ==========================================================

def load_dataset(
    drivers_path,
    trips_path,
    activity_path
):

    loader = DataLoader()

    # ------------------------------------------------------
    # LOAD DRIVERS
    # ------------------------------------------------------

    drivers = loader.load_drivers(
        drivers_path
    )

    # ------------------------------------------------------
    # LOAD TRIPS
    # ------------------------------------------------------

    trips = loader.load_trips(
        trips_path
    )

    # ------------------------------------------------------
    # LOAD DRIVER ACTIVITY
    # ------------------------------------------------------

    activities = loader.load_activities(
        activity_path
    )

    # ------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------

    validation = DataValidator(
        drivers,
        trips,
        activities
    )

    validation_result = (
        validation.validate_all()
    )

    # ------------------------------------------------------
    # CREATE ZONES
    # ------------------------------------------------------

    zones = loader.create_zones(
        trips
    )

    # ======================================================
    # DAY 2 + DAY 3 ANALYTICS
    # ======================================================

    analytics = AdvancedAnalyticsService(
        drivers,
        trips,
        activities
    )

    # ======================================================
    # DAY 4 - ANOMALY DETECTOR
    # ======================================================

    anomaly_detector = AnomalyDetector(
        drivers=drivers,
        trips=trips,
        activities=activities,

        # Configurable threshold
        fare_threshold=2000,

        # Distance must not be negative
        min_distance_km=0
    )

    # ======================================================
    # DAY 4 - INSIGHTS ENGINE
    # ======================================================

    insights_engine = InsightsEngine(
        analytics=analytics,
        advanced_analytics=analytics,
        anomaly_detector=anomaly_detector
    )

    # Generate business insights
    insights = (
        insights_engine.generate_insights()
    )

    # ======================================================
    # SAVE EVERYTHING IN APPLICATION STATE
    # ======================================================

    app_state["drivers"] = drivers

    app_state["trips"] = trips

    app_state["activities"] = activities

    app_state["zones"] = zones

    app_state["validation"] = (
        validation_result
    )

    app_state["analytics"] = analytics

    # DAY 4
    app_state["anomaly_detector"] = (
        anomaly_detector
    )

    app_state["insights"] = insights

    return validation_result


# ==========================================================
# HOME / UPLOAD
# ==========================================================

@app.route(
    "/",
    methods=["GET", "POST"]
)
def index():

    if request.method == "POST":

        try:

            drivers_file = request.files.get(
                "drivers_file"
            )

            trips_file = request.files.get(
                "trips_file"
            )

            activity_file = request.files.get(
                "activity_file"
            )

            # ------------------------------------------------
            # CHECK DRIVERS FILE
            # ------------------------------------------------

            if not drivers_file:

                flash(
                    "Please upload the drivers CSV file.",
                    "error"
                )

                return redirect(
                    url_for("index")
                )

            # ------------------------------------------------
            # CHECK TRIPS FILE
            # ------------------------------------------------

            if not trips_file:

                flash(
                    "Please upload the trips CSV file.",
                    "error"
                )

                return redirect(
                    url_for("index")
                )

            # ------------------------------------------------
            # CHECK ACTIVITY FILE
            # ------------------------------------------------

            if not activity_file:

                flash(
                    "Please upload the driver activity CSV file.",
                    "error"
                )

                return redirect(
                    url_for("index")
                )

            # ------------------------------------------------
            # SAVE FILES
            # ------------------------------------------------

            drivers_path = save_uploaded_file(
                drivers_file
            )

            trips_path = save_uploaded_file(
                trips_file
            )

            activity_path = save_uploaded_file(
                activity_file
            )

            # ------------------------------------------------
            # LOAD DATA
            # ------------------------------------------------

            validation_result = load_dataset(
                drivers_path,
                trips_path,
                activity_path
            )

            # ------------------------------------------------
            # DISPLAY VALIDATION MESSAGE
            # ------------------------------------------------

            if validation_result.errors:

                flash(
                    "Data loaded with validation errors. "
                    "See the dashboard for details.",
                    "error"
                )

            elif validation_result.warnings:

                flash(
                    "Data loaded with warnings. "
                    "See the dashboard for details.",
                    "warning"
                )

            else:

                flash(
                    "Data uploaded and validated successfully.",
                    "success"
                )

            return redirect(
                url_for("dashboard")
            )

        except Exception as exc:

            flash(
                f"Error while loading data: {exc}",
                "error"
            )

            return redirect(
                url_for("index")
            )

    return render_template(
        "index.html"
    )


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    analytics = app_state["analytics"]

    if analytics is None:

        flash(
            "Please upload the CSV files first.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    trip_summary = (
        analytics.trip_summary()
    )

    driver_summaries = (
        analytics.all_driver_summaries()
    )

    zone_summaries = (
        analytics.zone_summaries()
    )

    city_summaries = (
        analytics.city_summaries()
    )

    top_drivers = (
        analytics.rank_drivers_by_fare(10)
    )

    top_zones = (
        analytics.rank_zones_by_trips(10)
    )

    status_frequency = (
        analytics.trip_status_frequency()
    )

    cancellation_frequency = (
        analytics.cancellation_reason_frequency()
    )

    return render_template(
        "dashboard.html",

        drivers=analytics.drivers,

        trips=analytics.trips,

        activities=analytics.activities,

        validation=app_state["validation"],

        trip_summary=trip_summary,

        driver_summaries=driver_summaries,

        zone_summaries=zone_summaries,

        city_summaries=city_summaries,

        top_drivers=top_drivers,

        top_zones=top_zones,

        status_frequency=status_frequency,

        cancellation_frequency=cancellation_frequency
    )


# ==========================================================
# DRIVER PAGE
# ==========================================================

@app.route("/drivers")
def drivers():

    analytics = app_state["analytics"]

    if analytics is None:

        flash(
            "Please upload the CSV files first.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    if keyword:

        search_results = (
            analytics.search_drivers(
                keyword
            )
        )

    else:

        search_results = analytics.drivers

    driver_summaries = []

    for driver in search_results:

        summary = analytics.driver_summary(
            driver.driver_id
        )

        if summary is not None:

            driver_summaries.append(
                summary
            )

    return render_template(
        "drivers.html",

        drivers=search_results,

        driver_summaries=driver_summaries,

        keyword=keyword
    )


# ==========================================================
# TRIPS PAGE
# ==========================================================

@app.route("/trips")
def trips():

    analytics = app_state["analytics"]

    if analytics is None:

        flash(
            "Please upload the CSV files first.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    keyword = request.args.get(
        "q",
        ""
    ).strip()

    if keyword:

        trip_results = (
            analytics.search_trips(
                keyword
            )
        )

    else:

        trip_results = analytics.trips

    status_frequency = (
        analytics.trip_status_frequency()
    )

    cancellation_frequency = (
        analytics.cancellation_reason_frequency()
    )

    return render_template(
        "trips.html",

        trips=trip_results,

        keyword=keyword,

        status_frequency=status_frequency,

        cancellation_frequency=cancellation_frequency
    )


# ==========================================================
# ZONES PAGE
# ==========================================================

@app.route("/zones")
def zones():

    analytics = app_state["analytics"]

    if analytics is None:

        flash(
            "Please upload the CSV files first.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    zone_summaries = (
        analytics.zone_summaries()
    )

    top_zones = (
        analytics.rank_zones_by_trips(10)
    )

    return render_template(
        "zones.html",

        zone_summaries=zone_summaries,

        top_zones=top_zones
    )


# ==========================================================
# DAY 3 - ADVANCED ANALYTICS
# ==========================================================

@app.route("/advanced")
def advanced():

    analytics = app_state["analytics"]

    if analytics is None:

        flash(
            "Please upload the CSV files first.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    top_drivers = (
        analytics.top_k_drivers_by_fare(10)
    )

    consecutive_trips = (
        analytics.consecutive_trip_analysis()
    )

    idle_analysis = (
        analytics.idle_time_analysis(
            threshold_minutes=30
        )
    )

    peak_demand = (
        analytics.peak_demand_analysis()
    )

    utilization = (
        analytics.driver_utilization()
    )

    cancellation = (
        analytics.cancellation_intelligence()
    )

    return render_template(
        "advanced.html",

        top_drivers=top_drivers,

        consecutive_trips=consecutive_trips,

        idle_analysis=idle_analysis,

        peak_demand=peak_demand,

        utilization=utilization,

        cancellation=cancellation
    )


# ==========================================================
# DAY 4 - INSIGHTS AND ANOMALIES
# ==========================================================

@app.route("/insights")
def insights():

    analytics = app_state["analytics"]

    anomaly_detector = (
        app_state["anomaly_detector"]
    )

    if analytics is None:

        flash(
            "Please upload the CSV files first.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    if anomaly_detector is None:

        flash(
            "Anomaly detector is not initialized.",
            "error"
        )

        return redirect(
            url_for("index")
        )

    # ------------------------------------------------------
    # GET ANOMALIES
    # ------------------------------------------------------

    anomalies = (
        anomaly_detector.detect_all()
    )

    # ------------------------------------------------------
    # GET ANOMALY SUMMARY
    # ------------------------------------------------------

    anomaly_summary = (
        anomaly_detector.anomaly_summary()
    )

    # ------------------------------------------------------
    # GET CURRENT THRESHOLDS
    # ------------------------------------------------------

    thresholds = (
        anomaly_detector.get_thresholds()
    )

    return render_template(
        "insights.html",

        insights=app_state["insights"],

        anomalies=anomalies,

        anomaly_summary=anomaly_summary,

        thresholds=thresholds
    )


# ==========================================================
# FILE SIZE ERROR
# ==========================================================

@app.errorhandler(413)
def request_entity_too_large(error):

    flash(
        "Uploaded file is too large. Maximum size is 16 MB.",
        "error"
    )

    return redirect(
        url_for("index")
    )


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )