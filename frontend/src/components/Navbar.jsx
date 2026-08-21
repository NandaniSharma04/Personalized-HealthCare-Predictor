import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogIn, LogOut, UserPlus, ShieldCheck, User, HeartPulse } from "lucide-react";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  const role = user?.role?.toLowerCase();
  const isAdmin = role === "admin";

  return (
    <nav className="navbar">
      <Link to="/" className="brand">
        <HeartPulse size={22} className="accent-text" style={{ marginRight: 6 }} />
        <span>MediCare AI</span>
      </Link>
      
      <div className="nav-links">
        <Link to="/">Home</Link>

        {/* Disease Predictor — public, visible to everyone */}
        <Link to="/predictor">Disease Predictor</Link>

        {/* Role-specific dashboard link */}
        {isAdmin ? (
          <Link to="/admin" className="role-nav-highlight">
            <ShieldCheck size={14} className="inline mr-1" /> Admin Dashboard
          </Link>
        ) : user ? (
          <Link to="/dashboard">
            <User size={14} className="inline mr-1" /> My Dashboard
          </Link>
        ) : null}

        {/* About and Contact — public */}
        <Link to="/about">About</Link>
        <Link to="/contact">Contact</Link>
        
        {user ? (
          <div className="flex-center-y gap-2">
            <span
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                padding: "4px 8px",
                background: "rgba(59, 130, 246, 0.15)",
                border: "1px solid rgba(59, 130, 246, 0.3)",
                borderRadius: "6px",
                fontSize: "0.72rem",
                fontWeight: "600",
                color: "#60a5fa",
                textTransform: "uppercase"
              }}
            >
              {isAdmin ? <ShieldCheck size={12} /> : <User size={12} />}
              {role || 'USER'}
            </span>
            
            <button
              onClick={handleLogout}
              className="btn-outline text-xs"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "5px",
                padding: "6px 12px",
                borderRadius: "8px",
                cursor: "pointer"
              }}
            >
              <LogOut size={14} /> Log out
            </button>
          </div>
        ) : (
          <div className="flex-center-y gap-2">
            <Link
              to="/login"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                fontSize: "0.85rem",
                color: "#e2e8f0"
              }}
            >
              <LogIn size={15} /> Log in
            </Link>
            
            <button
              onClick={() => navigate("/signup")}
              className="btn-primary text-xs"
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: "4px",
                padding: "6px 14px",
                borderRadius: "8px",
                cursor: "pointer"
              }}
            >
              <UserPlus size={14} /> Sign up
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}