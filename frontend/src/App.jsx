
import { useEffect, useState } from "react";
import CandlestickChart from "./components/CandlestickChart";
import ChartPerformanceTest from "./components/ChartPerformanceTest";
import OrderBook from "./components/OrderBook";
import NewsPanel from "./components/NewsPanel";
import RiskPanel from "./components/RiskPanel";
import "./index.css";

export default function App() {
  const [orderBook, setOrderBook] = useState(null);
  const [marketPrice, setMarketPrice] = useState(null);
  const [sentiment, setSentiment] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("Connecting");

  useEffect(() => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws/market");

    socket.onopen = () => setConnectionStatus("Connected");
    socket.onerror = () => setConnectionStatus("Connection error");
    socket.onclose = () => setConnectionStatus("Disconnected");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "market_update") {
        setOrderBook({
          mid_price: data.mid_price,
          bids: data.bids,
          asks: data.asks,
        });
        setMarketPrice(data.mid_price);
        setSentiment(data.sentiment_score);
      }
    };

    return () => socket.close();
  }, []);

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>QuantFormer</h1>
          <p>Multimodal Order Book &amp; Sentiment Transformer</p>
        </div>
        <span className="simulation-badge">
          {connectionStatus.toUpperCase()}
        </span>
      </header>

      <div className="summary-grid">
        <section className="panel">
          <h2>Live Simulated Market</h2>
          <p className="muted">Mid price</p>
          <p className="risk-probability">
            {marketPrice === null ? "Waiting..." : marketPrice.toFixed(2)}
          </p>
          <p className="muted">
            {sentiment === null
              ? "Waiting for sentiment..."
              : `Simulated sentiment score: ${sentiment.toFixed(3)}`}
          </p>
        </section>
        <RiskPanel />
      </div>

      <div className="market-grid">
        <section className="panel chart-panel">
          <h2>Market Candlestick Chart</h2>
          <CandlestickChart   marketUpdate={marketPrice === null ? null : { mid_price: marketPrice }}
         />
        </section>
        <OrderBook orderBook={orderBook} />
      </div>

      <div className="summary-grid">
        <NewsPanel />
        <section className="panel">
          <h2>Backend Connection</h2>
          <p>Status: <strong>{connectionStatus}</strong></p>
          <p className="muted">
            Market updates are received through the WebSocket connection.
          </p>
        </section>
      </div>

      <section className="panel performance-panel">
        <ChartPerformanceTest />
      </section>

      <footer className="dashboard-footer">
        QuantFormer · Educational simulation · Not financial advice
      </footer>
    </main>
  );
}
