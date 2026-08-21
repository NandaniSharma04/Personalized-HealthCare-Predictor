import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import AdminDashboard from "./dashboards/admin/AdminDashboard";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Predictor from "./pages/Predictor";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <video
          className="site-video-bg"
          src="/videos/Background_video.mp4"
          autoPlay
          loop
          muted
          playsInline
        />
        <div className="site-video-overlay" />

        <div className="site-content">
          <Navbar />
          <Routes>
            {/* Public Landing & Auth Routes */}
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/register" element={<Signup />} />
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />

            {/* Disease Predictor — Public: accessible without login */}
            <Route path="/predictor" element={<Predictor />} />
            <Route path="/prediction" element={<Predictor />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="dashboard" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/predictions"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="history" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/personalized-care"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="recommendations" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/health-insights"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="insights" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/activity"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="activity" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/saved-plans"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="saved" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/notifications"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="notifications" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="profile" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <Dashboard defaultTab="settings" />
                </ProtectedRoute>
              }
            />

            {/* Admin Dashboard — Admin only */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
