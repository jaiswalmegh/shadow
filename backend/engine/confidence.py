import pandas as pd


# ==========================================
# CALCULATE CONFIDENCE FOR ONE ISSUE
# ==========================================

def calculate_issue_confidence(issue):

    evidence = issue.get("evidence", [])

    if not evidence:
        return 0

    # --------------------------------------
    # SIGNAL COUNT
    # --------------------------------------

    signal_count = len(evidence)

    if signal_count >= 5:
        signal_score = 35
    elif signal_count == 4:
        signal_score = 32
    elif signal_count == 3:
        signal_score = 28
    elif signal_count == 2:
        signal_score = 18
    else:
        signal_score = 8

    # --------------------------------------
    # SEVERITY
    # --------------------------------------

    severity_weights = {
        "SEVERE": 30,
        "ANOMALY": 20,
        "WATCH": 10,
        "NORMAL": 0
    }

    severity_scores = []

    for item in evidence:

        severity = str(
            item.get("severity", "")
        ).upper()

        severity_scores.append(
            severity_weights.get(
                severity,
                0
            )
        )

    severity_scores.sort(
        reverse=True
    )

    # Strongest 3 signals
    severity_score = sum(
        severity_scores[:3]
    )

    # --------------------------------------
    # INDEPENDENT SOURCES
    # --------------------------------------

    sources = set()

    for item in evidence:

        signal_type = str(
            item.get("signal_type", "")
        )

        if signal_type.startswith(
            "complaint_"
        ):
            sources.add("complaints")

        elif signal_type.startswith(
            "helpdesk_"
        ):
            sources.add("helpdesk")

        elif signal_type.startswith(
            "feedback_"
        ):
            sources.add("feedback")

        elif signal_type == "attendance":
            sources.add("attendance")

        elif signal_type == "occupancy":
            sources.add("facility_usage")

    source_count = len(sources)

    if source_count >= 4:
        source_score = 20
    elif source_count == 3:
        source_score = 18
    elif source_count == 2:
        source_score = 15
    else:
        source_score = 5

    # --------------------------------------
    # CROSS-SIGNAL COHERENCE
    # --------------------------------------

    signal_types = {
        item.get("signal_type")
        for item in evidence
    }

    network_signals = {
        "complaint_wifi",
        "helpdesk_network",
        "feedback_network"
    }

    network_count = len(
        signal_types.intersection(
            network_signals
        )
    )

    if network_count >= 3:
        coherence_score = 20

    elif network_count == 2:
        coherence_score = 16

    elif network_count == 1:
        coherence_score = 8

    else:
        coherence_score = 5

    # --------------------------------------
    # FINAL CONFIDENCE
    # --------------------------------------

    confidence = (
        signal_score
        + severity_score
        + source_score
        + coherence_score
    )

    confidence = min(
        max(confidence, 0),
        100
    )

    return int(confidence)


# ==========================================
# CONFIDENCE LEVEL
# ==========================================

def get_confidence_level(confidence):

    if confidence >= 80:
        return "HIGH"

    if confidence >= 60:
        return "MEDIUM"

    return "LOW"


# ==========================================
# APPLY CONFIDENCE
# ==========================================

def apply_confidence(issues):

    if issues is None:

        return pd.DataFrame()

    if isinstance(issues, list):

        if not issues:
            return pd.DataFrame()

        issues = pd.DataFrame(
            issues
        )

    if issues.empty:
        return issues

    results = []

    for _, issue in issues.iterrows():

        issue_data = issue.to_dict()

        confidence = (
            calculate_issue_confidence(
                issue_data
            )
        )

        issue_data["confidence"] = confidence

        issue_data["confidence_level"] = (
            get_confidence_level(
                confidence
            )
        )

        results.append(
            issue_data
        )

    return pd.DataFrame(results)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from backend.engine.detector import (
        run_anomaly_detection
    )

    from backend.engine.correlation import (
        correlate_anomalies
    )

    print("\n" + "=" * 60)
    print("              SHADOW CONFIDENCE ENGINE")
    print("=" * 60)

    anomalies = run_anomaly_detection()

    issues = correlate_anomalies(
        anomalies
    )

    issues = apply_confidence(
        issues
    )

    if issues.empty:

        print(
            "\nNo issues available."
        )

    else:

        print(
            f"\n✓ Confidence calculated "
            f"for {len(issues)} issue(s)"
        )

        print(
            "\n" + "-" * 60
        )

        for _, issue in issues.iterrows():

            print(
                f"\nLocation       : "
                f"{issue['location']}"
            )

            print(
                f"Issue          : "
                f"{issue['issue']}"
            )

            print(
                f"Signals        : "
                f"{issue['supporting_signal_count']}"
            )

            print(
                f"Sources        : "
                f"{issue['independent_sources']}"
            )

            print(
                f"Confidence     : "
                f"{issue['confidence']}%"
            )

            print(
                f"Level          : "
                f"{issue['confidence_level']}"
            )

    print(
        "\n" + "=" * 60
    )