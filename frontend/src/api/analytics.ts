import apiClient from "./client";

export const getSummary = async () => {
  const res = await apiClient.get("/analytics/summary");
  return res.data;
};

export const getMethodFrequency = async () => {
  const res = await apiClient.get("/analytics/methods/frequency");
  return res.data;
};

export const getLeakDistribution = async () => {
  const res = await apiClient.get("/analytics/leaks/distribution");
  return res.data;
};

export const getRiskDistribution = async () => {
  const res = await apiClient.get("/analytics/risk/distribution");
  return res.data;
};