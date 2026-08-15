import React from 'react';

export default function DriftChart({ driftScore, status }) {
  return (
    <div className="drift-chart-widget">
      <div className="drift-score-row">
        <span className="drift-label">KL Divergence Data Drift:</span>
        <span className="drift-value">{driftScore !== undefined ? driftScore : '0.042'}</span>
      </div>
      <div className={`status-good ${driftScore > 0.2 ? 'status-warning' : ''}`}>
        {status || '✓ Model Distribution Stable'}
      </div>
    </div>
  );
}
