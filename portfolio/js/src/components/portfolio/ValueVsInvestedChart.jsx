import { AreaSeries, LineSeries, LineStyle, createChart } from "lightweight-charts";
import { useEffect, useRef, useState } from "react";
import { analyticsAPI } from "../../services/api";
import { formatCurrency } from "../../utils/formatters.jsx";
import LoadingSpinner from "../shared/LoadingSpinner";

const RANGES = [
  ["3M", 90],
  ["6M", 180],
  ["1Y", 365],
  ["2Y", 730],
];

const ValueVsInvestedChart = ({ portfolioId }) => {
  const containerRef = useRef(null);
  const [days, setDays] = useState(365);
  const [points, setPoints] = useState(null);

  useEffect(() => {
    if (!portfolioId) return;
    let cancelled = false;
    setPoints(null);
    analyticsAPI
      .getPortfolioPerformanceHistory(portfolioId, days)
      .then((res) => {
        if (cancelled) return;
        const byDay = new Map();
        (res.history || []).forEach((h) => byDay.set(h.snapshot_date.slice(0, 10), h));
        setPoints(
          [...byDay.entries()]
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([time, h]) => ({
              time,
              value: Number(h.total_value),
              invested: Number(h.total_cost_basis),
            }))
        );
      })
      .catch(() => !cancelled && setPoints([]));
    return () => {
      cancelled = true;
    };
  }, [portfolioId, days]);

  useEffect(() => {
    if (!containerRef.current || !points?.length) return;
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { color: "transparent" }, textColor: "#94a3b8" },
      grid: { vertLines: { visible: false }, horzLines: { color: "#1e293b" } },
      rightPriceScale: { borderVisible: false },
      timeScale: { borderVisible: false },
      localization: {
        priceFormatter: (p) => formatCurrency(p, { notation: "compact" }),
      },
    });
    chart
      .addSeries(AreaSeries, {
        lineColor: "#38bdf8",
        topColor: "rgba(56, 189, 248, 0.25)",
        bottomColor: "rgba(56, 189, 248, 0)",
        lineWidth: 2,
        priceLineVisible: false,
        title: "Value",
      })
      .setData(points.map((p) => ({ time: p.time, value: p.value })));
    chart
      .addSeries(LineSeries, {
        color: "#94a3b8",
        lineWidth: 1,
        lineStyle: LineStyle.Dashed,
        priceLineVisible: false,
        lastValueVisible: false,
        title: "Invested",
      })
      .setData(points.map((p) => ({ time: p.time, value: p.invested })));
    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [points]);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-100">Value vs Invested</h3>
        <div className="flex gap-1">
          {RANGES.map(([label, d]) => (
            <button
              key={label}
              onClick={() => setDays(d)}
              className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
                days === d ? "bg-primary-600 text-white" : "text-gray-400 hover:bg-dark-700"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>
      {points === null ? (
        <LoadingSpinner text="Loading history..." centered className="h-80" />
      ) : points.length < 2 ? (
        <p className="h-80 flex items-center justify-center text-gray-400">No value history yet.</p>
      ) : (
        <div ref={containerRef} className="h-80" />
      )}
    </div>
  );
};

export default ValueVsInvestedChart;
