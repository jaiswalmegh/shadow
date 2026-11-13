import React from "react";

function SignalCard({ signal }) {
  const change = Number(
    signal.change_percent || 0
  );

  const signalName =
    signal.signal_type
      .replaceAll("_", " ")
      .toUpperCase();

  const isPositive = change >= 0;

  return (
    <article className="signal-card">
      <div className="signal-card-top">
        <span className="signal-card-label">
          SIGNAL
        </span>

        <span
          className={
            signal.severity === "SEVERE"
              ? "signal-severity severe"
              : "signal-severity watch"
          }
        >
          {signal.severity}
        </span>
      </div>

      <h3>{signalName}</h3>

      <div
        className={
          isPositive
            ? "signal-change positive"
            : "signal-change negative"
        }
      >
        {isPositive ? "+" : ""}
        {change}%
      </div>

      <div className="signal-meta">
        <span>
          BASELINE
          <strong>
            {signal.baseline}
          </strong>
        </span>

        <span>
          CURRENT
          <strong>
            {signal.current_value}
          </strong>
        </span>

        <span>
          PERIOD
          <strong>
            {signal.period}
          </strong>
        </span>
      </div>
    </article>
  );
}

export default SignalCard;