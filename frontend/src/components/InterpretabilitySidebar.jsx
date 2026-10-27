
import { useEffect, useState } from "react";
import "./InterpretabilitySidebar.css";

const API = "http://127.0.0.1:8000";

function ImportanceList({ title, items }) {
  if (!items?.length) return null;

  const max = Math.max(
    ...items.map((item) => Number(item.importance) || 0),
    0.000001
  );

  return (
    <section className="interpret-section">
      <h4>{title}</h4>

      {items.map((item, index) => {
        const score = Number(item.importance) || 0;
        const width = Math.min(100, (score / max) * 100);

        return (
          <div className="importance-item" key={`${item.feature}-${index}`}>
            <div className="importance-label">
              <span>{item.feature}</span>
              <strong>{score.toFixed(4)}</strong>
            </div>
            <div className="importance-track">
              <div
                className="importance-fill"
                style={{ width: `${width}%` }}
              />
            </div>
          </div>
        );
      })}
    </section>
  );
}

export default function InterpretabilitySidebar() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response = await fetch(`${API}/interpretability`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const result = await response.json();
        if (active) {
          setData(result);
          setError("");
        }
      } catch (err) {
        if (active) setError(err.message || "Unable to load interpretation");
      }
    }

    load();
    const timer = setInterval(load, 30000);

    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  const attention = data?.attention_top_steps ?? [];
  const maxAttention = Math.max(
    ...attention.map((item) => Number(item.attention) || 0),
    0.000001
  );

  return (
    <aside className="interpret-card">
      <div className="interpret-header">
        <div>
          <p className="interpret-eyebrow">WEEK 4 · MODEL EXPLAINABILITY</p>
          <h2>Model Interpretability</h2>
          <p className="interpret-subtitle">
            Temporal Fusion Transformer
          </p>
        </div>
        <span className={`interpret-status ${error ? "status-error" : ""}`}>
          {error ? "Unavailable" : data ? "Model loaded" : "Loading"}
        </span>
      </div>

      {error && (
        <p className="interpret-error">
          Could not load interpretation: {error}
        </p>
      )}

      {!data && !error && <p>Loading attention and feature importance…</p>}

      {data && (
        <>
          <section className="interpret-section">
            <h4>Top historical attention steps</h4>
            <p className="interpret-help">
              Relative attention assigned to historical positions.
            </p>

            {attention.length === 0 && <p>No attention data available.</p>}

            {attention.map((item, index) => {
              const weight = Number(item.attention) || 0;

              return (
                <div className="attention-item" key={`${item.step}-${index}`}>
                  <div className="importance-label">
                    <span>Historical step {item.step}</span>
                    <strong>{(weight * 100).toFixed(1)}%</strong>
                  </div>
                  <div className="importance-track">
                    <div
                      className="attention-fill"
                      style={{
                        width: `${Math.min(100, (weight / maxAttention) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </section>

          <ImportanceList
            title="Historical input importance"
            items={data.encoder_variable_importance}
          />

          <ImportanceList
            title="Forecast input importance"
            items={data.decoder_variable_importance}
          />

          <ImportanceList
            title="Static feature importance"
            items={data.static_variable_importance}
          />

          <div className="interpret-note">
            <strong>How to read this</strong>
            <p>
              These values describe patterns in the model's attention and
              feature selection. They do not prove that a feature or a
              particular news headline caused the prediction.
            </p>
            {data.note && <p>{data.note}</p>}
          </div>
        </>
      )}
    </aside>
  );
}
