
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function InterpretabilitySidebar() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadInterpretation() {
      try {
        const response = await fetch(
          `${API_URL}/interpretability`
        );

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const result = await response.json();

        if (!cancelled) {
          setData(result);
          setError("");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadInterpretation();

    // Refresh explanations periodically.
    const timer = setInterval(loadInterpretation, 30000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  if (loading) {
    return <aside>Loading model explanation...</aside>;
  }

  if (error) {
    return (
      <aside>
        <h3>Model Interpretability</h3>
        <p>Could not load explanation: {error}</p>
      </aside>
    );
  }

  const topSteps = data.attention_top_steps ?? [];
  const variables = data.encoder_variable_importance ?? [];

  return (
    <aside
      style={{
        padding: 16,
        border: "1px solid #374151",
        borderRadius: 12,
        color: "#e5e7eb",
        background: "#111827",
        width: "100%",
        boxSizing: "border-box",
      }}
    >
      <h3>Why did TFT predict this?</h3>

      <p style={{ color: "#9ca3af", fontSize: 12 }}>
        Attention and feature-selection explanation
      </p>

      <h4>Most attended historical steps</h4>

      {topSteps.length === 0 ? (
        <p>No attention data available.</p>
      ) : (
        topSteps.map((item) => (
          <div
            key={item.time_idx}
            style={{
              padding: "8px 0",
              borderBottom: "1px solid #374151",
            }}
          >
            <div style={{ fontSize: 13 }}>
              {item.timestamp
                ? new Date(item.timestamp).toLocaleString()
                : `Time step ${item.time_idx}`}
            </div>

            <div style={{ color: "#60a5fa", fontSize: 12 }}>
              Attention weight: {item.weight}
            </div>
          </div>
        ))
      )}

      <h4>Important historical inputs</h4>

      {variables.length === 0 ? (
        <p>No variable importance available.</p>
      ) : (
        variables.map((item) => (
          <div
            key={item.feature}
            style={{
              display: "flex",
              justifyContent: "space-between",
              gap: 12,
              padding: "6px 0",
            }}
          >
            <span>{item.feature}</span>
            <strong>{item.weight}</strong>
          </div>
        ))
      )}

      <p
        style={{
          fontSize: 11,
          lineHeight: 1.5,
          color: "#9ca3af",
          marginTop: 16,
        }}
      >
        {data.note}
      </p>
    </aside>
  );
}
