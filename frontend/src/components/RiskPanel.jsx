
export default function RiskPanel({ crashProbability }) {
  const threshold = 0.8;

  const hasLiveValue =
    crashProbability !== null &&
    crashProbability !== undefined &&
    crashProbability !== "" &&
    Number.isFinite(Number(crashProbability));

  const probability = hasLiveValue
    ? Math.max(0, Math.min(1, Number(crashProbability)))
    : null;

  const halted =
    probability !== null && probability >= threshold;

  const riskLevel =
    probability === null
      ? "WAITING"
      : halted
        ? "HIGH RISK"
        : "NORMAL";

  return (
    <section className="surface-card risk-card">

      <div className="card-heading">
        <div>
          <h3>AI Crash Risk Monitor</h3>
          <p>Model-estimated market crash probability</p>
        </div>

        <span className={`risk-status-tag ${probability === null ? "waiting" : halted ? "high" : "normal"}`}>
          {riskLevel}
        </span>
      </div>

      <div className="risk-display">

        <div>
          <span className="risk-label">
            CRASH PROBABILITY
          </span>

          <div className={`risk-main-value ${halted ? "high" : ""}`}>
            {probability === null
              ? "—"
              : `${(probability * 100).toFixed(1)}%`}
          </div>
        </div>

        <div className={`risk-orb ${probability == null ? "waiting" : halted ? "high" : "normal"}`}>
          !
        </div>

      </div>

      <div className="risk-track">

        {probability !== null && (
          <div
            className={`risk-fill ${halted ? "risk-high" : "risk-normal"}`}
            style={{ width: `${probability * 100}%` }}
          />
        )}

        <div
          className="risk-threshold-marker"
          style={{ left: `${threshold * 100}%` }}
        />

      </div>

      <div className="risk-scale">
        <span>0%</span>
        <span>80% Threshold</span>
        <span>100%</span>
      </div>

      <div className={`risk-message ${halted ? "high" : "normal"}`}>
        {probability === null
          ? "Waiting for model risk output..."
          : halted
            ? "HIGH RISK — Model threshold reached"
            : "ACTIVE — Below model risk threshold"}
      </div>

      <p className="risk-disclaimer">
        Educational model output. This is not a real trading halt
        or financial advice.
      </p>

    </section>
  );
}
