
import { useEffect, useState } from "react";
import CandlestickChart from "./components/CandlestickChart";
import ChartPerformanceTest from "./components/ChartPerformanceTest";
import OrderBook from "./components/OrderBook";
import NewsPanel from "./components/NewsPanel";
import RiskPanel from "./components/RiskPanel";
import RecentNews from "./components/RecentNews";
import InterpretabilitySidebar from "./components/InterpretabilitySidebar";
import "./index.css";

export default function App() {
  const [orderBook, setOrderBook] = useState(null);
  const [marketPrice, setMarketPrice] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [crashProbability, setCrashProbability] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("Connecting");

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/market");

    socket.onopen = () => setConnectionStatus("Connected");
    socket.onerror = () => setConnectionStatus("Connection error");
    socket.onclose = () => setConnectionStatus("Disconnected");

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === "market_update") {
          setOrderBook({
            mid_price: data.mid_price,
            bids: data.bids,
            asks: data.asks,
          });

          setMarketPrice(Number(data.mid_price));
          setSentiment(
            data.sentiment_score === undefined
              ? null
              : Number(data.sentiment_score)
          );

          setCrashProbability(
            data.crash_probability === undefined
              ? null
              : Number(data.crash_probability)
          );
        }
      } catch (error) {
        console.error("Invalid WebSocket message:", error);
      }
    };

    return () => socket.close();
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">Q</div>
          <div>
            <strong>QuantFormer</strong>
            <span>INTELLIGENT MARKETS</span>
          </div>
        </div>

        <p className="sidebar-label">WORKSPACE</p>

        <nav className="sidebar-nav">
          <a className="nav-link active" href="#overview">
            <span>◫</span> Overview
          </a>
          <a className="nav-link" href="#market">
            <span>⌁</span> Market Analysis
          </a>
          <a className="nav-link" href="#orderbook">
            <span>▤</span> Order Book
          </a>
          <a className="nav-link" href="#sentiment">
            <span>◉</span> Sentiment
          </a>
          <a className="nav-link" href="#interpretability">
            <span>◎</span> AI Explainability
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span
              className={`status-dot ${
                connectionStatus === "Connected" ? "online" : "offline"
              }`}
            />
            <div>
              <strong>Backend connection</strong>
              <small>{connectionStatus}</small>
            </div>
          </div>
          <p>QuantFormer · Educational simulation</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar" id="overview">
          <div>
            <p className="breadcrumb">QUANTFORMER / DASHBOARD</p>
            <h1>Market Overview</h1>
            <p className="page-subtitle">
              Multimodal Order Book &amp; Sentiment Transformer
            </p>
          </div>

          <div className="topbar-right">
            <span className="market-tag">SIMULATED MARKET</span>
            <span className="environment-tag">
              <span
                className={`status-dot ${
                  connectionStatus === "Connected" ? "online" : "offline"
                }`}
              />
              {connectionStatus.toUpperCase()}
            </span>
          </div>
        </header>

        <section className="section-block">
          <div className="section-heading">
            <div>
              <h2>Market Snapshot</h2>
              <p>Live simulated market indicators</p>
            </div>
            <span className="subtle-tag">REAL-TIME STREAM</span>
          </div>

          <div className="metrics-grid">
            <article className="metric-card">
              <div className="metric-top">
                Mid Price
                <span className="metric-icon blue">↗</span>
              </div>
              <strong className="metric-value">
                {marketPrice === null ? "—" : marketPrice.toFixed(2)}
              </strong>
              <small className="metric-caption">Latest market mid price</small>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                Market Sentiment
                <span className="metric-icon purple">◉</span>
              </div>
              <strong className="metric-value">
                {sentiment === null ? "—" : sentiment.toFixed(3)}
              </strong>
              <small className="metric-caption">
                Latest processed sentiment score
              </small>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                Crash Probability
                <span className="metric-icon orange">!</span>
              </div>
              <strong className="metric-value">
                {crashProbability === null
                  ? "—"
                  : `${(crashProbability * 100).toFixed(1)}%`}
              </strong>
              <small className="metric-caption">
                Backend model output
              </small>
            </article>

            <article className="metric-card">
              <div className="metric-top">
                Stream Status
                <span className="metric-icon green">⌁</span>
              </div>
              <strong className="metric-value connection-value">
                {connectionStatus}
              </strong>
              <small className="metric-caption">
                Market WebSocket connection
              </small>
            </article>
          </div>
        </section>

        <section className="section-block" id="market">
          <div className="section-heading">
            <div>
              <h2>Market Analytics</h2>
              <p>Price movement and order book liquidity</p>
            </div>
            <span className="live-indicator">
              <span className="status-dot online" />
              STREAMING
            </span>
          </div>

          <div className="analytics-grid">
            <section className="surface-card chart-card">
              <div className="card-heading">
                <div>
                  <h3>Market Candlestick Chart</h3>
                  <p>Price history and TFT forecast quantiles</p>
                </div>
                <span className="subtle-tag">TFT FORECAST</span>
              </div>
              <CandlestickChart
                marketUpdate={
                  marketPrice === null
                    ? null
                    : { mid_price: marketPrice }
                }
              />
            </section>

            <div id="orderbook">
              <OrderBook orderBook={orderBook} />
            </div>
          </div>
        </section>

        <section className="section-block" id="sentiment">
          <div className="section-heading">
            <div>
              <h2>Sentiment &amp; Risk Intelligence</h2>
              <p>News sentiment and model risk monitoring</p>
            </div>
          </div>

          <div className="analytics-grid">
            <NewsPanel sentiment={sentiment} />
            <RiskPanel crashProbability={crashProbability} />
          </div>
        </section>

        <section className="section-block">
          <div className="section-heading">
            <div>
              <h2>Recent News Feed</h2>
              <p>News events processed by the sentiment pipeline</p>
            </div>
          </div>
          <RecentNews />
        </section>

        <section className="section-block" id="interpretability">
          <div className="section-heading">
            <div>
              <h2>AI Model Explainability</h2>
              <p>Temporal Fusion Transformer feature importance</p>
            </div>
            <span className="subtle-tag">WEEK 4</span>
          </div>
          <InterpretabilitySidebar />
        </section>

        <section className="section-block">
          <div className="section-heading">
            <div>
              <h2>Chart Performance</h2>
              <p>Frontend chart performance test</p>
            </div>
          </div>
          <div className="surface-card performance-card">
            <ChartPerformanceTest />
          </div>
        </section>

        <footer className="dashboard-footer">
          <span>QuantFormer · Multimodal Financial Intelligence</span>
          <span>Educational simulation · Not financial advice</span>
        </footer>
      </main>
    </div>
  );
}
