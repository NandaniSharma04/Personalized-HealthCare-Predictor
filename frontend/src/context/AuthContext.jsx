import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const localUser = localStorage.getItem("currentUser");
    if (localUser) {
      try {
        const parsed = JSON.parse(localUser);
        if (parsed && parsed.id) return parsed;
      } catch (e) {}
    }
    return null;
  });
  const [loading, setLoading] = useState(true);

  // On first load, check active session from backend
  useEffect(() => {
    api
      .get("/api/auth/me")
      .then((res) => {
        if (res.data && res.data.logged_in && res.data.user) {
          setUser(res.data.user);
          localStorage.setItem("currentUser", JSON.stringify(res.data.user));
        } else {
          setUser(null);
          localStorage.removeItem("currentUser");
        }
      })
      .catch(() => {
        // If session check fails and no valid localStorage user, clear state
        const localUser = localStorage.getItem("currentUser");
        if (!localUser) {
          setUser(null);
        }
      })
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
    if (userData) {
      localStorage.setItem("currentUser", JSON.stringify(userData));
      setUser(userData);
    } else {
      localStorage.removeItem("currentUser");
      setUser(null);
    }
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
