import React from "react";
import { motion } from "framer-motion";
import { Link, useNavigate } from "react-router-dom";
import {
  Activity, Brain, ShieldCheck, UserPlus, ClipboardList,
  Sparkles, Stethoscope, TrendingUp, HeartPulse, ArrowRight
} from "lucide-react";
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
  const navigate = useNavigate();

  return (
    <div>
      {/* ---------------- HERO ---------------- */}
      <section className="hero-stage">
        <div className="hero">
          <motion.div initial="hidden" animate="show" variants={fadeUp}>
            <span className="eyebrow">
              <span className="eyebrow-dot" />
              AI Medical Recommendation Engine
            </span>
            <h1>
              Know what's going on <span className="accent">before you Google it wrong.</span>
            </h1>
            <p className="lead">
              Tell us your symptoms. Our machine learning system checks them against real diagnostic
              patterns, highlights expected disease symptoms, predicts candidate risks, and suggests tailored care.
            </p>
            <div className="hero-ctas">
              <button
                onClick={() => navigate(user ? "/predictor" : "/login")}
                className="btn-primary"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px", cursor: "pointer" }}
              >
                <HeartPulse size={18} /> Check My Symptoms
              </button>
              <button
                onClick={() => navigate(user ? "/dashboard" : "/signup")}
                className="btn-secondary"
                style={{ display: "inline-flex", alignItems: "center", gap: "6px", cursor: "pointer" }}
              >
                {user ? "View My Dashboard" : "Create Account"} <ArrowRight size={16} />
              </button>
            </div>
            <p className="disclaimer">
              <ShieldCheck size={15} /> Medical AI decision support tool. Authentication required for personalized clinical analysis.
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
            <span className="label">Primary Prediction</span>
            <div className="result-row">
              <div className="ring">
                <div className="ring-inner">85%</div>
              </div>
              <div>
                <h3>Common Cold / Respiratory Care</h3>
                <span style={{ color: "rgba(255,255,255,0.65)", fontSize: "0.85rem" }}>
                  Random Forest + TF-IDF + Cosine Matching
                </span>
              </div>
            </div>
            <span className="label">Expected Disease Symptoms</span>
            <div className="chip-row" style={{ marginTop: 6 }}>
              <span className="demo-chip" style={{ background: "rgba(255,255,255,0.1)", fontSize: "0.75rem" }}>Chills</span>
              <span className="demo-chip" style={{ background: "rgba(255,255,255,0.1)", fontSize: "0.75rem" }}>Sore Throat</span>
              <span className="demo-chip" style={{ background: "rgba(255,255,255,0.1)", fontSize: "0.75rem" }}>Sneezing</span>
            </div>
            <span className="label" style={{ marginTop: 12 }}>Suggested Next Steps</span>
            <div className="med-pill-row" style={{ marginTop: 6 }}>
              <span className="med-pill">Rest &amp; Hydration</span>
              <span className="med-pill">Symptom Monitoring</span>
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
          <span className="eyebrow">Interactive Workflow</span>
          <h2>Three Steps to Medical Intelligence</h2>
          <p>Structure your symptoms, analyze candidate diseases, and track your personalized history.</p>
        </motion.div>

        <div className="steps-grid">
          {[
            { icon: UserPlus, num: "01", title: "Create Your Account", desc: "A private healthcare profile storing your personal prediction history securely." },
            { icon: ClipboardList, num: "02", title: "Select Symptoms & Vitals", desc: "Choose from 230 tracked clinical symptoms with real-time multi-symptom search." },
            { icon: Brain, num: "03", title: "Multi-Model AI Diagnosis", desc: "Receive primary prediction, top 3 candidate diseases, expected symptoms, and risk level." },
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

      {/* ---------------- WHY PERSONALIZED ---------------- */}
      <section className="section">
        <motion.div
          className="section-head"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.4 }} variants={fadeUp}
        >
          <span className="eyebrow"><Sparkles size={13} style={{ marginRight: 4 }} />Personalized AI History</span>
          <h2>It Remembers, so It Gets Sharper Over Time</h2>
          <p>Every check is saved to your private profile history. Health patterns across visits provide deep medical context.</p>
        </motion.div>

        <motion.div
          className="timeline"
          initial="hidden" whileInView="show" viewport={{ once: true, amount: 0.3 }} variants={fadeUp}
        >
          <div className="timeline-item">
            <div className="timeline-dot"><Stethoscope size={18} /></div>
            <div className="timeline-content">
              <div className="t-title">First Check-in Logged</div>
              <div className="t-desc">Symptom selection saved with local timestamp &amp; risk rating.</div>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-dot"><Activity size={18} /></div>
            <div className="timeline-content">
              <div className="t-title">Follow-up Analysis</div>
              <div className="t-desc">Symptom progression tracked against previous diagnostic records.</div>
            </div>
          </div>
          <div className="timeline-item">
            <div className="timeline-dot"><TrendingUp size={18} /></div>
            <div className="timeline-content">
              <div className="t-title">Personalized Recommendation Matrix</div>
              <div className="t-desc">SVD Collaborative Filtering + Content-Based TF-IDF matching tailors care.</div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* ---------------- FOOTER ---------------- */}
      <footer className="site-footer">
        <span className="brand">MediCare AI</span>
        <span className="footer-note">Frontend: React · Backend: Flask · ML: scikit-learn &amp; Keras</span>
      </footer>
    </div>
  );
}
