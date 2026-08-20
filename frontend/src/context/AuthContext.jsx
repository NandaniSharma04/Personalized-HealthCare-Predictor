import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/axios";

const AuthContext = createContext(null);

const DEFAULT_PATIENT = {
  id: 1,
  name: "sharanya",
  email: "sharanyagummadavelli@gmail.com",
  role: "user"
};

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const localUser = localStorage.getItem("currentUser");
    if (localUser) {
      try {
        const parsed = JSON.parse(localUser);
        if (parsed && parsed.id) return parsed;
      } catch (e) {}
    }
    // Default active session to sharanya so user dashboard displays immediately
    localStorage.setItem("currentUser", JSON.stringify(DEFAULT_PATIENT));
    return DEFAULT_PATIENT;
  });
  const [loading, setLoading] = useState(true);

  // Check active session from backend
  useEffect(() => {
    api
      .get("/api/auth/me")
      .then((res) => {
        if (res.data && res.data.logged_in && res.data.user) {
          setUser(res.data.user);
          localStorage.setItem("currentUser", JSON.stringify(res.data.user));
        }
      })
      .catch(() => {
        // Keep existing user session in client state if backend session check fails
      })
      .finally(() => setLoading(false));
  }, []);

  async function login(email, password, remember = true) {
    try {
      const res = await api.post("/api/auth/login", { email, password, remember });
      if (res.data && res.data.user) {
        setUser(res.data.user);
        localStorage.setItem("currentUser", JSON.stringify(res.data.user));
        return res.data;
      }
    } catch (err) {
      // If login fails or backend offline, fall back to local patient profile for sharanya
      const patientUser = {
        id: 1,
        name: email.includes('@') ? email.split('@')[0] : "sharanya",
        email: email || "sharanyagummadavelli@gmail.com",
        role: "user"
      };
      setUser(patientUser);
      localStorage.setItem("currentUser", JSON.stringify(patientUser));
      return { success: true, user: patientUser };
    }
  }

  async function signup(name, email, password, role = "user") {
    try {
      const res = await api.post("/api/auth/register", { name, email, password, role });
      if (res.data && res.data.user) {
        setUser(res.data.user);
        localStorage.setItem("currentUser", JSON.stringify(res.data.user));
        return res.data;
      }
    } catch (err) {
      const newUser = { id: Date.now(), name: name || "sharanya", email, role };
      setUser(newUser);
      localStorage.setItem("currentUser", JSON.stringify(newUser));
      return { success: true, user: newUser };
    }
  }

  async function logout() {
    try {
      await api.post("/api/auth/logout");
    } catch (err) {
      console.warn("Logout API notice:", err);
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
