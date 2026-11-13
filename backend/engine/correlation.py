import pandas as pd


# ==========================================
# SIGNAL DEFINITIONS
# ==========================================

NETWORK_SIGNALS = {
    "complaint_wifi",
    "helpdesk_network",
    "feedback_network"
}

OPERATIONAL_SIGNALS = {
    "attendance",
    "occupancy"
}


# ==========================================
# DETERMINE SIGNAL SOURCE
# ==========================================

def get_source_type(signal_type):

    if signal_type.startswith("complaint_"):
        return "Complaints"

    if signal_type.startswith("helpdesk_"):
        return "Helpdesk"

    if signal_type.startswith("feedback_"):
        return "Feedback"

    if signal_type == "attendance":
        return "Attendance"

    if signal_type == "occupancy":
        return "Facility Usage"

    return "Other"


# ==========================================
# DETERMINE ISSUE
# ==========================================

def determine_issue(signal_types):

    signal_set = set(signal_types)

    network_count = len(
        signal_set.intersection(NETWORK_SIGNALS)
    )

    has_attendance = "attendance" in signal_set
    has_occupancy = "occupancy" in signal_set

    # Strong network evidence
    if network_count >= 2:

        return "Potential Network Infrastructure Problem"

    # Network + operational evidence
    if network_count >= 1 and (
        has_attendance or has_occupancy
    ):

        return "Potential Network Infrastructure Problem"

    # Operational disruption
    if has_attendance and has_occupancy:

        return "Potential Operational Disruption"

    return "Potential Campus Operational Issue"


# ==========================================
# BUILD EVIDENCE
# ==========================================

def build_evidence(row):

    return {
        "signal_type": row["signal_type"],
        "location": row["location"],
        "period": row["period"],
        "baseline": float(row["baseline"]),
        "current_value": float(row["current_value"]),
        "change_percent": float(row["change_percent"]),
        "anomaly_score": float(row["anomaly_score"]),
        "severity": row["severity"]
    }


# ==========================================
# CORRELATE ANOMALIES
# ==========================================

def correlate_anomalies(anomalies):

    if anomalies is None or anomalies.empty:

        return pd.DataFrame(
            columns=[
                "location",
                "issue",
                "supporting_signal_count",
                "independent_sources",
                "evidence"
            ]
        )

    df = anomalies.copy()

    # Only abnormal signals
    df = df[
        df["severity"].isin(
            ["WATCH", "ANOMALY", "SEVERE"]
        )
    ].copy()

    if df.empty:

        return pd.DataFrame(
            columns=[
                "location",
                "issue",
                "supporting_signal_count",
                "independent_sources",
                "evidence"
            ]
        )

    correlated_issues = []

    # ======================================
    # GROUP BY CAMPUS LOCATION
    # ======================================

    for location, group in df.groupby("location"):

        group = group.copy()

        # Strongest anomaly for each signal
        group = (
            group
            .sort_values(
                by="anomaly_score",
                ascending=False
            )
            .drop_duplicates(
                subset=["signal_type"]
            )
        )

        signal_types = group[
            "signal_type"
        ].tolist()

        # Need at least 2 different signals
        if len(signal_types) < 2:
            continue

        # ==================================
        # EVIDENCE
        # ==================================

        evidence = [
            build_evidence(row)
            for _, row in group.iterrows()
        ]

        # ==================================
        # INDEPENDENT DATA SOURCES
        # ==================================

        independent_sources = list({
            get_source_type(signal)
            for signal in signal_types
        })

        # ==================================
        # ISSUE HYPOTHESIS
        # ==================================

        issue = determine_issue(
            signal_types
        )

        # ==================================
        # SAVE ISSUE
        # ==================================

        correlated_issues.append({
            "location": location,
            "issue": issue,
            "supporting_signal_count": len(
                signal_types
            ),
            "independent_sources": len(
                independent_sources
            ),
            "evidence": evidence
        })

    # ==========================================
    # RETURN DATAFRAME
    # ==========================================

    return pd.DataFrame(
        correlated_issues,
        columns=[
            "location",
            "issue",
            "supporting_signal_count",
            "independent_sources",
            "evidence"
        ]
    )


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from backend.engine.detector import (
        run_anomaly_detection
    )

    print("\n" + "=" * 60)
    print("             SHADOW CORRELATION ENGINE")
    print("=" * 60)

    anomalies = run_anomaly_detection()

    print(
        f"\n✓ Abnormal signals: {len(anomalies)}"
    )

    issues = correlate_anomalies(
        anomalies
    )

    print(
        f"✓ Correlated issues: {len(issues)}"
    )

    if issues.empty:

        print(
            "\nNo correlated hidden issues detected."
        )

    else:

        print(
            "\n" + "-" * 60
        )

        for _, issue in issues.iterrows():

            print(
                f"\nLocation              : "
                f"{issue['location']}"
            )

            print(
                f"Issue                 : "
                f"{issue['issue']}"
            )

            print(
                f"Supporting Signals    : "
                f"{issue['supporting_signal_count']}"
            )

            print(
                f"Independent Sources   : "
                f"{issue['independent_sources']}"
            )

            print("\nEvidence:")

            for item in issue["evidence"]:

                print(
                    f"  • "
                    f"{item['signal_type']} | "
                    f"{item['change_percent']}% | "
                    f"{item['severity']}"
                )

    print(
        "\n" + "=" * 60
    )