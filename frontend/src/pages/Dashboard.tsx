import { useEffect, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import {
  generateComprehensiveReport,
  getAllCharts,
  getHeatmap,
  getLeakStream,
  getMonitorStatus,
  getRiskMetrics,
  getTimelineReport,
} from "../api/dashboard";

type MonitorStatus = {
  active_sessions: number;
  total_sessions: number;
  capturing: boolean;
  today_packets: number;
  today_leaks: number;
  capture_rate: number;
  last_capture_time: string;
};

type LeakItem = {
  id: string;
  session_id: string;
  leak_type: string;
  method_name: string;
  description: string;
  confidence: number;
  confidence_interval_low: number;
  confidence_interval_high: number;
  timestamp: string;
  created_at: string;
  address_hash: string;
  rule_id: string;
};

type RiskMetrics = {
  current_risk_level: string;
  average_risk_score: number;
  high_risk_sessions: number;
  medium_risk_sessions: number;
  low_risk_sessions: number;
  risk_trend: string;
  confidence: number;
  last_updated: string;
};

type TimelineEvent = {
  timestamp: string;
  event_type: string;
  leak_type: string | null;
  risk_score: number | null;
  description: string;
  session_id: string;
};

type HeatmapCell = {
  row_label: string;
  col_label: string;
  value: number;
  count: number;
};

type ChartDataPoint = {
  x: string;
  y: number;
};

type ChartSeries = {
  label: string;
  data_points: ChartDataPoint[];
};

type DashboardChart = {
  chart_type: string;
  title: string;
  x_axis_label?: string;
  y_axis_label?: string;
  series: ChartSeries[];
};

type ComprehensiveReport = {
  report_metadata?: {
    generated_at: string;
    time_range: string;
    num_sessions_tested: number;
    total_sessions: number;
  };
  results?: Record<string, any>;
};

function formatUTCToBeijing(time?: string) {
  if (!time) return "-";

  let normalized = time.trim();

  // 已经带时区，直接用
  if (
    !normalized.endsWith("Z") &&
    !/[+-]\d{2}:\d{2}$/.test(normalized)
  ) {
    normalized = `${normalized}Z`;
  }

  const date = new Date(normalized);
  if (Number.isNaN(date.getTime())) return "-";

  const formatted = date.toLocaleString("zh-CN", {
    timeZone: "Asia/Shanghai",
    hour12: false,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  return formatted.replace(/\//g, "-");
}

function formatUTCToBeijingSplit(time?: string) {
  const full = formatUTCToBeijing(time);
  const [date = "-", clock = "-"] = full.split(" ");
  return { date, clock };
}

function RiskBadge({ level }: { level: string }) {
  const normalized = (level || "").toLowerCase();

  let bg = "#374151";
  let color = "#e5e7eb";

  if (normalized === "low") {
    bg = "rgba(16,185,129,0.15)";
    color = "#34d399";
  } else if (normalized === "medium") {
    bg = "rgba(245,158,11,0.15)";
    color = "#fbbf24";
  } else if (normalized === "high") {
    bg = "rgba(239,68,68,0.15)";
    color = "#f87171";
  } else if (normalized === "critical") {
    bg = "rgba(168,85,247,0.18)";
    color = "#c084fc";
  }

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "6px 12px",
        borderRadius: "999px",
        background: bg,
        color,
        fontSize: "13px",
        fontWeight: 700,
        textTransform: "uppercase",
      }}
    >
      {level || "-"}
    </span>
  );
}

function SectionCard({
  title,
  subtitle,
  children,
  action,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <div style={sectionCardStyle}>
      <div style={sectionHeaderStyle}>
        <div>
          <h2 style={sectionTitleStyle}>{title}</h2>
          {subtitle ? <p style={sectionSubtitleStyle}>{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

function EmptyState({ text }: { text: string }) {
  return (
    <div
      style={{
        height: 280,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#9ca3af",
        fontSize: "15px",
      }}
    >
      {text}
    </div>
  );
}

export default function Dashboard() {
  const [status, setStatus] = useState<MonitorStatus | null>(null);
  const [leaks, setLeaks] = useState<LeakItem[]>([]);
  const [riskMetrics, setRiskMetrics] = useState<RiskMetrics | null>(null);
  const [timelineEvents, setTimelineEvents] = useState<TimelineEvent[]>([]);
  const [timelineSummary, setTimelineSummary] = useState<any>(null);
  const [heatmapRows, setHeatmapRows] = useState<string[]>([]);
  const [heatmapCols, setHeatmapCols] = useState<string[]>([]);
  const [heatmapCells, setHeatmapCells] = useState<HeatmapCell[]>([]);
  const [charts, setCharts] = useState<DashboardChart[]>([]);
  const [report, setReport] = useState<ComprehensiveReport | null>(null);

  const [timeRange, setTimeRange] = useState("last_7d");
  const [heatmapType, setHeatmapType] = useState("timeofday");
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);

  const fetchDashboard = async () => {
    try {
      setLoading(true);

      const [
        statusRes,
        leaksRes,
        riskRes,
        timelineRes,
        heatmapRes,
        chartsRes,
      ] = await Promise.all([
        getMonitorStatus(),
        getLeakStream(5, 0),
        getRiskMetrics(),
        getTimelineReport(timeRange),
        getHeatmap(heatmapType),
        getAllCharts(timeRange),
      ]);

      setStatus(statusRes.data || null);
      setLeaks(leaksRes.data?.events || leaksRes.data?.leaks || [])
      setRiskMetrics(riskRes.data || null);

      setTimelineEvents(timelineRes.data?.events || []);
      setTimelineSummary(timelineRes.data?.summary || null);

      setHeatmapRows(heatmapRes.data?.row_labels || []);
      setHeatmapCols(heatmapRes.data?.col_labels || []);
      setHeatmapCells(heatmapRes.data?.cells || []);

      setCharts(chartsRes.data?.charts || []);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, [timeRange, heatmapType]);

  const handleGenerateReport = async () => {
    try {
      setReportLoading(true);
      const res = await generateComprehensiveReport("last_24h");
      setReport(res.data || null);
    } catch (error) {
      console.error("Failed to generate report:", error);
    } finally {
      setReportLoading(false);
    }
  };

  const timelineChart = useMemo(() => {
    const chart = charts.find((item) => item.chart_type === "timeline");
    if (!chart) return null;

    const xAxis = chart.series[0]?.data_points.map((point) => point.x) || [];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#111827",
        borderColor: "#374151",
        textStyle: { color: "#f9fafb" },
      },
      legend: {
        top: 0,
        textStyle: { color: "#d1d5db" },
      },
      grid: {
        left: 50,
        right: 20,
        top: 50,
        bottom: 30,
      },
      xAxis: {
        type: "category",
        data: xAxis,
        axisLabel: { color: "#d1d5db" },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#d1d5db" },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      series: chart.series.map((series) => ({
        name: series.label,
        type: "line",
        smooth: true,
        data: series.data_points.map((point) => point.y),
      })),
    };
  }, [charts]);

  const riskPieChart = useMemo(() => {
    const chart = charts.find((item) => item.chart_type === "pie");
    if (!chart) return null;

    const points = chart.series[0]?.data_points || [];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        backgroundColor: "#111827",
        borderColor: "#374151",
        textStyle: { color: "#f9fafb" },
      },
      legend: {
        bottom: 0,
        textStyle: { color: "#d1d5db" },
      },
      series: [
        {
          type: "pie",
          radius: ["42%", "72%"],
          itemStyle: {
            borderRadius: 8,
            borderColor: "#1f2937",
            borderWidth: 3,
          },
          label: { color: "#f9fafb" },
          data: points.map((point) => ({
            name: point.x,
            value: point.y,
          })),
        },
      ],
    };
  }, [charts]);

  const trafficBarChart = useMemo(() => {
    const chart = charts.find((item) => item.chart_type === "bar");
    if (!chart) return null;

    const points = chart.series[0]?.data_points || [];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#111827",
        borderColor: "#374151",
        textStyle: { color: "#f9fafb" },
      },
      grid: {
        left: 50,
        right: 20,
        top: 20,
        bottom: 30,
      },
      xAxis: {
        type: "category",
        data: points.map((point) => point.x),
        axisLabel: { color: "#d1d5db" },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#d1d5db" },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      series: [
        {
          type: "bar",
          data: points.map((point) => point.y),
          barWidth: "45%",
          itemStyle: {
            color: "#3b82f6",
            borderRadius: [10, 10, 0, 0],
          },
        },
      ],
    };
  }, [charts]);

  const latencyLineChart = useMemo(() => {
    const chart = charts.find((item) => item.chart_type === "line");
    if (!chart) return null;

    const points = chart.series[0]?.data_points || [];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#111827",
        borderColor: "#374151",
        textStyle: { color: "#f9fafb" },
      },
      grid: {
        left: 50,
        right: 20,
        top: 20,
        bottom: 30,
      },
      xAxis: {
        type: "category",
        data: points.map((point) => point.x),
        axisLabel: { color: "#d1d5db" },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      yAxis: {
        type: "value",
        axisLabel: { color: "#d1d5db" },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.08)" } },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      series: [
        {
          type: "line",
          smooth: true,
          data: points.map((point) => point.y),
          lineStyle: { color: "#10b981", width: 3 },
          itemStyle: { color: "#10b981" },
        },
      ],
    };
  }, [charts]);

  const heatmapOption = useMemo(() => {
    if (!heatmapRows.length || !heatmapCols.length) return null;

    const maxValue =
      Math.max(...heatmapCells.map((cell) => cell.value), 1) || 1;

    return {
      backgroundColor: "transparent",
      tooltip: {
        position: "top",
        backgroundColor: "#111827",
        borderColor: "#374151",
        textStyle: { color: "#f9fafb" },
        formatter: (params: any) => {
          const [x, y, value] = params.value;
          return `${heatmapRows[y]} / ${heatmapCols[x]}<br/>Value: ${value}`;
        },
      },
      grid: {
        left: 80,
        right: 80,
        top: 40,
        bottom: 60,
      },
      xAxis: {
        type: "category",
        data: heatmapCols,
        splitArea: { show: false },
        axisLabel: { color: "#d1d5db" },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      yAxis: {
        type: "category",
        data: heatmapRows,
        splitArea: { show: false },
        axisLabel: { color: "#d1d5db" },
        axisLine: { lineStyle: { color: "#4b5563" } },
      },
      visualMap: {
        min: 0,
        max: maxValue,
        calculable: true,
        orient: "vertical",
        right: 10,
        top: "center",
      },
      series: [
        {
          type: "heatmap",
          data: heatmapCells.map((cell) => [
            heatmapCols.indexOf(cell.col_label),
            heatmapRows.indexOf(cell.row_label),
            cell.value,
          ]),
          label: { show: false },
          emphasis: {
            itemStyle: {
              shadowBlur: 8,
              shadowColor: "rgba(0, 0, 0, 0.4)",
            },
          },
        },
      ],
    };
  }, [heatmapRows, heatmapCols, heatmapCells]);
    const timelineStats = useMemo(() => {
    const summary = timelineSummary || {};

    const fallbackTotal = timelineEvents.length;
    const fallbackSessions = new Set(timelineEvents.map((e) => e.session_id)).size;
    const fallbackLeaks = timelineEvents.filter((e) => e.event_type === "leak").length;
    const fallbackAssessments = timelineEvents.filter((e) => e.event_type === "risk").length;

    return {
      total_events:
        summary.total_events && summary.total_events > 0
          ? summary.total_events
          : fallbackTotal,
      session_count:
        summary.session_count && summary.session_count > 0
          ? summary.session_count
          : fallbackSessions,
      leak_count:
        summary.leak_count && summary.leak_count > 0
          ? summary.leak_count
          : fallbackLeaks,
      assessment_count:
        summary.assessment_count && summary.assessment_count > 0
          ? summary.assessment_count
          : fallbackAssessments,
    };
  }, [timelineSummary, timelineEvents]);

  const displayedTimelineEvents = useMemo(() => {
    return [...timelineEvents]
      .sort(
        (a, b) =>
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )
      .slice(0, 8);
  }, [timelineEvents]);
  if (loading) {
    return <div style={pageStyle}>Loading dashboard...</div>;
  }

  return (
    <div style={pageStyle}>
      <div style={heroStyle}>
        <div>
          <h1 style={titleStyle}>Visualization Dashboard</h1>
          <p style={subtitleStyle}>
            Built strictly from Module 3.4 dashboard APIs.
          </p>
        </div>

        <div style={toolbarStyle}>
          <select
            style={selectStyle}
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="last_hour">last_hour</option>
            <option value="last_24h">last_24h</option>
            <option value="last_7d">last_7d</option>
            <option value="last_30d">last_30d</option>
          </select>

          <select
            style={selectStyle}
            value={heatmapType}
            onChange={(e) => setHeatmapType(e.target.value)}
          >
            <option value="timeofday">timeofday</option>
            <option value="method_frequency">method_frequency</option>
            <option value="dayofweek">dayofweek</option>
          </select>

          <button style={buttonStyle} onClick={fetchDashboard}>
            Refresh
          </button>

          <button
            style={reportButtonStyle}
            onClick={handleGenerateReport}
            disabled={reportLoading}
          >
            {reportLoading ? "Generating..." : "Generate Report"}
          </button>
        </div>
      </div>

      <div style={statGridStyle}>
        <StatCard
          title="Active Sessions"
          value={status?.active_sessions ?? 0}
        />
        <StatCard
          title="Total Sessions"
          value={status?.total_sessions ?? 0}
        />
        <StatCard
          title="Today's Packets"
          value={status?.today_packets ?? 0}
        />
        <StatCard title="Today's Leaks" value={status?.today_leaks ?? 0} />
      </div>

      <div style={twoColumnGridStyle}>
        <SectionCard
          title="Current Monitor Status"
          subtitle="GET /dashboard/monitor/status"
        >
          <div style={infoGridStyle}>
            <InfoItem label="Capturing">
              <RiskBadge level={status?.capturing ? "active" : "idle"} />
            </InfoItem>
            <InfoItem label="Capture Rate">
              {status?.capture_rate ?? 0} pkt/s
            </InfoItem>
            <InfoItem label="Last Capture Time">
              <TimeBlock value={status?.last_capture_time} />
            </InfoItem>
            <InfoItem label="Metadata Time">
              <TimeBlock value={riskMetrics?.last_updated} />
            </InfoItem>
          </div>
        </SectionCard>

        <SectionCard
          title="Risk Metrics"
          subtitle="GET /dashboard/monitor/risk/metrics"
        >
          <div style={infoGridStyle}>
            <InfoItem label="Current Risk">
              <RiskBadge level={riskMetrics?.current_risk_level || "-"} />
            </InfoItem>
            <InfoItem label="Average Risk Score">
              {riskMetrics?.average_risk_score ?? 0}
            </InfoItem>
            <InfoItem label="High Risk Sessions">
              {riskMetrics?.high_risk_sessions ?? 0}
            </InfoItem>
            <InfoItem label="Trend">{riskMetrics?.risk_trend ?? "-"}</InfoItem>
          </div>
        </SectionCard>
      </div>

      <SectionCard
        title="Real-time Leak Stream"
        subtitle="GET /dashboard/monitor/leaks/stream"
      >
        {leaks.length === 0 ? (
          <EmptyState text="No leak stream data available" />
        ) : (
          <div style={tableWrapperStyle}>
            <table style={tableStyle}>
              <thead>
                <tr>
                  <th style={thStyle}>Leak Type</th>
                  <th style={thStyle}>Method</th>
                  <th style={thStyle}>Confidence</th>
                  <th style={thStyle}>Description</th>
                  <th style={thStyle}>Created</th>
                </tr>
              </thead>
              <tbody>
                {leaks.map((item) => (
                  <tr key={item.id}>
                    <td style={tdStyle}>
                      <RiskBadge level={item.leak_type} />
                    </td>
                    <td style={tdStyle}>{item.method_name}</td>
                    <td style={tdStyle}>{item.confidence.toFixed(3)}</td>
                    <td style={tdStyle}>{item.description}</td>
                    <td style={tdStyle}>
                      <TimeBlock value={item.created_at} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      <SectionCard
        title="Timeline Report"
        subtitle="GET /dashboard/reports/timeline"
      >
        <div style={timelineSummaryBarStyle}>
          <span>Total Events: {timelineStats.total_events}</span>
          <span>Sessions: {timelineStats.session_count}</span>
          <span>Leaks: {timelineStats.leak_count}</span>
          <span>Assessments: {timelineStats.assessment_count}</span>
        </div>

        {timelineEvents.length === 0 ? (
          <EmptyState text="No timeline data available" />
        ) : (
          <div style={timelineListStyle}>
            {timelineEvents.map((event, index) => (
              <div key={`${event.session_id}-${index}`} style={timelineItemStyle}>
                <div style={timelineDotStyle} />
                <div style={timelineContentStyle}>
                  <div style={timelineTopRowStyle}>
                    <strong>{event.event_type}</strong>
                    <span style={timelineTimeStyle}>
                      {formatUTCToBeijing(event.timestamp)}
                    </span>
                  </div>
                  <div style={timelineDescStyle}>{event.description}</div>
                  <div style={timelineMetaStyle}>
                    Session: {event.session_id}
                    {event.leak_type ? ` | Leak: ${event.leak_type}` : ""}
                    {event.risk_score !== null ? ` | Score: ${event.risk_score}` : ""}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      <SectionCard
        title="Heatmap Report"
        subtitle="GET /dashboard/reports/heatmap"
      >
        {heatmapOption ? (
          <ReactECharts option={heatmapOption} style={{ height: 420, width: "100%" }} />
        ) : (
          <EmptyState text="No heatmap data available" />
        )}
      </SectionCard>

      <div style={twoColumnGridStyle}>
        <SectionCard
          title="Privacy Leak Events Over Time"
          subtitle="GET /dashboard/charts"
        >
          {timelineChart ? (
            <ReactECharts option={timelineChart} style={{ height: 340, width: "100%" }} />
          ) : (
            <EmptyState text="No timeline chart data available" />
          )}
        </SectionCard>

        <SectionCard
          title="Risk Level Distribution"
          subtitle="GET /dashboard/charts"
        >
          {riskPieChart ? (
            <ReactECharts option={riskPieChart} style={{ height: 340, width: "100%" }} />
          ) : (
            <EmptyState text="No risk distribution chart data available" />
          )}
        </SectionCard>
      </div>

      <div style={twoColumnGridStyle}>
        <SectionCard
          title="Network Traffic Volume"
          subtitle="GET /dashboard/charts"
        >
          {trafficBarChart ? (
            <ReactECharts option={trafficBarChart} style={{ height: 340, width: "100%" }} />
          ) : (
            <EmptyState text="No traffic chart data available" />
          )}
        </SectionCard>

        <SectionCard
          title="RPC Response Time Latency"
          subtitle="GET /dashboard/charts"
        >
          {latencyLineChart ? (
            <ReactECharts option={latencyLineChart} style={{ height: 340, width: "100%" }} />
          ) : (
            <EmptyState text="No latency chart data available" />
          )}
        </SectionCard>
      </div>

      <SectionCard
        title="Comprehensive Report"
        subtitle="POST /dashboard/comprehensive-report"
        action={
          <button
            style={reportButtonStyle}
            onClick={handleGenerateReport}
            disabled={reportLoading}
          >
            {reportLoading ? "Generating..." : "Regenerate"}
          </button>
        }
      >
        {report ? (
          <div style={reportBoxStyle}>
            <div style={infoGridStyle}>
              <InfoItem label="Generated At">
                <TimeBlock value={report.report_metadata?.generated_at} />
              </InfoItem>
              <InfoItem label="Time Range">
                {report.report_metadata?.time_range ?? "-"}
              </InfoItem>
              <InfoItem label="Sessions Tested">
                {report.report_metadata?.num_sessions_tested ?? 0}
              </InfoItem>
              <InfoItem label="Total Sessions">
                {report.report_metadata?.total_sessions ?? 0}
              </InfoItem>
            </div>

            <pre style={preStyle}>
              {JSON.stringify(report.results, null, 2)}
            </pre>
          </div>
        ) : (
          <EmptyState text="No comprehensive report generated yet" />
        )}
      </SectionCard>
    </div>
  );
}

function TimeBlock({ value }: { value?: string }) {
  const { date, clock } = formatUTCToBeijingSplit(value);

  return (
    <div style={{ lineHeight: 1.35 }}>
      <div>{date}</div>
      <div style={{ color: "#9ca3af", fontSize: "13px" }}>{clock}</div>
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <div style={statCardStyle}>
      <div style={statTitleStyle}>{title}</div>
      <div style={statValueStyle}>{value}</div>
    </div>
  );
}

function InfoItem({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div style={infoItemStyle}>
      <div style={infoLabelStyle}>{label}</div>
      <div style={infoValueStyle}>{children}</div>
    </div>
  );
}

const pageStyle: React.CSSProperties = {
  minHeight: "100vh",
  background: "#111827",
  color: "#f9fafb",
  padding: "32px",
  fontFamily:
    "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
};

const heroStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  gap: "16px",
  marginBottom: "28px",
  flexWrap: "wrap",
};

const titleStyle: React.CSSProperties = {
  fontSize: "46px",
  fontWeight: 700,
  margin: 0,
  marginBottom: "10px",
};

const subtitleStyle: React.CSSProperties = {
  margin: 0,
  color: "#9ca3af",
  fontSize: "15px",
};

const toolbarStyle: React.CSSProperties = {
  display: "flex",
  gap: "12px",
  flexWrap: "wrap",
};

const selectStyle: React.CSSProperties = {
  background: "#1f2937",
  color: "#f9fafb",
  border: "1px solid #374151",
  borderRadius: "10px",
  padding: "10px 12px",
};

const buttonStyle: React.CSSProperties = {
  background: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "10px",
  padding: "10px 16px",
  cursor: "pointer",
  fontWeight: 600,
};

const reportButtonStyle: React.CSSProperties = {
  background: "#7c3aed",
  color: "#fff",
  border: "none",
  borderRadius: "10px",
  padding: "10px 16px",
  cursor: "pointer",
  fontWeight: 600,
};

const statGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
  gap: "18px",
  marginBottom: "24px",
};

const statCardStyle: React.CSSProperties = {
  background: "linear-gradient(145deg, #1f2937 0%, #233147 100%)",
  border: "1px solid #374151",
  borderRadius: "16px",
  padding: "24px",
  boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
};

const statTitleStyle: React.CSSProperties = {
  color: "#d1d5db",
  fontSize: "16px",
  fontWeight: 600,
  marginBottom: "18px",
};

const statValueStyle: React.CSSProperties = {
  fontSize: "34px",
  fontWeight: 700,
};

const twoColumnGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(420px, 1fr))",
  gap: "20px",
  marginBottom: "20px",
};

const sectionCardStyle: React.CSSProperties = {
  background: "linear-gradient(145deg, #1f2937 0%, #233147 100%)",
  border: "1px solid #374151",
  borderRadius: "18px",
  padding: "22px",
  boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
  marginBottom: "20px",
};

const sectionHeaderStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "flex-start",
  gap: "12px",
  marginBottom: "16px",
  flexWrap: "wrap",
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: "28px",
  fontWeight: 700,
  margin: 0,
};

const sectionSubtitleStyle: React.CSSProperties = {
  margin: 0,
  marginTop: "6px",
  color: "#9ca3af",
  fontSize: "14px",
};

const infoGridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
  gap: "16px",
};

const infoItemStyle: React.CSSProperties = {
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(255,255,255,0.06)",
  borderRadius: "14px",
  padding: "16px",
};

const infoLabelStyle: React.CSSProperties = {
  color: "#9ca3af",
  fontSize: "13px",
  marginBottom: "10px",
};

const infoValueStyle: React.CSSProperties = {
  fontSize: "18px",
  fontWeight: 600,
};

const tableWrapperStyle: React.CSSProperties = {
  overflowX: "auto",
};

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
};

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "12px",
  borderBottom: "1px solid #374151",
  color: "#d1d5db",
  fontSize: "13px",
};

const tdStyle: React.CSSProperties = {
  padding: "12px",
  borderBottom: "1px solid #374151",
  fontSize: "14px",
  verticalAlign: "top",
};

const timelineSummaryBarStyle: React.CSSProperties = {
  display: "flex",
  gap: "18px",
  flexWrap: "wrap",
  color: "#d1d5db",
  marginBottom: "18px",
  fontSize: "14px",
};

const timelineListStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  maxHeight: "720px",
  overflowY: "auto",
  paddingRight: "6px",
};

const timelineItemStyle: React.CSSProperties = {
  display: "flex",
  gap: "14px",
};

const timelineDotStyle: React.CSSProperties = {
  width: "12px",
  height: "12px",
  borderRadius: "999px",
  background: "#60a5fa",
  marginTop: "7px",
  flexShrink: 0,
};

const timelineContentStyle: React.CSSProperties = {
  flex: 1,
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(255,255,255,0.06)",
  borderRadius: "14px",
  padding: "14px 16px",
};

const timelineTopRowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: "16px",
  flexWrap: "wrap",
  marginBottom: "8px",
};

const timelineTimeStyle: React.CSSProperties = {
  color: "#9ca3af",
  fontSize: "13px",
};

const timelineDescStyle: React.CSSProperties = {
  marginBottom: "8px",
};

const timelineMetaStyle: React.CSSProperties = {
  color: "#9ca3af",
  fontSize: "13px",
  wordBreak: "break-all",
};

const reportBoxStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "20px",
};

const preStyle: React.CSSProperties = {
  background: "#0f172a",
  border: "1px solid #1f2937",
  borderRadius: "14px",
  padding: "16px",
  overflowX: "auto",
  fontSize: "13px",
  lineHeight: 1.5,
  color: "#d1d5db",
};