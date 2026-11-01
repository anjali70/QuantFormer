
export default function NewsPanel({ sentiment }) {
  const hasValue =
    sentiment !== null &&
    sentiment !== undefined &&
    Number.isFinite(Number(sentiment));

  const score = hasValue
    ? Math.max(-1, Math.min(1, Number(sentiment)))
    : null;

  const label =
    score === null
      ? "Waiting"
      : score > 0.05
        ? "Positive"
        : score < -0.05
          ? "Negative"
          : "Neutral";

  const tone = label.toLowerCase();

  return (
    <section className="surface-card sentiment-card">

      <div className="card-heading">
        <div>
          <h3>AI Market Sentiment</h3>
          <p>FinBERT news intelligence analysis</p>
        </div>

        <span className={`sentiment-tag ${tone}`}>
          {label.toUpperCase()}
        </span>
      </div>

      <div className="sentiment-display">

        <div>
          <span className="sentiment-label">
            SENTIMENT SCORE
          </span>

          <div className={`sentiment-score ${tone}`}>
            {score === null ? "—" : score.toFixed(3)}
          </div>
        </div>

        <div className={`sentiment-orb ${tone}`}>
          {score === null ? "◉" : score > 0.05 ? "↗" : score < -0.05 ? "↘" : "→"}
        </div>

      </div>

      <div className="sentiment-track">
        <div className="sentiment-center" />

        {score !== null && (
          <div
            className={`sentiment-marker ${tone}`}
            style={{
              left: `${((score + 1) / 2) * 100}%`,
            }}
          />
        )}
      </div>

      <div className="sentiment-scale">
        <span>−1 Negative</span>
        <span>0 Neutral</span>
        <span>+1 Positive</span>
      </div>

      <div className={`sentiment-insight ${tone}`}>
        <strong>
          {score === null
            ? "Awaiting AI analysis"
            : `${label} market outlook`}
        </strong>

        <p>
          {score === null
            ? "Waiting for a processed news event."
            : "The displayed score represents the latest processed news sentiment used as a model input."}
        </p>
      </div>

    </section>
  );
}
