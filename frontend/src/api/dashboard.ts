import apiClient from "./client";

export const getMonitorStatus = async () => {
  const res = await apiClient.get("/dashboard/monitor/status");
  return res.data;
};

export const getLeakStream = async (limit = 20, offset = 0) => {
  const res = await apiClient.get(
    `/dashboard/monitor/leaks/stream?limit=${limit}&offset=${offset}`
  );
  return res.data;
};

export const getRiskMetrics = async () => {
  const res = await apiClient.get("/dashboard/monitor/risk/metrics");
  return res.data;
};

export const getTimelineReport = async (timeRange = "last_7d") => {
  const res = await apiClient.get(
    `/dashboard/reports/timeline?time_range=${timeRange}`
  );
  return res.data;
};

export const getHeatmap = async (heatmapType: string) => {
  const res = await apiClient.get(
    `/dashboard/reports/heatmap?heatmap_type=${heatmapType}`
  );
  return res.data;
};

export const getAllCharts = async (timeRange = "last_7d") => {
  const res = await apiClient.get(
    `/dashboard/charts?time_range=${timeRange}`
  );
  return res.data;
};

export const generateComprehensiveReport = async (timeRange = "last_24h") => {
  const res = await apiClient.post(
    `/dashboard/comprehensive-report?time_range=${timeRange}`
  );
  return res.data;
};