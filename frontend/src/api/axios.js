import axios from "axios";

// All requests go to the Flask API. `withCredentials: true` is required
// so the browser sends/receives the session cookie Flask-Login uses --
// without this, login would appear to work but you'd get logged out on
// every page refresh.
const DEFAULT_BACKEND_URL = "https://personalized-healthcare-predictor-2.onrender.com";

const resolvedBaseURL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "" : DEFAULT_BACKEND_URL);

const api = axios.create({
  baseURL: resolvedBaseURL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export default api;
