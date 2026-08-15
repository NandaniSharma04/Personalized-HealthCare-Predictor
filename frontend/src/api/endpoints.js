/**
 * Centralized API Endpoint Registry
 * Maps all frontend services to verified backend endpoints.
 */
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    LOGOUT: '/api/auth/logout',
    ME: '/api/auth/me',
    CHANGE_PASSWORD: '/api/auth/change-password',
    FORGOT_PASSWORD: '/api/auth/forgot-password',
  },
  USER: {
    DASHBOARD: '/api/user/dashboard',
    PROFILE: '/api/user/profile',
    HEALTH_PROFILE: '/api/user/health-profile',
  },
  HEALTH: {
    SYMPTOMS: '/api/symptoms',
    PREDICT: '/api/predict',
    HEALTH_CHECK: '/health',
  },
  RECOMMENDATIONS: {
    GET_CARE_PLAN: '/api/recommendations',
    SAVE: '/api/recommendations/save',
    FEEDBACK: '/api/recommendations/feedback',
  },
  ANALYTICS: {
    SUMMARY: '/api/analytics/summary',
    PREVALENCE: '/api/analytics/prevalence',
    DRIFT: '/api/analytics/drift',
    MODEL_PERFORMANCE: '/api/analytics/model-performance',
    PREDICTION_ANALYTICS: '/api/analytics/prediction-analytics',
    RECOMMENDATION_ANALYTICS: '/api/analytics/recommendation-analytics',
    SENTIMENT: '/api/analytics/sentiment',
    DATA_QUALITY: '/api/analytics/data-quality',
  },
  ADMIN: {
    DASHBOARD_ANALYTICS: '/api/admin/dashboard-analytics',
    USERS: '/api/admin/users',
    USER_DETAIL: (id) => `/api/admin/users/${id}`,
    UPDATE_ROLE: (id) => `/api/admin/users/${id}/role`,
    UPDATE_STATUS: (id) => `/api/admin/users/${id}/status`,
    PREDICTIONS: '/api/admin/predictions',
    RECOMMENDATIONS: '/api/admin/recommendations',
    DISEASES: '/api/admin/diseases',
    MEDICINES: '/api/admin/medicines',
    MODELS: '/api/admin/models',
    ANALYTICS: '/api/admin/analytics',
    AUDIT_LOGS: '/api/admin/audit-logs',
    SETTINGS: '/api/admin/settings',
  }
};
