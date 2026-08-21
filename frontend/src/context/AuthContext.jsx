import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check active session from backend on mount
  useEffect(() => {
    let isMounted = true;
    
    api
      .get("/api/auth/me")
      .then((res) => {
        if (isMounted) {
          if (res.data && res.data.logged_in && res.data.user) {
            setUser(res.data.user);
          } else {
            setUser(null);
          }
        }
      })
      .catch((err) => {
        if (isMounted) {
          console.warn("Auth check failed:", err);
          setUser(null);
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });
      
    return () => { isMounted = false; };
  }, []);

  async function login(email, password, remember = true) {
    try {
      const res = await api.post("/api/auth/login", { email, password, remember });
      if (res.data && res.data.user) {
        setUser(res.data.user);
        return res.data;
      }
      return { success: false, error: "Login failed to return user data." };
    } catch (err) {
      const errorMsg = err.response?.data?.error || "Invalid credentials or network error.";
      return { success: false, error: errorMsg };
    }
  }

  async function signup(name, email, password, role = "user") {
    try {
      // Pass role only if necessary, though backend usually forces 'user' for public signup
      const res = await api.post("/api/auth/register", { name, email, password, role });
      if (res.data && res.data.user) {
        setUser(res.data.user);
        return res.data;
      }
      return { success: false, error: "Registration failed to return user data." };
    } catch (err) {
      const errorMsg = err.response?.data?.error || "Registration failed. Please try again.";
      return { success: false, error: errorMsg };
    }
  }

  async function logout() {
    try {
      await api.post("/api/auth/logout");
    } catch (err) {
      console.warn("Logout API notice:", err);
    } finally {
      setUser(null);
    }
  }

  const setDirectUser = (userData) => {
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
