import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from '../../api/axios';
import SymptomSelector from '../../components/SymptomSelector';
import HealthSummaryCard from '../../components/HealthSummaryCard';
import RecommendationCard from '../../components/RecommendationCard';
import PieChart from '../../charts/PieChart';
import BarChart from '../../charts/BarChart';
import LineChart from '../../charts/LineChart';
import { formatDate, getRiskColorClass } from '../../utils/formatters';
import { useAuth } from '../../context/AuthContext';
import {
  LayoutDashboard, HeartPulse, History, Sparkles, LineChart as LineChartIcon,
  Activity, Bookmark, Bell, User, Settings, LogOut,
  ShieldCheck, AlertTriangle, CheckCircle2, ChevronRight,
  Search, Filter, Calendar, Star, Info, RefreshCw,
  Clock, Pill, Shield, Utensils, Dumbbell, ArrowUpRight,
  TrendingUp, FileText, Check, ChevronDown, ChevronUp, UserCheck,
  PieChart as PieChartIcon, BarChart3
} from 'lucide-react';

export default function UserDashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  // Active Navigation Tab
  const [activeTab, setActiveTab] = useState('dashboard'); // 'dashboard', 'prediction', 'history', 'recommendations', 'insights', 'activity', 'saved', 'notifications', 'profile', 'settings'
  
  // API Data States
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Symptom Checker State in Predictor Tab
  const [allSymptoms, setAllSymptoms] = useState(ALL_CLINICAL_SYMPTOMS);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);
  const [predError, setPredError] = useState('');

  // Save / Feedback Notifications
  const [actionMsg, setActionMsg] = useState('');

  // Profile Form States
  const [profileForm, setProfileForm] = useState({ name: '', phone: '', address: '', bio: '' });
  const [healthForm, setHealthForm] = useState({ age: '', gender: 'Male', allergies: '', existing_conditions: '', current_medications: '' });
  const [profileMsg, setProfileMsg] = useState('');

  // Settings State
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '' });
  const [pwMsg, setPwMsg] = useState('');

  // History Search & Filter State
  const [historySearch, setHistorySearch] = useState('');
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);

  // Recommendations Category Filter & Expanded Explanations
  const [selectedRecCategory, setSelectedRecCategory] = useState('all');
  const [expandedReasons, setExpandedReasons] = useState({});

  useEffect(() => {
    fetchDashboardData();
    fetchSymptomsList();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get('/api/user/dashboard');
      if (res.data && res.data.success) {
        setDashboardData(res.data);
        if (res.data.user) {
          setProfileForm(prev => ({
            ...prev,
            name: res.data.user.name || '',
          }));
        }
      } else {
        setError(res.data?.error || "Failed to load dashboard data.");
      }
    } catch (err) {
      if (err.response?.status === 401) {
        navigate('/login');
      } else {
        setError(err.response?.data?.error || "Network error while connecting to backend service.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchSymptomsList = async () => {
    try {
      const res = await axios.get('/api/symptoms');
      if (res.data && res.data.symptoms) {
        setAllSymptoms(res.data.symptoms);
      }
    } catch (err) {
      console.warn("Could not load symptoms catalog:", err);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Personalized Greeting based on local time
  const greetingText = useMemo(() => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good Morning';
    if (hour < 18) return 'Good Afternoon';
    return 'Good Evening';
  }, []);

  // Handle Symptom Prediction
  const handleRunPrediction = async () => {
    if (selectedSymptoms.length === 0) {
      setPredError("Please select at least one symptom to run clinical evaluation.");
      return;
    }
    setPredError('');
    setPredicting(true);
    try {
      const res = await axios.post('/api/predict', { symptoms: selectedSymptoms });
      if (res.data && res.data.success) {
        setPrediction(res.data);
        fetchDashboardData();
      } else {
        setPredError(res.data?.error || "Prediction analysis failed.");
      }
    } catch (err) {
      setPredError(err.response?.data?.error || "Prediction request failed. Please check network.");
    } finally {
      setPredicting(false);
    }
  };

  // Save Recommendation
  const handleSaveRecommendation = async (rec) => {
    try {
      const res = await axios.post('/api/recommendations/save', {
        recommendation_id: rec.id || 1,
        title: rec.recommendation || rec.title || "Personalized Healthcare Plan",
        notes: `Category: ${rec.category || 'General'} | Source: ${rec.source || 'Medical Knowledge Base'}`
      });
      if (res.data && res.data.success) {
        setActionMsg(`Saved "${rec.recommendation || 'Recommendation'}" to your private health profile.`);
        setTimeout(() => setActionMsg(''), 4000);
        fetchDashboardData();
      }
    } catch (err) {
      setActionMsg("Could not save recommendation at this time.");
      setTimeout(() => setActionMsg(''), 4000);
    }
  };

  // Submit Feedback Rating
  const handleFeedback = async (recId, rating) => {
    try {
      await axios.post('/api/recommendations/feedback', {
        recommendation_id: recId || 1,
        rating: rating,
        feedback_text: `User rating: ${rating} stars`
      });
      setActionMsg(`Thank you! Your ${rating}-star feedback updates AI care precision.`);
      setTimeout(() => setActionMsg(''), 4000);
      fetchDashboardData();
    } catch (err) {
      console.warn("Feedback submission error:", err);
    }
  };

  // Mark Notification Read
  const handleMarkNotificationRead = async (noteId) => {
    try {
      await axios.put(`/api/user/notifications/${noteId}/read`);
      fetchDashboardData();
    } catch (err) {
      console.warn("Notification update error:", err);
    }
  };

  // Toggle expandable explanation
  const toggleExplanation = (id) => {
    setExpandedReasons(prev => ({ ...prev, [id]: !prev[id] }));
  };

  // ========================================================
  // REAL VISUALIZATION DATA GENERATORS (Zero Fabricated Data)
  // ========================================================

  // 1. Recommendation Category Breakdown (Pie / Donut Chart)
  const recCategoryData = useMemo(() => {
    const recs = dashboardData?.top_recommendations || [];
    if (recs.length === 0) return [];
    
    const counts = { medicine: 0, precaution: 0, diet: 0, workout: 0 };
    recs.forEach(r => {
      const cat = (r.category || 'medicine').toLowerCase();
      if (counts[cat] !== undefined) {
        counts[cat] += 1;
      } else {
        counts.medicine = (counts.medicine || 0) + 1;
      }
    });

    return [
      { label: 'Medications', value: counts.medicine, color: '#3b82f6' },
      { label: 'Precautions', value: counts.precaution, color: '#10b981' },
      { label: 'Dietary', value: counts.diet, color: '#f59e0b' },
      { label: 'Activity/Workout', value: counts.workout, color: '#a855f7' },
    ].filter(item => item.value > 0);
  }, [dashboardData]);

  // 2. Diagnostic Likelihood Progression (Line Chart)
  const confidenceTrendData = useMemo(() => {
    const list = dashboardData?.prediction_history || [];
    if (list.length === 0) return [];

    return list.slice(0, 7).reverse().map((item, idx) => {
      const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : `#${idx+1}`;
      return {
        label: dateStr,
        value: Math.round(Number(item.confidence) || 0),
        condition: item.predicted_disease
      };
    });
  }, [dashboardData]);

  // 3. Risk Stratification Breakdown (Pie Chart)
  const riskBreakdownData = useMemo(() => {
    const list = dashboardData?.prediction_history || [];
    if (list.length === 0) return [];

    const counts = { high: 0, medium: 0, low: 0 };
    list.forEach(p => {
      const r = (p.risk_level || 'low').toLowerCase();
      if (counts[r] !== undefined) counts[r] += 1;
      else counts.low += 1;
    });

    return [
      { label: 'High Risk', value: counts.high, color: '#ef4444' },
      { label: 'Medium Risk', value: counts.medium, color: '#f59e0b' },
      { label: 'Low Risk', value: counts.low, color: '#10b981' },
    ].filter(item => item.value > 0);
  }, [dashboardData]);

  // 4. Most Frequent Symptoms Analyzed (Bar Chart)
  const symptomFrequencyData = useMemo(() => {
    const list = dashboardData?.prediction_history || [];
    if (list.length === 0) return [];

    const freqMap = {};
    list.forEach(p => {
      (p.symptoms_input || []).forEach(s => {
        const cleaned = s.trim();
        freqMap[cleaned] = (freqMap[cleaned] || 0) + 1;
      });
    });

    return Object.entries(freqMap)
      .map(([label, value]) => ({ label, value }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 5);
  }, [dashboardData]);

  // 5. Activity by Type (Bar Chart)
  const activityTypeData = useMemo(() => {
    const acts = dashboardData?.recent_activity || [];
    if (acts.length === 0) return [];

    const counts = {};
    acts.forEach(a => {
      const t = a.type || 'GENERAL';
      counts[t] = (counts[t] || 0) + 1;
    });

    const colorPalette = {
      PREDICTION: '#3b82f6',
      LOGIN: '#10b981',
      PROFILE_UPDATE: '#f59e0b',
      FEEDBACK: '#a855f7',
      SAVE_RECOMMENDATION: '#ec4899',
      VIEW_PREDICTION: '#06b6d4'
    };

    return Object.entries(counts).map(([label, value]) => ({
      label: label.replace(/_/g, ' '),
      value,
      color: colorPalette[label] || '#64748b'
    }));
  }, [dashboardData]);

  // Filtered Predictions History
  const filteredHistory = useMemo(() => {
    const list = dashboardData?.prediction_history || [];
    if (!historySearch.trim()) return list;
    const q = historySearch.toLowerCase();
    return list.filter(item => 
      (item.predicted_disease || '').toLowerCase().includes(q) ||
      (item.symptoms_input || []).some(s => s.toLowerCase().includes(q))
    );
  }, [dashboardData, historySearch]);

  // Filtered Recommendations
  const filteredRecommendations = useMemo(() => {
    const list = dashboardData?.top_recommendations || [];
    if (selectedRecCategory === 'all') return list;
    return list.filter(r => (r.category || '').toLowerCase() === selectedRecCategory.toLowerCase());
  }, [dashboardData, selectedRecCategory]);

  if (loading) {
    return (
      <div className="page-loading flex-center" style={{ minHeight: "75vh", flexDirection: "column" }}>
        <RefreshCw size={36} className="spin accent-text" />
        <p style={{ marginTop: "16px", color: "#94a3b8", fontWeight: "500" }}>
          Loading your personalized healthcare insights...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-container flex-center" style={{ minHeight: "65vh", flexDirection: "column" }}>
        <div className="card glass p-8 text-center max-w-500">
          <AlertTriangle size={48} color="#f59e0b" style={{ margin: "0 auto 16px" }} />
          <h2 style={{ fontSize: "1.3rem", fontWeight: "700", marginBottom: "8px" }}>Dashboard Connection Notice</h2>
          <p style={{ color: "#94a3b8", fontSize: "0.88rem", marginBottom: "20px" }}>{error}</p>
          <div style={{ display: "flex", gap: "10px", justifyContent: "center" }}>
            <button onClick={fetchDashboardData} className="btn-primary text-xs px-4 py-2">
              <RefreshCw size={14} className="inline mr-1" /> Retry Loading
            </button>
            <button onClick={() => navigate('/login')} className="btn-outline text-xs px-4 py-2">
              Sign In Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const kpis = dashboardData?.kpi_stats || {};
  const recentPred = dashboardData?.recent_prediction;
  const profileComp = dashboardData?.profile_completion || 40;
  const unreadCount = dashboardData?.unread_notifications_count || 0;
  const insights = dashboardData?.health_insights || {};

  return (
    <div className="user-dashboard-layout">
      {/* ========================================================
          SIDEBAR NAVIGATION (11 Items)
      ======================================================== */}
      <aside className="user-sidebar glass">
        <div className="sidebar-brand p-4 flex-center-y gap-2 border-b border-glass">
          <HeartPulse size={22} className="accent-text" />
          <span style={{ fontWeight: "700", fontSize: "1.05rem", letterSpacing: "0.02em" }}>HealthAI Portal</span>
        </div>

        <nav className="sidebar-nav p-3 flex-column gap-1">
          <button
            className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={16} /> Dashboard
          </button>

          <button
            className={`nav-item ${activeTab === 'prediction' ? 'active' : ''}`}
            onClick={() => setActiveTab('prediction')}
          >
            <HeartPulse size={16} /> AI Health Prediction
          </button>

          <button
            className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <History size={16} /> My Predictions
          </button>

          <button
            className={`nav-item ${activeTab === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveTab('recommendations')}
          >
            <Sparkles size={16} /> Personalized Care
          </button>

          <button
            className={`nav-item ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <LineChartIcon size={16} /> Health Insights
          </button>

          <button
            className={`nav-item ${activeTab === 'activity' ? 'active' : ''}`}
            onClick={() => setActiveTab('activity')}
          >
            <Activity size={16} /> My Activity
          </button>

          <button
            className={`nav-item ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            <Bookmark size={16} /> Saved Plans
          </button>

          <button
            className={`nav-item ${activeTab === 'notifications' ? 'active' : ''}`}
            onClick={() => setActiveTab('notifications')}
          >
            <Bell size={16} /> Notifications
            {unreadCount > 0 && <span className="nav-badge">{unreadCount}</span>}
          </button>

          <div style={{ height: "1px", background: "rgba(255,255,255,0.08)", margin: "8px 0" }} />

          <button
            className={`nav-item ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            <User size={16} /> My Profile
          </button>

          <button
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => setActiveTab('settings')}
          >
            <Settings size={16} /> Settings
          </button>

          <button
            className="nav-item text-red"
            onClick={handleLogout}
            style={{ marginTop: "12px", color: "#f87171" }}
          >
            <LogOut size={16} /> Logout
          </button>
        </nav>
      </aside>

      {/* ========================================================
          MAIN CONTENT VIEWPORT
      ======================================================== */}
      <main className="user-main-content">
        {/* Toast Action Feedback */}
        {actionMsg && (
          <div className="toast-banner glass flex-between p-3 mb-4 rounded-lg">
            <span className="flex-center-y gap-2 text-xs text-blue">
              <CheckCircle2 size={16} /> {actionMsg}
            </span>
            <button className="border-none bg-none pointer text-muted" onClick={() => setActionMsg('')}>✕</button>
          </div>
        )}

        {/* ========================================================
            TOP DASHBOARD HEADER
        ======================================================== */}
        <header className="dashboard-top-header glass p-4 rounded-xl mb-6 flex-between flex-wrap gap-4">
          <div>
            <h1 style={{ fontSize: "1.45rem", fontWeight: "700", margin: 0, color: "#ffffff" }}>
              {greetingText}, {dashboardData?.user?.name || user?.name || 'Patient'}
            </h1>
            <p style={{ color: "#94a3b8", fontSize: "0.82rem", margin: "3px 0 0" }}>
              Your personalized healthcare insights are ready.
            </p>
          </div>

          <div className="flex-center-y gap-3">
            {/* Notifications Bell */}
            <button
              className="icon-btn-glass relative"
              onClick={() => setActiveTab('notifications')}
              title="Notifications"
            >
              <Bell size={18} />
              {unreadCount > 0 && <span className="notification-dot">{unreadCount}</span>}
            </button>

            {/* Profile Avatar Pill */}
            <button
              className="user-profile-badge glass-panel-sm flex-center-y gap-2 p-1 pl-2 pr-3 rounded-full pointer"
              onClick={() => setActiveTab('profile')}
            >
              <div className="avatar-circle">
                {(dashboardData?.user?.name || user?.name || 'U').charAt(0).toUpperCase()}
              </div>
              <span className="text-xs font-semibold">{dashboardData?.user?.name || user?.name || 'Profile'}</span>
            </button>
          </div>
        </header>

        {/* ========================================================
            TAB 1: OVERVIEW DASHBOARD
        ======================================================== */}
        {activeTab === 'dashboard' && (
          <div className="flex-column gap-6">
            {/* SECTION 1 — HEALTH OVERVIEW (4 KPI CARDS) */}
            <div className="grid-4col gap-4">
              <div className="kpi-card glass card p-4 pointer" onClick={() => setActiveTab('history')}>
                <div className="flex-between mb-2">
                  <span className="text-muted text-xs font-medium">Total Predictions</span>
                  <div className="kpi-icon-box blue"><HeartPulse size={18} /></div>
                </div>
                <div className="kpi-value">{kpis.predictions_completed || 0}</div>
                <div className="kpi-subtext text-xs text-muted flex-center-y gap-1 mt-1">
                  <span>Diagnostic assessments logged</span>
                </div>
              </div>

              <div className="kpi-card glass card p-4 pointer" onClick={() => setActiveTab('prediction')}>
                <div className="flex-between mb-2">
                  <span className="text-muted text-xs font-medium">Latest Prediction</span>
                  <div className="kpi-icon-box cyan"><Sparkles size={18} /></div>
                </div>
                <div className="kpi-value text-ellipsis" style={{ fontSize: "1.15rem" }}>
                  {recentPred ? recentPred.predicted_disease : 'None Recorded'}
                </div>
                <div className="kpi-subtext text-xs text-muted mt-1">
                  {recentPred ? `${recentPred.confidence}% confidence score` : 'Complete your first check'}
                </div>
              </div>

              <div className="kpi-card glass card p-4 pointer" onClick={() => setActiveTab('recommendations')}>
                <div className="flex-between mb-2">
                  <span className="text-muted text-xs font-medium">Recommendations</span>
                  <div className="kpi-icon-box purple"><Pill size={18} /></div>
                </div>
                <div className="kpi-value">{kpis.recommendations_available || 0}</div>
                <div className="kpi-subtext text-xs text-muted mt-1">
                  <span>Active clinical care guidelines</span>
                </div>
              </div>

              <div className="kpi-card glass card p-4 pointer" onClick={() => setActiveTab('saved')}>
                <div className="flex-between mb-2">
                  <span className="text-muted text-xs font-medium">Saved Care Plans</span>
                  <div className="kpi-icon-box emerald"><Bookmark size={18} /></div>
                </div>
                <div className="kpi-value">{kpis.saved_recommendations || 0}</div>
                <div className="kpi-subtext text-xs text-muted mt-1">
                  <span>Bookmarked health protocols</span>
                </div>
              </div>
            </div>

            {/* INTERACTIVE VISUALIZATIONS ROW (Pie Chart & Line Chart) */}
            <div className="grid-2col gap-6">
              {/* Chart 1: Donut / Pie Chart for Recommendations Breakdown */}
              <div className="card glass p-5">
                <div className="flex-between mb-3">
                  <div className="flex-center-y gap-2">
                    <PieChartIcon size={16} className="text-cyan" />
                    <h3 style={{ fontSize: "0.95rem", fontWeight: "700", margin: 0 }}>
                      Care Protocol Distribution
                    </h3>
                  </div>
                  <span className="pill-badge bg-glass text-xxs font-mono">
                    {dashboardData?.top_recommendations?.length || 0} ITEMS
                  </span>
                </div>
                <p style={{ color: "#94a3b8", fontSize: "0.78rem", marginBottom: "16px" }}>
                  Clinical care composition across medications, precautions, diet, and physical routines.
                </p>
                <PieChart data={recCategoryData} title="Protocols" size={190} />
              </div>

              {/* Chart 2: Longitudinal Confidence Likelihood Trajectory */}
              <div className="card glass p-5">
                <div className="flex-between mb-3">
                  <div className="flex-center-y gap-2">
                    <TrendingUp size={16} className="text-blue" />
                    <h3 style={{ fontSize: "0.95rem", fontWeight: "700", margin: 0 }}>
                      Diagnostic Likelihood Trajectory
                    </h3>
                  </div>
                  <span className="pill-badge bg-glass text-xxs font-mono">
                    LAST {confidenceTrendData.length} CHECKS
                  </span>
                </div>
                <p style={{ color: "#94a3b8", fontSize: "0.78rem", marginBottom: "16px" }}>
                  Sequential statistical confidence across historical clinical evaluations.
                </p>
                <LineChart data={confidenceTrendData} height={190} lineColor="#38bdf8" />
              </div>
            </div>

            {/* SECTION 2 — FEATURED AI HEALTH PREDICTION & QUICK ACTIONS */}
            <div className="grid-2col gap-6">
              {/* Featured Prediction Card */}
              <div className="card glass p-6 flex-column justify-between">
                <div>
                  <div className="flex-between mb-3">
                    <span className="eyebrow-pill">⭐ LATEST CLINICAL EVALUATION</span>
                    {recentPred && (
                      <span className={`risk-badge risk-${recentPred.risk_level || 'low'}`}>
                        {(recentPred.risk_level || 'low').toUpperCase()} RISK
                      </span>
                    )}
                  </div>

                  {recentPred ? (
                    <div>
                      <h2 style={{ fontSize: "1.35rem", fontWeight: "700", margin: "4px 0 8px", textTransform: "capitalize" }}>
                        {recentPred.predicted_disease}
                      </h2>

                      {/* Confidence visualization bar */}
                      <div className="confidence-meter-box p-3 glass-panel-sm rounded-lg mb-4">
                        <div className="flex-between text-xs mb-1">
                          <span className="text-muted">Statistical Likelihood</span>
                          <span className="font-bold text-cyan">{recentPred.confidence}%</span>
                        </div>
                        <div className="progress-bar-bg">
                          <div className="progress-bar-fill" style={{ width: `${recentPred.confidence}%` }}></div>
                        </div>
                      </div>

                      <div className="text-xs text-muted mb-3 flex-center-y gap-3">
                        <span className="flex-center-y gap-1"><Calendar size={13} /> {formatDate(recentPred.created_at)}</span>
                        <span className="flex-center-y gap-1"><ShieldCheck size={13} /> Model {recentPred.model_version || 'v1.0.0'}</span>
                      </div>

                      <p style={{ color: "#cbd5e1", fontSize: "0.84rem", lineHeight: "1.5", marginBottom: "12px" }}>
                        {recentPred.description || 'Clinical evaluation generated based on submitted symptom indicators.'}
                      </p>

                      <div className="mb-4">
                        <span className="text-xs text-muted block mb-1">Evaluated Symptoms:</span>
                        <div className="flex-wrap gap-1">
                          {(recentPred.symptoms_input || []).map((s, idx) => (
                            <span key={idx} className="chip text-xs">{s}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <HeartPulse size={40} className="text-muted mb-2 opacity-50" />
                      <h3 style={{ fontSize: "1.05rem", fontWeight: "600" }}>No Prediction Logged Yet</h3>
                      <p style={{ color: "#94a3b8", fontSize: "0.8rem", marginTop: "4px" }}>
                        Run your first clinical check to see diagnostic likelihood and personalized care.
                      </p>
                    </div>
                  )}
                </div>

                <div>
                  <div className="medical-disclaimer-box p-2 glass-panel-sm rounded text-xs text-muted mb-3">
                    <ShieldCheck size={13} className="inline mr-1" />
                    <strong>Notice:</strong> AI prediction based on the symptoms provided. This result is for decision support and does not replace professional medical diagnosis.
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => setActiveTab('prediction')}
                      className="btn-primary flex-1 text-xs py-2"
                    >
                      {recentPred ? 'Check New Symptoms' : 'Run First Evaluation'}
                    </button>
                    {recentPred && (
                      <button
                        onClick={() => setActiveTab('history')}
                        className="btn-outline flex-1 text-xs py-2"
                      >
                        View Full History
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {/* SECTION 8 & 9 — QUICK ACTIONS & PROFILE COMPLETION */}
              <div className="flex-column gap-6">
                {/* SECTION 9 — Profile Completion Progress */}
                <div className="card glass p-5">
                  <div className="flex-between mb-3">
                    <span className="font-semibold text-xs text-muted">PROFILE INTEGRITY</span>
                    <span className="font-bold text-cyan text-xs">{profileComp}% COMPLETE</span>
                  </div>

                  <div className="progress-bar-bg mb-3">
                    <div className="progress-bar-fill" style={{ width: `${profileComp}%` }}></div>
                  </div>

                  <p style={{ fontSize: "0.78rem", color: "#94a3b8", marginBottom: "12px" }}>
                    {profileComp >= 80
                      ? 'Your clinical health profile is comprehensive and up to date.'
                      : 'Complete your clinical vitals (allergies, medications, conditions) for higher AI precision.'}
                  </p>

                  <button
                    onClick={() => setActiveTab('profile')}
                    className="btn-outline text-xs w-full py-2"
                  >
                    <UserCheck size={14} className="inline mr-1" /> Complete Health Profile
                  </button>
                </div>

                {/* SECTION 8 — 4 Real Quick Action Cards */}
                <div className="grid-2col gap-3 flex-1">
                  <div
                    className="quick-action-card glass card p-3 pointer flex-column justify-between"
                    onClick={() => setActiveTab('prediction')}
                  >
                    <div className="flex-between">
                      <HeartPulse size={18} className="text-cyan" />
                      <ArrowUpRight size={14} className="text-muted" />
                    </div>
                    <div>
                      <span className="font-bold text-xs block mt-2">Check Symptoms</span>
                      <span className="text-muted text-xxs">230 tracked conditions</span>
                    </div>
                  </div>

                  <div
                    className="quick-action-card glass card p-3 pointer flex-column justify-between"
                    onClick={() => setActiveTab('history')}
                  >
                    <div className="flex-between">
                      <History size={18} className="text-blue" />
                      <ArrowUpRight size={14} className="text-muted" />
                    </div>
                    <div>
                      <span className="font-bold text-xs block mt-2">My Predictions</span>
                      <span className="text-muted text-xxs">View past evaluations</span>
                    </div>
                  </div>

                  <div
                    className="quick-action-card glass card p-3 pointer flex-column justify-between"
                    onClick={() => setActiveTab('recommendations')}
                  >
                    <div className="flex-between">
                      <Sparkles size={18} className="text-purple" />
                      <ArrowUpRight size={14} className="text-muted" />
                    </div>
                    <div>
                      <span className="font-bold text-xs block mt-2">Care Plans</span>
                      <span className="text-muted text-xxs">Medications &amp; Diet</span>
                    </div>
                  </div>

                  <div
                    className="quick-action-card glass card p-3 pointer flex-column justify-between"
                    onClick={() => setActiveTab('profile')}
                  >
                    <div className="flex-between">
                      <User size={18} className="text-emerald" />
                      <ArrowUpRight size={14} className="text-muted" />
                    </div>
                    <div>
                      <span className="font-bold text-xs block mt-2">Update Profile</span>
                      <span className="text-muted text-xxs">Manage health vitals</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* SECTION 3 — TOP PERSONALIZED RECOMMENDATIONS PREVIEW */}
            <div className="card glass p-6">
              <div className="flex-between mb-4">
                <div>
                  <h3 style={{ fontSize: "1.1rem", fontWeight: "700", margin: 0 }}>Recommended Care Routine</h3>
                  <p style={{ color: "#94a3b8", fontSize: "0.78rem", margin: "2px 0 0" }}>
                    Tailored medications, precautions, diet, and physical workouts for your profile.
                  </p>
                </div>
                <button
                  onClick={() => setActiveTab('recommendations')}
                  className="btn-outline text-xs px-3 py-1"
                >
                  View All ({kpis.recommendations_available || 0})
                </button>
              </div>

              {dashboardData?.top_recommendations?.length > 0 ? (
                <div className="grid-3col gap-4">
                  {dashboardData.top_recommendations.slice(0, 3).map((rec, idx) => (
                    <div key={idx} className="rec-card glass-panel-sm p-4 rounded-xl flex-column justify-between">
                      <div>
                        <div className="flex-between mb-2">
                          <span className={`category-pill cat-${(rec.category || 'general').toLowerCase()}`}>
                            {rec.category || 'General'}
                          </span>
                          <span className="text-muted text-xxs">{rec.source || 'Clinical Knowledge'}</span>
                        </div>
                        <h4 style={{ fontSize: "0.95rem", fontWeight: "600", margin: "4px 0 6px" }}>
                          {rec.recommendation}
                        </h4>
                        <p style={{ color: "#94a3b8", fontSize: "0.78rem", lineHeight: "1.4" }}>
                          {rec.reason}
                        </p>
                      </div>

                      <div className="mt-3 pt-3 border-t border-glass flex-between">
                        <div className="flex-center-y gap-1">
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              type="button"
                              className="star-btn pointer"
                              onClick={() => handleFeedback(rec.id, star)}
                              title={`Rate ${star} stars`}
                            >
                              ★
                            </button>
                          ))}
                        </div>
                        <button
                          onClick={() => handleSaveRecommendation(rec)}
                          className="btn-outline text-xxs px-2 py-1"
                        >
                          <Bookmark size={12} className="inline mr-1" /> Save
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-muted text-xs">
                  No active recommendations available yet. Run a symptom assessment to generate personalized care plans.
                </div>
              )}
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 2: AI HEALTH PREDICTION (Interactive Checker)
        ======================================================== */}
        {activeTab === 'prediction' && (
          <div className="flex-column gap-6">
            <div className="card glass p-6">
              <div className="mb-4">
                <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>AI Clinical Symptom Checker</h2>
                <p style={{ color: "#94a3b8", fontSize: "0.82rem", margin: "4px 0 0" }}>
                  Select from 230 tracked clinical conditions to run real-time inference against the trained gradient boosting model.
                </p>
              </div>

              {predError && (
                <div className="status-warning p-3 mb-4 rounded text-xs flex-between">
                  <span>⚠️ {predError}</span>
                  <button className="border-none bg-none pointer" onClick={() => setPredError('')}>✕</button>
                </div>
              )}

              <SymptomSelector
                allSymptoms={allSymptoms}
                selectedSymptoms={selectedSymptoms}
                onChange={setSelectedSymptoms}
              />

              <div className="mt-4 flex-between">
                <span className="text-xs text-muted">
                  {selectedSymptoms.length} symptom(s) currently selected for evaluation.
                </span>
                <button
                  onClick={handleRunPrediction}
                  disabled={predicting || selectedSymptoms.length === 0}
                  className="btn-primary text-xs px-6 py-3 font-semibold"
                >
                  {predicting ? (
                    <span className="flex-center-y gap-2"><RefreshCw size={14} className="spin" /> Evaluating Symptoms...</span>
                  ) : (
                    <span className="flex-center-y gap-2"><HeartPulse size={16} /> Run Diagnostic Prediction</span>
                  )}
                </button>
              </div>
            </div>

            {/* Prediction Result Display */}
            {prediction && (
              <div className="card glass p-6">
                <div className="flex-between mb-3">
                  <span className="eyebrow-pill">DIAGNOSTIC ASSESSMENT RESULT</span>
                  <span className={`risk-badge risk-${prediction.risk_level || 'low'}`}>
                    {(prediction.risk_level || 'low').toUpperCase()} RISK
                  </span>
                </div>

                <h3 style={{ fontSize: "1.4rem", fontWeight: "700", textTransform: "capitalize", margin: "4px 0 8px" }}>
                  {prediction.predicted_disease}
                </h3>

                <div className="grid-3col gap-4 mb-4">
                  <div className="glass-panel-sm p-3 rounded">
                    <span className="text-muted text-xxs block">CONFIDENCE SCORE</span>
                    <span className="text-lg font-bold text-cyan">{prediction.confidence}%</span>
                  </div>
                  <div className="glass-panel-sm p-3 rounded">
                    <span className="text-muted text-xxs block">MODEL VERSION</span>
                    <span className="text-sm font-semibold">{prediction.model_version || 'v1.0.0'}</span>
                  </div>
                  <div className="glass-panel-sm p-3 rounded">
                    <span className="text-muted text-xxs block">TIME LOGGED</span>
                    <span className="text-xs font-semibold">{formatDate(prediction.prediction_timestamp)}</span>
                  </div>
                </div>

                <p style={{ color: "#cbd5e1", fontSize: "0.88rem", lineHeight: "1.6", marginBottom: "16px" }}>
                  {prediction.description}
                </p>

                {/* Top Candidates */}
                {prediction.top_candidates?.length > 1 && (
                  <div className="mb-4 p-4 glass-panel-sm rounded-lg">
                    <h4 className="text-xs font-bold text-muted uppercase mb-2">Differential Diagnoses (Top Candidates)</h4>
                    <div className="grid-2col gap-2">
                      {prediction.top_candidates.map((cand, i) => (
                        <div key={i} className="flex-between text-xs p-2 glass rounded">
                          <span style={{ textTransform: "capitalize" }}>{i + 1}. {cand.disease}</span>
                          <span className="font-bold text-cyan">{cand.confidence}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Care Plan Grid */}
                <div className="grid-2col gap-4 mb-4">
                  <div className="p-4 glass-panel-sm rounded-lg">
                    <h4 className="text-xs font-bold text-muted uppercase mb-2 flex-center-y gap-1">
                      <Pill size={14} className="text-cyan" /> Suggested Medications
                    </h4>
                    <ul className="text-xs flex-column gap-1 pl-4">
                      {(prediction.medicines || prediction.medications || []).map((m, i) => (
                        <li key={i}>{m}</li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-4 glass-panel-sm rounded-lg">
                    <h4 className="text-xs font-bold text-muted uppercase mb-2 flex-center-y gap-1">
                      <Shield size={14} className="text-emerald" /> Recommended Precautions
                    </h4>
                    <ul className="text-xs flex-column gap-1 pl-4">
                      {(prediction.advice || prediction.precautions || []).map((a, i) => (
                        <li key={i}>{a}</li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="medical-disclaimer-box p-3 glass-panel-sm rounded text-xs text-muted">
                  <ShieldCheck size={14} className="inline mr-1" />
                  <strong>Clinical Notice:</strong> AI prediction based on the symptoms provided. This result is for decision support and does not replace professional medical diagnosis.
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================
            TAB 3: MY PREDICTIONS (History)
        ======================================================== */}
        {activeTab === 'history' && (
          <div className="card glass p-6">
            <div className="flex-between mb-4 flex-wrap gap-3">
              <div>
                <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>Prediction History</h2>
                <p style={{ color: "#94a3b8", fontSize: "0.8rem", margin: "2px 0 0" }}>
                  Search and inspect your logged health assessments.
                </p>
              </div>

              <div className="flex-center-y gap-2">
                <div className="relative">
                  <Search size={14} style={{ position: "absolute", left: "10px", top: "10px", color: "#64748b" }} />
                  <input
                    type="text"
                    className="search-input text-xs pl-8 py-2"
                    placeholder="Search past conditions..."
                    value={historySearch}
                    onChange={(e) => setHistorySearch(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {filteredHistory.length > 0 ? (
              <div className="table-responsive">
                <table className="custom-table text-xs">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Predicted Condition</th>
                      <th>Confidence</th>
                      <th>Risk Level</th>
                      <th>Symptoms Evaluated</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredHistory.map((item, idx) => (
                      <tr key={idx}>
                        <td>{formatDate(item.created_at)}</td>
                        <td className="font-semibold capitalize">{item.predicted_disease}</td>
                        <td><span className="font-bold text-cyan">{item.confidence}%</span></td>
                        <td>
                          <span className={`risk-badge risk-${item.risk_level || 'low'}`}>
                            {item.risk_level || 'low'}
                          </span>
                        </td>
                        <td>
                          <div className="flex-wrap gap-1 max-w-300">
                            {(item.symptoms_input || []).slice(0, 3).map((s, i) => (
                              <span key={i} className="chip text-xxs">{s}</span>
                            ))}
                            {(item.symptoms_input || []).length > 3 && (
                              <span className="text-muted text-xxs">+{item.symptoms_input.length - 3} more</span>
                            )}
                          </div>
                        </td>
                        <td>
                          <button
                            onClick={() => setSelectedHistoryItem(item)}
                            className="btn-outline text-xxs px-2 py-1"
                          >
                            Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-muted">
                <History size={36} className="opacity-40 mb-2" />
                <p className="text-xs">No prediction history records match your search.</p>
              </div>
            )}

            {/* History Details Modal */}
            {selectedHistoryItem && (
              <div className="modal-overlay flex-center" onClick={() => setSelectedHistoryItem(null)}>
                <div className="modal-card glass p-6 max-w-500 w-full" onClick={(e) => e.stopPropagation()}>
                  <div className="flex-between mb-3">
                    <h3 className="text-base font-bold capitalize">{selectedHistoryItem.predicted_disease}</h3>
                    <button className="border-none bg-none pointer text-muted" onClick={() => setSelectedHistoryItem(null)}>✕</button>
                  </div>
                  <div className="flex-between text-xs text-muted mb-3">
                    <span>Date: {formatDate(selectedHistoryItem.created_at)}</span>
                    <span className="font-bold text-cyan">{selectedHistoryItem.confidence}% Confidence</span>
                  </div>
                  <p className="text-xs text-slate-300 mb-4">{selectedHistoryItem.description}</p>
                  
                  <div className="mb-3">
                    <span className="text-xs font-semibold block mb-1">Submitted Symptoms:</span>
                    <div className="flex-wrap gap-1">
                      {(selectedHistoryItem.symptoms_input || []).map((s, i) => (
                        <span key={i} className="chip text-xs">{s}</span>
                      ))}
                    </div>
                  </div>

                  <div className="text-right">
                    <button onClick={() => setSelectedHistoryItem(null)} className="btn-primary text-xs px-4 py-2">
                      Close
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ========================================================
            TAB 4: PERSONALIZED RECOMMENDATIONS
        ======================================================== */}
        {activeTab === 'recommendations' && (
          <div className="card glass p-6">
            <div className="flex-between mb-4 flex-wrap gap-3">
              <div>
                <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>Personalized Care Plans</h2>
                <p style={{ color: "#94a3b8", fontSize: "0.8rem", margin: "2px 0 0" }}>
                  Clinical care recommendations tailored to your active evaluations.
                </p>
              </div>

              {/* Supported Category Filter */}
              <div className="flex-wrap gap-1">
                {['all', 'medicine', 'precaution', 'diet', 'workout'].map((cat) => (
                  <button
                    key={cat}
                    className={`btn-filter text-xs ${selectedRecCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedRecCategory(cat)}
                  >
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {filteredRecommendations.length > 0 ? (
              <div className="grid-2col gap-4">
                {filteredRecommendations.map((rec, idx) => {
                  const recId = rec.id || idx + 1;
                  const isExpanded = expandedReasons[recId];

                  return (
                    <div key={idx} className="rec-card glass-panel-sm p-4 rounded-xl flex-column justify-between">
                      <div>
                        <div className="flex-between mb-2">
                          <span className={`category-pill cat-${(rec.category || 'general').toLowerCase()}`}>
                            {rec.category || 'General'}
                          </span>
                          <span className="text-muted text-xxs font-mono">{rec.source || 'Medical Knowledge Base'}</span>
                        </div>

                        <h3 style={{ fontSize: "1rem", fontWeight: "700", margin: "6px 0" }}>
                          {rec.recommendation}
                        </h3>

                        <p style={{ color: "#cbd5e1", fontSize: "0.82rem", lineHeight: "1.5", margin: "6px 0" }}>
                          {rec.reason}
                        </p>

                        {/* Expandable Explanation ("Why am I seeing this?") */}
                        <button
                          type="button"
                          className="btn-text text-xxs flex-center-y gap-1 text-cyan mt-1 pointer"
                          onClick={() => toggleExplanation(recId)}
                        >
                          <Info size={12} /> Why am I seeing this? {isExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                        </button>

                        {isExpanded && (
                          <div className="mt-2 p-2 glass rounded text-xxs text-muted leading-relaxed">
                            This recommendation is clinically indicated based on your present symptom patterns and matching disease profile from the healthcare dataset.
                          </div>
                        )}
                      </div>

                      <div className="mt-4 pt-3 border-t border-glass flex-between">
                        <div className="flex-center-y gap-1">
                          <span className="text-xxs text-muted mr-1">Feedback:</span>
                          {[1, 2, 3, 4, 5].map((star) => (
                            <button
                              key={star}
                              type="button"
                              className="star-btn pointer"
                              onClick={() => handleFeedback(rec.id, star)}
                              title={`Rate ${star} stars`}
                            >
                              ★
                            </button>
                          ))}
                        </div>

                        <button
                          onClick={() => handleSaveRecommendation(rec)}
                          className="btn-outline text-xs px-3 py-1 font-medium"
                        >
                          <Bookmark size={13} className="inline mr-1" /> Save Plan
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-12 text-muted">
                <Sparkles size={36} className="opacity-40 mb-2" />
                <p className="text-xs">No care recommendations available for the selected category.</p>
              </div>
            )}
          </div>
        )}

        {/* ========================================================
            TAB 5: HEALTH INSIGHTS & VISUALIZATIONS
        ======================================================== */}
        {activeTab === 'insights' && (
          <div className="flex-column gap-6">
            <div className="card glass p-6">
              <div className="flex-between mb-4">
                <div>
                  <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>AI Health Insights &amp; Analytics</h2>
                  <p style={{ color: "#94a3b8", fontSize: "0.8rem", margin: "2px 0 0" }}>
                    Longitudinal pattern analytics generated strictly from your authentic health check-ins.
                  </p>
                </div>
                <span className="pill-badge bg-glass text-xs">
                  {insights.has_sufficient_data ? 'Active Clinical Profile' : 'Initial Assessment Phase'}
                </span>
              </div>

              <div className="grid-3col gap-4 mb-6">
                <div className="glass-panel-sm p-4 rounded-xl">
                  <span className="text-muted text-xs block mb-1">Total Evaluations</span>
                  <span className="text-xl font-bold text-cyan">{insights.total_evaluations || 0}</span>
                </div>
                <div className="glass-panel-sm p-4 rounded-xl">
                  <span className="text-muted text-xs block mb-1">Dominant Condition</span>
                  <span className="text-base font-semibold capitalize">{insights.dominant_condition || 'None Recorded'}</span>
                </div>
                <div className="glass-panel-sm p-4 rounded-xl">
                  <span className="text-muted text-xs block mb-1">Care Routine Status</span>
                  <span className="text-sm font-semibold">{insights.care_plan_status || 'Pending'}</span>
                </div>
              </div>

              {/* TWO ANALYTIC VISUALIZATIONS IN INSIGHTS */}
              <div className="grid-2col gap-6 mb-6">
                {/* Pie Chart: Risk Severity Breakdown */}
                <div className="p-5 glass-panel-sm rounded-xl">
                  <div className="flex-center-y gap-2 mb-2">
                    <PieChartIcon size={16} className="text-cyan" />
                    <h4 style={{ fontSize: "0.95rem", fontWeight: "700", margin: 0 }}>Risk Stratification Ratio</h4>
                  </div>
                  <p style={{ color: "#94a3b8", fontSize: "0.75rem", marginBottom: "12px" }}>
                    Breakdown of evaluations by assessed severity levels.
                  </p>
                  <PieChart data={riskBreakdownData} title="Risk Levels" size={170} />
                </div>

                {/* Bar Graph: Frequently Selected Symptoms */}
                <div className="p-5 glass-panel-sm rounded-xl">
                  <div className="flex-center-y gap-2 mb-2">
                    <BarChart3 size={16} className="text-blue" />
                    <h4 style={{ fontSize: "0.95rem", fontWeight: "700", margin: 0 }}>Most Frequent Symptoms</h4>
                  </div>
                  <p style={{ color: "#94a3b8", fontSize: "0.75rem", marginBottom: "12px" }}>
                    Top recurring indicators submitted across your assessments.
                  </p>
                  <BarChart data={symptomFrequencyData} title="Top Symptoms" horizontal={true} />
                </div>
              </div>

              <div className="p-4 glass rounded-xl">
                <h3 className="text-xs font-bold text-muted uppercase mb-1 flex-center-y gap-1">
                  <TrendingUp size={14} className="text-cyan" /> Health Trajectory Summary
                </h3>
                <p style={{ color: "#cbd5e1", fontSize: "0.88rem", lineHeight: "1.6", margin: 0 }}>
                  {insights.trend_summary}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 6: MY ACTIVITY
        ======================================================== */}
        {activeTab === 'activity' && (
          <div className="card glass p-6">
            <div className="mb-4">
              <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>User Activity Analytics</h2>
              <p style={{ color: "#94a3b8", fontSize: "0.8rem", margin: "2px 0 0" }}>
                Interaction metrics and immutable audit trail of your account events.
              </p>
            </div>

            {/* Activity by Type Bar Chart */}
            {activityTypeData.length > 0 && (
              <div className="p-5 glass-panel-sm rounded-xl mb-6">
                <div className="flex-center-y gap-2 mb-2">
                  <BarChart3 size={16} className="text-cyan" />
                  <h4 style={{ fontSize: "0.95rem", fontWeight: "700", margin: 0 }}>Action Volume by Category</h4>
                </div>
                <p style={{ color: "#94a3b8", fontSize: "0.75rem", marginBottom: "12px" }}>
                  Quantified distribution of user interactions (evaluations, saves, profile edits, feedback).
                </p>
                <BarChart data={activityTypeData} horizontal={false} height={160} />
              </div>
            )}

            {dashboardData?.recent_activity?.length > 0 ? (
              <div className="activity-timeline flex-column gap-3">
                <h4 style={{ fontSize: "0.88rem", fontWeight: "700", margin: "8px 0 4px", color: "#e2e8f0" }}>
                  Recent Activity Logs
                </h4>
                {dashboardData.recent_activity.map((act, i) => (
                  <div key={i} className="activity-item glass-panel-sm p-3 rounded-lg flex-between">
                    <div className="flex-center-y gap-3">
                      <div className="activity-icon-badge">
                        <Activity size={14} className="text-cyan" />
                      </div>
                      <div>
                        <span className="text-xs font-bold uppercase text-slate-200">{act.type}</span>
                        <p className="text-xxs text-muted margin-0">
                          {act.details?.disease ? `Evaluated: ${act.details.disease}` : act.details?.action || 'User interaction logged'}
                        </p>
                      </div>
                    </div>
                    <span className="text-xxs text-muted flex-center-y gap-1">
                      <Clock size={11} /> {formatDate(act.timestamp)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted text-xs">
                Not enough activity data yet. Complete actions to build your activity history.
              </div>
            )}
          </div>
        )}

        {/* ========================================================
            TAB 7: SAVED RECOMMENDATIONS
        ======================================================== */}
        {activeTab === 'saved' && (
          <div className="card glass p-6">
            <div className="mb-4">
              <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>Saved Care Plans &amp; Recommendations</h2>
              <p style={{ color: "#94a3b8", fontSize: "0.8rem", margin: "2px 0 0" }}>
                Bookmarked treatment guidelines and care protocols.
              </p>
            </div>

            {dashboardData?.saved_recommendations?.length > 0 ? (
              <div className="grid-2col gap-4">
                {dashboardData.saved_recommendations.map((saved, i) => (
                  <div key={i} className="glass-panel-sm p-4 rounded-xl flex-column justify-between">
                    <div>
                      <div className="flex-between mb-2">
                        <span className="pill-badge bg-glass text-xxs">Saved Protocol</span>
                        <span className="text-xxs text-muted">{formatDate(saved.timestamp)}</span>
                      </div>
                      <h3 className="text-sm font-bold mb-1">{saved.title}</h3>
                      <p className="text-xs text-muted">{saved.notes}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted">
                <Bookmark size={36} className="opacity-40 mb-2" />
                <p className="text-xs">No saved care plans yet. Explore recommendations and bookmark helpful protocols.</p>
              </div>
            )}
          </div>
        )}

        {/* ========================================================
            TAB 8: NOTIFICATIONS
        ======================================================== */}
        {activeTab === 'notifications' && (
          <div className="card glass p-6">
            <div className="flex-between mb-4">
              <div>
                <h2 style={{ fontSize: "1.25rem", fontWeight: "700", margin: 0 }}>Notification Center</h2>
                <p style={{ color: "#94a3b8", fontSize: "0.8rem", margin: "2px 0 0" }}>
                  Alerts on predictions, care plans, and security updates.
                </p>
              </div>
              <span className="text-xs text-cyan font-semibold">
                {unreadCount} unread alert(s)
              </span>
            </div>

            {dashboardData?.notifications?.length > 0 ? (
              <div className="flex-column gap-3">
                {dashboardData.notifications.map((note) => (
                  <div
                    key={note.id}
                    className={`notification-item p-3 rounded-lg flex-between ${note.is_read ? 'glass-panel-sm opacity-70' : 'glass border-primary'}`}
                  >
                    <div>
                      <div className="flex-center-y gap-2 mb-1">
                        <span className="font-bold text-xs">{note.title}</span>
                        {!note.is_read && <span className="unread-dot" />}
                      </div>
                      <p className="text-xs text-slate-300 margin-0">{note.message}</p>
                      <span className="text-xxs text-muted block mt-1">{formatDate(note.timestamp)}</span>
                    </div>

                    {!note.is_read && (
                      <button
                        onClick={() => handleMarkNotificationRead(note.id)}
                        className="btn-outline text-xxs px-2 py-1"
                      >
                        Mark Read
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-muted text-xs">
                <Bell size={36} className="opacity-40 mb-2" />
                <p>No notifications at this time.</p>
              </div>
            )}
          </div>
        )}

        {/* ========================================================
            TAB 9: MY PROFILE & HEALTH VITALS
        ======================================================== */}
        {activeTab === 'profile' && (
          <div className="grid-2col gap-6">
            <div className="card glass p-6">
              <h3 className="text-base font-bold mb-3">Personal Information</h3>
              {profileMsg && <div className="toast-banner glass p-2 mb-3 rounded text-xs text-cyan">{profileMsg}</div>}
              
              <form onSubmit={async (e) => {
                e.preventDefault();
                try {
                  await axios.put('/api/user/profile', profileForm);
                  setProfileMsg("Personal profile saved successfully.");
                  setTimeout(() => setProfileMsg(''), 4000);
                  fetchDashboardData();
                } catch (err) {
                  setProfileMsg("Could not save profile details.");
                }
              }} className="flex-column gap-3 text-xs">
                <div>
                  <label className="text-muted block mb-1">Full Legal Name</label>
                  <input
                    type="text"
                    className="search-input w-full text-xs"
                    value={profileForm.name}
                    onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-muted block mb-1">Contact Phone</label>
                  <input
                    type="text"
                    className="search-input w-full text-xs"
                    placeholder="+1 (555) 000-0000"
                    value={profileForm.phone}
                    onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-muted block mb-1">Residential Address</label>
                  <input
                    type="text"
                    className="search-input w-full text-xs"
                    placeholder="City, State, Country"
                    value={profileForm.address}
                    onChange={(e) => setProfileForm({ ...profileForm, address: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-muted block mb-1">Personal Health Bio</label>
                  <textarea
                    rows={3}
                    className="search-input w-full text-xs"
                    placeholder="Any general wellness notes..."
                    value={profileForm.bio}
                    onChange={(e) => setProfileForm({ ...profileForm, bio: e.target.value })}
                  />
                </div>

                <button type="submit" className="btn-primary text-xs py-2 mt-2">
                  Save Personal Info
                </button>
              </form>
            </div>

            <div className="card glass p-6">
              <h3 className="text-base font-bold mb-3">Clinical Health Vitals</h3>
              <form onSubmit={async (e) => {
                e.preventDefault();
                try {
                  await axios.put('/api/user/health-profile', {
                    age: parseInt(healthForm.age) || null,
                    gender: healthForm.gender,
                    allergies: typeof healthForm.allergies === 'string' ? healthForm.allergies.split(',').map(s => s.trim()).filter(Boolean) : healthForm.allergies,
                    existing_conditions: typeof healthForm.existing_conditions === 'string' ? healthForm.existing_conditions.split(',').map(s => s.trim()).filter(Boolean) : healthForm.existing_conditions,
                    current_medications: typeof healthForm.current_medications === 'string' ? healthForm.current_medications.split(',').map(s => s.trim()).filter(Boolean) : healthForm.current_medications
                  });
                  setProfileMsg("Clinical health vitals updated.");
                  setTimeout(() => setProfileMsg(''), 4000);
                  fetchDashboardData();
                } catch (err) {
                  setProfileMsg("Could not save clinical vitals.");
                }
              }} className="flex-column gap-3 text-xs">
                <div className="grid-2col gap-2">
                  <div>
                    <label className="text-muted block mb-1">Patient Age</label>
                    <input
                      type="number"
                      className="search-input w-full text-xs"
                      placeholder="e.g. 32"
                      value={healthForm.age}
                      onChange={(e) => setHealthForm({ ...healthForm, age: e.target.value })}
                    />
                  </div>

                  <div>
                    <label className="text-muted block mb-1">Gender</label>
                    <select
                      className="search-input w-full text-xs"
                      value={healthForm.gender}
                      onChange={(e) => setHealthForm({ ...healthForm, gender: e.target.value })}
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other / Non-binary</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="text-muted block mb-1">Known Allergies (comma separated)</label>
                  <input
                    type="text"
                    className="search-input w-full text-xs"
                    placeholder="e.g. Penicillin, Peanuts, Pollen"
                    value={healthForm.allergies}
                    onChange={(e) => setHealthForm({ ...healthForm, allergies: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-muted block mb-1">Existing Medical Conditions</label>
                  <input
                    type="text"
                    className="search-input w-full text-xs"
                    placeholder="e.g. Mild Asthma, Hypertension"
                    value={healthForm.existing_conditions}
                    onChange={(e) => setHealthForm({ ...healthForm, existing_conditions: e.target.value })}
                  />
                </div>

                <div>
                  <label className="text-muted block mb-1">Current Active Medications</label>
                  <input
                    type="text"
                    className="search-input w-full text-xs"
                    placeholder="e.g. Albuterol, Multivitamins"
                    value={healthForm.current_medications}
                    onChange={(e) => setHealthForm({ ...healthForm, current_medications: e.target.value })}
                  />
                </div>

                <button type="submit" className="btn-primary text-xs py-2 mt-2">
                  Save Clinical Profile
                </button>
              </form>
            </div>
          </div>
        )}

        {/* ========================================================
            TAB 10: SETTINGS
        ======================================================== */}
        {activeTab === 'settings' && (
          <div className="card glass p-6 max-w-500">
            <h3 className="text-base font-bold mb-3">Security &amp; Account Settings</h3>
            {pwMsg && <div className="toast-banner glass p-2 mb-3 rounded text-xs text-cyan">{pwMsg}</div>}

            <form onSubmit={async (e) => {
              e.preventDefault();
              try {
                await axios.post('/api/auth/change-password', pwForm);
                setPwMsg("Password updated successfully.");
                setPwForm({ old_password: '', new_password: '' });
              } catch (err) {
                setPwMsg(err.response?.data?.error || "Password change failed.");
              }
            }} className="flex-column gap-3 text-xs">
              <div>
                <label className="text-muted block mb-1">Current Password</label>
                <input
                  type="password"
                  required
                  className="search-input w-full text-xs"
                  placeholder="••••••••••••"
                  value={pwForm.old_password}
                  onChange={(e) => setPwForm({ ...pwForm, old_password: e.target.value })}
                />
              </div>

              <div>
                <label className="text-muted block mb-1">New Password</label>
                <input
                  type="password"
                  required
                  className="search-input w-full text-xs"
                  placeholder="••••••••••••"
                  value={pwForm.new_password}
                  onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
                />
                <small className="text-muted block mt-1">Must be at least 6 characters.</small>
              </div>

              <button type="submit" className="btn-primary text-xs py-2 mt-2">
                Update Password
              </button>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
