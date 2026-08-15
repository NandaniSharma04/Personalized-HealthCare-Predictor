/**
 * Health & Prediction Service
 */
import axios from '../api/axios';
import { API_ENDPOINTS } from '../api/endpoints';

export const getSymptomsList = async () => {
  const response = await axios.get(API_ENDPOINTS.HEALTH.SYMPTOMS);
  return response.data;
};

export const predictDisease = async (symptoms) => {
  const response = await axios.post(API_ENDPOINTS.HEALTH.PREDICT, { symptoms });
  return response.data;
};

export const getPredictionHistory = async () => {
  const response = await axios.get(API_ENDPOINTS.HEALTH.HISTORY);
  return response.data;
};
