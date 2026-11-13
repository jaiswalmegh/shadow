import pandas as pd
import numpy as np


# ==========================================
# CHANGE PERCENTAGE
# ==========================================

def calculate_change(baseline, current):
    """
    Calculate percentage change from baseline.
    """

    if baseline == 0:
        return 0.0

    change = ((current - baseline) / abs(baseline)) * 100

    return round(change, 2)


# ==========================================
# ANOMALY SCORE
# ==========================================

def calculate_anomaly_score(change_percent):
    """
    Convert deviation into an anomaly score between 0 and 1.
    """

    magnitude = abs(change_percent)

    if magnitude >= 100:
        return 1.0

    return round(magnitude / 100, 2)


# ==========================================
# CLASSIFICATION
# ==========================================

def classify_anomaly(change_percent):
    """
    Classify a signal based on deviation.
    """

    magnitude = abs(change_percent)

    if magnitude >= 100:
        return "SEVERE"

    elif magnitude >= 50:
        return "ANOMALY"

    elif magnitude >= 20:
        return "WATCH"

    return "NORMAL"


# ==========================================
# SINGLE SIGNAL DETECTION
# ==========================================

def detect_anomaly(historical_values, current_value):
    """
    Compare the current value with historical values.
    """

    if not historical_values:
        return {
            "baseline": 0,
            "current_value": current_value,
            "change_percent": 0,
            "anomaly_score": 0,
            "severity": "NORMAL"
        }

    baseline = float(
        np.mean(historical_values)
    )

    change_percent = calculate_change(
        baseline,
        current_value
    )

    anomaly_score = calculate_anomaly_score(
        change_percent
    )

    severity = classify_anomaly(
        change_percent
    )

    return {
        "baseline": round(baseline, 2),
        "current_value": round(float(current_value), 2),
        "change_percent": change_percent,
        "anomaly_score": anomaly_score,
        "severity": severity
    }


# ==========================================
# ALL SIGNAL ANOMALIES
# ==========================================

def detect_signal_anomalies(df):
    """
    Detect anomalies across all locations,
    periods and signal types.

    The latest date is treated as the current
    observation and previous dates form the baseline.
    """

    df = df.copy()

    df["date"] = pd.to_datetime(
        df["date"]
    )

    latest_date = df["date"].max()

    current_data = df[
        df["date"] == latest_date
    ]

    historical_data = df[
        df["date"] < latest_date
    ]

    results = []

    group_columns = [
        "location",
        "period",
        "signal_type"
    ]

    for keys, current_group in current_data.groupby(
        group_columns
    ):

        location, period, signal_type = keys

        historical_group = historical_data[
            (historical_data["location"] == location)
            &
            (historical_data["period"] == period)
            &
            (historical_data["signal_type"] == signal_type)
        ]

        historical_values = (
            historical_group[
                "signal_value"
            ]
            .dropna()
            .tolist()
        )

        current_value = (
            current_group[
                "signal_value"
            ]
            .mean()
        )

        result = detect_anomaly(
            historical_values,
            current_value
        )

        result.update({
            "date": latest_date.strftime("%Y-%m-%d"),
            "location": location,
            "period": period,
            "signal_type": signal_type
        })

        results.append(result)

    return pd.DataFrame(results)