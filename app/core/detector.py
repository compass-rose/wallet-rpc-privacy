import re
import math
import hashlib
from datetime import datetime
from typing import List
from web3 import Web3
from app.models.schemas import NetworkTrafficSchema, PrivacyLeakEventSchema, LeakType

class PrivacyDetector:
    def __init__(self):
        self.w3 = Web3()
        self.risk_keywords = ["private", "key", "secret", "mnemonic", "seed", "phrase"]
        self.erc20_balance_selector = "70a08231" # balanceOf(address)

    def _calculate_entropy(self, text: str) -> float:
        """香农信息熵：识别随机私钥"""
        if not text or len(text) < 10: return 0.0
        prob = [text.count(c) / len(text) for c in set(text)]
        return -sum(p * math.log2(p) for p in prob)

    def _anonymize_address(self, content: str) -> str:
        """PR-2: 地址脱敏：SHA-256 后截取前 8 位"""
        addr_match = re.search(r"0x[a-fA-F0-9]{40}", content)
        if not addr_match: return "N/A"
        addr = addr_match.group(0).lower()
        return hashlib.sha256(addr.encode()).hexdigest()[:8]

    def _create_event(self, traffic, l_type, desc, conf, rule_id, details=None, content=""):
        """工厂方法：快速创建事件对象"""
        return PrivacyLeakEventSchema(
            session_id=traffic.session_id,
            leak_type=l_type,
            method_name=traffic.rpc_method or "HTTP",
            description=desc,
            confidence=round(conf, 2),
            confidence_interval_low=round(max(0, conf - 0.05), 2),
            confidence_interval_high=round(min(1.0, conf + 0.05), 2),
            details=details or {},
            timestamp=traffic.request_timestamp,
            address_hash=self._anonymize_address(content if "0x" in content else content),
            rule_id=rule_id
        )

    def analyze_traffic(self, traffic: NetworkTrafficSchema) -> List[PrivacyLeakEventSchema]:
        findings = []
        body = traffic.request_body or ""
        method = traffic.rpc_method or ""
        ctx = body.lower()

        # 1. DR-ID-1: 以太坊地址泄露
        addrs = re.findall(r"0x[a-fA-F0-9]{40}", body)
        for addr in set(addrs):
            is_valid = self.w3.is_checksum_address(addr)
            findings.append(self._create_event(traffic, LeakType.IDENTITY, "Plaintext address detected", 0.98 if is_valid else 0.8, "DR-ID-1", content=addr))

        # 2. DR-ID-2: 私钥检测
        keys = re.findall(r"(?<![a-fA-F0-9])[a-fA-F0-9]{64}(?![a-fA-F0-9])", body)
        for k in set(keys):
            score = 0.5 + (0.3 if any(w in ctx for w in self.risk_keywords) else 0) + (0.18 if self._calculate_entropy(k) > 3.8 else 0)
            if score > 0.6:
                findings.append(self._create_event(traffic, LeakType.IDENTITY, "Potential private key", score, "DR-ID-2", content=k))

        # 3. DR-ID-3: 助记词检测 (12词模式)
        if re.search(r"([a-z]{3,8}\s){11}[a-z]{3,8}", ctx):
            findings.append(self._create_event(traffic, LeakType.IDENTITY, "Mnemonic pattern found", 0.95, "DR-ID-3"))

        # 4. DR-AS-1: 余额轮询
        if method == "eth_getBalance":
            findings.append(self._create_event(traffic, LeakType.ASSET, "Balance tracking", 0.90, "DR-AS-1"))

        # 5. DR-AS-2: ERC-20 资产查询
        if method == "eth_call" and self.erc20_balance_selector in body:
            findings.append(self._create_event(traffic, LeakType.ASSET, "Token balance tracking", 0.95, "DR-AS-2"))

        # 6. DR-LO-1: 钱包品牌指纹 (UA)
        if traffic.user_agent and "MetaMask" in traffic.user_agent:
            findings.append(self._create_event(traffic, LeakType.LOCATION, "MetaMask fingerprint", 0.85, "DR-LO-1"))

        # 7. DR-LO-2: 来源域名泄露 (Referer)
        if "Referer" in str(traffic):
            findings.append(self._create_event(traffic, LeakType.LOCATION, "Referer domain leak", 0.80, "DR-LO-2"))

        # 8. DR-BE-1: Nonce 泄露 (频率分析)
        if method == "eth_getTransactionCount":
            findings.append(self._create_event(traffic, LeakType.BEHAVIOR, "User activity frequency leak", 0.75, "DR-BE-1"))

        # 9. DR-BE-2: 交易意图预判 (Gas)
        if method == "eth_estimateGas":
            findings.append(self._create_event(traffic, LeakType.BEHAVIOR, "Transaction intent leak", 0.70, "DR-BE-2"))

        # 10. DR-BE-3: 合约交互模式
        if method == "eth_getLogs":
            findings.append(self._create_event(traffic, LeakType.BEHAVIOR, "Contract interest profiling", 0.65, "DR-BE-3"))

        return findings