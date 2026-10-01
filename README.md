# Mobility Operations Intelligence Tool

## Day 1 - Architecture + Data Layer

This project is a Flask-based Mobility Operations Intelligence Tool.

Day 1 implements:

- Flask application
- CSV upload
- CSV validation
- Object-oriented Driver, Trip, Zone and DriverActivity models
- Data loading
- Validation error handling
- Loaded-data summary

## Project Flow

```text
Upload CSV files
      ↓
Flask request
      ↓
DataLoader
      ↓
Driver / Trip / DriverActivity objects
      ↓
DataValidator
      ↓
Zone object creation
      ↓
Dashboard summary
```

## Setup

Create a virtual environment:

```bash
python3 -m venv venv
```

Activate it:

Linux/macOS:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Generate the sample dataset:

```bash
python generate_sample_data.py
```

Run the application:

```bash
python python_app.py
```

Open:

```text
http://127.0.0.1:5000
```

## CSV Files

### drivers.csv

Required columns:

```text
driver_id
driver_name
city
vehicle_type
rating
status
```

### trips.csv

Required columns:

```text
trip_id
driver_id
rider_id
city
pickup_zone
drop_zone
request_time
pickup_time
drop_time
distance_km
fare
status
cancellation_reason
```

### driver_activity.csv

Required columns:

```text
driver_id
timestamp
status
```

## OOP Concepts

### Encapsulation

Driver, Trip, Zone and DriverActivity store their attributes using private fields such as:

```python
self.__driver_id
```

Properties provide controlled access.

### Methods

Examples:

```python
driver.is_active()
driver.get_profile()

trip.is_completed()
trip.calculate_duration()
trip.calculate_fare_per_km()

zone.get_total_requests()
```

### Separation of Responsibility

- `DataLoader` loads data.
- `DataValidator` validates data.
- Model classes represent business entities.
- Flask handles the web interface.

## Day 1 DSA

The following structures are already used:

- Lists for collections of objects.
- Sets for duplicate and ID validation.
- Dictionaries for zone indexing.
- Sequential traversal for validation and object creation.

Day 2 and Day 3 will extend this into search, frequency counting, ranking and Top-K analysis.

## Known Day 1 Limitation

Analytics such as revenue, utilization, Top-K, anomaly detection and cancellation intelligence are intentionally implemented in later days.
