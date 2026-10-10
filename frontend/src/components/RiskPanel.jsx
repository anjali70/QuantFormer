
export default function RiskPanel() {
  // Demo value only; this is not a live model prediction.
  const crashProbability = 0.35;
  const threshold = 0.8;
  const halted = crashProbability >= threshold;

  return (
    <section className="panel">
      <h2>Crash Risk Monitor</h2>

      <p className="risk-probability">
        {(crashProbability * 100).toFixed(1)}%
      </p>
      <p className="muted">Demo crash probability</p>

      <div className="risk-track">
        <div
          className={`risk-fill ${halted ? "risk-high" : "risk-normal"}`}
          style={{ width: `${crashProbability * 100}%` }}
        />
      </div>

      <p>
        Risk threshold: {(threshold * 100).toFixed(0)}%
      </p>

      <p className={halted ? "status-halted" : "status-active"}>
        {halted ? "HALTED — High risk" : "ACTIVE — Below threshold"}
      </p>
    </section>
  );
}
