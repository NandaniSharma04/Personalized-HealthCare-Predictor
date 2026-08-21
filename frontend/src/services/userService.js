import api from './api';

export const getProfile = async () => {
  const res = await api.get('/api/user/profile');
  return res.data;
};

export const updateProfile = async (tokenOrData, maybeData) => {
  const data = maybeData !== undefined ? maybeData : tokenOrData;
  const res = await api.put('/api/user/profile', data);
  return res.data;
};

export const getMedical = async () => {
  const res = await api.get('/api/user/health-profile');
  return res.data;
};

export const updateMedical = async (tokenOrData, maybeData) => {
  const data = maybeData !== undefined ? maybeData : tokenOrData;
  const res = await api.put('/api/user/health-profile', data);
  return res.data;
};
