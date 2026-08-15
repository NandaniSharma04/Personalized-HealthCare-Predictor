import React, { useState } from 'react';

/**
 * Interactive SVG Line / Area Chart Component
 * @param {Array<{ label: string, value: number }>} data
 * @param {string} title
 * @param {number} height
 */
export default function LineChart({ data = [], title = "Trajectory", height = 180, lineColor = "#06b6d4" }) {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  if (!data || data.length === 0) {
    return (
      <div className="flex-center p-6 text-center text-muted" style={{ minHeight: `${height}px`, flexDirection: "column" }}>
        <span style={{ fontSize: "0.78rem" }}>No longitudinal data logged yet</span>
      </div>
    );
  }

  const width = 450;
  const padding = 30;
  const graphWidth = width - padding * 2;
  const graphHeight = height - padding * 2;

  const values = data.map(d => Number(d.value) || 0);
  const maxVal = Math.max(...values, 100);
  const minVal = Math.min(...values, 0);
  const range = maxVal - minVal || 1;

  // Calculate points
  const points = data.map((item, idx) => {
    const x = padding + (idx / Math.max(data.length - 1, 1)) * graphWidth;
    const y = padding + graphHeight - ((Number(item.value) - minVal) / range) * graphHeight;
    return { x, y, ...item };
  });

  const pathD = points.reduce((acc, pt, idx) => {
    return idx === 0 ? `M ${pt.x} ${pt.y}` : `${acc} L ${pt.x} ${pt.y}`;
  }, '');

  const areaD = points.length > 0
    ? `${pathD} L ${points[points.length - 1].x} ${height - padding} L ${points[0].x} ${height - padding} Z`
    : '';

  return (
    <div className="line-chart-wrapper" style={{ width: "100%", overflowX: "auto" }}>
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} style={{ overflow: "visible" }}>
        <defs>
          <linearGradient id="lineAreaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={lineColor} stopOpacity="0.35" />
            <stop offset="100%" stopColor={lineColor} stopOpacity="0.0" />
          </linearGradient>
        </defs>

        {/* Gridlines */}
        <line x1={padding} y1={padding} x2={width - padding} y2={padding} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <line x1={padding} y1={padding + graphHeight / 2} x2={width - padding} y2={padding + graphHeight / 2} stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
        <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="rgba(255,255,255,0.12)" />

        {/* Shaded Area */}
        {areaD && <path d={areaD} fill="url(#lineAreaGrad)" />}

        {/* Line */}
        {pathD && (
          <path
            d={pathD}
            fill="none"
            stroke={lineColor}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )}

        {/* Dots */}
        {points.map((pt, idx) => (
          <g key={idx}>
            <circle
              cx={pt.x}
              cy={pt.y}
              r={hoveredPoint === idx ? 6 : 4}
              fill="#0b101e"
              stroke={lineColor}
              strokeWidth="2.5"
              style={{ cursor: "pointer", transition: "r 0.15s" }}
              onMouseEnter={() => setHoveredPoint(idx)}
              onMouseLeave={() => setHoveredPoint(null)}
            />
            {hoveredPoint === idx && (
              <g>
                <rect
                  x={pt.x - 30}
                  y={pt.y - 30}
                  width="60"
                  height="22"
                  rx="4"
                  fill="rgba(15, 23, 42, 0.95)"
                  stroke="rgba(255,255,255,0.2)"
                />
                <text
                  x={pt.x}
                  y={pt.y - 15}
                  textAnchor="middle"
                  fill="#ffffff"
                  fontSize="10"
                  fontWeight="bold"
                >
                  {pt.value}%
                </text>
              </g>
            )}
          </g>
        ))}

        {/* Bottom Labels */}
        {points.map((pt, idx) => (
          <text
            key={idx}
            x={pt.x}
            y={height - 10}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="9"
          >
            {pt.label}
          </text>
        ))}
      </svg>
    </div>
  );
}
