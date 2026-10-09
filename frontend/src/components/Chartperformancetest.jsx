
import { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

export default function ChartPerformanceTest() {
  const chartContainer = useRef(null);
  const [updatesPerSecond, setUpdatesPerSecond] = useState(0);
  const [totalUpdates, setTotalUpdates] = useState(0);

  useEffect(() => {
    if (!chartContainer.current) return;

    const chart = createChart(chartContainer.current, {
      width: chartContainer.current.clientWidth,
      height: 350,
      layout: {
        background: { color: "#111827" },
        textColor: "#d1d5db",
      },
      grid: {
        vertLines: { color: "#263244" },
        horzLines: { color: "#263244" },
      },
    });

    const series = chart.addCandlestickSeries();

    const startTime = Math.floor(Date.now() / 1000);
    let price = 100;
    let updateCount = 0;
    let displayedTotal = 0;

    series.setData(
      Array.from({ length: 30 }, (_, i) => {
        const open = 100 + Math.sin(i / 3);
        return {
          time: startTime - 30 + i,
          open,
          high: open + 0.5,
          low: open - 0.5,
          close: open + 0.1,
        };
      })
    );

    // Send 10 chart updates per second.
    const updateTimer = setInterval(() => {
      const open = price;
      price += (Math.random() - 0.5) * 0.2;

      const time = Math.floor(Date.now() / 1000);

      series.update({
        time,
        open,
        high: Math.max(open, price) + 0.05,
        low: Math.min(open, price) - 0.05,
        close: price,
      });

      updateCount++;
      displayedTotal++;
    }, 100);

    // Measure the number of updates in each one-second period.
    const measurementTimer = setInterval(() => {
      setUpdatesPerSecond(updateCount);
      setTotalUpdates(displayedTotal);
      updateCount = 0;
    }, 1000);

    const resizeObserver = new ResizeObserver(() => {
      if (chartContainer.current) {
        chart.applyOptions({
          width: chartContainer.current.clientWidth,
        });
      }
    });

    resizeObserver.observe(chartContainer.current);

    return () => {
      clearInterval(updateTimer);
      clearInterval(measurementTimer);
      resizeObserver.disconnect();
      chart.remove();
    };
  }, []);

  return (
    <div style={{ padding: 20, color: "#e5e7eb" }}>
      <h2>QuantFormer Chart Performance Test</h2>

      <p>
        Updates per second: <strong>{updatesPerSecond}</strong>
      </p>

      <p>
        Total chart updates: <strong>{totalUpdates}</strong>
      </p>

      <p>
        Performance status:{" "}
        <strong>
          {updatesPerSecond >= 10 ? "Target reached" : "Testing..."}
        </strong>
      </p>

      <div
        ref={chartContainer}
        style={{ width: "100%", minHeight: 350 }}
      />
    </div>
  );
}
