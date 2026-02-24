from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime
import uuid

# 规范 9.1 定义的枚举值
class LeakType(str, Enum):
    IDENTITY = "IDENTITY"
    ASSET = "ASSET"
    BEHAVIOR = "BEHAVIOR"
    LOCATION = "LOCATION"

# 3.1 模块会传给你的数据格式 (Entity 2: NetworkTraffic)
class NetworkTrafficSchema(BaseModel):
    session_id: str
    rpc_method: Optional[str] = None
    request_body: Optional[str] = None
    user_agent: Optional[str] = None
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)

# 你需要输出并存入数据库的格式 (Entity 3: PrivacyLeakEvent)
class PrivacyLeakEventSchema(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    leak_type: LeakType
    method_name: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0) # 规范要求 [0.0, 1.0]
    confidence_interval_low: float
    confidence_interval_high: float
    details: Dict[str, Any]
    timestamp: datetime
    address_hash: str # 规范 PR-2 要求：SHA-256后截取8位
    rule_id: str