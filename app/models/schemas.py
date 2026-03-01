from pydantic import BaseModel
from typing import Dict, Any

class PrivacyLeakEventSchema(BaseModel):
    session_id: str
    leak_type: str
    method_name: str
    description: str
    confidence: float
    details: Dict[str, Any]
    timestamp: str
    address_hash: str
    rule_id: str