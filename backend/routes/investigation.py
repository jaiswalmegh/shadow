from flask import Blueprint, jsonify

from backend.engine.detector import run_anomaly_detection
from backend.engine.correlation import correlate_anomalies
from backend.engine.confidence import apply_confidence
from backend.ai.analyzer import analyze_all_issues


# ==========================================
# INVESTIGATION BLUEPRINT
# ==========================================

investigation_bp = Blueprint(
    "investigation",
    __name__,
    url_prefix="/api/investigation"
)


# ==========================================
# ALL INVESTIGATIONS
# ==========================================

@investigation_bp.route("/", methods=["GET"])
def get_investigations():

    anomalies = run_anomaly_detection()

    issues = correlate_anomalies(anomalies)

    issues = apply_confidence(issues)

    analyzed_issues = analyze_all_issues(issues)

    return jsonify({
        "status": "success",
        "investigations": analyzed_issues
    })


# ==========================================
# LOCATION INVESTIGATION
# ==========================================

@investigation_bp.route("/<path:location>", methods=["GET"])
def get_location_investigation(location):

    anomalies = run_anomaly_detection()

    issues = correlate_anomalies(anomalies)

    issues = apply_confidence(issues)

    analyzed_issues = analyze_all_issues(issues)

    location_issues = [
        issue
        for issue in analyzed_issues
        if issue["location"].lower() == location.lower()
    ]

    return jsonify({
        "status": "success",
        "location": location,
        "issue_count": len(location_issues),
        "investigations": location_issues
    })