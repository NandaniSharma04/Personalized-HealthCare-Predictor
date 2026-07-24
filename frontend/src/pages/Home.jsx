import { useState, useEffect, useMemo } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  Activity, Brain, ShieldCheck, UserPlus, ClipboardList,
  Sparkles, HeartPulse, Stethoscope, TrendingUp, Search, X,
} from "lucide-react";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } },
};

function PulseDivider() {
  return (
    <div className="pulse-divider" aria-hidden="true">
      <svg viewBox="0 0 1180 60" preserveAspectRatio="none">
        <defs>
          <linearGradient id="pulseGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#1D4ED8" stopOpacity="0" />
            <stop offset="15%" stopColor="#1D4ED8" />
            <stop offset="50%" stopColor="#06B6D4" />
            <stop offset="85%" stopColor="#7C6FF0" />
            <stop offset="100%" stopColor="#7C6FF0" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          className="pulse-line-path"
          d="M0,30 L260,30 L285,30 L300,8 L320,52 L340,30 L370,30 L900,30 L920,30 L935,8 L955,52 L975,30 L1000,30 L1180,30"
        />
      </svg>
    </div>
  );
}

export default function Home() {
  const { user } = useAuth();
  const [allSymptoms, setAllSymptoms] = useState([]);
  const [selected, setSelected] = useState([]);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/api/symptoms").then((res) => setAllSymptoms(res.data.symptoms || []));
  }, []);

  const suggestions = useMemo(() => {
    if (!query.trim()) return [];
    const q = query.toLowerCase();
    return allSymptoms
      .filter((s) => !selected.includes(s) && s.toLowerCase().includes(q))
      .slice(0, 8);
  }, [query, allSymptoms, selected]);

  function addSymptom(s) {
    setSelected([...selected, s]);
    setQuery("");
  }
  function removeSymptom(s) {
    setSelected(selected.filter((x) => x !== s));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    if (selected.length === 0) {
      setError("Select at least one symptom.");
      return;
    }
    setLoading(true);
    try {
      const res = await api.post("/predict", { symptoms: selected });
      setResult(res.data);
    } catch (err) {
      if (err.response?.status === 401) {
        setError("Please log in to get a prediction.");
      } else {
        setError(err.response?.data?.error || "Prediction failed. Try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      {/* ---------------- HERO ---------------- */}
      <section className="hero-stage">
        <div className="hero">
        <motion.div initial="hidden" animate="show" variants={fadeUp}>
          <span className="eyebrow">
            <span className="eyebrow-dot" />
            AI symptom analysis
          </span>
          <h1>
            Know what's going on <span className="accent">before you Google it wrong.</span>
          </h1>
          <p className="lead">
            Tell us your symptoms. Our model checks them against real diagnostic
            patterns, suggests next steps, and remembers your history — so every
            check gets a little more personal.
          </p>
          <div className="hero-ctas">
            <a href="#checker" className="btn-primary">Check my symptoms</a>
            <a href="#how-it-works" className="btn-secondary">See how it works</a>
          </div>
          <p className="disclaimer">
            <ShieldCheck size={15} /> Support tool, not a replacement for a real doctor.
          </p>
        </motion.div>

        <motion.div
          className="hero-card"
          initial={{ opacity: 0, y: 30, scale: 0.97 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.15, ease: "easeOut" }}
        >
          <span className="label">Symptoms selected</span>
          <div className="chip-row">
            <span className="demo-chip">Fever</span>
            <span className="demo-chip">Cough</span>
            <span className="demo-chip">Fatigue</span>
          </div>
          <span className="label">Prediction</span>
          <div className="result-row">
            <div className="ring">
              <div className="ring-inner">78%</div>
            </div>
            <div>
              <h3>Likely Influenza</h3>
              <span style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.85rem" }}>
                Based on 4 symptoms &amp; vitals
              </span>
            </div>
          </div>
          <span className="label">Suggested next step</span>
          <div className="med-pill-row" style={{ marginTop: 10 }}>
            <span className="med-pill">Rest 8–10 hrs</span>
            <span className="med-pill">Hydration</span>
            <span className="med-pill">Monitor 48h</span>
          </div>
        </motion.div>
        </div>
      </section>

      <PulseDivider />

      {/* ---------------- HOW IT WORKS ---------------- */}
      <section className="section" id="how-it-works">
        <motion.div
          className="section-head"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.4 }} variants={fadeUp}
        >
          <span className="eyebrow">The process</span>
          <h2>Three steps, every time you check in</h2>
          <p>No paperwork, no waiting room — just a quick, structured check that gets logged to your account.</p>
        </motion.div>

        <div className="steps-grid">
          {[
            { icon: UserPlus, num: "01", title: "Create your account", desc: "A secure, private profile — nobody sees your data but you." },
            { icon: ClipboardList, num: "02", title: "Enter symptoms & vitals", desc: "Fever, cough, fatigue, breathing, age, blood pressure — the basics." },
            { icon: Brain, num: "03", title: "Get your AI prediction", desc: "A likely condition, a confidence score, and suggested next steps." },
          ].map((s, i) => (
            <motion.div
              key={s.num}
              className="step-card glass"
              initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.4 }}
              variants={fadeUp}
              transition={{ delay: i * 0.1 }}
            >
              <s.icon size={26} color="var(--primary)" style={{ marginBottom: 14 }} />
              <div className="step-num">{s.num}</div>
              <h3>{s.title}</h3>
              <p>{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      <PulseDivider />

      {/* ---------------- SYMPTOM CHECKER (functional) ---------------- */}
      <section className="section" id="checker">
        <motion.div
          className="section-head"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.4 }} variants={fadeUp}
        >
          <span className="eyebrow"><Activity size={13} style={{ marginRight: 4 }} />Try it now</span>
          <h2>Check your symptoms</h2>
          <p>Select what you're feeling. The more you select, the sharper the prediction.</p>
        </motion.div>

        <motion.div
          className="checker-wrap glass"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.2 }} variants={fadeUp}
        >
          <form className="checker-form" onSubmit={handleSubmit}>
            <h3>Symptom checker</h3>
            <p>Search and add every symptom that applies — {allSymptoms.length || "230"} tracked conditions.</p>

            <span className="field-label">Search symptoms</span>
            <div className="symptom-search">
              <Search size={17} className="symptom-search-icon" />
              <input
                type="text"
                placeholder="e.g. chest pain, fatigue, dizziness..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              {suggestions.length > 0 && (
                <div className="symptom-suggestions">
                  {suggestions.map((s) => (
                    <button type="button" key={s} onClick={() => addSymptom(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <span className="field-label" style={{ marginTop: 20 }}>
              Selected ({selected.length})
            </span>
            <div className="symptom-grid">
              {selected.length === 0 && (
                <span style={{ color: "var(--ink-faint)", fontSize: "0.88rem" }}>
                  Nothing selected yet — search above to add symptoms.
                </span>
              )}
              {selected.map((s) => (
                <button
                  type="button"
                  key={s}
                  className="symptom active"
                  onClick={() => removeSymptom(s)}
                >
                  {s} <X size={13} style={{ marginLeft: 4 }} />
                </button>
              ))}
            </div>

            <button type="submit" disabled={loading} style={{ marginTop: 10 }}>
              {loading ? "Analyzing..." : user ? "Get prediction" : "Log in to get a prediction"}
            </button>

            {error && <p className="predict-error">{error}</p>}
            {!user && (
              <p style={{ marginTop: 14, fontSize: "0.85rem", color: "var(--ink-faint)" }}>
                Don't have an account? <Link to="/signup" style={{ color: "var(--primary)", fontWeight: 600 }}>Sign up free</Link>
              </p>
            )}
          </form>

          <div className={result ? "checker-result glass" : "checker-result empty glass"}>
            {!result && (
              <>
                <HeartPulse size={40} />
                <p>Your prediction will appear here once you submit.</p>
              </>
            )}
            {result && (
              <div>
                <span className="field-label">Prediction</span>
                <h3 className="result-disease">{result.disease}</h3>
                <div className="result-meta">
                  <span>{result.confidence}% confidence</span>
                  <span className={`risk-badge risk-${result.risk}`}>{result.risk} risk</span>
                </div>
                <p style={{ color: "var(--ink-soft)", fontSize: "0.92rem", lineHeight: 1.6 }}>
                  {result.description}
                </p>
                <div className="result-block">
                  <h4>Precautions</h4>
                  <ul>{result.precautions.map((m, i) => <li key={i}>{m}</li>)}</ul>
                </div>
                <div className="result-block">
                  <h4>Suggested medications</h4>
                  <ul>{result.medications.map((a, i) => <li key={i}>{a}</li>)}</ul>
                </div>
                {result.diet?.length > 0 && (
                  <div className="result-block">
                    <h4>Diet</h4>
                    <ul>{result.diet.map((d, i) => <li key={i}>{d}</li>)}</ul>
                  </div>
                )}
                {result.workout?.length > 0 && (
                  <div className="result-block">
                    <h4>Recommended activity</h4>
                    <ul>{result.workout.map((w, i) => <li key={i}>{w}</li>)}</ul>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </section>

      <PulseDivider />

      {/* ---------------- WHY PERSONALIZED ---------------- */}
      <section className="section">
        <motion.div
          className="section-head"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.4 }} variants={fadeUp}
        >
          <span className="eyebrow"><Sparkles size={13} style={{ marginRight: 4 }} />Why "personalized"</span>
          <h2>It remembers, so it gets sharper over time</h2>
          <p>Every check is saved to your account. Patterns across visits are worth more than any single check alone.</p>
        </motion.div>

        <motion.div
          className="timeline"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.3 }} variants={fadeUp}
        >
          <div className="timeline-item">
            <div className="timeline-dot"><Stethoscope size={18} /></div>
            <div className="timeline-content">
              <div className="t-title">First check-in</div>
              <div className="t-desc">Fever + cough logged, flagged as low risk.</div>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-dot"><Activity size={18} /></div>
            <div className="timeline-content">
              <div className="t-title">Second check-in, 3 months later</div>
              <div className="t-desc">Breathing difficulty logged again — third respiratory flag this year.</div>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-dot"><TrendingUp size={18} /></div>
            <div className="timeline-content">
              <div className="t-title">Your dashboard notices the pattern</div>
              <div className="t-desc">Recurring respiratory symptoms — worth mentioning at your next real appointment.</div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ---------------- FOOTER ---------------- */}
      <footer className="site-footer">
        <span className="brand">MediCare AI</span>
        <span className="footer-note">Frontend: React · Backend: Flask · ML: scikit-learn</span>
      </footer>
    </div>
  );
}
