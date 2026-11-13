# SHADOW AI Analyzer

# ==========================================
# GENERATE EXPLANATION
# ==========================================

def generate_explanation(issue):

    location = issue["location"]
    issue_name = issue["issue"]
    confidence = issue["confidence"]

    evidence = issue["evidence"]

    explanation = (
        f"SHADOW detected a potential issue at {location}. "
        f"The system identified {issue_name.lower()} "
        f"with a confidence score of {confidence}%."
    )

    if evidence:

        explanation += "\n\nEvidence supporting this finding:"

        for item in evidence:

            signal = item["signal_type"]
            change = item["change_percent"]
            severity = item["severity"]

            direction = "increased" if change > 0 else "decreased"

            explanation += (
                f"\n• {signal.replace('_', ' ').title()} "
                f"{direction} by {abs(change)}% "
                f"({severity})."
            )

    return explanation


# ==========================================
# GENERATE RECOMMENDATION
# ==========================================

def generate_recommendation(issue):

    issue_name = issue["issue"].lower()
    location = issue["location"]

    if "network" in issue_name:

        return (
            f"Investigate network infrastructure at {location}. "
            f"Check Wi-Fi access points, network connectivity, "
            f"and network capacity during high-occupancy periods."
        )

    if "attendance" in issue_name:

        return (
            f"Investigate the cause of the attendance decline at "
            f"{location} and compare it with operational conditions "
            f"during the affected period."
        )

    return (
        f"Conduct a targeted investigation at {location} "
        f"using the available supporting evidence."
    )


# ==========================================
# ANALYZE ISSUE
# ==========================================

def analyze_issue(issue):

    explanation = generate_explanation(issue)

    recommendation = generate_recommendation(issue)

    return {
        "location": issue["location"],
        "issue": issue["issue"],
        "confidence": issue["confidence"],
        "confidence_level": issue["confidence_level"],
        "supporting_signal_count": issue["supporting_signal_count"],
        "independent_sources": issue["independent_sources"],
        "explanation": explanation,
        "recommendation": recommendation,
        "evidence": issue["evidence"]
    }


# ==========================================
# ANALYZE ALL ISSUES
# ==========================================

def analyze_all_issues(issues):

    if issues.empty:
        return []

    analyzed_issues = []

    for _, issue in issues.iterrows():

        analyzed = analyze_issue(issue)

        analyzed_issues.append(analyzed)

    return analyzed_issues


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from backend.engine.detector import run_anomaly_detection
    from backend.engine.correlation import correlate_anomalies
    from backend.engine.confidence import apply_confidence

    print("\n" + "=" * 60)
    print("                SHADOW AI ANALYZER")
    print("=" * 60)

    # --------------------------------------
    # Run detection
    # --------------------------------------

    anomalies = run_anomaly_detection()

    # --------------------------------------
    # Correlate signals
    # --------------------------------------

    issues = correlate_anomalies(anomalies)

    # --------------------------------------
    # Calculate confidence
    # --------------------------------------

    issues = apply_confidence(issues)

    # --------------------------------------
    # AI analysis
    # --------------------------------------

    analyzed_issues = analyze_all_issues(issues)

    if not analyzed_issues:

        print("\nNo hidden issues available for analysis.")

    else:

        print(f"\n✓ AI analyzed {len(analyzed_issues)} issue(s)")

        for issue in analyzed_issues:

            print("\n" + "-" * 60)

            print(f"Location       : {issue['location']}")
            print(f"Issue          : {issue['issue']}")
            print(f"Confidence     : {issue['confidence']}%")
            print(f"Confidence     : {issue['confidence_level']}")

            print("\nAI Explanation:")
            print(issue["explanation"])

            print("\nRecommendation:")
            print(issue["recommendation"])

            print("\nEvidence Chain:")

            for evidence in issue["evidence"]:

                print(
                    f"  • {evidence['signal_type']} | "
                    f"{evidence['change_percent']}% | "
                    f"{evidence['severity']}"
                )

    print("\n" + "=" * 60)