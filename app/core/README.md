# Wallet / RPC Privacy Leakage Detection Engine (Milestone 2)

## English Version

### Overview
This engine is a high-precision privacy audit tool designed for Web3 traffic analysis. It processes JSON-RPC flows to identify Identity, Location, Asset, and Behavior leakages. In Milestone 2, the engine has been upgraded to support deep-nested data structures (compatible with module 3.1) and implements a multi-dimensional risk matrix for cross-session correlation.

### Key Features
* **Deep Nested Inspection**: Specifically optimized to traverse `request` and `response` objects within complex traffic logs.
* **M2 Risk Matrix**: Calculates a unified Severity Score (0-100) based on the convergence of different leak types.
* **LDJSON Support**: High-performance parsing for large-scale Line-Delimited JSON files.
* **PR-2 Anonymization**: Automatic SHA-256 hashing for wallet addresses to ensure data privacy during reporting.

### Implementation Status (10 Rules)
| Rule ID | Category | Logic |
| :--- | :--- | :--- |
| **DR-ID-1** | Identity | Plaintext Wallet Address detection in body/path/params. |
| **DR-ID-2** | Identity | High Entropy Secret (Private Key) detection via Shannon Entropy. |
| **DR-LO-1** | Location | Phishing Detection API Telemetry (MetaMask) identification. |
| **DR-AS-1** | Asset | Account balance polling via `eth_getBalance` method. |
| **DR-BE-1** | Behavior | Activity frequency tracking via `getTransactionCount`. |

---

# 钱包与 RPC 隐私泄露检测引擎 (里程碑 2)

## 中文版

### 项目概述
本引擎是专为 Web3 流量分析设计的高精度隐私审计工具。它通过处理 JSON-RPC 流来识别身份、位置、资产和行为泄露。在里程碑 2 中，引擎已升级为支持深度嵌套的数据结构（兼容 3.1 模块），并实现了用于跨会话关联分析的多维风险矩阵。

### 核心功能
* **深度嵌套检测**：专门针对复杂流量日志中的 `request` 和 `response` 对象进行遍历优化。
* **M2 风险矩阵**：基于不同泄露类型的收敛性计算统一的“严重性得分”（0-100）。
* **LDJSON 支持**：针对大规模行分隔 JSON (LDJSON) 文件的高性能解析。
* **PR-2 匿名化**：自动对钱包地址进行 SHA-256 哈希处理，确保报告过程中的数据隐私。

### 规则实现状态 (10 条规则)
| 规则 ID | 类别 | 检测逻辑 |
| :--- | :--- | :--- |
| **DR-ID-1** | 身份 | 检测 Body/Path/Params 中的明文钱包地址。 |
| **DR-ID-2** | 身份 | 通过香农熵检测高熵密钥（私钥）。 |
| **DR-LO-1** | 位置 | 识别指向 MetaMask 钓鱼检测 API 的遥测调用。 |
| **DR-AS-1** | 资产 | 通过 `eth_getBalance` 方法检测账户余额轮询。 |
| **DR-BE-1** | 行为 | 通过 `getTransactionCount` 追踪活动频率。 |