import React from 'react';
import axios from '../api/axios';

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

      {/* Patient Prediction Feedback Section */}
      <PredictionFeedbackSection disease={predicted_disease} />
    </div>
  );
}

function PredictionFeedbackSection({ disease }) {
  const [submitted, setSubmitted] = React.useState(false);
  const [rating, setRating] = React.useState(null); // 'accurate' | 'inaccurate'
  const [comment, setComment] = React.useState('');

  const handleFeedbackSubmit = (e) => {
    e.preventDefault();
    if (!rating) return;

    const newFeedback = {
      id: Date.now(),
      disease: disease || "General Prediction",
      isAccurate: rating === 'accurate',
      comment: comment.trim(),
      date: new Date().toISOString()
    };

    const existingLogs = JSON.parse(localStorage.getItem('patient_prediction_feedback') || '[]');
    existingLogs.push(newFeedback);
    localStorage.setItem('patient_prediction_feedback', JSON.stringify(existingLogs));

    // Optional POST to backend if running
    axios.post('/api/feedback', newFeedback).catch(() => {});

    setSubmitted(true);
  };

  if (submitted) {
    return (
      <div style={{
        marginTop: '20px',
        padding: '16px',
        borderRadius: '12px',
        background: 'rgba(34, 197, 94, 0.12)',
        border: '1px solid rgba(34, 197, 94, 0.3)',
        color: '#4ade80',
        textAlign: 'center',
        fontSize: '0.85rem'
      }}>
        ✨ <strong>Thank you for your feedback!</strong> Your review has been recorded to compute live model accuracy on the Admin Dashboard.
      </div>
    );
  }

  return (
    <div style={{
      marginTop: '20px',
      padding: '18px',
      borderRadius: '14px',
      background: 'rgba(15, 23, 42, 0.6)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      color: '#f8fafc'
    }}>
      <h4 style={{ margin: '0 0 6px 0', fontSize: '0.92rem', color: '#60a5fa', display: 'flex', alignItems: 'center', gap: '6px' }}>
        💬 Patient Feedback: Was this prediction accurate?
      </h4>
      <p style={{ margin: '0 0 12px 0', fontSize: '0.78rem', color: '#94a3b8' }}>
        Help us continuously improve model accuracy by rating the diagnostic result.
      </p>

      <form onSubmit={handleFeedbackSubmit}>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '12px' }}>
          <button
            type="button"
            onClick={() => setRating('accurate')}
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '8px',
              border: rating === 'accurate' ? '2px solid #22c55e' : '1px solid rgba(255,255,255,0.15)',
              background: rating === 'accurate' ? 'rgba(34, 197, 94, 0.25)' : 'rgba(30, 41, 59, 0.6)',
              color: rating === 'accurate' ? '#86efac' : '#cbd5e1',
              fontWeight: '600',
              fontSize: '0.82rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            👍 Accurate Prediction
          </button>

          <button
            type="button"
            onClick={() => setRating('inaccurate')}
            style={{
              flex: 1,
              padding: '10px',
              borderRadius: '8px',
              border: rating === 'inaccurate' ? '2px solid #ef4444' : '1px solid rgba(255,255,255,0.15)',
              background: rating === 'inaccurate' ? 'rgba(239, 68, 68, 0.25)' : 'rgba(30, 41, 59, 0.6)',
              color: rating === 'inaccurate' ? '#fca5a5' : '#cbd5e1',
              fontWeight: '600',
              fontSize: '0.82rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px'
            }}
          >
            👎 Inaccurate Prediction
          </button>
        </div>

        {rating && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <input
              type="text"
              placeholder="Optional: Add clinical notes or comment..."
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              style={{
                width: '100%',
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid rgba(255,255,255,0.15)',
                background: 'rgba(15, 23, 42, 0.8)',
                color: '#fff',
                fontSize: '0.8rem',
                boxSizing: 'border-box'
              }}
            />
            <button
              type="submit"
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                background: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
                color: '#fff',
                fontWeight: '600',
                fontSize: '0.8rem',
                cursor: 'pointer',
                alignSelf: 'flex-end'
              }}
            >
              Submit Feedback
            </button>
          </div>
        )}
      </form>
    </div>
  );
}

