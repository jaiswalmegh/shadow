import sys
from pathlib import Path

# =========================================================
# SHADOW PROJECT ROOT
# Allows app.py to run directly from VS Code
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =========================================================
# IMPORTS
# =========================================================

from flask import (
    Flask,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

from backend.engine.detector import (
    run_anomaly_detection,
    prepare_data
)

from backend.engine.correlation import (
    correlate_anomalies
)

from backend.engine.confidence import (
    apply_confidence
)

from backend.ai.analyzer import (
    analyze_all_issues
)

from backend.routes.investigation import (
    investigation_bp
)


# =========================================================
# PATHS
# =========================================================

FRONTEND_DIST = (
    PROJECT_ROOT /
    "frontend" /
    "dist"
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIST),
    static_url_path=""
)

CORS(app)


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(
    investigation_bp
)


# =========================================================
# HOME / REACT ENTRY
# =========================================================

@app.route("/")
def home():

    index_file = (
        FRONTEND_DIST /
        "index.html"
    )

    if index_file.exists():

        return send_from_directory(
            str(FRONTEND_DIST),
            "index.html"
        )

    return jsonify({
        "system": "SHADOW",
        "status": "online",
        "message": "SHADOW Intelligence Engine is running",
        "warning": "Frontend build not found. Run npm run build inside frontend."
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health")
def health():

    return jsonify({
        "system": "SHADOW",
        "status": "online",
        "backend": "Flask",
        "frontend": "React",
        "architecture": "Single Server"
    })


# =========================================================
# BUILD TREND DATA
# =========================================================

def build_trend_data(analyzed_issues):

    if not analyzed_issues:
        return {}


    data = prepare_data()

    trends = {}


    for issue in analyzed_issues:

        location = issue.get(
            "location"
        )

        evidence = issue.get(
            "evidence",
            []
        )


        signal_types = [
            item.get(
                "signal_type"
            )
            for item in evidence
            if item.get(
                "signal_type"
            )
        ]


        if (
            not location
            or not signal_types
        ):
            continue


        location_data = data[
            data["location"] == location
        ].copy()


        if location_data.empty:
            continue


        location_data = location_data[
            location_data[
                "signal_type"
            ].isin(signal_types)
        ].copy()


        if location_data.empty:
            continue


        location_data["date"] = (
            location_data["date"]
            .dt.strftime(
                "%Y-%m-%d"
            )
        )


        grouped = (
            location_data
            .groupby(
                [
                    "date",
                    "signal_type"
                ],
                as_index=False
            )["signal_value"]
            .mean()
        )


        records = []


        for _, row in grouped.iterrows():

            records.append({
                "date": row["date"],
                "signal_type": row[
                    "signal_type"
                ],
                "value": round(
                    float(
                        row["signal_value"]
                    ),
                    2
                )
            })


        trends[location] = records


    return trends


# =========================================================
# DASHBOARD API
# =========================================================

@app.route("/api/dashboard")
def dashboard():

    try:

        # -------------------------------------------------
        # 1. DETECT ANOMALIES
        # -------------------------------------------------

        anomalies = (
            run_anomaly_detection()
        )


        # -------------------------------------------------
        # 2. CORRELATE SIGNALS
        # -------------------------------------------------

        issues = (
            correlate_anomalies(
                anomalies
            )
        )


        # -------------------------------------------------
        # 3. CALCULATE CONFIDENCE
        # -------------------------------------------------

        issues = (
            apply_confidence(
                issues
            )
        )


        # -------------------------------------------------
        # 4. AI ANALYSIS
        # -------------------------------------------------

        analyzed_issues = (
            analyze_all_issues(
                issues
            )
        )


        # -------------------------------------------------
        # 5. BUILD 30-DAY TRENDS
        # -------------------------------------------------

        trends = (
            build_trend_data(
                analyzed_issues
            )
        )


        # -------------------------------------------------
        # 6. RESPONSE
        # -------------------------------------------------

        return jsonify({

            "status": "success",

            "system": "SHADOW",

            "issue_count": len(
                analyzed_issues
            ),

            "issues": analyzed_issues,

            "trends": trends

        })


    except Exception as error:

        print(
            "\nSHADOW API ERROR:"
        )

        print(error)


        return jsonify({

            "status": "error",

            "message":
                "SHADOW Intelligence Engine encountered an error.",

            "details":
                str(error)

        }), 500


# =========================================================
# REACT STATIC FILE FALLBACK
# =========================================================
#
# Any frontend route that is not an API route
# should return React's index.html.
#
# Example:
#
# /investigation
# /dashboard
# /anything
#
# =========================================================

@app.route(
    "/<path:path>"
)
def serve_frontend(path):

    # -----------------------------------------------------
    # NEVER intercept API routes
    # -----------------------------------------------------

    if path.startswith("api/"):

        return jsonify({
            "error": "API route not found"
        }), 404


    requested_file = (
        FRONTEND_DIST /
        path
    )


    # -----------------------------------------------------
    # Serve actual frontend asset
    # -----------------------------------------------------

    if requested_file.is_file():

        return send_from_directory(
            str(FRONTEND_DIST),
            path
        )


    # -----------------------------------------------------
    # Otherwise React handles the route
    # -----------------------------------------------------

    index_file = (
        FRONTEND_DIST /
        "index.html"
    )


    if index_file.exists():

        return send_from_directory(
            str(FRONTEND_DIST),
            "index.html"
        )


    return jsonify({

        "system": "SHADOW",

        "status": "online",

        "message":
            "Frontend build not found.",

        "solution":
            "Run npm run build inside frontend."

    }), 404


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    print()
    print("=" * 64)
    print(
        "                 SHADOW SERVER"
    )
    print("=" * 64)

    print()
    print(
        "✓ SHADOW Intelligence Engine"
    )

    print(
        "✓ Flask Backend"
    )

    print(
        "✓ React Frontend"
    )

    print(
        "✓ Single Server Architecture"
    )

    print()

    if FRONTEND_DIST.exists():

        print(
            "✓ React production build found"
        )

        print(
            f"✓ Frontend: {FRONTEND_DIST}"
        )

    else:

        print(
            "⚠ React production build NOT found"
        )

        print(
            "⚠ Run: cd frontend && npm run build"
        )

    print()

    print(
        "Dashboard : http://127.0.0.1:5000"
    )

    print(
        "API       : http://127.0.0.1:5000/api/dashboard"
    )

    print(
        "Health    : http://127.0.0.1:5000/api/health"
    )

    print()

    print("=" * 64)
    print()


    app.run(
    host="127.0.0.1",
    port=5000,
    debug=False
)