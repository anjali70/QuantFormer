
import { useEffect, useRef, useState } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";

export default function ChartPerformanceTest() {
  const containerRef = useRef(null);
  const [updatesPerSecond, setUpdatesPerSecond] = useState(0);
  const [totalUpdates, setTotalUpdates] = useState(0);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const chart = createChart(container, {
      width: container.clientWidth,
      height: 260,
      layout: {
        background: { color: "#0b0f14" },
        textColor: "#d1d5db",
      },
      grid: {
        vertLines: { color: "#1f2937" },
        horzLines: { color: "#1f2937" },
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderVisible: false,
      wickUpColor: "#22c55e",
      wickDownColor: "#ef4444",
    });

    let price = 100;
    let updatesThisSecond = 0;
    let total = 0;
    let currentTime = Math.floor(Date.now() / 1000);

    series.setData(
      Array.from({ length: 30 }, (_, i) => ({
        time: currentTime - 30 + i,
        open: 100,
        high: 100.2,
        low: 99.8,
        close: 100,
      }))
    );

    const updateTimer = setInterval(() => {
      const open = price;
      price += (Math.random() - 0.5) * 0.2;

      // Ten updates per second, updating the current candle.
      series.update({
        time: currentTime,
        open,
        high: Math.max(open, price) + 0.05,
        low: Math.min(open, price) - 0.05,
        close: price,
      });

      updatesThisSecond += 1;
      total += 1;
    }, 100);

    const measurementTimer = setInterval(() => {
      setUpdatesPerSecond(updatesThisSecond);
      setTotalUpdates(total);
      updatesThisSecond = 0;
      currentTime += 1;
    }, 1000);

    const observer = new ResizeObserver(() => {
      chart.applyOptions({ width: container.clientWidth });
    });
    observer.observe(container);

    return () => {
      clearInterval(updateTimer);
      clearInterval(measurementTimer);
      observer.disconnect();
      chart.remove();
    };
  }, []);

  return (
    <div>
      <h2>Chart Performance Test</h2>
      <div className="performance-stats">
        <p>Updates per second: <strong>{updatesPerSecond}</strong></p>
        <p>Total updates: <strong>{totalUpdates}</strong></p>
        <p>
          Status:{" "}
          <strong>
            {updatesPerSecond >= 10 ? "Target reached" : "Testing"}
          </strong>
        </p>
      </div>
      <div ref={containerRef} style={{ width: "100%" }} />
      <p className="muted">
        This counts chart update calls. It does not by itself prove that the
        browser thread is never blocked.
      </p>
    </div>
  );
}
