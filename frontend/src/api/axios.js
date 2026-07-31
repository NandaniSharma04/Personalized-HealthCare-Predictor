import axios from "axios";

// All requests go to the Flask API. `withCredentials: true` is required
// so the browser sends/receives the session cookie Flask-Login uses --
// without this, login would appear to work but you'd get logged out on
// every page refresh.
const api = axios.create({
  baseURL: "http://localhost:5000",
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});

export default api;
