from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict, List
from enum import Enum


class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    TIMELINE = "timeline"
    GAUGE = "gauge"


class ExportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"


class TimeRange(str, Enum):
    LAST_HOUR = "last_hour"
    LAST_24H = "last_24h"
    LAST_7D = "last_7d"
    LAST_30D = "last_30d"
    ALL = "all"


class MonitorStatus(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    active_sessions: int = Field(..., description="Number of currently active capture sessions")
    total_sessions: int = Field(..., description="Total number of sessions")
    capturing: bool = Field(..., description="Whether any session is currently capturing traffic")
    today_packets: int = Field(..., description="Packets captured today")
    today_leaks: int = Field(..., description="Privacy leaks detected today")
    capture_rate: float = Field(..., ge=0.0, description="Current capture rate (packets/second)")
    last_capture_time: Optional[str] = Field(None, description="Last packet capture timestamp")


class RealtimeLeakStream(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    events: List[Dict[str, Any]] = Field(..., description="Recent leak events")
    stream_position: str = Field(..., description="Current stream position for pagination")
    has_more: bool = Field(..., description="Whether more events are available")
    leak_rate: float = Field(..., ge=0.0, description="Current leak detection rate (events/minute)")


class RealtimeRiskMetrics(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    current_risk_level: str = Field(..., description="Current overall risk level")
    average_risk_score: float = Field(..., ge=0.0, le=100.0, description="Average risk score across all sessions")
    high_risk_sessions: int = Field(..., description="Number of sessions with high or critical risk")
    risk_trend: str = Field(..., description="Risk trend: increasing, stable, or decreasing")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in risk assessment")
    last_updated: str = Field(..., description="Last update timestamp")


class TimelineEvent(BaseModel):
    timestamp: str
    event_type: str
    leak_type: Optional[str] = None
    risk_score: Optional[int] = None
    description: str
    session_id: Optional[str] = None


class TimelineResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    events: List[TimelineEvent] = Field(..., description="Timeline events sorted by timestamp")
    time_range: str = Field(..., description="Time range of the timeline (e.g., '2026-03-01 to 2026-03-09')")
    total_events: int = Field(..., description="Total number of events in timeline")
    leak_distribution: Dict[str, int] = Field(..., description="Leak type distribution count")


class HeatmapCell(BaseModel):
    row_label: str
    col_label: str
    value: float
    count: int


class HeatmapResponse(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    heatmap_type: str = Field(..., description="Type of heatmap: 'timeofday', 'dayofweek', 'method_frequency'")
    row_labels: List[str] = Field(..., description="Labels for y-axis")
    col_labels: List[str] = Field(..., description="Labels for x-axis")
    cells: List[HeatmapCell] = Field(..., description="Heatmap cell data")
    max_value: float = Field(..., description="Maximum value in heatmap for normalization")
    min_value: float = Field(..., description="Minimum value in heatmap for normalization")


class SeriesData(BaseModel):
    label: str
    data_points: List[Dict[str, Any]]


class ChartData(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    chart_type: ChartType = Field(..., description="Type of visualization")
    title: str = Field(..., description="Chart title")
    subtitle: Optional[str] = Field(None, description="Chart subtitle")
    x_axis_label: Optional[str] = Field(None, description="X-axis label")
    y_axis_label: Optional[str] = Field(None, description="Y-axis label")
    series: List[SeriesData] = Field(..., description="Data series")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional chart metadata")


class StatisticsSummary(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    overall_stats: Dict[str, Any] = Field(..., description="Overall key statistics")
    leak_statistics: Dict[str, Any] = Field(..., description="Leak-type statistics")
    risk_statistics: Dict[str, Any] = Field(..., description="Risk-level statistics")
    traffic_statistics: Dict[str, Any] = Field(..., description="Traffic statistics")
    top_charts: List[ChartData] = Field(..., description="Top visualization charts")
