import React, { useState } from 'react';

/**
 * Interactive SVG Donut / Pie Chart Component
 * @param {Array<{ label: string, value: number, color: string }>} data
 * @param {string} title
 * @param {number} size
 */
export default function PieChart({ data = [], title = "Distribution", size = 220, innerRadiusRatio = 0.6 }) {
  const [hoveredIdx, setHoveredIdx] = useState(null);

  const total = data.reduce((sum, item) => sum + (Number(item.value) || 0), 0);

  if (total === 0 || data.length === 0) {
    return (
      <div className="flex-center p-6 text-center text-muted" style={{ minHeight: `${size}px`, flexDirection: "column" }}>
        <div style={{ width: "80px", height: "80px", borderRadius: "50%", border: "2px dashed rgba(255,255,255,0.15)", margin: "0 auto 10px" }} />
        <span style={{ fontSize: "0.78rem" }}>No distribution data recorded yet</span>
      </div>
    );
  }

  const radius = size / 2;
  const innerRadius = radius * innerRadiusRatio;
  const strokeWidth = radius - innerRadius;
  const center = radius;

  // Compute SVG arc slices
  let accumulatedAngle = 0;
  const slices = data.map((item, idx) => {
    const value = Number(item.value) || 0;
    const percentage = (value / total) * 100;
    const angle = (value / total) * 360;
    
    // Convert polar to cartesian coordinates
    const startAngle = accumulatedAngle;
    const endAngle = accumulatedAngle + angle;
    accumulatedAngle += angle;

    const startRad = (startAngle - 90) * (Math.PI / 180);
    const endRad = (endAngle - 90) * (Math.PI / 180);

    const x1 = center + (radius - strokeWidth / 2) * Math.cos(startRad);
    const y1 = center + (radius - strokeWidth / 2) * Math.sin(startRad);
    const x2 = center + (radius - strokeWidth / 2) * Math.cos(endRad);
    const y2 = center + (radius - strokeWidth / 2) * Math.sin(endRad);

    const largeArcFlag = angle > 180 ? 1 : 0;
    const pathData = `M ${x1} ${y1} A ${radius - strokeWidth / 2} ${radius - strokeWidth / 2} 0 ${largeArcFlag} 1 ${x2} ${y2}`;

    return {
      ...item,
      percentage: percentage.toFixed(1),
      pathData,
      idx
    };
  });

  const activeItem = hoveredIdx !== null ? slices[hoveredIdx] : null;

  return (
    <div className="pie-chart-container" style={{ display: "flex", alignItems: "center", gap: "20px", flexWrap: "wrap", justifyContent: "center" }}>
      <div style={{ position: "relative", width: `${size}px`, height: `${size}px` }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {slices.map((slice) => (
            <path
              key={slice.idx}
              d={slice.pathData}
              fill="none"
              stroke={slice.color || "#3b82f6"}
              strokeWidth={hoveredIdx === slice.idx ? strokeWidth + 4 : strokeWidth}
              strokeLinecap="butt"
              style={{
                cursor: "pointer",
                transition: "stroke-width 0.2s ease, filter 0.2s ease",
                filter: hoveredIdx === slice.idx ? `drop-shadow(0 0 8px ${slice.color})` : "none",
                opacity: hoveredIdx !== null && hoveredIdx !== slice.idx ? 0.6 : 1
              }}
              onMouseEnter={() => setHoveredIdx(slice.idx)}
              onMouseLeave={() => setHoveredIdx(null)}
            />
          ))}
        </svg>

        {/* Center Donut Label */}
        <div
          style={{
            position: "absolute",
            inset: `${strokeWidth}px`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            borderRadius: "50%",
            pointerEvents: "none",
            textAlign: "center"
          }}
        >
          <span style={{ fontSize: "1.1rem", fontWeight: "700", color: "#ffffff" }}>
            {activeItem ? `${activeItem.percentage}%` : total}
          </span>
          <span style={{ fontSize: "0.68rem", color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.03em" }}>
            {activeItem ? activeItem.label : title}
          </span>
        </div>
      </div>

      {/* Legend */}
      <div style={{ display: "flex", flexDirection: "column", gap: "8px", minWidth: "130px" }}>
        {slices.map((slice) => (
          <div
            key={slice.idx}
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: "8px",
              fontSize: "0.75rem",
              padding: "4px 8px",
              borderRadius: "6px",
              background: hoveredIdx === slice.idx ? "rgba(255,255,255,0.08)" : "transparent",
              cursor: "pointer",
              transition: "background 0.15s"
            }}
            onMouseEnter={() => setHoveredIdx(slice.idx)}
            onMouseLeave={() => setHoveredIdx(null)}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span
                style={{
                  width: "10px",
                  height: "10px",
                  borderRadius: "50%",
                  backgroundColor: slice.color || "#3b82f6"
                }}
              />
              <span style={{ color: "#cbd5e1" }}>{slice.label}</span>
            </div>
            <span style={{ fontWeight: "600", color: "#94a3b8" }}>{slice.value} ({slice.percentage}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
