"""
scripts/generate_synthetic_dataset.py
=======================================
Generates a realistic synthetic traffic dataset that mimics the structure
of the popular Kaggle 'Traffic Flow Dataset' and 'Metro Interstate Traffic
Volume' datasets.

The generated CSV simulates:
  - 8 junction locations (matching SignalAI demo junctions)
  - 30 days of observations (every 15 minutes per junction)
  - Realistic rush-hour patterns (morning: 8-10am, evening: 5-8pm)
  - Weekend vs weekday traffic differences
  - Weather-based traffic variation
  - Seasonal patterns

Output: data/raw/kaggle_traffic_dataset.csv

Usage:
    cd "/Users/sahilp4514/Desktop/mini project/all code file"
    python3 scripts/generate_synthetic_dataset.py
"""

import csv
import random
import math
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────────────────────────

OUTPUT_FILE = "data/raw/kaggle_traffic_dataset.csv"
RANDOM_SEED = 42          # For reproducibility
DAYS = 30                 # 30-day dataset
INTERVAL_MINUTES = 15     # Reading every 15 minutes
START_DATE = datetime(2024, 1, 1, 0, 0, 0)

# Junction definitions matching SignalAI demo junctions
JUNCTIONS = [
    {"junction_id": "J-101", "location_name": "Main St & 5th Ave",     "base_volume": 160},
    {"junction_id": "J-102", "location_name": "Broadway & 8th",         "base_volume": 140},
    {"junction_id": "J-103", "location_name": "Park Ave & Central",     "base_volume": 100},
    {"junction_id": "J-104", "location_name": "Oak St & 2nd Ave",       "base_volume": 90},
    {"junction_id": "J-105", "location_name": "Elm Rd & North Ring",    "base_volume": 60},
    {"junction_id": "J-106", "location_name": "Lake View & Sector 3",   "base_volume": 40},
    {"junction_id": "J-107", "location_name": "Industrial Bypass",      "base_volume": 30},
    {"junction_id": "J-108", "location_name": "Station Rd & MG Ave",    "base_volume": 150},
]

WEATHER_CONDITIONS = ["Clear", "Cloudy", "Light Rain", "Heavy Rain", "Fog", "Hazy"]
WEATHER_WEIGHTS    = [0.45,    0.25,     0.15,         0.05,         0.05,  0.05]

# ── Traffic pattern functions ─────────────────────────────────────────────────

def traffic_multiplier(hour: int, minute: int, is_weekend: bool) -> float:
    """
    Returns a multiplier (0.1 – 1.0) based on time of day and day type.
    Simulates realistic rush-hour patterns.
    """
    time_frac = hour + minute / 60.0

    if is_weekend:
        # Weekends: gentler, later peaks
        if 10 <= time_frac <= 14:
            return 0.6 + 0.2 * math.sin(math.pi * (time_frac - 10) / 4)
        elif 16 <= time_frac <= 20:
            return 0.5 + 0.15 * math.sin(math.pi * (time_frac - 16) / 4)
        elif 1 <= time_frac <= 5:
            return 0.05
        else:
            return 0.2
    else:
        # Weekdays: sharp morning and evening peaks
        if 7.5 <= time_frac <= 10:
            return 0.5 + 0.5 * math.sin(math.pi * (time_frac - 7.5) / 2.5)
        elif 16.5 <= time_frac <= 19.5:
            return 0.6 + 0.4 * math.sin(math.pi * (time_frac - 16.5) / 3.0)
        elif 12 <= time_frac <= 13.5:
            return 0.4  # lunch dip
        elif 1 <= time_frac <= 5:
            return 0.03
        else:
            return 0.2

def weather_multiplier(weather: str) -> float:
    """Returns volume reduction due to weather conditions."""
    return {
        "Clear":       1.00,
        "Cloudy":      0.95,
        "Light Rain":  0.85,
        "Heavy Rain":  0.60,
        "Fog":         0.70,
        "Hazy":        0.90,
    }.get(weather, 1.0)

def congestion_from_volume(volume: int, base_volume: int) -> int:
    """
    Derives congestion percentage (0–100) from vehicle volume
    relative to the junction's baseline capacity.
    """
    ratio = volume / max(base_volume, 1)
    congestion = min(100, int(ratio * 65))  # 65 = saturation point multiplier
    return max(0, congestion)

def traffic_level_from_congestion(congestion: int) -> str:
    """Assigns categorical traffic level based on congestion percentage."""
    if congestion < 40:
        return "LOW"
    elif congestion < 70:
        return "MODERATE"
    elif congestion < 90:
        return "HIGH"
    else:
        return "CRITICAL"

# ── Main generation ────────────────────────────────────────────────────────────

def generate():
    random.seed(RANDOM_SEED)
    rows = []

    total_timestamps = DAYS * 24 * (60 // INTERVAL_MINUTES)
    print(f"Generating dataset...")
    print(f"  Junctions : {len(JUNCTIONS)}")
    print(f"  Days      : {DAYS}")
    print(f"  Interval  : every {INTERVAL_MINUTES} minutes")
    print(f"  Est. rows : {len(JUNCTIONS) * total_timestamps:,}")

    current_dt = START_DATE

    for day in range(DAYS):
        dt = START_DATE + timedelta(days=day)
        is_weekend = dt.weekday() >= 5  # Saturday=5, Sunday=6

        for hour in range(24):
            for minute in range(0, 60, INTERVAL_MINUTES):
                ts = datetime(dt.year, dt.month, dt.day, hour, minute, 0)

                # Pick weather once per hour (same for all junctions that hour)
                weather = random.choices(WEATHER_CONDITIONS, WEATHER_WEIGHTS)[0]
                w_mult  = weather_multiplier(weather)
                t_mult  = traffic_multiplier(hour, minute, is_weekend)

                for junc in JUNCTIONS:
                    # Add realistic noise
                    noise = random.gauss(1.0, 0.12)
                    noise = max(0.05, noise)

                    volume = int(junc["base_volume"] * t_mult * w_mult * noise)
                    volume = max(0, volume)

                    congestion = congestion_from_volume(volume, junc["base_volume"])
                    level = traffic_level_from_congestion(congestion)

                    # Occasionally inject missing values (simulate real-world data quality)
                    if random.random() < 0.008:   # 0.8% missing vehicles
                        volume_str = ""
                    else:
                        volume_str = str(volume)

                    if random.random() < 0.003:   # 0.3% missing congestion
                        congestion_str = ""
                    else:
                        congestion_str = str(congestion)

                    rows.append({
                        "timestamp":            ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "junction_id":          junc["junction_id"],
                        "location_name":        junc["location_name"],
                        "vehicle_count":        volume_str,
                        "congestion_pct":       congestion_str,
                        "traffic_level":        level,
                        "weather_condition":    weather,
                        "day_of_week":          ts.strftime("%A"),
                        "is_weekend":           "1" if is_weekend else "0",
                        "hour_of_day":          str(hour),
                    })

    # Write CSV
    fieldnames = [
        "timestamp", "junction_id", "location_name",
        "vehicle_count", "congestion_pct", "traffic_level",
        "weather_condition", "day_of_week", "is_weekend", "hour_of_day",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✓ Written {len(rows):,} rows to: {OUTPUT_FILE}")
    print(f"  Columns: {', '.join(fieldnames)}")

    return len(rows)


if __name__ == "__main__":
    count = generate()
    print(f"\nDataset generation complete. Total rows: {count:,}")
