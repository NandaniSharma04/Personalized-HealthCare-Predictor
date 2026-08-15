import React, { useState } from 'react';

export default function RecommendationCard({ predictionResult }) {
  const [activeTab, setActiveTab] = useState('medications');

  if (!predictionResult) return null;

  const { medicines, advice, diet, workout } = predictionResult;

  return (
    <div className="recommendation-card">
      <div className="recommendation-header">
        <h3>Personalized Health Care & Treatment Plan</h3>
        <p>Verified recommendations from medical datasets for this condition</p>
      </div>

      <div className="recommendation-tabs">
        <button
          type="button"
          className={`rec-tab ${activeTab === 'medications' ? 'rec-tab-active' : ''}`}
          onClick={() => setActiveTab('medications')}
        >
          💊 Medications ({medicines?.length || 0})
        </button>
        <button
          type="button"
          className={`rec-tab ${activeTab === 'advice' ? 'rec-tab-active' : ''}`}
          onClick={() => setActiveTab('advice')}
        >
          🛡️ Precautions ({advice?.length || 0})
        </button>
        <button
          type="button"
          className={`rec-tab ${activeTab === 'diet' ? 'rec-tab-active' : ''}`}
          onClick={() => setActiveTab('diet')}
        >
          🥗 Dietary Plan ({diet?.length || 0})
        </button>
        <button
          type="button"
          className={`rec-tab ${activeTab === 'workout' ? 'rec-tab-active' : ''}`}
          onClick={() => setActiveTab('workout')}
        >
          🏃 Workout & Exercise ({workout?.length || 0})
        </button>
      </div>

      <div className="rec-tab-content">
        {activeTab === 'medications' && (
          <div className="rec-list-container">
            <h4>Prescribed Medications & Treatments</h4>
            {medicines && medicines.length > 0 ? (
              <ul className="rec-list">
                {medicines.map((med, idx) => (
                  <li key={idx} className="rec-item med-item">
                    <span className="item-icon">💊</span>
                    <span className="item-text">{med}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">Consult a physician for tailored clinical prescription details.</p>
            )}
          </div>
        )}

        {activeTab === 'advice' && (
          <div className="rec-list-container">
            <h4>Important Safety Precautions & Actions</h4>
            {advice && advice.length > 0 ? (
              <ul className="rec-list">
                {advice.map((item, idx) => (
                  <li key={idx} className="rec-item advice-item">
                    <span className="item-icon">✓</span>
                    <span className="item-text">{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">Maintain normal hydration and consult a physician if symptoms persist.</p>
            )}
          </div>
        )}

        {activeTab === 'diet' && (
          <div className="rec-list-container">
            <h4>Nutritional Guidelines & Diet Plan</h4>
            {diet && diet.length > 0 ? (
              <ul className="rec-list">
                {diet.map((item, idx) => (
                  <li key={idx} className="rec-item diet-item">
                    <span className="item-icon">🥗</span>
                    <span className="item-text">{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">Balanced high-fiber, low-sodium diet with optimal hydration recommended.</p>
            )}
          </div>
        )}

        {activeTab === 'workout' && (
          <div className="rec-list-container">
            <h4>Recommended Physical Activities & Workouts</h4>
            {workout && workout.length > 0 ? (
              <ul className="rec-list">
                {workout.map((item, idx) => (
                  <li key={idx} className="rec-item workout-item">
                    <span className="item-icon">🏃</span>
                    <span className="item-text">{item}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="no-data">Light walking and mild stretching exercises as tolerated.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
