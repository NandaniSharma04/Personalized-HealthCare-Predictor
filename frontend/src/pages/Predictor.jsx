import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import SymptomSelector from '../components/SymptomSelector';
import HealthSummaryCard from '../components/HealthSummaryCard';
import RecommendationCard from '../components/RecommendationCard';
import { ALL_CLINICAL_SYMPTOMS } from '../constants/symptoms';

export default function Predictor() {
  const [allSymptoms, setAllSymptoms] = useState(ALL_CLINICAL_SYMPTOMS);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSymptoms();
  }, []);

  // Clear previous prediction result whenever selected symptoms change
  // Ensures old result is never presented as the prediction for new inputs
  useEffect(() => {
    setResult(null);
    setError('');
  }, [selectedSymptoms]);

  const fetchSymptoms = async () => {
    try {
      const res = await axios.get('/api/symptoms');
      if (res.data && res.data.symptoms && res.data.symptoms.length > 0) {
        setAllSymptoms(res.data.symptoms);
      }
    } catch (err) {
      setAllSymptoms(ALL_CLINICAL_SYMPTOMS);
    }
  };

  const handlePredict = async (e) => {
    if (e) e.preventDefault();
    if (selectedSymptoms.length === 0) {
      setError("Please select at least one symptom to run clinical evaluation.");
      return;
    }
    setError('');
    setLoading(true);

    try {
      const res = await axios.post('/api/predict', {
        symptoms: selectedSymptoms
      });
      if (res && res.data) {
        const payload = res.data.data || res.data;
        setResult(payload);
      }
    } catch (err) {
      console.error("Prediction error:", err);
      setError(err.response?.data?.error || err.response?.data?.detail || err.message || "Failed to generate prediction from ML service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container predictor-page">
      <div className="page-header text-center">
        <h1 className="page-title">Personalized Disease Predictor</h1>
        <p className="page-subtitle">
          Select symptoms below for real-time ML disease prediction and verified healthcare recommendations
        </p>
      </div>

      <div className="predictor-layout">
        <div className="predictor-selector-column">
          <SymptomSelector
            allSymptoms={allSymptoms}
            selectedSymptoms={selectedSymptoms}
            setSelectedSymptoms={setSelectedSymptoms}
          />
          {error && <div className="error-banner">{error}</div>}
          
          <button
            type="button"
            onClick={handlePredict}
            disabled={loading || selectedSymptoms.length === 0}
            className="btn-primary btn-block btn-lg mt-4"
          >
            {loading ? 'Analyzing Clinical Model...' : `Run Healthcare Prediction (${selectedSymptoms.length} Symptoms)`}
          </button>
        </div>

        <div className="predictor-results-column">
          {loading && (
            <div className="loading-spinner-box">
              <div className="spinner"></div>
              <p>Processing 230-feature vector with Gradient Boosted ML classifier...</p>
            </div>
          )}

          {!loading && result && (
            <div className="results-container">
              <HealthSummaryCard predictionResult={result} />
              <RecommendationCard predictionResult={result} />
            </div>
          )}

          {!loading && !result && (
            <div className="placeholder-card">
              <div className="placeholder-icon">🏥</div>
              <h3>Ready for Diagnosis</h3>
              <p>Select your present symptoms on the left panel and click "Run Healthcare Prediction".</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
