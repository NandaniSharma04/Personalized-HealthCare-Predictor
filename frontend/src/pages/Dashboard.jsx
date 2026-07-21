import { useEffect, useState } from "react";
import api from "../api/axios";

export default function Dashboard() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/history")
      .then((res) => setHistory(res.data.history))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="page-loading">Loading your history...</div>;

  return (
    <div className="dashboard-page">
      <h1>Your prediction history</h1>
      {history.length === 0 ? (
        <p>No predictions yet — try the symptom checker on the home page.</p>
      ) : (
        <div className="history-list">
          {history.map((h) => (
            <div className="history-card glass" key={h.id}>
              <h3>{h.predicted_disease}</h3>
              <p>Confidence: {h.confidence}% · Risk: {h.risk_level}</p>
              <p className="history-date">{new Date(h.created_at).toLocaleString()}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
