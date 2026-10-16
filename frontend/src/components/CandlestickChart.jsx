
import { useEffect, useRef, useState } from "react";
import {
  createChart,
  CandlestickSeries,
  LineSeries,
} from "lightweight-charts";

export default function CandlestickChart({ marketUpdate }) {
  const containerRef = useRef(null);
  const seriesRef = useRef(null);
  const lastCandleRef = useRef(null);
  const forecastSeriesRef = useRef({});

  const [forecastStatus, setForecastStatus] = useState("Waiting for forecast");

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 380,
      layout: {
        background: { color: "#0b0f14" },
        textColor: "#d1d5db",
      },
      grid: {
        vertLines: { color: "#1f2937" },
        horzLines: { color: "#1f2937" },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: true,
      },
    });

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    const median = chart.addSeries(LineSeries, {
      color: "#60a5fa",
      lineWidth: 3,
      title: "TFT median",
      lastValueVisible: false,
      priceLineVisible: false,
    });

    const lower = chart.addSeries(LineSeries, {
      color: "#f59e0b",
      lineWidth: 1,
      title: "Lower quantile",
      lastValueVisible: false,
      priceLineVisible: false,
    });

    const upper = chart.addSeries(LineSeries, {
      color: "#c084fc",
      lineWidth: 1,
      title: "Upper quantile",
      lastValueVisible: false,
      priceLineVisible: false,
    });

    const now = Math.floor(Date.now() / 60000) * 60;

    const initialData = Array.from({ length: 30 }, (_, i) => {
      const close = 100 + Math.sin(i / 3);

      return {
        time: now - (30 - i) * 60,
        open: close - 0.1,
        high: close + 0.2,
        low: close - 0.2,
        close,
      };
    });

    candles.setData(initialData);
    lastCandleRef.current = initialData[initialData.length - 1];
    seriesRef.current = candles;

    forecastSeriesRef.current = { median, lower, upper };

    const resizeObserver = new ResizeObserver(() => {
      chart.applyOptions({ width: container.clientWidth });
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      seriesRef.current = null;
      lastCandleRef.current = null;
      forecastSeriesRef.current = {};
    };
  }, []);

  // Update the live candle using market events from Kafka.
  useEffect(() => {
    if (!marketUpdate || !seriesRef.current) return;

    const price = Number(marketUpdate.mid_price);
    if (!Number.isFinite(price)) return;

    const time = Math.floor(Date.now() / 60000) * 60;
    const previous = lastCandleRef.current;
    if (!previous) return;

    let candle;

    if (time > previous.time) {
      candle = {
        time,
        open: previous.close,
        high: Math.max(previous.close, price),
        low: Math.min(previous.close, price),
        close: price,
      };
    } else {
      candle = {
        time: previous.time,
        open: previous.open,
        high: Math.max(previous.high, price),
        low: Math.min(previous.low, price),
        close: price,
      };
    }

    seriesRef.current.update(candle);
    lastCandleRef.current = candle;
  }, [marketUpdate]);

  // Fetch the latest TFT forecast every five seconds.
  useEffect(() => {
    let stopped = false;

    async function loadForecast() {
      try {
        const response = await fetch("http://127.0.0.1:8000/forecast");

        if (!response.ok) {
          throw new Error(`Forecast API returned ${response.status}`);
        }

        const result = await response.json();
        if (stopped) return;

        const forecasts = result.forecasts ?? [];

        const toPoints = (key) =>
          forecasts
            .map((item) => ({
              time: Math.floor(
                new Date(item.timestamp).getTime() / 1000
              ),
              value: Number(item[key]),
            }))
            .filter(
              (item) =>
                Number.isFinite(item.time) &&
                Number.isFinite(item.value)
            )
            .sort((a, b) => a.time - b.time)
            .filter(
              (item, index, all) =>
                index === 0 || item.time > all[index - 1].time
            );

        const { median, lower, upper } = forecastSeriesRef.current;

        if (median && lower && upper) {
          median.setData(toPoints("median"));
          lower.setData(toPoints("lower"));
          upper.setData(toPoints("upper"));
          setForecastStatus(`Forecast updated: ${forecasts.length} steps`);
        }
      } catch (error) {
        if (!stopped) {
          setForecastStatus("Forecast unavailable — check backend/model");
          console.error("Could not load TFT forecast:", error);
        }
      }
    }

    loadForecast();
    const timer = setInterval(loadForecast, 5000);

    return () => {
      stopped = true;
      clearInterval(timer);
    };
  }, []);

  return (
    <div>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "14px",
          marginBottom: "10px",
          fontSize: "12px",
        }}
      >
        <span style={{ color: "#60a5fa" }}>━ TFT median (50%)</span>
        <span style={{ color: "#f59e0b" }}>━ Lower bound (10%)</span>
        <span style={{ color: "#c084fc" }}>━ Upper bound (90%)</span>
      </div>

      <div ref={containerRef} style={{ width: "100%" }} />

      <p style={{ color: "#94a3b8", fontSize: "12px" }}>
        {forecastStatus}
      </p>
    </div>
  );
}
