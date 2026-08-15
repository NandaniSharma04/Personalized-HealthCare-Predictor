import React, { useState, useEffect } from 'react';
import axios from '../api/axios';
import SymptomSelector from '../components/SymptomSelector';
import HealthSummaryCard from '../components/HealthSummaryCard';
import RecommendationCard from '../components/RecommendationCard';

export default function Predictor() {
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSymptoms();
  }, []);

  const fetchSymptoms = async () => {
    try {
      const res = await axios.get('/api/symptoms');
      if (res.data && res.data.symptoms) {
        setAllSymptoms(res.data.symptoms);
      }
    } catch (err) {
      console.error("Failed to load symptoms list:", err);
      // Fallback default sample symptoms list
      setAllSymptoms([
        "anxiety and nervousness", "depression", "shortness of breath", "sharp chest pain",
        "dizziness", "insomnia", "chest tightness", "headache", "fever", "cough",
        "nausea", "vomiting", "fatigue", "abdominal pain", "skin rash", "itching"
      ]);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    if (selectedSymptoms.length === 0) {
      setError("Please select at least one symptom to run clinical prediction.");
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);

    try {
      const res = await axios.post('/api/predict', {
        symptoms: selectedSymptoms
      });
      setResult(res.data);
    } catch (err) {
      console.error("Prediction error:", err);
      setError(err.response?.data?.detail || "Failed to generate prediction. Please try again.");
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
