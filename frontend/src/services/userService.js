import api from './api'

export const getProfile = async (token) => {
  const res = await api.get('/users/me', { headers: { Authorization: `Bearer ${token}` } })
  return res.data
}

export const updateProfile = async (token, data) => {
  const res = await api.put('/users/me', data, { headers: { Authorization: `Bearer ${token}` } })
  return res.data
}

export const getMedical = async (token) => {
  const res = await api.get('/users/me/medical', { headers: { Authorization: `Bearer ${token}` } })
  return res.data
}

export const updateMedical = async (token, data) => {
  const res = await api.put('/users/me/medical', data, { headers: { Authorization: `Bearer ${token}` } })
  return res.data
}
