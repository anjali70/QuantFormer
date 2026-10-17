
import { useEffect, useState } from "react";
import ForecastRisk from "./components/ForecastRisk";

export default function ForecastRisk() {
  const [risk, setRisk] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadRisk() {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/forecast-risk"
        );

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const data = await response.json();

        if (!cancelled) {
          setRisk(data);
          setError("");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err.message);
        }
      }
    }

    loadRisk();
    const timer = setInterval(loadRisk, 10000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  if (error) {
    return <p>Forecast risk unavailable: {error}</p>;
  }

  if (!risk) {
    return <p>Loading forecast risk...</p>;
  }

  return (
    <section
      style={{
        padding: "16px",
        border: "1px solid #374151",
        borderRadius: "12px",
        marginTop: "12px",
      }}
    >
      <h3>TFT Forecast Risk</h3>

      <p>
        Risk level: <strong>{risk.risk_level}</strong>
      </p>

      <p>
        Risk score: <strong>{risk.risk_score}/100</strong>
      </p>

      <p>
        Current price: {risk.current_price}
      </p>

      <p>
        Worst forecasted decline:{" "}
        {risk.worst_forecast_decline_pct}%
      </p>

      <p>
        Average forecast interval:{" "}
        {risk.average_forecast_interval_pct}%
      </p>

      <small>{risk.interpretation}</small>
    </section>
  );
}
