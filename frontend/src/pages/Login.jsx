import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ShieldCheck, UserCheck, Mail, Lock, Sparkles } from "lucide-react";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  // If user is already authenticated, redirect immediately to dashboard
  useEffect(() => {
    if (user) {
      if (user.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    }
  }, [user, navigate]);

  // Selected login persona: 'user' | 'admin'
  const [activeRole, setActiveRole] = useState('user');
  const [form, setForm] = useState({ email: "", password: "", remember: true });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    setSubmitting(true);
    try {
      const data = await login(form.email, form.password, form.remember);

      // Save logged in user account for admin tracking
      if (data?.user) {
        const accounts = JSON.parse(localStorage.getItem("logged_in_accounts") || "[]");
        if (!accounts.some(a => a.email.toLowerCase() === data.user.email.toLowerCase())) {
          accounts.push(data.user);
          localStorage.setItem("logged_in_accounts", JSON.stringify(accounts));
        }
      }

      const userRole = data?.user?.role?.toLowerCase() || activeRole;

      if (activeRole === "admin" && userRole !== "admin") {
        setError("This account is not authorized to access the Administrator Portal.");
        return;
      }

      if (userRole === "admin") {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      setError(err.response?.data?.error || "Invalid email or password. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{
      minHeight: "75vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px 16px"
    }}>
      <div style={{
        width: "100%",
        maxWidth: "400px",
        background: "rgba(15, 23, 42, 0.85)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        border: "1px solid rgba(255, 255, 255, 0.12)",
        borderRadius: "20px",
        padding: "28px 24px",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.05)",
        color: "#f8fafc"
      }}>
        
        {/* Header Badge & Title */}
        <div style={{ textAlign: "center", marginBottom: "16px" }}>
          <span style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "5px",
            padding: "3px 10px",
            background: "rgba(59, 130, 246, 0.15)",
            border: "1px solid rgba(59, 130, 246, 0.3)",
            borderRadius: "999px",
            fontSize: "0.72rem",
            fontWeight: "600",
            color: "#60a5fa",
            letterSpacing: "0.04em",
            textTransform: "uppercase"
          }}>
            <Sparkles size={12} />
            {activeRole === 'admin' ? 'Admin Portal' : 'Patient Portal'}
          </span>
          <h1 style={{ fontSize: "1.45rem", fontWeight: "700", margin: "8px 0 2px", color: "#ffffff" }}>
            Sign In to HealthAI
          </h1>
          <p style={{ fontSize: "0.78rem", color: "#94a3b8", margin: 0 }}>
            {activeRole === 'admin' ? 'System governance and analytics console' : 'Access your personalized healthcare predictions'}
          </p>
        </div>

        {/* 2-Role Selector Tabs: Patient and Admin */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "6px",
          background: "rgba(30, 41, 59, 0.7)",
          padding: "4px",
          borderRadius: "12px",
          marginBottom: "18px",
          border: "1px solid rgba(255, 255, 255, 0.06)"
        }}>
          <button
            type="button"
            style={{
              padding: "7px 4px",
              fontSize: "0.75rem",
              fontWeight: "600",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              transition: "all 0.2s",
              background: activeRole === 'user' ? "linear-gradient(135deg, #2563eb, #1d4ed8)" : "transparent",
              color: activeRole === 'user' ? "#ffffff" : "#94a3b8",
              boxShadow: activeRole === 'user' ? "0 4px 12px rgba(37, 99, 235, 0.4)" : "none"
            }}
            onClick={() => setActiveRole('user')}
          >
            <UserCheck size={13} /> Patient
          </button>
          
          <button
            type="button"
            style={{
              padding: "7px 4px",
              fontSize: "0.75rem",
              fontWeight: "600",
              borderRadius: "8px",
              border: "none",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "4px",
              transition: "all 0.2s",
              background: activeRole === 'admin' ? "linear-gradient(135deg, #2563eb, #1d4ed8)" : "transparent",
              color: activeRole === 'admin' ? "#ffffff" : "#94a3b8",
              boxShadow: activeRole === 'admin' ? "0 4px 12px rgba(37, 99, 235, 0.4)" : "none"
            }}
            onClick={() => setActiveRole('admin')}
          >
            <ShieldCheck size={13} /> Administrator
          </button>
        </div>

        {/* Error Notification */}
        {error && (
          <div style={{
            background: "rgba(239, 68, 68, 0.15)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            color: "#fca5a5",
            padding: "8px 12px",
            borderRadius: "10px",
            fontSize: "0.75rem",
            marginBottom: "14px",
            display: "flex",
            alignItems: "center",
            gap: "6px"
          }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.75rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "4px" }}>
              Email Address
            </label>
            <div style={{ position: "relative" }}>
              <Mail size={15} style={{ position: "absolute", left: "10px", top: "11px", color: "#64748b" }} />
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                style={{
                  width: "100%",
                  padding: "9px 12px 9px 34px",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: "10px",
                  color: "#ffffff",
                  fontSize: "0.82rem",
                  boxSizing: "border-box"
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.75rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "4px" }}>
              Password
            </label>
            <div style={{ position: "relative" }}>
              <Lock size={15} style={{ position: "absolute", left: "10px", top: "11px", color: "#64748b" }} />
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                style={{
                  width: "100%",
                  padding: "9px 12px 9px 34px",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: "10px",
                  color: "#ffffff",
                  fontSize: "0.82rem",
                  boxSizing: "border-box"
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            style={{
              width: "100%",
              padding: "11px",
              marginTop: "4px",
              background: "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              borderRadius: "10px",
              color: "#ffffff",
              fontSize: "0.85rem",
              fontWeight: "600",
              cursor: submitting ? "not-allowed" : "pointer",
              boxShadow: "0 4px 14px rgba(37, 99, 235, 0.4)",
              transition: "all 0.2s ease"
            }}
          >
            {submitting ? "Signing in..." : `Sign in as ${activeRole === 'admin' ? 'Administrator' : 'Patient'}`}
          </button>
        </form>

        <div style={{ marginTop: "16px", textAlign: "center", fontSize: "0.78rem", color: "#94a3b8" }}>
          Don't have an account?{" "}
          <Link to="/signup" style={{ color: "#38bdf8", fontWeight: "600", textDecoration: "none" }}>
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
