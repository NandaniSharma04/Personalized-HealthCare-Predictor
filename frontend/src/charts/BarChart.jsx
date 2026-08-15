import React, { useState } from 'react';

/**
 * Interactive SVG Bar Chart Component
 * @param {Array<{ label: string, value: number, color?: string }>} data
 * @param {string} title
 * @param {boolean} horizontal
 * @param {number} height
 */
export default function BarChart({ data = [], title = "Activity Frequency", horizontal = true, height = 220 }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="flex-center p-6 text-center text-muted" style={{ minHeight: `${height}px`, flexDirection: "column" }}>
        <span style={{ fontSize: "0.78rem" }}>No activity data available to graph</span>
      </div>
    );
  }

  const maxValue = Math.max(...data.map(d => Number(d.value) || 0), 1);

  if (horizontal) {
    return (
      <div className="bar-chart-horizontal" style={{ display: "flex", flexDirection: "column", gap: "10px", width: "100%" }}>
        {data.map((item, idx) => {
          const val = Number(item.value) || 0;
          const percentage = Math.min((val / maxValue) * 100, 100);
          const barColor = item.color || "linear-gradient(90deg, #2563eb, #06b6d4)";

          return (
            <div
              key={idx}
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "4px",
                padding: "4px 6px",
                borderRadius: "6px",
                background: hoveredIdx === idx ? "rgba(255,255,255,0.04)" : "transparent",
                transition: "background 0.15s"
              }}
              onMouseEnter={() => setHoveredIdx(idx)}
              onMouseLeave={() => setHoveredIdx(null)}
            >
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.75rem" }}>
                <span style={{ color: "#e2e8f0", fontWeight: "500", textTransform: "capitalize" }}>{item.label}</span>
                <span style={{ color: "#38bdf8", fontWeight: "700" }}>{val} event(s)</span>
              </div>
              <div style={{ width: "100%", height: "8px", background: "rgba(255,255,255,0.08)", borderRadius: "4px", overflow: "hidden" }}>
                <div
                  style={{
                    width: `${Math.max(percentage, 4)}%`,
                    height: "100%",
                    background: barColor,
                    borderRadius: "4px",
                    transition: "width 0.4s ease"
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  // Vertical Bar Chart
  return (
    <div className="bar-chart-vertical" style={{ display: "flex", alignItems: "flex-end", gap: "12px", height: `${height}px`, width: "100%", padding: "10px 0" }}>
      {data.map((item, idx) => {
        const val = Number(item.value) || 0;
        const percentage = Math.min((val / maxValue) * 100, 100);
        const barColor = item.color || "#3b82f6";

        return (
          <div
            key={idx}
            style={{
              flex: 1,
              height: "100%",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "flex-end",
              gap: "6px",
              cursor: "pointer"
            }}
            onMouseEnter={() => setHoveredIdx(idx)}
            onMouseLeave={() => setHoveredIdx(null)}
          >
            <span style={{ fontSize: "0.7rem", fontWeight: "700", color: hoveredIdx === idx ? "#38bdf8" : "#94a3b8" }}>
              {val}
            </span>
            <div
              style={{
                width: "100%",
                maxWidth: "32px",
                height: `${Math.max(percentage, 6)}%`,
                backgroundColor: barColor,
                borderRadius: "6px 6px 0 0",
                transition: "all 0.25s ease",
                filter: hoveredIdx === idx ? `drop-shadow(0 0 6px ${barColor})` : "none",
                opacity: hoveredIdx !== null && hoveredIdx !== idx ? 0.6 : 1
              }}
            />
            <span style={{ fontSize: "0.68rem", color: "#cbd5e1", textAlign: "center", textOverflow: "ellipsis", overflow: "hidden", whiteSpace: "nowrap", width: "100%" }}>
              {item.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
