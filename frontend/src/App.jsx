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
import AnalystDashboard from "./dashboards/analyst/AnalystDashboard";
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
            <Route path="/about" element={<About />} />
            <Route path="/contact" element={<Contact />} />

            {/* Main Interactive Routes */}
            <Route path="/predictor" element={<Predictor />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route
              path="/admin"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/analyst"
              element={
                <ProtectedRoute allowedRoles={["analyst", "admin"]}>
                  <AnalystDashboard />
                </ProtectedRoute>
              }
            />
          </Routes>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
}
