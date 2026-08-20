import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

const DEFAULT_PATIENT = {
  id: 1,
  name: "Patient",
  email: "patient@healthai.org",
  role: "user"
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const localUser = localStorage.getItem("currentUser");
    if (localUser) {
      try {
        const parsed = JSON.parse(localUser);
        if (parsed) return parsed;
      } catch (e) {}
    }
    return DEFAULT_PATIENT;
  });
  const [loading, setLoading] = useState(true);

  // On first load, check active session from backend
  useEffect(() => {
    api
      .get("/api/auth/me")
      .then((res) => {
        if (res.data && res.data.logged_in) {
          setUser(res.data.user);
          localStorage.setItem("currentUser", JSON.stringify(res.data.user));
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password, remember = false) {
    const res = await api.post("/api/auth/login", { email, password, remember });
    if (res.data && res.data.user) {
      setUser(res.data.user);
      localStorage.setItem("currentUser", JSON.stringify(res.data.user));
    }
    return res.data;
  }

  async function signup(name, email, password, role = "user") {
    const res = await api.post("/api/auth/register", { name, email, password, role });
    if (res.data && res.data.user) {
      setUser(res.data.user);
      localStorage.setItem("currentUser", JSON.stringify(res.data.user));
    }
    return res.data;
  }

  async function logout() {
    try {
      await api.post("/api/auth/logout");
    } catch (err) {
      console.warn("Logout API failed:", err);
    } finally {
      localStorage.removeItem("currentUser");
      setUser(null);
    }
  }

  const setDirectUser = (userData) => {
    localStorage.setItem("currentUser", JSON.stringify(userData));
    setUser(userData);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, setDirectUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
