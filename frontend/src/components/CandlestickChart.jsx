
import { useEffect, useRef, useState } from "react";
import {
  createChart,
  CandlestickSeries,
  LineSeries,
} from "lightweight-charts";

const API_URL = "http://127.0.0.1:8000";

export default function CandlestickChart({ marketUpdate }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const candleRef = useRef(null);
  const lastCandleRef = useRef(null);
  const forecastRef = useRef({});
  const [status, setStatus] = useState("Loading forecast...");

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
      title: "TFT median (50%)",
      priceLineVisible: false,
    });

    const lower = chart.addSeries(LineSeries, {
      color: "#f59e0b",
      lineWidth: 2,
      title: "Lower quantile (10%)",
      priceLineVisible: false,
    });

    const upper = chart.addSeries(LineSeries, {
      color: "#c084fc",
      lineWidth: 2,
      title: "Upper quantile (90%)",
      priceLineVisible: false,
    });

    candleRef.current = candles;
    chartRef.current = chart;
    forecastRef.current = { median, lower, upper };

    // Sample candles are placeholders until real history is loaded.
    const now = Math.floor(Date.now() / 1000);
    const initial = Array.from({ length: 20 }, (_, i) => {
      const close = 100 + Math.sin(i / 3);

      return {
        time: now - (20 - i) * 60,
        open: close - 0.1,
        high: close + 0.2,
        low: close - 0.2,
        close,
      };
    });

    candles.setData(initial);
    lastCandleRef.current = initial[initial.length - 1];

    const resizeObserver = new ResizeObserver(() => {
      chart.applyOptions({ width: container.clientWidth });
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      candleRef.current = null;
      lastCandleRef.current = null;
      forecastRef.current = {};
    };
  }, []);

  useEffect(() => {
    if (!marketUpdate || !candleRef.current) return;

    const price = Number(marketUpdate.mid_price);
    if (!Number.isFinite(price)) return;

    // Use minute candles to match the initial chart data.
    const time = Math.floor(Date.now() / 60_000) * 60;
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

    candleRef.current.update(candle);
    lastCandleRef.current = candle;
  }, [marketUpdate]);

  useEffect(() => {
    let stopped = false;

    async function loadForecast() {
      try {
        const response = await fetch(`${API_URL}/forecast`);

        if (!response.ok) {
          throw new Error(`Forecast API returned ${response.status}`);
        }

        const result = await response.json();
        if (stopped) return;

        const forecasts = result.forecasts ?? [];

        if (forecasts.length !== 5) {
          throw new Error(
            `Expected 5 forecast steps; received ${forecasts.length}`
          );
        }

        const points = (key) =>
          forecasts
            .map((item) => ({
              time: Math.floor(
                new Date(item.timestamp).getTime() / 1000
              ),
              value: Number(item[key]),
            }))
            .filter(
              (point) =>
                Number.isFinite(point.time) &&
                Number.isFinite(point.value)
            )
            .sort((a, b) => a.time - b.time);

        const { median, lower, upper } = forecastRef.current;

        if (
          !median ||
          !lower ||
          !upper
        ) {
          return;
        }

        const medianPoints = points("median");
        const lowerPoints = points("lower");
        const upperPoints = points("upper");

        if (
          medianPoints.length !== 5 ||
          lowerPoints.length !== 5 ||
          upperPoints.length !== 5
        ) {
          throw new Error("Forecast quantile values are incomplete.");
        }

        median.setData(medianPoints);
        lower.setData(lowerPoints);
        upper.setData(upperPoints);

        chartRef.current?.timeScale().fitContent();

        setStatus("TFT forecast loaded: 5 steps, 10th/50th/90th quantiles");
      } catch (error) {
        if (!stopped) {
          console.error("TFT forecast error:", error);
          setStatus(`Forecast unavailable: ${error.message}`);
        }
      }
    }

    loadForecast();
    const timer = setInterval(loadForecast, 10000);

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
          gap: 14,
          marginBottom: 10,
          fontSize: 12,
        }}
      >
        <span style={{ color: "#60a5fa" }}>
          ━ Median (50%)
        </span>
        <span style={{ color: "#f59e0b" }}>
          ━ Lower bound (10%)
        </span>
        <span style={{ color: "#c084fc" }}>
          ━ Upper bound (90%)
        </span>
      </div>

      <div ref={containerRef} style={{ width: "100%" }} />

      <p style={{ color: "#94a3b8", fontSize: 12 }}>
        {status}
      </p>
    </div>
  );
}
