/**
 * Analytics Service for AI Analyst Dashboard
 */
import axios from '../api/axios';
import { API_ENDPOINTS } from '../api/endpoints';

export const getAnalyticsSummary = async () => {
  const response = await axios.get(API_ENDPOINTS.ANALYTICS.SUMMARY);
  return response.data;
};

export const getPrevalenceData = async () => {
  const response = await axios.get(API_ENDPOINTS.ANALYTICS.PREVALENCE);
  return response.data;
};

export const getDriftData = async () => {
  const response = await axios.get(API_ENDPOINTS.ANALYTICS.DRIFT);
  return response.data;
};
