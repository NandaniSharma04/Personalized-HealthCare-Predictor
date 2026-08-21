import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Mail, Lock, User, Sparkles, CheckCircle } from "lucide-react";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!form.name.trim()) {
      setError("Please enter your full name.");
      return;
    }
    if (form.password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);
    try {
      const result = await signup(form.name, form.email, form.password);
      if (result && result.success === false) {
        setError(result.error || "Registration failed. Please try again.");
        return;
      }
      // Show success message then redirect to LOGIN (user must sign in)
      setSuccess(true);
      setTimeout(() => {
        navigate("/login");
      }, 1800);
    } catch (err) {
      const msg =
        err.response?.data?.error ||
        err.response?.data?.message ||
        err.message ||
        "Registration failed. Please check your details or sign in if you already have an account.";
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  }

  const inputStyle = {
    width: "100%",
    padding: "9px 12px 9px 34px",
    background: "rgba(15, 23, 42, 0.6)",
    border: "1px solid rgba(255, 255, 255, 0.12)",
    borderRadius: "10px",
    color: "#ffffff",
    fontSize: "0.82rem",
    boxSizing: "border-box",
    outline: "none",
  };

  const labelStyle = {
    display: "block",
    fontSize: "0.72rem",
    fontWeight: "600",
    color: "#cbd5e1",
    marginBottom: "4px",
  };

  const iconStyle = {
    position: "absolute",
    left: "10px",
    top: "11px",
    color: "#64748b",
  };

  return (
    <div style={{
      minHeight: "80vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "24px 16px",
    }}>
      <div style={{
        width: "100%",
        maxWidth: "420px",
        background: "rgba(15, 23, 42, 0.88)",
        backdropFilter: "blur(20px)",
        WebkitBackdropFilter: "blur(20px)",
        border: "1px solid rgba(255, 255, 255, 0.12)",
        borderRadius: "20px",
        padding: "30px 26px",
        boxShadow: "0 25px 50px -12px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.05)",
        color: "#f8fafc",
      }}>

        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: "18px" }}>
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
            textTransform: "uppercase",
          }}>
            <Sparkles size={12} />
            Patient Portal
          </span>
          <h1 style={{ fontSize: "1.45rem", fontWeight: "700", margin: "8px 0 2px", color: "#ffffff" }}>
            Create Your Account
          </h1>
          <p style={{ fontSize: "0.78rem", color: "#94a3b8", margin: 0 }}>
            Join HealthAI for AI-powered disease prediction
          </p>
        </div>

        {/* Success Message */}
        {success && (
          <div style={{
            background: "rgba(34, 197, 94, 0.15)",
            border: "1px solid rgba(34, 197, 94, 0.35)",
            color: "#4ade80",
            padding: "10px 14px",
            borderRadius: "10px",
            fontSize: "0.82rem",
            marginBottom: "14px",
            display: "flex",
            alignItems: "center",
            gap: "8px",
            fontWeight: "600",
          }}>
            <CheckCircle size={16} />
            Account created! Redirecting to login...
          </div>
        )}

        {/* Error Message */}
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
            gap: "6px",
          }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        {!success && (
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "12px" }}>

            {/* Full Name */}
            <div>
              <label style={labelStyle}>Full Name</label>
              <div style={{ position: "relative" }}>
                <User size={15} style={iconStyle} />
                <input
                  type="text"
                  required
                  placeholder="Your full name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label style={labelStyle}>Email Address</label>
              <div style={{ position: "relative" }}>
                <Mail size={15} style={iconStyle} />
                <input
                  type="email"
                  required
                  placeholder="you@example.com"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label style={labelStyle}>Password</label>
              <div style={{ position: "relative" }}>
                <Lock size={15} style={iconStyle} />
                <input
                  type="password"
                  required
                  placeholder="Min. 6 characters"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  style={inputStyle}
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label style={labelStyle}>Confirm Password</label>
              <div style={{ position: "relative" }}>
                <Lock size={15} style={iconStyle} />
                <input
                  type="password"
                  required
                  placeholder="Repeat your password"
                  value={form.confirmPassword}
                  onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                  style={{
                    ...inputStyle,
                    borderColor: form.confirmPassword && form.password !== form.confirmPassword
                      ? "rgba(239, 68, 68, 0.5)"
                      : form.confirmPassword && form.password === form.confirmPassword
                        ? "rgba(34, 197, 94, 0.5)"
                        : "rgba(255, 255, 255, 0.12)",
                  }}
                />
              </div>
              {form.confirmPassword && form.password !== form.confirmPassword && (
                <p style={{ fontSize: "0.7rem", color: "#f87171", marginTop: "3px" }}>Passwords do not match</p>
              )}
            </div>

            {/* Submit */}
            <button
              type="submit"
              disabled={submitting}
              style={{
                width: "100%",
                padding: "11px",
                marginTop: "4px",
                background: submitting ? "rgba(37, 99, 235, 0.5)" : "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
                border: "1px solid rgba(255,255,255,0.15)",
                borderRadius: "10px",
                color: "#ffffff",
                fontSize: "0.85rem",
                fontWeight: "600",
                cursor: submitting ? "not-allowed" : "pointer",
                boxShadow: "0 4px 14px rgba(37, 99, 235, 0.4)",
                transition: "all 0.2s ease",
              }}
            >
              {submitting ? "Creating account..." : "Create Account"}
            </button>
          </form>
        )}

        {/* Footer Link */}
        <div style={{ marginTop: "16px", textAlign: "center", fontSize: "0.78rem", color: "#94a3b8" }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "#38bdf8", fontWeight: "600", textDecoration: "none" }}>
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
