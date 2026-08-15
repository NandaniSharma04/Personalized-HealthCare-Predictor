import React from 'react';

export default function HealthSummaryCard({ predictionResult }) {
  if (!predictionResult) return null;

  const {
    predicted_disease,
    confidence,
    risk_level,
    description,
    top_candidates
  } = predictionResult;

  const getRiskBadge = (level) => {
    switch (level?.toLowerCase()) {
      case 'high':
        return <span className="risk-badge risk-high">High Risk</span>;
      case 'medium':
        return <span className="risk-badge risk-medium">Moderate Risk</span>;
      default:
        return <span className="risk-badge risk-low">Low Risk</span>;
    }
  };

  return (
    <div className="health-summary-card">
      <div className="summary-header">
        <div>
          <span className="summary-label">Primary Diagnostic Prediction</span>
          <h2 className="disease-title">{predicted_disease}</h2>
        </div>
        <div>{getRiskBadge(risk_level)}</div>
      </div>

      <div className="confidence-meter-container">
        <div className="confidence-label-row">
          <span>AI Prediction Confidence</span>
          <span className="confidence-value">{confidence}%</span>
        </div>
        <div className="confidence-bar-bg">
          <div
            className="confidence-bar-fill"
            style={{ width: `${Math.min(confidence, 100)}%` }}
          ></div>
        </div>
      </div>

      {description && (
        <div className="disease-description">
          <h4>Medical Description</h4>
          <p>{description}</p>
        </div>
      )}

      {top_candidates && top_candidates.length > 0 && (
        <div className="top-candidates-section">
          <h4>Differential Diagnosis Candidates</h4>
          <div className="candidates-list">
            {top_candidates.map((cand, idx) => (
              <div key={idx} className="candidate-row">
                <span className="cand-name">{cand.disease}</span>
                <span className="cand-score">{cand.confidence}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
