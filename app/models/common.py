"""
Common Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict, List
from datetime import datetime
from enum import Enum


class ErrorCode(str, Enum):
    """Error code enumeration"""
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    UNAUTHORIZED = "UNAUTHORIZED"


class APIResponse(BaseModel):
    """Standard API response model for successful requests"""
    model_config = ConfigDict(use_enum_values=True)

    success: bool = True
    data: Optional[Any] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model for failed requests"""
    model_config = ConfigDict(use_enum_values=True)

    success: bool = False
    error: ErrorDetail
    metadata: Optional[Dict[str, Any]] = None


# Response models for each entity


class LeakType(str, Enum):
    """Leak type enumeration"""
    IDENTITY = "identity"
    ASSET = "asset"
    BEHAVIOR = "behavior"
    LOCATION = "location"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SessionStatus(str, Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class Priority(str, Enum):
    """Rule priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SessionCreate(BaseModel):
    """Create session request"""
    wallet_type: str = Field(..., min_length=1, max_length=255)
    rpc_provider: str = Field(..., min_length=1, max_length=255)


class SessionResponse(BaseModel):
    """Session response"""
    id: str
    wallet_type: str
    rpc_provider: str
    start_time: str
    end_time: Optional[str] = None
    packet_count: int
    duration_seconds: Optional[int] = None
    status: SessionStatus
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str


class NetworkTrafficResponse(BaseModel):
    """Network traffic record response"""
    id: str
    session_id: str
    method: str
    endpoint: str
    rpc_method: Optional[str] = None
    request_timestamp: Optional[str] = None
    response_time_ms: Optional[int] = None
    response_status: Optional[int] = None
    response_size_bytes: Optional[int] = None
    created_at: str


class PrivacyLeakEventResponse(BaseModel):
    """Privacy leak event response"""
    id: str
    session_id: str
    leak_type: LeakType
    method_name: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_interval_low: float
    confidence_interval_high: float
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    address_hash: str
    rule_id: str
    created_at: str


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    id: str
    session_id: Optional[str] = None
    address_hash: Optional[str] = None
    overall_score: int = Field(..., ge=0, le=100)
    entropy_score: float = Field(..., ge=0.0, le=1.0)
    uniqueness_score: float = Field(..., ge=0.0, le=1.0)
    correlation_score: float = Field(..., ge=0.0, le=1.0)
    temporal_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_interval_low: float
    confidence_interval_high: float
    risk_level: RiskLevel
    recommendations: List[str] = Field(..., min_length=1)
    baseline_comparison: Optional[Dict[str, Any]] = None
    assessed_at: str
    created_at: str


class DetectionRuleResponse(BaseModel):
    """Detection rule response"""
    id: str
    name: str
    category: LeakType
    enabled: bool
    priority: Priority


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    limit: int
    offset: int
