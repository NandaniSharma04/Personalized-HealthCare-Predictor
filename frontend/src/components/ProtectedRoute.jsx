import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="page-loading flex-center" style={{ minHeight: "60vh" }}>
        <div className="spinner-border"></div>
        <p style={{ marginTop: "12px", color: "#94a3b8" }}>Authenticating session...</p>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const role = user.role?.toLowerCase() || "user";
    if (!allowedRoles.includes(role) && role !== "admin") {
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
}
