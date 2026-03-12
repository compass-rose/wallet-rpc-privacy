import apiClient from "./client";

export const getSessions = async (skip = 0, limit = 50) => {
  const res = await apiClient.get(`/sessions?skip=${skip}&limit=${limit}`);
  return res.data;
};

export const getSessionDetail = async (id: string) => {
  const res = await apiClient.get(`/sessions/${id}`);
  return res.data;
};

export const createSession = async (payload: {
  wallet_type: string;
  rpc_provider: string;
}) => {
  const res = await apiClient.post("/sessions", payload);
  return res.data;
};

export const deleteSession = async (id: string) => {
  const res = await apiClient.delete(`/sessions/${id}`);
  return res.data;
};