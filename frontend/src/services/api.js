import axios from 'axios'

const DEFAULT_BACKEND_URL = "https://personalized-healthcare-predictor-2.onrender.com"

const envBase = typeof import.meta !== 'undefined' && import.meta.env
  ? (import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL)
  : undefined

const BASE = envBase || (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.DEV ? '/api' : DEFAULT_BACKEND_URL)

const api = axios.create({
  baseURL: BASE,
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' }
})

export default api
