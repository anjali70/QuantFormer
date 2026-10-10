
const sampleNews = [
  {
    headline: "Company reports stronger quarterly earnings",
    sentiment: "Positive",
    score: 0.78,
  },
  {
    headline: "Market volatility increases before policy announcement",
    sentiment: "Neutral",
    score: 0.04,
  },
  {
    headline: "Company warns of lower future revenue",
    sentiment: "Negative",
    score: -0.72,
  },
];

export default function NewsPanel() {
  return (
    <section className="panel">
      <h2>News Sentiment</h2>
      <p className="muted">Sample headlines for dashboard preview</p>

      {sampleNews.map((news, index) => (
        <article className="news-item" key={index}>
          <p>{news.headline}</p>
          <div className="news-meta">
            <span
              className={`sentiment sentiment-${news.sentiment.toLowerCase()}`}
            >
              {news.sentiment}
            </span>
            <span>Score: {news.score.toFixed(2)}</span>
          </div>
        </article>
      ))}
    </section>
  );
}
