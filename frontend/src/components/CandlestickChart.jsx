
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
  const fittedRef = useRef(false);

  const [status, setStatus] = useState("Loading forecast...");
  const [lastPrice, setLastPrice] = useState(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 390,

      layout: {
        background: { color: "#111c2d" },
        textColor: "#91a3bd",
        fontFamily: "Inter, sans-serif",
        fontSize: 11,
      },

      grid: {
        vertLines: { color: "#26364d55" },
        horzLines: { color: "#26364d77" },
      },

      crosshair: {
        vertLine: {
          color: "#5794ff88",
          width: 1,
          style: 2,
          labelBackgroundColor: "#347dff",
        },
        horzLine: {
          color: "#5794ff88",
          width: 1,
          style: 2,
          labelBackgroundColor: "#347dff",
        },
      },

      rightPriceScale: {
        borderColor: "#30425c",
        scaleMargins: {
          top: 0.12,
          bottom: 0.12,
        },
      },

      timeScale: {
        borderColor: "#30425c",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 5,
      },

      localization: {
        priceFormatter: (price) => price.toFixed(2),
      },

      handleScroll: true,
      handleScale: true,
    });

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: "#20c997",
      downColor: "#ff647c",
      borderUpColor: "#20c997",
      borderDownColor: "#ff647c",
      wickUpColor: "#20c997",
      wickDownColor: "#ff647c",
      borderVisible: false,
      priceLineVisible: true,
      lastValueVisible: true,
    });

    const median = chart.addSeries(LineSeries, {
      color: "#5794ff",
      lineWidth: 3,
      title: "Median 50%",
      lineStyle: 0,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const lower = chart.addSeries(LineSeries, {
      color: "#f6ad55",
      lineWidth: 2,
      title: "Lower 10%",
      lineStyle: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const upper = chart.addSeries(LineSeries, {
      color: "#b794f6",
      lineWidth: 2,
      title: "Upper 90%",
      lineStyle: 2,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    candleRef.current = candles;
    chartRef.current = chart;
    forecastRef.current = { median, lower, upper };

    // Initial demo candles until historical data is available.
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
    setLastPrice(initial[initial.length - 1].close);

    const observer = new ResizeObserver(() => {
      chart.applyOptions({
        width: container.clientWidth,
      });
    });

    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.remove();

      chartRef.current = null;
      candleRef.current = null;
      lastCandleRef.current = null;
      forecastRef.current = {};
      fittedRef.current = false;
    };
  }, []);

  // Live market updates
  useEffect(() => {
    if (!marketUpdate || !candleRef.current) return;

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

    candleRef.current.update(candle);
    lastCandleRef.current = candle;
    setLastPrice(price);
  }, [marketUpdate]);

  // TFT forecast
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

        if (!median || !lower || !upper) return;

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

        // Fit the chart only on the first successful forecast.
        if (!fittedRef.current) {
          chartRef.current?.timeScale().fitContent();
          fittedRef.current = true;
        }

        setStatus("TFT forecast successfully synchronized");
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
    <div className="trading-chart">

      <div className="chart-toolbar">

        <div className="chart-price-info">
          <span>MARKET PRICE</span>

          <strong>
            {lastPrice === null ? "—" : lastPrice.toFixed(2)}
          </strong>
        </div>

        <div className="chart-status">
          <span className="status-dot online" />
          LIVE MARKET
        </div>

      </div>

      <div className="chart-legend">

        <span>
          <i className="legend-line median-line" />
          Median (50%)
        </span>

        <span>
          <i className="legend-line lower-line" />
          Lower (10%)
        </span>

        <span>
          <i className="legend-line upper-line" />
          Upper (90%)
        </span>

        <span>
          <i className="legend-candle" />
          Market candles
        </span>

      </div>

      <div
        className="trading-chart-container"
        ref={containerRef}
      />

      <div className="chart-footer">
        <span>{status}</span>
        <span>TEMPORAL FUSION TRANSFORMER</span>
      </div>

    </div>
  );
}
