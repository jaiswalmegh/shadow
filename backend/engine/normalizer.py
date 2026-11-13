import pandas as pd


def normalize_attendance(df):
    normalized = df.copy()

    normalized["signal_type"] = "attendance"
    normalized["signal_value"] = normalized["attendance_percentage"]

    return normalized[
        [
            "date",
            "location",
            "period",
            "signal_type",
            "signal_value"
        ]
    ]


def normalize_complaints(df):
    normalized = df.copy()

    normalized["signal_type"] = (
        "complaint_"
        + normalized["category"]
        .str.lower()
        .str.replace(" ", "_")
    )

    normalized["signal_value"] = normalized["complaint_count"]

    normalized["period"] = "All Day"

    return normalized[
        [
            "date",
            "location",
            "period",
            "signal_type",
            "signal_value"
        ]
    ]


def normalize_facility_usage(df):
    normalized = df.copy()

    normalized["signal_type"] = "occupancy"
    normalized["signal_value"] = normalized["occupancy_level"]

    return normalized[
        [
            "date",
            "location",
            "period",
            "signal_type",
            "signal_value"
        ]
    ]


def normalize_helpdesk(df):
    normalized = df.copy()

    normalized["signal_type"] = (
        "helpdesk_"
        + normalized["category"]
        .str.lower()
        .str.replace(" ", "_")
    )

    normalized["signal_value"] = normalized["ticket_count"]

    normalized["period"] = "All Day"

    return normalized[
        [
            "date",
            "location",
            "period",
            "signal_type",
            "signal_value"
        ]
    ]


def normalize_feedback(df):
    normalized = df.copy()

    normalized["signal_type"] = (
        "feedback_"
        + normalized["topic"]
        .str.lower()
        .str.replace(" ", "_")
    )

    normalized["signal_value"] = normalized["rating"]

    normalized["period"] = "All Day"

    return normalized[
        [
            "date",
            "location",
            "period",
            "signal_type",
            "signal_value"
        ]
    ]


def normalize_all_data(
    attendance,
    complaints,
    facility_usage,
    helpdesk,
    feedback
):
    """
    Normalize all five SHADOW datasets
    into one unified dataframe.
    """

    attendance_data = normalize_attendance(
        attendance
    )

    complaints_data = normalize_complaints(
        complaints
    )

    facility_data = normalize_facility_usage(
        facility_usage
    )

    helpdesk_data = normalize_helpdesk(
        helpdesk
    )

    feedback_data = normalize_feedback(
        feedback
    )

    combined = pd.concat(
        [
            attendance_data,
            complaints_data,
            facility_data,
            helpdesk_data,
            feedback_data
        ],
        ignore_index=True
    )

    combined["date"] = pd.to_datetime(
        combined["date"]
    )

    combined["signal_value"] = pd.to_numeric(
        combined["signal_value"],
        errors="coerce"
    )

    return combined.sort_values(
        by=["date", "location", "period"]
    ).reset_index(drop=True)