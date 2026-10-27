
import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function RecentNews() {
  const [news, setNews] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let stopped = false;

    async function loadNews() {
      try {
        const response = await fetch(
          `${API_URL}/news-history?limit=10`
        );

        if (!response.ok) {
          throw new Error(`API returned ${response.status}`);
        }

        const result = await response.json();

        if (!stopped) {
          setNews(result.news || []);
          setError("");
        }
      } catch (err) {
        if (!stopped) {
          setError(err.message || "Unable to load news.");
        }
      } finally {
        if (!stopped) {
          setLoading(false);
        }
      }
    }

    loadNews();
    const timer = setInterval(loadNews, 15000);

    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, []);

  const panelStyle = {
    background: "#111827",
    color: "#e5e7eb",
    border: "1px solid #273449",
    borderRadius: 12,
    padding: 16,
  };

  return (
    <section style={panelStyle}>
      <h2 style={{ fontSize: 18, marginTop: 0 }}>
        Recent News & Sentiment
      </h2>

      <p style={{ color: "#9ca3af", fontSize: 12 }}>
        News events associated with recorded sentiment scores
      </p>

      {loading && <p>Loading news...</p>}

      {error && (
        <p style={{ color: "#fca5a5", fontSize: 13 }}>
          {error}
        </p>
      )}

      {!loading && !error && news.length === 0 && (
        <p style={{ color: "#9ca3af", fontSize: 13 }}>
          No news events recorded yet. Start the news producer
          and connect it to the news history logger.
        </p>
      )}

      {news.map((item, index) => {
        const label = String(
          item.sentiment_label || "Neutral"
        );

        const sentimentColor =
          label.toLowerCase() === "negative"
            ? "#f87171"
            : label.toLowerCase() === "positive"
              ? "#4ade80"
              : "#fbbf24";

        return (
          <article
            key={`${item.timestamp}-${index}`}
            style={{
              padding: "12px 0",
              borderTop: "1px solid #273449",
            }}
          >
            <div
              style={{
                color: "#9ca3af",
                fontSize: 11,
              }}
            >
              {item.timestamp
                ? new Date(item.timestamp).toLocaleString()
                : "Timestamp unavailable"}
              {" · "}
              {item.source || "Unknown source"}
            </div>

            <p
              style={{
                fontSize: 13,
                lineHeight: 1.5,
                overflowWrap: "anywhere",
              }}
            >
              {item.headline}
            </p>

            <div
              style={{
                color: sentimentColor,
                fontSize: 12,
                fontWeight: 600,
              }}
            >
              {label} sentiment · Score:{" "}
              {Number(item.sentiment_score).toFixed(3)}
            </div>
          </article>
        );
      })}
    </section>
  );
}
