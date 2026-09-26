import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries
} from "lightweight-charts";


export default function CandlestickChart() {

  const chartContainer = useRef(null);

  useEffect(() => {

    const chart = createChart(
      chartContainer.current,
      {
        width: 900,
        height: 450,

        layout: {
          background: {
            color: "#0b0f14"
          },
          textColor: "#d1d5db"
        },

        grid: {
          vertLines: {
            color: "#1f2937"
          },
          horzLines: {
            color: "#1f2937"
          }
        }
      }
    );

    const series = chart.addSeries(
      CandlestickSeries,
      {
        upColor: "#22c55e",
        downColor: "#ef4444",
        borderVisible: false,
        wickUpColor: "#22c55e",
        wickDownColor: "#ef4444"
      }
    );

    const data = [];

    let price = 100;

    for (let i = 0; i < 100; i++) {

      const open = price;

      const close =
        price + (Math.random() - 0.5) * 0.5;

      const high =
        Math.max(open, close) +
        Math.random() * 0.2;

      const low =
        Math.min(open, close) -
        Math.random() * 0.2;

      data.push({
        time: 1700000000 + i * 60,
        open,
        high,
        low,
        close
      });

      price = close;
    }

    series.setData(data);

    return () => {
      chart.remove();
    };

  }, []);

  return (
    <div
      ref={chartContainer}
      style={{
        width: "100%",
        height: "450px"
      }}
    />
  );
}