# Technical Specification (Milestone 2)

## English Version

### 1. M2 Scoring Methodology
The engine moves beyond simple binary detection by implementing a weighted risk matrix. The **Severity Score** accounts for the correlation between different privacy dimensions:

$$Score = \min\left( \sum (Weight_i \times Confidence_i) \times (1 + (N_{types}-1) \times 0.4) \times 8, 100 \right)$$

* **Weights**: Identity (0.45), Location (0.30), Asset (0.15), Behavior (0.10).
* **Correlation Multiplier**: A penalty coefficient applied when multiple leak types appear in the same session.

### 2. Recursive Parsing Logic
The engine implements a recursive search space to handle the `output.json` structure from the 3.1 module:
* **Flattening**: It extracts text from `request.headers`, `request.content`, and `response.content`.
* **Sanitization**: It filters out non-dictionary artifacts (metadata integers) to prevent processing errors.

### 3. Compliance (PR-2)
In accordance with PR-2 specifications, sensitive identifiers are anonymized:
`address_hash = SHA256(lowercase_address).hexdigest()[:8]`

---

# 技术规格说明 (里程碑 2)

## 中文版

### 1. M2 评分方法论
引擎超越了简单的二元检测，实现了加权风险矩阵。**严重性得分**考虑了不同隐私维度之间的关联性：

$$Score = \min\left( \sum (Weight_i \times Confidence_i) \times (1 + (N_{types}-1) \times 0.4) \times 8, 100 \right)$$

* **权重**：身份 (0.45), 位置 (0.30), 资产 (0.15), 行为 (0.10)。
* **关联乘数**：当同一会话中出现多种泄露类型时应用的惩罚系数。

### 2. 递归解析逻辑
引擎实现了递归搜索空间，以处理来自 3.1 模块的 `output.json` 结构：
* **扁平化**：提取 `request.headers`、`request.content` 和 `response.content` 中的文本。
* **数据清洗**：过滤掉非字典伪影（元数据整数），以防止处理错误。

### 3. 合规性 (PR-2)
根据 PR-2 规范，敏感标识符将被匿名化处理：
`address_hash = SHA256(lowercase_address).hexdigest()[:8]`