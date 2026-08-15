import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // On first load, check active session from backend
  useEffect(() => {
    api
      .get("/api/auth/me")
      .then((res) => {
        if (res.data && res.data.logged_in) setUser(res.data.user);
      })
      .catch(() => {
        // Session not active
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password, remember = false) {
    const res = await api.post("/api/auth/login", { email, password, remember });
    if (res.data && res.data.user) {
      setUser(res.data.user);
    }
    return res.data;
  }

  async function signup(name, email, password, role = "user") {
    const res = await api.post("/api/auth/register", { name, email, password, role });
    if (res.data && res.data.user) {
      setUser(res.data.user);
    }
    return res.data;
  }

  async function logout() {
    try {
      await api.post("/api/auth/logout");
    } catch (err) {
      console.warn("Logout API failed:", err);
    } finally {
      setUser(null);
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
