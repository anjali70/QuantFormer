
import { useEffect, useRef } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";

export default function CandlestickChart({ marketUpdate }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const lastCandleTimeRef = useRef(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 400,
      layout: {
        background: { color: "#0b0f14" },
        textColor: "#d1d5db",
      },
      grid: {
        vertLines: { color: "#1f2937" },
        horzLines: { color: "#1f2937" },
      },
      timeScale: { timeVisible: true },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const now = Math.floor(Date.now() / 60_000) * 60;
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

    series.setData(initialData);
    lastCandleTimeRef.current = initialData[initialData.length - 1].time;

    const observer = new ResizeObserver(() => {
      chart.applyOptions({ width: container.clientWidth });
    });
    observer.observe(container);

    return () => {
      observer.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!marketUpdate || !seriesRef.current) return;

    const time = Math.floor(Date.now() / 60_000) * 60;
    const price = marketUpdate.mid_price;
    const previousTime = lastCandleTimeRef.current;

    if (time > previousTime) {
      seriesRef.current.update({
        time,
        open: price,
        high: price,
        low: price,
        close: price,
      });
      lastCandleTimeRef.current = time;
    } else {
      // Update the current candle with the newest market price.
      // Lightweight Charts expects the latest candle timestamp here.
      seriesRef.current.update({
        time: previousTime,
        open: price,
        high: price,
        low: price,
        close: price,
      });
    }
  }, [marketUpdate]);

  return <div ref={containerRef} style={{ width: "100%" }} />;
}
