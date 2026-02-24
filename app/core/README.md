# Wallet / RPC Privacy Leakage Detection Engine

## Overview
This module is the core detection engine (Task 3.2) for the Privacy Measurement System. It is designed to automatically identify, classify, and quantify privacy leakages within wallet-to-RPC communication traffic. The engine ensures high precision through heuristic analysis and maintains privacy compliance by anonymizing sensitive data before storage.

## Key Features
* **10 Automated Rules**: Comprehensive detection covering Identity, Asset, Behavior, and Location dimensions.
* **Dynamic Confidence Scoring**: Advanced scoring mechanism using Shannon Entropy and EIP-55 Checksum validation.
* **Privacy Compliance**: Strictly implements the **PR-2** specification (SHA-256 hashing for wallet addresses).
* **Industrial Integration**: Standardized JSON output aligned with Section 9 of the Project Specification, ready for 3.1 module data ingestion.

## Milestone 1 Implementation Status (All 10 Rules)
| Rule ID | Category | Rule Name | Confidence Range |
|:---|:---|:---|:---|
| **DR-ID-1** | Identity | Plaintext Address Leak | 0.80 - 0.98 |
| **DR-ID-2** | Identity | Private Key Detection | 0.60 - 0.95 |
| **DR-ID-3** | Identity | Mnemonic Pattern Matching | 0.95 |
| **DR-AS-1** | Asset | Account Balance Polling | 0.90 |
| **DR-AS-2** | Asset | Token Asset Tracking (ERC-20) | 0.95 |
| **DR-LO-1** | Location | Wallet Brand Fingerprinting (UA) | 0.85 |
| **DR-LO-2** | Location | DApp Source Leakage (Referer) | 0.80 |
| **DR-BE-1** | Behavior | Activity Frequency Tracking (Nonce) | 0.75 |
| **DR-BE-2** | Behavior | Transaction Intent Pre-analysis (Gas) | 0.70 |
| **DR-BE-3** | Behavior | Contract Interest Profiling (Logs) | 0.65 |

---

# 钱包与 RPC 隐私泄露检测引擎

## 项目概述
本模块是隐私测量系统的核心检测引擎（任务 3.2）。其设计目的是自动识别、分类并量化钱包与 RPC 通信流量中的隐私泄露风险。引擎通过启发式分析确保高精度检测，并在存储前对敏感数据进行匿名化处理，以符合隐私合规要求。

## 核心功能
* **10 条自动化规则**: 全面覆盖身份、资产、行为和位置维度的泄露检测。
* **动态置信度评分**: 利用香农信息熵和 EIP-55 校验和实现的高级评分机制。
* **隐私合规**: 严格执行 **PR-2** 规范（对钱包地址进行 SHA-256 哈希处理）。
* **工业级集成**: 标准化 JSON 输出，完全对接项目规范第 9 节，可直接接收 3.1 模块的流量数据。

## 里程碑 1 实现进度 (全部 10 条规则)
| 规则 ID | 类别 | 规则名称 | 置信度范围 |
|:---|:---|:---|:---|
| **DR-ID-1** | 身份 | 明文地址泄露 | 0.80 - 0.98 |
| **DR-ID-2** | 身份 | 私钥特征检测 | 0.60 - 0.95 |
| **DR-ID-3** | 身份 | 助记词特征匹配 | 0.95 |
| **DR-AS-1** | 资产 | 账户余额轮询 | 0.90 |
| **DR-AS-2** | 资产 | 代币资产追踪 (ERC-20) | 0.95 |
| **DR-LO-1** | 位置 | 钱包品牌指纹识别 (UA) | 0.85 |
| **DR-LO-2** | 位置 | 来源域名泄露 (Referer) | 0.80 |
| **DR-BE-1** | 行为 | 活跃频率追踪 (Nonce) | 0.75 |
| **DR-BE-2** | 行为 | 交易意图预判 (Gas) | 0.70 |
| **DR-BE-3** | 行为 | 合约兴趣画像 (Logs) | 0.65 |