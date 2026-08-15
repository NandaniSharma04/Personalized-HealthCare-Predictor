import React from 'react';

export default function PrevalenceChart({ prevalenceData }) {
  if (!prevalenceData) return null;

  const entries = Object.entries(prevalenceData).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((acc, curr) => acc + curr[1], 0) || 1;

  return (
    <div className="prevalence-chart">
      <div className="bars-container">
        {entries.slice(0, 7).map(([disease, count]) => {
          const pct = Math.round((count / total) * 100);
          return (
            <div key={disease} className="bar-row">
              <div className="bar-label-col">
                <span className="bar-disease-name">{disease}</span>
                <span className="bar-count">{count} cases ({pct}%)</span>
              </div>
              <div className="bar-bg">
                <div className="bar-fill" style={{ width: `${Math.max(pct, 10)}%` }}></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
