import React, {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import SignalCard from "./components/SignalCard";

const API = import.meta.env.DEV
  ? "http://127.0.0.1:5000"
  : "";

function formatSignalName(signalType = "") {
  return signalType
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function getSignalsForIssue(issue) {
  return Array.isArray(issue?.evidence)
    ? issue.evidence
    : [];
}

function parseAIExplanation(explanation = "") {
  const marker = "Evidence supporting this finding:";
  const markerIndex = explanation.indexOf(marker);

  if (markerIndex === -1) {
    return {
      summary: explanation.trim(),
      evidence: [],
    };
  }

  const summary = explanation
    .slice(0, markerIndex)
    .trim();

  const evidenceText = explanation
    .slice(markerIndex + marker.length)
    .trim();

  const evidence = evidenceText
    .split("•")
    .map((item) => item.trim())
    .filter(Boolean);

  return {
    summary,
    evidence,
  };
}

function getTrendSeries(
  trends,
  location,
  signalType
) {
  const records = trends?.[location] || [];

  return records
    .filter(
      (item) =>
        item.signal_type === signalType
    )
    .sort((a, b) =>
      String(a.date).localeCompare(
        String(b.date)
      )
    );
}

function buildTrendPoints(
  series,
  width = 900,
  height = 300
) {
  if (!series.length) return [];

  const values = series.map(
    (item) => Number(item.value) || 0
  );

  let min = Math.min(...values);
  let max = Math.max(...values);

  if (min === max) {
    min -= 1;
    max += 1;
  }

  const range = max - min;

  const left = 48;
  const right = 24;
  const top = 28;
  const bottom = 46;

  const chartWidth =
    width - left - right;

  const chartHeight =
    height - top - bottom;

  return series.map((item, index) => {
    const x =
      series.length === 1
        ? left + chartWidth / 2
        : left +
          (index /
            (series.length - 1)) *
            chartWidth;

    const value =
      Number(item.value) || 0;

    const normalized =
      (value - min) / range;

    const y =
      top +
      (1 - normalized) *
        chartHeight;

    return {
      x,
      y,
      value,
      date: item.date,
    };
  });
}

function pointsToString(points) {
  return points
    .map(
      (point) =>
        `${point.x},${point.y}`
    )
    .join(" ");
}

/* =========================================================
   SIGNAL COLORS
   ========================================================= */

function getSignalColor(
  signalType = "",
  index = 0
) {
  const type =
    signalType.toLowerCase();

  if (
    type.includes("helpdesk_network")
  ) {
    return "#ff4652";
  }

  if (
    type.includes("feedback_network")
  ) {
    return "#6ea8ff";
  }

  if (
    type.includes("occupancy")
  ) {
    return "#e0b557";
  }

  if (
    type.includes("attendance")
  ) {
    return "#8b7cff";
  }

  if (
    type.includes("complaint_wifi")
  ) {
    return "#e0b557";
  }

  /*
     Fallback ensures every visible graph
     still receives a unique color.
  */

  const fallbackColors = [
    "#ff4652",
    "#e0b557",
    "#6ea8ff",
    "#8b7cff",
    "#63c990",
  ];

  return (
    fallbackColors[
      index %
        fallbackColors.length
    ]
  );
}

/* =========================================================
   TREND GRAPH
   ========================================================= */

function TrendGraph({
  signal,
  trends,
  location,
  index,
}) {
  const graphRef =
    useRef(null);

  const clipRef =
    useRef(null);

  const animationRef =
    useRef(null);

  const [visible, setVisible] =
    useState(false);

  const series = useMemo(
    () =>
      getTrendSeries(
        trends,
        location,
        signal.signal_type
      ),
    [
      trends,
      location,
      signal.signal_type,
    ]
  );

  const points = useMemo(
    () =>
      buildTrendPoints(series),
    [series]
  );

  useEffect(() => {
    const element =
      graphRef.current;

    if (!element) return;

    if (
      window.matchMedia?.(
        "(prefers-reduced-motion: reduce)"
      ).matches
    ) {
      setVisible(true);
      return;
    }

    if (
      !(
        "IntersectionObserver" in
        window
      )
    ) {
      setVisible(true);
      return;
    }

    const observer =
      new IntersectionObserver(
        ([entry]) => {
          if (
            entry.isIntersecting
          ) {
            setVisible(true);
            observer.disconnect();
          }
        },
        {
          threshold: 0.22,
        }
      );

    observer.observe(element);

    return () =>
      observer.disconnect();
  }, []);

  useEffect(() => {
    if (
      !visible ||
      !clipRef.current
    ) {
      return;
    }

    const clip =
      clipRef.current;

    if (animationRef.current) {
      cancelAnimationFrame(
        animationRef.current
      );
    }

    if (
      window.matchMedia?.(
        "(prefers-reduced-motion: reduce)"
      ).matches
    ) {
      clip.setAttribute(
        "width",
        "900"
      );
      return;
    }

    clip.setAttribute(
      "width",
      "0"
    );

    const duration =
      1900;

    let start = null;

    const animate = (
      timestamp
    ) => {
      if (!start) {
        start = timestamp;
      }

      const elapsed =
        timestamp - start;

      const raw =
        Math.min(
          elapsed / duration,
          1
        );

      const eased =
        1 -
        Math.pow(
          1 - raw,
          3
        );

      clip.setAttribute(
        "width",
        String(
          900 * eased
        )
      );

      if (raw < 1) {
        animationRef.current =
          requestAnimationFrame(
            animate
          );
      }
    };

    animationRef.current =
      requestAnimationFrame(
        animate
      );

    return () => {
      if (
        animationRef.current
      ) {
        cancelAnimationFrame(
          animationRef.current
        );
      }
    };
  }, [
    visible,
    points.length,
  ]);

  if (!points.length) {
    return (
      <div
        ref={graphRef}
        className={`trend-card trend-card-${index}`}
      >
        <div className="trend-topline">
          <span>
            SIGNAL{" "}
            {String(
              index + 1
            ).padStart(
              2,
              "0"
            )}
          </span>

          <span>
            NO DATA
          </span>
        </div>

        <h3>
          {formatSignalName(
            signal.signal_type
          )}
        </h3>

        <div className="trend-empty">
          No historical trend
          data available.
        </div>
      </div>
    );
  }

  const linePoints =
    pointsToString(points);

  const change =
    Number(
      signal.change_percent ||
        0
    );

  const signalColor =
    getSignalColor(
      signal.signal_type,
      index
    );

  const clipId =
    `shadow-trend-${index}-${String(
      signal.signal_type
    ).replaceAll(
      "_",
      "-"
    )}`;

  const lastPoint =
    points[
      points.length - 1
    ];

  return (
    <div
      ref={graphRef}
      className={`trend-card trend-card-${index} ${
        visible
          ? "trend-visible"
          : ""
      }`}
    >
      <div className="trend-header">
        <div>
          <div className="trend-index">
            SIGNAL{" "}
            {String(
              index + 1
            ).padStart(
              2,
              "0"
            )}
          </div>

          <h3>
            {formatSignalName(
              signal.signal_type
            )}
          </h3>
        </div>

        <div className="trend-reading">
          <span>
            30 DAY WINDOW
          </span>

          <strong
            className={
              change >= 0
                ? "danger-text"
                : "positive-text"
            }
          >
            {change >= 0
              ? "+"
              : ""}
            {change}%
          </strong>
        </div>
      </div>

      <div className="trend-chart">
        <svg
          viewBox="0 0 900 300"
          preserveAspectRatio="none"
          role="img"
          aria-label={`${formatSignalName(
            signal.signal_type
          )} trend`}
        >
          <defs>
            <clipPath
              id={clipId}
            >
              <rect
                ref={clipRef}
                x="0"
                y="0"
                width="0"
                height="300"
              />
            </clipPath>

            <filter
              id={`glow-${index}`}
              x="-50%"
              y="-50%"
              width="200%"
              height="200%"
            >
              <feGaussianBlur
                stdDeviation="5"
                result="blur"
              />

              <feMerge>
                <feMergeNode
                  in="blur"
                />

                <feMergeNode
                  in="SourceGraphic"
                />
              </feMerge>
            </filter>
          </defs>

          {[35, 100, 165, 230].map(
            (y) => (
              <line
                key={y}
                x1="48"
                y1={y}
                x2="876"
                y2={y}
                stroke="#1d2025"
                strokeWidth="1"
              />
            )
          )}

          <line
            x1="48"
            y1="246"
            x2="876"
            y2="246"
            stroke="#353940"
            strokeWidth="1"
          />

          <g
            clipPath={`url(#${clipId})`}
          >
            <polyline
              points={linePoints}
              fill="none"
              stroke={signalColor}
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
            />

            <polyline
              points={linePoints}
              fill="none"
              stroke={signalColor}
              strokeWidth="9"
              strokeLinecap="round"
              strokeLinejoin="round"
              opacity="0.08"
              filter={`url(#glow-${index})`}
            />

            {points.map(
              (
                point,
                pointIndex
              ) => (
                <circle
                  key={`${point.date}-${pointIndex}`}
                  cx={point.x}
                  cy={point.y}
                  r={
                    pointIndex ===
                    points.length - 1
                      ? 5
                      : 2
                  }
                  fill={
                    pointIndex ===
                    points.length - 1
                      ? signalColor
                      : "#08090b"
                  }
                  stroke={
                    signalColor
                  }
                  strokeWidth={
                    pointIndex ===
                    points.length - 1
                      ? 2
                      : 1
                  }
                />
              )
            )}

            <line
              x1={lastPoint.x}
              y1="28"
              x2={lastPoint.x}
              y2="246"
              stroke={
                signalColor
              }
              strokeWidth="1"
              strokeDasharray="4 6"
              opacity="0.35"
            />
          </g>

          <text
            x="48"
            y="276"
            fill="#686d76"
            fontFamily="DM Mono, monospace"
            fontSize="9"
          >
            {series[0]?.date}
          </text>

          <text
            x="876"
            y="276"
            fill="#686d76"
            fontFamily="DM Mono, monospace"
            fontSize="9"
            textAnchor="end"
          >
            {
              series[
                series.length - 1
              ]?.date
            }
          </text>
        </svg>
      </div>

      <div className="trend-footer">
        <div>
          <span>
            BASELINE
          </span>

          <strong>
            {signal.baseline}
          </strong>
        </div>

        <div>
          <span>
            CURRENT
          </span>

          <strong>
            {signal.current_value}
          </strong>
        </div>

        <div>
          <span>
            DELTA
          </span>

          <strong
            className={
              change >= 0
                ? "danger-text"
                : "positive-text"
            }
          >
            {change >= 0
              ? "+"
              : ""}
            {change}%
          </strong>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   STATUS BAR
   ========================================================= */

function StatusBar() {
  return (
    <div className="status-bar">
      <div className="status-left">
        <span className="status-dot" />

        <span>
          SYSTEM ONLINE
        </span>
      </div>

      <div className="status-right">
        <span>
          SHADOW ENGINE
        </span>

        <span className="status-separator">
          /
        </span>

        <span>
          LIVE ANALYSIS
        </span>
      </div>
    </div>
  );
}

/* =========================================================
   HEADER
   ========================================================= */

function Header() {
  return (
    <header className="dashboard-header">
      <div className="brand-wrap">
        <div className="brand-mark">
          S
        </div>

        <div>
          <div className="brand">
            SHADOW
          </div>

          <div className="brand-sub">
            CAMPUS INTELLIGENCE ENGINE
          </div>
        </div>
      </div>

      <StatusBar />
    </header>
  );
}

/* =========================================================
   SECTION HEADING
   ========================================================= */

function SectionHeading({
  eyebrow,
  title,
  description,
  right,
}) {
  return (
    <div className="section-heading">
      <div>
        <div className="section-eyebrow">
          {eyebrow}
        </div>

        <h2>
          {title}
        </h2>

        {description && (
          <p>
            {description}
          </p>
        )}
      </div>

      {right && (
        <div className="section-right">
          {right}
        </div>
      )}
    </div>
  );
}

/* =========================================================
   CONFIDENCE
   ========================================================= */

function ConfidenceBlock({
  issue,
}) {
  return (
    <div className="confidence-block">
      <div className="confidence-main">
        <div className="confidence-label">
          DETECTION CONFIDENCE
        </div>

        <div className="confidence-number">
          {issue.confidence}

          <span>
            %
          </span>
        </div>

        <div className="confidence-status">
          <span className="confidence-dot" />

          {
            issue.confidence_level
          }{" "}
          CONFIDENCE
        </div>
      </div>

      <div className="confidence-meter">
        <div
          className="confidence-fill"
          style={{
            width: `${issue.confidence}%`,
          }}
        />
      </div>

      <div className="confidence-data">
        <div>
          <span>
            SUPPORTING SIGNALS
          </span>

          <strong>
            {
              issue.supporting_signal_count
            }
          </strong>
        </div>

        <div>
          <span>
            INDEPENDENT SOURCES
          </span>

          <strong>
            {
              issue.independent_sources
            }
          </strong>
        </div>

        <div>
          <span>
            ASSESSMENT
          </span>

          <strong>
            EVIDENCE-BACKED
          </strong>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   SIGNAL FIELD
   ========================================================= */

function SignalField({
  evidence,
  location,
}) {
  return (
    <div className="signal-field">
      <div className="field-center">
        <div className="field-pulse" />

        <div className="field-core">
          <span>
            {location.toUpperCase()}
          </span>

          <small>
            ACTIVE PATTERN
          </small>
        </div>
      </div>

      {evidence.map(
        (
          item,
          index
        ) => (
          <div
            key={`${item.signal_type}-${index}`}
            className={`field-node field-node-${index}`}
          >
            <div className="field-line" />

            <div className="field-node-dot" />

            <div className="field-node-label">
              <span>
                {formatSignalName(
                  item.signal_type
                )}
              </span>

              <strong>
                {item.change_percent >=
                0
                  ? "+"
                  : ""}
                {
                  item.change_percent
                }%
              </strong>
            </div>
          </div>
        )
      )}

      <div className="field-location">
        LOCATION /{" "}
        {location}
      </div>
    </div>
  );
}

/* =========================================================
   MAIN APP
   ========================================================= */

function App() {
  const [issues, setIssues] =
    useState([]);

  const [trends, setTrends] =
    useState({});

  const [
    selectedIssue,
    setSelectedIssue,
  ] = useState(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  async function fetchDashboard() {
    try {
      setLoading(true);
      setError("");

      const response =
        await fetch(
          `${API}/api/dashboard`
        );

      if (!response.ok) {
        throw new Error(
          `API returned ${response.status}`
        );
      }

      const data =
        await response.json();

      setIssues(
        Array.isArray(
          data.issues
        )
          ? data.issues
          : []
      );

      setTrends(
        data.trends &&
          typeof data.trends ===
            "object"
          ? data.trends
          : {}
      );
    } catch (err) {
      console.error(
        "SHADOW API ERROR:",
        err
      );

      setError(
        "Unable to connect to SHADOW Intelligence Engine."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchDashboard();
  }, []);

  function openInvestigation(
    issue
  ) {
    setSelectedIssue(
      issue
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  function goBack() {
    setSelectedIssue(
      null
    );

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  }

  const totalSignals = 5;

  const totalLocations = 11;

  const totalDays = 30;

  /* =========================================================
     INVESTIGATION PAGE
     ========================================================= */

  if (selectedIssue) {
    const evidence =
      getSignalsForIssue(
        selectedIssue
      );

    const analysis =
      parseAIExplanation(
        selectedIssue.explanation ||
          selectedIssue.analysis ||
          ""
      );

    return (
      <div className="app">
        <Header />

        <main className="dashboard investigation-page">

          <div className="investigation-nav">
            <button
              className="back-button"
              onClick={goBack}
            >
              <span>
                ←
              </span>

              BACK TO INTELLIGENCE
            </button>

            <span>
              INVESTIGATION / 01
            </span>
          </div>

          <section className="investigation-hero">
            <div className="hero-grid">

              <div>
                <div className="hero-eyebrow">
                  HIDDEN ISSUE DETECTED
                </div>

                <div className="hero-location">
                  {
                    selectedIssue.location
                  }
                </div>

                <h1>
                  {
                    selectedIssue.issue
                  }
                </h1>

                <p>
                  SHADOW identified a
                  cross-signal pattern
                  across independent
                  campus systems.
                </p>
              </div>

              <div className="hero-index">
                <span>
                  CASE
                </span>

                <strong>
                  01
                </strong>

                <span>
                  EVIDENCE-BASED
                </span>
              </div>

            </div>
          </section>

          <section>
            <SectionHeading
              eyebrow="01 / SYSTEM ASSESSMENT"
              title="Detection Confidence"
              description="Confidence is calculated from signal count, severity, source diversity and cross-signal coherence."
            />

            <ConfidenceBlock
              issue={
                selectedIssue
              }
            />
          </section>

          <section>
            <SectionHeading
              eyebrow="02 / SIGNAL FIELD"
              title="Why SHADOW Flagged This"
              description="Independent weak signals converge around the same operational location."
            />

            <SignalField
              evidence={
                evidence
              }
              location={
                selectedIssue.location
              }
            />
          </section>

          <section>
            <SectionHeading
              eyebrow="03 / EVIDENCE CHAIN"
              title="Independent Signals"
              description="Each signal contributes an observable piece of the detection."
            />

            <div className="evidence-grid">
              {evidence.map(
                (
                  item,
                  index
                ) => (
                  <div
                    className="evidence-panel"
                    key={`${item.signal_type}-${index}`}
                  >
                    <div className="evidence-panel-top">

                      <span>
                        0
                        {
                          index + 1
                        }
                      </span>

                      <span
                        className={
                          item.severity ===
                          "SEVERE"
                            ? "severity severe"
                            : "severity watch"
                        }
                      >
                        {
                          item.severity
                        }
                      </span>

                    </div>

                    <div className="evidence-source">
                      {formatSignalName(
                        item.signal_type
                      )}
                    </div>

                    <div
                      className={
                        item.change_percent >=
                        0
                          ? "evidence-change danger-text"
                          : "evidence-change positive-text"
                      }
                    >
                      {item.change_percent >=
                      0
                        ? "+"
                        : ""}
                      {
                        item.change_percent
                      }%
                    </div>

                    <div className="evidence-values">

                      <div>
                        <span>
                          BASELINE
                        </span>

                        <strong>
                          {
                            item.baseline
                          }
                        </strong>
                      </div>

                      <div>
                        <span>
                          CURRENT
                        </span>

                        <strong>
                          {
                            item.current_value
                          }
                        </strong>
                      </div>

                    </div>
                  </div>
                )
              )}
            </div>
          </section>

          <section>
            <SectionHeading
              eyebrow="04 / CORRELATION"
              title="Signal Correlation"
              description="The system does not rely on a single abnormal reading. It looks for convergence."
              right={
                <span className="technical-tag">
                  {
                    evidence.length
                  }{" "}
                  SIGNALS
                  /
                  {" "}
                  {
                    selectedIssue.independent_sources
                  }{" "}
                  SOURCES
                </span>
              }
            />

            <div className="signal-grid">
              {evidence.map(
                (
                  signal,
                  index
                ) => (
                  <SignalCard
                    key={`${signal.signal_type}-${index}`}
                    signal={
                      signal
                    }
                  />
                )
              )}
            </div>
          </section>

          <section>
            <SectionHeading
              eyebrow="05 / TEMPORAL ANALYSIS"
              title="30-Day Signal Trends"
              description="The timeline reveals when the underlying pattern begins to separate from normal behaviour."
              right={
                <span className="scroll-hint">
                  SCROLL TO REVEAL ↓
                </span>
              }
            />

            <div className="trend-stack">
              {evidence.map(
                (
                  signal,
                  index
                ) => (
                  <TrendGraph
                    key={`${signal.signal_type}-trend`}
                    signal={
                      signal
                    }
                    trends={
                      trends
                    }
                    location={
                      selectedIssue.location
                    }
                    index={
                      index
                    }
                  />
                )
              )}
            </div>
          </section>

          <section>
            <SectionHeading
              eyebrow="06 / INTELLIGENCE LAYER"
              title="AI Analysis"
              description="The AI layer translates correlated evidence into an interpretable assessment."
            />

            <div className="ai-panel">

              <div className="ai-panel-header">

                <div className="ai-orb">
                  S
                </div>

                <div>
                  <span>
                    SHADOW AI
                  </span>

                  <h3>
                    Emerging Pattern
                    Detected
                  </h3>
                </div>

                <div className="ai-status">
                  ANALYSIS COMPLETE
                </div>

              </div>

              <div className="ai-summary">
                {
                  analysis.summary ||
                  "SHADOW identified a pattern across multiple campus signals."
                }
              </div>

              {analysis.evidence.length >
                0 && (
                <div className="ai-evidence-list">

                  <div className="ai-list-label">
                    SUPPORTING EVIDENCE
                  </div>

                  {analysis.evidence.map(
                    (
                      point,
                      index
                    ) => {

                      const severe =
                        point.includes(
                          "(SEVERE)"
                        );

                      const watch =
                        point.includes(
                          "(WATCH)"
                        );

                      const clean =
                        point
                          .replace(
                            "(SEVERE)",
                            ""
                          )
                          .replace(
                            "(WATCH)",
                            ""
                          )
                          .trim();

                      return (
                        <div
                          className="ai-evidence-row"
                          key={
                            index
                          }
                        >
                          <span>
                            {String(
                              index + 1
                            ).padStart(
                              2,
                              "0"
                            )}
                          </span>

                          <p>
                            {
                              clean
                            }
                          </p>

                          <b
                            className={
                              severe
                                ? "danger-text"
                                : watch
                                  ? "watch-text"
                                  : ""
                            }
                          >
                            {severe
                              ? "SEVERE"
                              : watch
                                ? "WATCH"
                                : "SIGNAL"}
                          </b>
                        </div>
                      );
                    }
                  )}

                </div>
              )}

            </div>
          </section>

          <section>
            <div className="action-panel">

              <div>
                <div className="section-eyebrow">
                  07 / RECOMMENDED ACTION
                </div>

                <h2>
                  Investigate the
                  detected pattern.
                </h2>
              </div>

              <p>
                {
                  selectedIssue.recommendation ||
                  "Conduct a targeted investigation using the available supporting evidence."
                }
              </p>

            </div>
          </section>

          <section>
            <div className="responsible-panel">

              <div className="responsible-icon">
                ✓
              </div>

              <div>
                <div className="section-eyebrow">
                  RESPONSIBLE AI
                </div>

                <p>
                  SHADOW produces an
                  evidence-backed
                  hypothesis, not a final
                  operational decision.
                  Campus teams remain
                  responsible for
                  verification and action.
                </p>
              </div>

            </div>
          </section>

          <footer className="site-footer">
            <span>
              SHADOW / CAMPUS
              INTELLIGENCE ENGINE
            </span>

            <span>
              INVESTIGATION COMPLETE
            </span>
          </footer>

        </main>
      </div>
    );
  }

  /* =========================================================
     DASHBOARD PAGE
     ========================================================= */

  return (
    <div className="app">

      <Header />

      <main className="dashboard">

        <section className="hero">

          <div className="hero-topline">
            <span>
              CAMPUS INTELLIGENCE ENGINE
            </span>

            <span>
              BUILD / 01
            </span>
          </div>

          <div className="hero-content">

            <div>

              <div className="hero-eyebrow">
                PROACTIVE CAMPUS
                INTELLIGENCE
              </div>

              <h1>
                DETECT WHAT
                <br />
                HASN'T BEEN{" "}
                <span>
                  REPORTED.
                </span>
              </h1>

              <p>
                SHADOW correlates weak
                signals across campus
                systems to identify
                emerging problems before
                they become formal
                complaints.
              </p>

              <div className="hero-actions">

                <a
                  href="#detections"
                  className="primary-action"
                >
                  VIEW DETECTIONS

                  <span>
                    ↓
                  </span>
                </a>

                <span className="hero-note">
                  30-DAY SIGNAL ANALYSIS
                  ACTIVE
                </span>

              </div>

            </div>

            <div className="hero-visual">

              <div className="visual-ring ring-one" />

              <div className="visual-ring ring-two" />

              <div className="visual-ring ring-three" />

              <div className="visual-core">

                <span>
                  SHADOW
                </span>

                <small>
                  INTELLIGENCE ACTIVE
                </small>

              </div>

              <div className="visual-signal signal-a" />

              <div className="visual-signal signal-b" />

              <div className="visual-signal signal-c" />

            </div>

          </div>
        </section>

        <section className="metrics-section">

          <div className="metric-strip">

            <div className="metric">

              <span>
                SIGNAL SOURCES
              </span>

              <strong>
                {String(
                  totalSignals
                ).padStart(
                  2,
                  "0"
                )}
              </strong>

              <small>
                ATTENDANCE / USAGE /
                FEEDBACK / HELP DESK /
                COMPLAINTS
              </small>

            </div>

            <div className="metric">

              <span>
                CAMPUS LOCATIONS
              </span>

              <strong>
                {String(
                  totalLocations
                ).padStart(
                  2,
                  "0"
                )}
              </strong>

              <small>
                MONITORED OPERATIONAL
                ZONES
              </small>

            </div>

            <div className="metric">

              <span>
                ANALYSIS WINDOW
              </span>

              <strong>
                {String(
                  totalDays
                ).padStart(
                  2,
                  "0"
                )}
              </strong>

              <small>
                DAYS OF SIGNAL HISTORY
              </small>

            </div>

            <div className="metric metric-alert">

              <span>
                HIDDEN ISSUES
              </span>

              <strong>
                {String(
                  issues.length
                ).padStart(
                  2,
                  "0"
                )}
              </strong>

              <small>
                CROSS-SIGNAL PATTERNS
              </small>

            </div>

          </div>

        </section>

        <section
          id="detections"
          className="detections-section"
        >

          <SectionHeading
            eyebrow="01 / DETECTION FEED"
            title="Hidden Issues"
            description="Patterns discovered through correlated weak signals rather than direct reporting."
            right={
              <span className="live-indicator">

                <i />

                LIVE

              </span>
            }
          />

          {loading && (
            <div className="loading-panel">

              <div className="loader-line" />

              <span>
                ANALYZING CAMPUS SIGNALS
              </span>

            </div>
          )}

          {error && (
            <div className="error-panel">
              {
                error
              }
            </div>
          )}

          {!loading &&
            !error &&
            issues.length ===
              0 && (
              <div className="empty-panel">

                <span>
                  NO ACTIVE SIGNAL
                </span>

                <h3>
                  No hidden issue
                  currently detected.
                </h3>

                <p>
                  SHADOW is continuing to
                  evaluate campus signals.
                </p>

              </div>
            )}

          {!loading &&
            !error &&
            issues.map(
              (
                issue,
                index
              ) => (
                <article
                  className="issue-row"
                  key={`${issue.location}-${index}`}
                >

                  <div className="issue-number">
                    {String(
                      index + 1
                    ).padStart(
                      2,
                      "0"
                    )}
                  </div>

                  <div className="issue-main">

                    <div className="issue-location">
                      {
                        issue.location
                      }
                    </div>

                    <h3>
                      {
                        issue.issue
                      }
                    </h3>

                    <p>
                      {
                        issue.supporting_signal_count
                      }{" "}
                      supporting signals
                      across{" "}
                      {
                        issue.independent_sources
                      }{" "}
                      independent sources.
                    </p>

                  </div>

                  <div className="issue-confidence">

                    <span>
                      CONFIDENCE
                    </span>

                    <strong>
                      {
                        issue.confidence
                      }%
                    </strong>

                    <small>
                      {
                        issue.confidence_level
                      }
                    </small>

                  </div>

                  <button
                    className="issue-open"
                    onClick={() =>
                      openInvestigation(
                        issue
                      )
                    }
                  >

                    <span>
                      INVESTIGATE
                    </span>

                    <b>
                      ↗
                    </b>

                  </button>

                </article>
              )
            )}

        </section>

        <section>

          <SectionHeading
            eyebrow="02 / SYSTEM LOGIC"
            title="How SHADOW Thinks"
            description="The intelligence pipeline turns isolated campus data into an evidence-backed hypothesis."
          />

          <div className="logic-grid">

            <div className="logic-step">

              <span>
                01
              </span>

              <strong>
                INGEST
              </strong>

              <p>
                Campus data from
                multiple operational
                sources.
              </p>

            </div>

            <div className="logic-connector">
              →
            </div>

            <div className="logic-step">

              <span>
                02
              </span>

              <strong>
                DETECT
              </strong>

              <p>
                Identify abnormal
                movement against
                historical baselines.
              </p>

            </div>

            <div className="logic-connector">
              →
            </div>

            <div className="logic-step">

              <span>
                03
              </span>

              <strong>
                CORRELATE
              </strong>

              <p>
                Find independent
                signals converging on
                one location.
              </p>

            </div>

            <div className="logic-connector">
              →
            </div>

            <div className="logic-step active">

              <span>
                04
              </span>

              <strong>
                EXPLAIN
              </strong>

              <p>
                Generate evidence,
                confidence and a
                recommended action.
              </p>

            </div>

          </div>

        </section>

        <section>

          <div className="closing-panel">

            <div className="closing-index">
              SHADOW / 03
            </div>

            <h2>
              MOST SYSTEMS
              <br />
              ANALYZE WHAT PEOPLE
              <span>
                {" "}
                REPORT.
              </span>
            </h2>

            <div className="closing-line" />

            <p>
              SHADOW analyzes what they
              don't.
            </p>

          </div>

        </section>

        <footer className="site-footer">

          <span>
            SHADOW / CAMPUS
            INTELLIGENCE ENGINE
          </span>

          <span>
            30-DAY ANALYSIS ACTIVE
          </span>

        </footer>

      </main>
    </div>
  );
}

export default App;