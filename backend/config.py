# SHADOW Configuration


# =========================
# CAMPUS LOCATIONS
# =========================

CAMPUS_LOCATIONS = [
    "AI Block",
    "A Block",
    "B Block",
    "C Block",
    "D Block",
    "Cafeteria",
    "Main Stage Area",
    "C Block Auditorium 1",
    "C Block Auditorium 2",
    "Cricket Nets",
    "Basketball Court"
]


# =========================
# DATASET SETTINGS
# =========================

DATA_DAYS = 30


# =========================
# ANOMALY THRESHOLDS
# =========================

ANOMALY_THRESHOLDS = {
    "watch": 20,
    "anomaly": 50,
    "severe": 100
}


# =========================
# SHADOW ENGINE SETTINGS
# =========================

SHADOW_CONFIG = {
    "minimum_signals_for_issue": 2,
    "high_confidence": 80,
    "medium_confidence": 60
}