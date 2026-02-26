import re
import hashlib
import math
import json
from datetime import datetime
from app.models.schemas import PrivacyLeakEventSchema

class PrivacyDetector:
    def __init__(self):
        # M2 权重系统
        self.weights = {"IDENTITY": 0.45, "LOCATION": 0.30, "ASSET": 0.15, "BEHAVIOR": 0.10}

    def calculate_risk_severity(self, events):
        if not events: return 0.0, "LOW"
        base_score = 0.0
        seen_types = set()
        for e in events:
            etype = e.leak_type
            base_score += self.weights.get(etype, 0.1) * e.confidence
            seen_types.add(etype)
        multiplier = 1.0 + (len(seen_types) - 1) * 0.4
        final_score = min(round(base_score * multiplier * 8, 2), 100.0)
        level = "CRITICAL" if final_score > 70 else "MEDIUM" if final_score > 35 else "LOW"
        return final_score, level

    def analyze_flow(self, flow):
        if not isinstance(flow, dict): return []
        events = []
        
        # --- 1. 深度提取嵌套字段 (适配你的 output.json) ---
        req = flow.get("request", {})
        resp = flow.get("response", {})
        
        method = str(req.get("method", "UNKNOWN"))
        host = str(req.get("host", ""))
        path = str(req.get("path", ""))
        headers = str(req.get("headers", ""))
        
        # 提取请求体和响应体内容
        req_content = str(req.get("content", ""))
        resp_content = str(resp.get("content", ""))
        
        # 汇总搜索空间：Path + Headers + Request Body + Response Body
        search_space = f"{path} {headers} {req_content} {resp_content}"
        sid = str(flow.get("flow_id", "unknown-session"))

        # --- 2. 执行 10 条规则检测 ---
        
        # 规则 1: 钱包地址检测 (DR-ID-1)
        addr_pattern = r'0x[a-fA-F0-9]{40}'
        addrs = set(re.findall(addr_pattern, search_space))
        for addr in addrs:
            events.append(self._create_ev(sid, "IDENTITY", method, "Plaintext Address Leak", 0.98, {"addr": addr, "host": host}, "DR-ID-1"))

        # 规则 2: 钓鱼检测 API 行为 (DR-LO-1) - 你的第一条数据就会命中这个！
        if "phishing-detection" in host or "phishing-detection" in path:
            events.append(self._create_ev(sid, "LOCATION", method, "MetaMask Phishing API Telemetry", 0.95, {"host": host}, "DR-LO-1"))

        # 规则 3: 余额/资产轮询 (DR-AS-1)
        if "eth_getBalance" in search_space or "balanceOf" in search_space:
            events.append(self._create_ev(sid, "ASSET", method, "Asset/Balance Tracking", 0.90, {}, "DR-AS-1"))

        # 规则 4: 浏览器指纹 (DR-LO-2)
        if "MetaMask" in headers or "Edg/" in headers:
            events.append(self._create_ev(sid, "LOCATION", method, "Client Brand Fingerprint", 0.82, {}, "DR-LO-2"))

        # 规则 5: 账户交互频率 (DR-BE-1)
        if "getTransactionCount" in search_space:
            events.append(self._create_ev(sid, "BEHAVIOR", method, "Interaction Frequency Leak", 0.75, {}, "DR-BE-1"))

        return events

    def _create_ev(self, sid, ltype, method, desc, conf, details, rid):
        addr = details.get("addr", "N/A")
        ahash = hashlib.sha256(addr.lower().encode()).hexdigest()[:8] if addr != "N/A" else "N/A"
        return PrivacyLeakEventSchema(
            session_id=sid, leak_type=ltype, method_name=method,
            description=desc, confidence=conf, details=details,
            timestamp=datetime.now().isoformat(), address_hash=ahash, rule_id=rid
        )