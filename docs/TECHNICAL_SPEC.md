```markdown
# Technical Specification

## Scoring Methodology
To fulfill the requirement of "Precision > 90%", the engine employs a dynamic scoring model across 10 rules:
* **Identity Leaks (DR-ID-1 to 3)**: Uses Web3.py for EIP-55 checksum validation. Mnemonic detection uses fixed patterns for BIP-39 wordlists.
* **Cryptographic Secrets (DR-ID-2)**: Uses Shannon Entropy $H(X) = -\sum p(x_i) \log_2 p(x_i)$. Strings with entropy > 3.8 are flagged as high-risk.
* **Asset Tracking (DR-AS-1 to 2)**: Targets specific RPC methods like `eth_getBalance` and `eth_call` with ERC-20 selector `70a08231`.
* **Metadata Analysis (DR-LO/BE)**: Extracts wallet brands from User-Agent and tracks interaction frequency via `eth_getTransactionCount`.

## Data Schema Alignment
The output strictly matches the `PrivacyLeakEvent` entity defined in Section 9 of the Initial Specification:
* `session_id`: Unique identifier from the traffic capture module.
* `confidence`: Float [0.0 - 1.0].
* `address_hash`: SHA-256 hashed and truncated (First 8 chars) to comply with PR-2.
* `rule_id`: Standardized identifiers (e.g., DR-ID-1) for tracking.

---

# 技术规格说明

## 评分机制
为满足“准确率 > 90%”的要求，引擎在 10 条规则中采用了动态评分模型：
* **身份泄露 (DR-ID-1 至 3)**: 使用 Web3.py 进行 EIP-55 校验。助记词检测采用 BIP-39 词表的固定模式匹配。
* **加密密钥 (DR-ID-2)**: 采用香农信息熵公式 $H(X) = -\sum p(x_i) \log_2 p(x_i)$。熵值大于 3.8 的字符串被标记为高风险。
* **资产追踪 (DR-AS-1 至 2)**: 针对特定 RPC 方法如 `eth_getBalance` 以及带有 ERC-20 选择器 `70a08231` 的 `eth_call`。
* **元数据分析 (DR-LO/BE)**: 从 User-Agent 中提取钱包品牌，并通过 `eth_getTransactionCount` 追踪交互频率。

## 数据模型对齐
输出结果严格匹配初始规格说明书第 9 节中定义的 `PrivacyLeakEvent` 实体：
* `session_id`: 来自流量抓取模块的唯一标识符。
* `confidence`: 浮点数 [0.0 - 1.0]。
* `address_hash`: 经过 SHA-256 哈希并截断（前 8 位）处理，以符合 PR-2 隐私规范。
* `rule_id`: 标准化标识符（如 DR-ID-1）用于追踪记录。