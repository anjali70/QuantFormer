
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

  return (
    <section className="surface-card recent-news-card">

      <div className="card-heading">
        <div>
          <h3>Market Intelligence Feed</h3>
          <p>Latest news events processed by the AI pipeline</p>
        </div>

        <span className="live-indicator">
          <span className="status-dot online" />
          AUTO REFRESH
        </span>
      </div>

      {loading && (
        <div className="news-empty">
          <span className="news-loading-dot" />
          Loading market intelligence...
        </div>
      )}

      {error && (
        <div className="news-empty news-error">
          <strong>Unable to load news</strong>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && news.length === 0 && (
        <div className="news-empty">
          <span className="news-empty-icon">◈</span>
          <strong>No news events yet</strong>
          <p>
            Start the news producer and connect it to the
            news history logger.
          </p>
        </div>
      )}

      {!error && news.length > 0 && (
        <div className="news-list">

          {news.map((item, index) => {
            const label = String(
              item.sentiment_label || "Neutral"
            );

            const tone =
              label.toLowerCase() === "negative"
                ? "negative"
                : label.toLowerCase() === "positive"
                  ? "positive"
                  : "neutral";

            const rawScore = Number(item.sentiment_score);
            const score = Number.isFinite(rawScore)
              ? rawScore.toFixed(3)
              : "—";

            return (
              <article
                className="news-item"
                key={`${item.timestamp}-${index}`}
              >

                <div className="news-timeline">
                  <span className={`news-dot ${tone}`} />
                  {index !== news.length - 1 && (
                    <span className="news-line" />
                  )}
                </div>

                <div className="news-content">

                  <div className="news-meta">
                    <span>
                      {item.timestamp
                        ? new Date(item.timestamp).toLocaleString()
                        : "Timestamp unavailable"}
                    </span>

                    <span className="news-source">
                      {item.source || "Unknown source"}
                    </span>
                  </div>

                  <h4>
                    {item.headline || "Untitled news event"}
                  </h4>

                  <div className="news-bottom">
                    <span className={`news-sentiment ${tone}`}>
                      {label.toUpperCase()}
                    </span>

                    <span className="news-score">
                      SCORE: {score}
                    </span>
                  </div>

                </div>

              </article>
            );
          })}

        </div>
      )}

    </section>
  );
}
