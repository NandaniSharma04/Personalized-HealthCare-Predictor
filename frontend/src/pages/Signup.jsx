import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { UserPlus, ShieldCheck, UserCheck, Mail, Lock, User, Sparkles } from "lucide-react";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "user" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      const data = await signup(form.name, form.email, form.password, form.role);
      const userRole = data?.user?.role?.toLowerCase() || form.role;

      if (userRole === "admin") {
        navigate("/admin");
      } else {
        navigate("/dashboard");
      }
    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.message || err.message || "Registration failed. Please try again.";
      setError(msg);
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
            Instant Medical Access
          </span>
          <h1 style={{ fontSize: "1.45rem", fontWeight: "700", margin: "8px 0 2px", color: "#ffffff" }}>
            Create Your Account
          </h1>
          <p style={{ fontSize: "0.78rem", color: "#94a3b8", margin: 0 }}>
            Join HealthAI for AI-assisted clinical diagnosis and personalized care plans
          </p>
        </div>

        {/* 2-Role Selector */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "6px",
          background: "rgba(30, 41, 59, 0.7)",
          padding: "4px",
          borderRadius: "12px",
          marginBottom: "14px",
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
              background: form.role === 'user' ? "linear-gradient(135deg, #2563eb, #1d4ed8)" : "transparent",
              color: form.role === 'user' ? "#ffffff" : "#94a3b8",
              boxShadow: form.role === 'user' ? "0 4px 12px rgba(37, 99, 235, 0.4)" : "none"
            }}
            onClick={() => setForm({ ...form, role: 'user' })}
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
              background: form.role === 'admin' ? "linear-gradient(135deg, #2563eb, #1d4ed8)" : "transparent",
              color: form.role === 'admin' ? "#ffffff" : "#94a3b8",
              boxShadow: form.role === 'admin' ? "0 4px 12px rgba(37, 99, 235, 0.4)" : "none"
            }}
            onClick={() => setForm({ ...form, role: 'admin' })}
          >
            <ShieldCheck size={13} /> Administrator
          </button>
        </div>

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

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          <div>
            <label style={{ display: "block", fontSize: "0.72rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "3px" }}>
              Full Name
            </label>
            <div style={{ position: "relative" }}>
              <User size={14} style={{ position: "absolute", left: "10px", top: "10px", color: "#64748b" }} />
              <input
                type="text"
                required
                placeholder="Dr. Jane Doe"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                style={{
                  width: "100%",
                  padding: "8px 12px 8px 32px",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: "10px",
                  color: "#ffffff",
                  fontSize: "0.8rem",
                  boxSizing: "border-box"
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.72rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "3px" }}>
              Email Address
            </label>
            <div style={{ position: "relative" }}>
              <Mail size={14} style={{ position: "absolute", left: "10px", top: "10px", color: "#64748b" }} />
              <input
                type="email"
                required
                placeholder="jane@example.com"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                style={{
                  width: "100%",
                  padding: "8px 12px 8px 32px",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: "10px",
                  color: "#ffffff",
                  fontSize: "0.8rem",
                  boxSizing: "border-box"
                }}
              />
            </div>
          </div>

          <div>
            <label style={{ display: "block", fontSize: "0.72rem", fontWeight: "600", color: "#cbd5e1", marginBottom: "3px" }}>
              Password
            </label>
            <div style={{ position: "relative" }}>
              <Lock size={14} style={{ position: "absolute", left: "10px", top: "10px", color: "#64748b" }} />
              <input
                type="password"
                required
                placeholder="••••••••••••"
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                style={{
                  width: "100%",
                  padding: "8px 12px 8px 32px",
                  background: "rgba(15, 23, 42, 0.6)",
                  border: "1px solid rgba(255, 255, 255, 0.12)",
                  borderRadius: "10px",
                  color: "#ffffff",
                  fontSize: "0.8rem",
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
              padding: "10px",
              marginTop: "4px",
              background: "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
              border: "1px solid rgba(255, 255, 255, 0.15)",
              borderRadius: "10px",
              color: "#ffffff",
              fontSize: "0.82rem",
              fontWeight: "600",
              cursor: submitting ? "not-allowed" : "pointer",
              boxShadow: "0 4px 14px rgba(37, 99, 235, 0.4)",
              transition: "all 0.2s ease"
            }}
          >
            {submitting ? "Registering..." : `Create ${form.role === 'admin' ? 'Admin' : 'Patient'} Account`}
          </button>
        </form>

        <div style={{ marginTop: "14px", textAlign: "center", fontSize: "0.75rem", color: "#94a3b8" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "#38bdf8", fontWeight: "600", textDecoration: "none" }}>
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
