import React from 'react';

export default function ConfidenceChart({ confidence }) {
  const score = Math.min(Math.max(confidence || 0, 0), 100);
  return (
    <div className="confidence-chart">
      <div className="confidence-label-row">
        <span>Model Confidence</span>
        <span className="confidence-value">{score}%</span>
      </div>
      <div className="confidence-bar-bg">
        <div className="confidence-bar-fill" style={{ width: `${score}%` }}></div>
      </div>
    </div>
  );
}
