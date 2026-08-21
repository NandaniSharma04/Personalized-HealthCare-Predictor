import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from '../api/axios';
import { useAuth } from '../context/AuthContext';
import SymptomSelector from '../components/SymptomSelector';
import HealthSummaryCard from '../components/HealthSummaryCard';
import RecommendationCard from '../components/RecommendationCard';
import { ALL_CLINICAL_SYMPTOMS } from '../constants/symptoms';
import { LogIn, Lock, Sparkles, AlertCircle } from 'lucide-react';

export default function Predictor() {
  const { user } = useAuth();
  const [allSymptoms, setAllSymptoms] = useState(ALL_CLINICAL_SYMPTOMS);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSymptoms();
  }, []);

  // Clear result whenever symptoms change
  useEffect(() => {
    setResult(null);
    setError('');
  }, [selectedSymptoms]);

  const fetchSymptoms = async () => {
    try {
      const res = await axios.get('/api/symptoms');
      if (res.data?.symptoms?.length > 0) {
        setAllSymptoms(res.data.symptoms);
      }
    } catch {
      setAllSymptoms(ALL_CLINICAL_SYMPTOMS);
    }
  };

  const handlePredict = async (e) => {
    if (e) e.preventDefault();

    // Guard: must be logged in
    if (!user) {
      setError("If you log in, only then disease prediction happens. Please sign in to proceed.");
      return;
    }

    if (selectedSymptoms.length === 0) {
      setError("Please select at least one symptom to evaluate.");
      return;
    }
    setError('');
    setResult(null);
    setLoading(true);

    try {
      const res = await axios.post('/api/predict', { symptoms: selectedSymptoms });
      const payload = res.data?.data || res.data;
      if (payload?.predicted_disease) {
        setResult(payload);
      } else {
        setError("Prediction returned no result. Please try different symptoms.");
      }
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.message;
      if (err.response?.status === 401) {
        setError("Authentication required: If you log in, only then disease prediction happens.");
      } else if (msg) {
        setError(msg);
      } else {
        setError("Could not reach the prediction server. Please make sure the backend is running.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container predictor-page">
      <div className="page-header text-center">
        <h1 className="page-title">AI Disease Predictor</h1>
        <p className="page-subtitle">
          Select clinical symptoms for AI diagnosis and personalized recommendations
        </p>
      </div>

      {/* Prominent Banner when user is NOT logged in */}
      {!user && (
        <div style={{
          maxWidth: "1100px",
          margin: "0 auto 20px",
          padding: "14px 20px",
          background: "linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(59, 130, 246, 0.12))",
          border: "1px solid rgba(239, 68, 68, 0.35)",
          borderRadius: "14px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "12px",
          boxShadow: "0 8px 24px rgba(0,0,0,0.3)"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <AlertCircle size={22} style={{ color: "#f87171", flexShrink: 0 }} />
            <div>
              <div style={{ color: "#ffffff", fontWeight: "700", fontSize: "0.92rem" }}>
                Authentication Required for Disease Prediction
              </div>
              <div style={{ color: "#cbd5e1", fontSize: "0.82rem" }}>
                If you log in, only then disease prediction happens and results are generated.
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: "10px" }}>
            <Link
              to="/login"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 18px",
                background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
                color: "#ffffff",
                borderRadius: "8px",
                fontSize: "0.82rem",
                fontWeight: "600",
                textDecoration: "none",
                boxShadow: "0 4px 12px rgba(37, 99, 235, 0.4)"
              }}
            >
              <LogIn size={14} /> Log In to Predict
            </Link>
            <Link
              to="/signup"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 18px",
                background: "rgba(255, 255, 255, 0.08)",
                border: "1px solid rgba(255, 255, 255, 0.18)",
                color: "#e2e8f0",
                borderRadius: "8px",
                fontSize: "0.82rem",
                fontWeight: "600",
                textDecoration: "none"
              }}
            >
              Sign Up
            </Link>
          </div>
        </div>
      )}

      <div className="predictor-layout">
        {/* Left: Symptom Selector */}
        <div className="predictor-selector-column">
          <SymptomSelector
            allSymptoms={allSymptoms}
            selectedSymptoms={selectedSymptoms}
            setSelectedSymptoms={setSelectedSymptoms}
          />

          {error && (
            <div className="error-banner" style={{ marginTop: "12px" }}>
              ⚠️ {error}
            </div>
          )}

          {/* Predict button — only active when logged in */}
          {user ? (
            <button
              type="button"
              onClick={handlePredict}
              disabled={loading || selectedSymptoms.length === 0}
              className="btn-primary btn-block btn-lg mt-4"
            >
              {loading
                ? 'Analyzing clinical model...'
                : selectedSymptoms.length === 0
                  ? 'Select symptoms to predict'
                  : `Run Healthcare Prediction (${selectedSymptoms.length} symptom${selectedSymptoms.length > 1 ? 's' : ''})`
              }
            </button>
          ) : (
            /* Not logged in — clear notice */
            <div style={{
              marginTop: "16px",
              padding: "18px 20px",
              background: "rgba(15, 23, 42, 0.85)",
              border: "1px solid rgba(59, 130, 246, 0.35)",
              borderRadius: "14px",
              textAlign: "center",
              boxShadow: "0 10px 25px rgba(0,0,0,0.5)"
            }}>
              <Lock size={26} style={{ color: "#60a5fa", marginBottom: "8px" }} />
              <h3 style={{ color: "#ffffff", fontSize: "1rem", margin: "0 0 6px", fontWeight: "700" }}>
                Login Required
              </h3>
              <p style={{ color: "#cbd5e1", fontSize: "0.84rem", margin: "0 0 14px", lineHeight: "1.4" }}>
                If you log in, only then disease prediction happens. Please sign in to analyze your selected symptoms.
              </p>
              <div style={{ display: "flex", gap: "10px", justifyContent: "center", flexWrap: "wrap" }}>
                <Link
                  to="/login"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "9px 22px",
                    background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
                    color: "#fff",
                    borderRadius: "8px",
                    fontSize: "0.84rem",
                    fontWeight: "600",
                    textDecoration: "none",
                    boxShadow: "0 4px 14px rgba(37,99,235,0.4)",
                  }}
                >
                  <LogIn size={15} /> Log In Now
                </Link>
                <Link
                  to="/signup"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "9px 20px",
                    background: "rgba(255,255,255,0.08)",
                    border: "1px solid rgba(255,255,255,0.18)",
                    color: "#e2e8f0",
                    borderRadius: "8px",
                    fontSize: "0.84rem",
                    fontWeight: "600",
                    textDecoration: "none",
                  }}
                >
                  Create Account
                </Link>
              </div>
            </div>
          )}
        </div>

        {/* Right: Results panel */}
        <div className="predictor-results-column">
          {loading && (
            <div className="loading-spinner-box">
              <div className="spinner"></div>
              <p>Running ML classifier on {selectedSymptoms.length} symptom{selectedSymptoms.length > 1 ? 's' : ''}...</p>
            </div>
          )}

          {!loading && result && (
            <div className="results-container">
              <HealthSummaryCard predictionResult={result} />
              <RecommendationCard predictionResult={result} />
            </div>
          )}

          {!loading && !result && !user && (
            <div className="placeholder-card" style={{ padding: "40px 24px", textAlign: "center" }}>
              <div className="placeholder-icon" style={{ fontSize: "2.8rem" }}>🔒</div>
              <h3 style={{ color: "#ffffff", marginTop: "12px" }}>Sign In to View Disease Prediction</h3>
              <p style={{ color: "#94a3b8", fontSize: "0.88rem", maxWidth: "380px", margin: "8px auto 16px" }}>
                If you log in, only then disease prediction happens. Your diagnostic results and health care protocols will appear right here.
              </p>
              <Link
                to="/login"
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "6px",
                  padding: "9px 20px",
                  background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
                  color: "#fff",
                  borderRadius: "8px",
                  fontSize: "0.84rem",
                  fontWeight: "600",
                  textDecoration: "none"
                }}
              >
                <LogIn size={15} /> Log In to Run Prediction
              </Link>
            </div>
          )}

          {!loading && !result && user && (
            <div className="placeholder-card">
              <div className="placeholder-icon">🏥</div>
              <h3>Ready for AI Evaluation</h3>
              <p>Select your symptoms on the left panel and click <strong>"Run Healthcare Prediction"</strong> to get your disease prediction.</p>
              <p style={{ fontSize: "0.78rem", color: "#64748b", marginTop: "8px" }}>
                Trained on 230 symptoms across 100+ disease categories.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
