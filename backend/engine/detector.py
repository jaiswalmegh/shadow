import pandas as pd
from pathlib import Path

from backend.engine.normalizer import normalize_all_data
from backend.engine.anomaly import detect_signal_anomalies


# =========================
# DATA PATH
# =========================

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# =========================
# LOAD DATASETS
# =========================

def load_datasets():
    """
    Load all SHADOW campus datasets.
    """

    attendance = pd.read_csv(
        DATA_DIR / "attendance.csv"
    )

    complaints = pd.read_csv(
        DATA_DIR / "complaints.csv"
    )

    facility_usage = pd.read_csv(
        DATA_DIR / "facility_usage.csv"
    )

    helpdesk = pd.read_csv(
        DATA_DIR / "helpdesk.csv"
    )

    feedback = pd.read_csv(
        DATA_DIR / "feedback.csv"
    )

    return (
        attendance,
        complaints,
        facility_usage,
        helpdesk,
        feedback
    )


# =========================
# PREPARE DATA
# =========================

def prepare_data():
    """
    Load and normalize all datasets.
    """

    (
        attendance,
        complaints,
        facility_usage,
        helpdesk,
        feedback
    ) = load_datasets()

    combined_data = normalize_all_data(
        attendance,
        complaints,
        facility_usage,
        helpdesk,
        feedback
    )

    return combined_data


# =========================
# RUN ANOMALY DETECTION
# =========================

def run_anomaly_detection():
    """
    Run SHADOW anomaly detection
    across all normalized signals.
    """

    combined_data = prepare_data()

    anomalies = detect_signal_anomalies(
        combined_data
    )

    # Keep only actual anomalies
    detected = anomalies[
        anomalies["severity"] != "NORMAL"
    ].copy()

    # Sort strongest anomalies first
    detected = detected.sort_values(
        by="anomaly_score",
        ascending=False
    ).reset_index(drop=True)

    return detected


# =========================
# QUICK TERMINAL TEST
# =========================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("              SHADOW ANOMALY ENGINE")
    print("=" * 60)

    print("\nLoading campus datasets...")

    data = prepare_data()

    print(
        f"✓ Loaded {len(data)} normalized signals"
    )

    print("\nRunning anomaly detection...")

    anomalies = run_anomaly_detection()

    print(
        f"✓ Detected {len(anomalies)} abnormal signals"
    )

    print("\n" + "-" * 60)
    print("DETECTED ANOMALIES")
    print("-" * 60)

    if anomalies.empty:

        print("No anomalies detected.")

    else:

        display_columns = [
            "location",
            "period",
            "signal_type",
            "baseline",
            "current_value",
            "change_percent",
            "anomaly_score",
            "severity"
        ]

        print(
            anomalies[
                display_columns
            ].to_string(index=False)
        )

    print("\n" + "=" * 60)