# Wallet RPC Privacy Leakage Measurement API Documentation
# 钱包RPC隐私泄露测量系统API文档

---

## 目录 (Table of Contents)

### 功能模块一：网络流量捕获与分析 (Module 1: Network Traffic Capture & Analysis)
1. [会话管理 (Session Management)](#1-会话管理-session-management)
   - [1.1 创建会话 (Create Session)](#11-创建会话-create-session)
   - [1.2 获取会话详情 (Get Session Details)](#12-获取会话详情-get-session-details)
   - [1.3 列出会话 (List Sessions)](#13-列出会话-list-sessions)
   - [1.4 更新会话 (Update Session)](#14-更新会话-update-session)
   - [1.5 删除会话 (Delete Session)](#15-删除会话-delete-session)
2. [流量捕获 (Traffic Capture)](#2-流量捕获-traffic-capture)
   - [2.1 开始流量捕获 (Start Traffic Capture)](#21-开始流量捕获-start-traffic-capture)
   - [2.2 停止流量捕获 (Stop Traffic Capture)](#22-停止流量捕获-stop-traffic-capture)
   - [2.3 获取流量记录 (Get Traffic Records)](#23-获取流量记录-get-traffic-records)
   - [2.4 记录单条流量 (Record Single Traffic)](#24-记录单条流量-record-single-traffic)
3. [分析统计 (Analytics & Statistics)](#3-分析统计-analytics--statistics)
   - [3.1 获取摘要统计 (Get Summary Statistics)](#31-获取摘要统计-get-summary-statistics)
   - [3.2 获取趋势分析 (Get Trends)](#32-获取趋势分析-get-trends)
   - [3.3 获取方法频率 (Get Method Frequency)](#31-获取方法频率-get-method-frequency)
   - [3.4 获取响应时间统计 (Get Response Time Stats)](#34-获取响应时间统计-get-response-time-stats)

### 功能模块二：隐私泄露检测与分类 (Module 2: Privacy Leak Detection & Classification)
4. [检测规则 (Detection Rules)](#4-检测规则-detection-rules)
   - [4.1 列出规则 (List Rules)](#41-列出规则-list-rules)
   - [4.2 获取规则摘要 (Get Rules Summary)](#42-获取规则摘要-get-rules-summary)
   - [4.3 获取规则详情 (Get Rule Details)](#43-获取规则详情-get-rule-details)
5. [隐私泄露事件 (Privacy Leak Events)](#5-隐私泄露事件-privacy-leak-events)
   - [5.1 获取会话泄露 (Get Session Leaks)](#51-获取会话泄露-get-session-leaks)
   - [5.2 列出所有泄露 (List All Leaks)](#52-列出所有泄露-list-all-leaks)

### 功能模块三：风险量化评估 (Module 3: Risk Quantitative Assessment)
6. [风险评估 (Risk Assessment)](#6-风险评估-risk-assessment)
   - [6.1 运行风险评估 (Run Risk Assessment)](#61-运行风险评估-run-risk-assessment)
   - [6.2 获取评估结果 (Get Assessment)](#62-获取评估结果-get-assessment)
   - [6.3 列出所有评估 (List Assessments)](#63-列出所有评估-list-assessments)
7. [风险分析 (Risk Analysis)](#7-风险分析-risk-analysis)
   - [7.1 获取泄露分布 (Get Leak Distribution)](#71-获取泄露分布-get-leak-distribution)
   - [7.2 获取风险分布 (Get Risk Distribution)](#72-获取风险分布-get-risk-distribution)
   - [7.3 获取高风险会话 (Get Top Risk Sessions)](#73-获取高风险会话-get-top-risk-sessions)

---

## 功能模块一：网络流量捕获与分析
## Module 1: Network Traffic Capture & Analysis

### 模块概述 (Module Overview)

**功能描述**：捕获并深度分析钱包与RPC节点之间的网络通信流量，支持多种协议解析和数据结构化存储。

**核心技术**：
- 流量捕获：HTTPS/TLS解密、WebSocket支持、多协议识别
- 协议解析：JSON-RPC方法调用解析、ABI信息提取、签名验证
- 数据存储：结构化存储、高效查询、元数据标注

**原理解释**：
1. **流量捕获层**：使用中间人代理技术拦截钱包-RPC通信
2. **协议解析层**：解析JSON-RPC请求/响应，提取关键字段
3. **数据处理层**：将原始数据转换为结构化格式并存储

---

## 1. 会话管理 (Session Management)

### 1.1 创建会话 (Create Session)

#### 接口地址 (Endpoint Address)
```
POST /api/v1/sessions
```

#### 功能说明 (Function Description)
**概述**：创建一个新的捕获会话，用于分析钱包-RPC通信

**功能描述**：
- 生成唯一的会话ID（UUID）
- 初始化会话状态为ACTIVE
- 记录钱包类型和RPC提供商信息
- 设置捕获开始时间

**技术实现**：
- 使用UUID V4生成会话ID
- 会话状态机：ACTIVE → COMPLETED
- 元数据存储：wallet_type, rpc_provider, start_time

**工作原理**：
1. 接收钱包类型和RPC提供商参数
2. 生成随机UUID作为会话标识
3. 初始化数据库记录
4. 返回会话ID和初始状态

---

#### 请求参数 (Request Parameters)

**请求格式**：application/json

| 参数名 | 类型 | 必填 | 说明 | 示例 |
|--------|------|------|------|------|
| wallet_type | string | 是 | 钱包类型（metamask, walletconnect等） | "metamask" |
| rpc_provider | string | 是 | RPC提供商（infura, alchemy等） | "infura" |

**请求示例**：
```json
{
  "wallet_type": "metamask",
  "rpc_provider": "infura"
}
```

---

#### 返回结果 (Return Result)

**200 OK Response**

| 参数名 | 类型 | 说明 |
|--------|------|------|
| success | boolean | 请求成功状态 |
| data.id | string | 会话UUID |
| data.wallet_type | string | 钱包类型 |
| data.rpc_provider | string | RPC提供商 |
| data.status | string | 会话状态（active, completed） |
| data.created_at | string | 创建时间戳（ISO格式） |
| metadata.request_id | string | 请求ID（用于追踪） |
| metadata.timestamp | string | 响应时间戳（ISO格式） |

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "id": "bff84090-799b-4b01-a5cb-f43a1f11ab12",
    "wallet_type": "metamask",
    "rpc_provider": "infura",
    "status": "active",
    "created_at": "2026-03-02T04:07:58"
  },
  "metadata": {
    "request_id": "62fbe0b0-1280-4b8a-b59d-e06564b0298b",
    "timestamp": "2026-03-02T04:07:58.197261+00:00"
  }
}
```

---

### 1.2 获取会话详情 (Get Session Details)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/sessions/{session_id}
```

#### 功能说明 (Function Description)
**概述**：获取指定会话的详细信息

**功能描述**：
- 查询会话基本信息（ID、类型、提供商）
- 获取流量捕获统计（包数量、持续时间）
- 显示会话状态和元数据

**工作原理**：
1. 通过session_id查询数据库
2. 聚合流量统计信息
3. 格式化为标准响应格式

---

#### 路径参数 (Path Parameters)

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| session_id | string | 是 | 会话UUID |

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "id": "9831004e-9af2-4e7c-93c2-b23b01171e55",
    "wallet_type": "MetaMask",
    "rpc_provider": "https://test.rpc.com",
    "start_time": "2026-03-01T04:33:20.607460+00:00",
    "end_time": null,
    "packet_count": 0,
    "duration_seconds": null,
    "status": "active",
    "session_metadata": null,
    "created_at": "2026-03-01T04:33:21",
    "updated_at": "2026-03-01T04:33:21"
  },
  "metadata": {
    "request_id": "c66b6e7b-bc6c-4420-bd98-07a507e527e8",
    "timestamp": "2026-03-02T04:10:55.307261+00:00"
  }
}
```

---

### 1.3 列出会话 (List Sessions)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/sessions
```

#### 功能说明 (Function Description)
**概述**：列出所有会话，支持分页和过滤

**功能描述**：
- 支持按钱包类型、RPC提供商、状态过滤
- 支持分页查询（skip, limit）
- 返回会话摘要信息

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|--------|------|------|--------|------|------|
| skip | integer | 否 | 0 | - | 跳过记录数 |
| limit | integer | 否 | 50 | 1-100 | 返回记录数 |
| wallet_type | string | 否 | - | - | 按钱包类型过滤 |
| rpc_provider | string | 否 | - | - | 按RPC提供商过滤 |
| status | string | 否 | - | - | 按状态过滤（active, completed） |

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "ca6ffa93-8069-4a8f-abda-f0b4179059e1",
        "wallet_type": "walletconnect",
        "rpc_provider": "alchemy",
        "status": "active",
        "packet_count": 0,
        "created_at": "2026-03-02T04:10:27"
      }
    ],
    "total": 12,
    "limit": 5,
    "offset": 0
  },
  "metadata": {
    "request_id": "028788dc-f089-4f2f-9f99-ac961d42501d",
    "timestamp": "2026-03-02T04:10:38.102861+00:00"
  }
}
```

---

### 1.4 更新会话 (Update Session)

#### 接口地址 (Endpoint Address)
```
PUT /api/v1/sessions/{session_id}
```

#### 功能说明 (Function Description)
**概述**：更新会话状态和元数据

**功能描述**：
- 更新会话状态（ACTIVE → COMPLETED）
- 设置捕获结束时间
- 更新数据包统计

---

### 1.5 删除会话 (Delete Session)

#### 接口地址 (Endpoint Address)
```
DELETE /api/v1/sessions/{session_id}
```

#### 功能说明 (Function Description)
**概述**：删除会话及关联数据

**功能描述**：
- 删除会话记录
- 级联删除关联的流量记录
- 级联删除关联的泄露事件
- 级联删除关联的评估结果

---

## 2. 流量捕获 (Traffic Capture)

### 2.1 开始流量捕获 (Start Traffic Capture)

#### 接口地址 (Endpoint Address)
```
POST /api/v1/sessions/{session_id}/traffic/start
```

#### 功能说明 (Function Description)
**概述**：开始捕获指定会话的网络流量

**功能描述**：
- 初始化流量捕获器
- 配置捕获参数（包数量、持续时间）
- 启动实时流量记录

**技术实现**：
- **流量提供者模式**：支持mock和mitm两种模式
- **Mock提供者**：生成模拟流量数据用于测试
- **Mitm提供者**：拦截真实HTTPS/TLS流量（生产环境）

**工作流程**：
1. 验证会话状态（必须为ACTIVE）
2. 选择流量提供者类型（mock/mitm）
3. 配置捕获参数
4. 启动流量捕获
5. 流式存储到数据库

**核心算法**：
- Mock流量生成算法：基于统计模型生成真实感数据
- 流量分类算法：按RPC方法类型（eth_getBalance, eth_call等）

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|--------|------|------|--------|------|------|
| packet_count | integer | 否 | 500 | 1-10000 | 捕获数据包数量 |
| duration_seconds | integer | 否 | null | 1-3600 | 捕获持续时间（秒） |

---

#### 返回示例
```json
{
  "success": true,
  "data": {
    "active": true,
    "packets_captured": 500,
    "session_id": "bff84090-799b-4b01-a5cb-f43a1f11ab12"
  },
  "metadata": {
    "request_id": "62fbe0b0-1280-4b8a-b59d-e06564b0298b",
    "timestamp": "2026-03-02T04:07:58.197261+00:00"
  }
}
```

---

### 2.2 停止流量捕获 (Stop Traffic Capture)

#### 接口地址 (Endpoint Address)
```
POST /api/v1/sessions/{session_id}/traffic/stop
```

#### 功能说明 (Function Description)
**概述**：停止流量捕获并完成会话

**功能描述**：
- 停止流量捕获器
- 更新会话状态为COMPLETED
- 计算捕获统计信息
- 触发隐私检测流程

**工作流程**：
1. 停止流量捕获器
2. 获取捕获统计（包数量、持续时间）
3. 更新会话状态
4. 自动触发隐私检测

---

### 2.3 获取流量记录 (Get Traffic Records)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/sessions/{session_id}/traffic
```

#### 功能说明 (Function Description)
**概述**：获取指定会话的流量记录，支持过滤和分页

**功能描述**：
- 获取会话所有流量记录
- 支持按HTTP方法、RPC方法过滤
- 支持分页查询
- 返回详细的流量分析数据

**技术实现**：
- SQL查询优化：使用索引加速查询
- 数据类型转换：时间戳格式化
- 响应时间统计：实时计算

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|--------|------|------|--------|------|------|
| method | string | 否 | - | - | 按HTTP方法过滤（GET, POST等） |
| rpc_method | string | 否 | - | - | 按RPC方法过滤 |
| limit | integer | 否 | 100 | 1-1000 | 返回记录数 |
| offset | integer | 否 | 0 | - | 跳过记录数 |

**核心数据结构**：
```json
{
  "traffic": [
    {
      "id": "string",
      "session_id": "string",
      "method": "POST",
      "endpoint": "string",
      "rpc_method": "eth_getBalance",
      "request_timestamp": "ISO-8601",
      "response_time_ms": 125,
      "response_status": 200,
      "response_size_bytes": 256,
      "user_agent": "string"
    }
  ],
  "total": 500,
  "limit": 100,
  "offset": 0
}
```

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "traffic": [
      {
        "id": "d4ed36da-d968-4b1c-bd34-a5d89f4b18dd",
        "session_id": "ca6ffa93-8069-4a8f-abda-f0b4179059e1",
        "method": "POST",
        "endpoint": "https://eth-mainnet.g.alchemy.com/v2/",
        "rpc_method": "eth_getBalance",
        "request_timestamp": "2026-03-02T04:12:00",
        "response_time_ms": 125,
        "response_status": 200,
        "response_size_bytes": 256,
        "user_agent": "WalletConnect/2.0.0"
      }
    ],
    "total": 3,
    "limit": 100,
    "offset": 0
  },
  "metadata": {
    "request_id": "f0342205-427e-44a5-86b8-a68af1158af3",
    "timestamp": "2026-03-02T04:12:00.895069+00:00"
  }
}
```

---

### 2.4 记录单条流量 (Record Single Traffic)

#### 接口地址 (Endpoint Address)
```
POST /api/v1/sessions/{session_id}/traffic/record
```

#### 功能说明 (Function Description)
**概述**：记录单条流量记录（用于RPC代理集成）

**功能描述**：
- RPC代理调用此接口上传流量数据
- 自动生成时间戳和响应时间
- 支持IP地址哈希保护隐私

**隐私保护机制**：
- IP地址哈希：SHA-256哈希后截取前16位
- 地址哈希：保护账户隐私
- 不存储原始IP或地址

**请求体参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| method | string | 否 | HTTP方法（默认：POST） |
| endpoint | string | 否 | 请求端点 |
| request_body | string | 否 | 请求体 |
| rpc_method | string | 否 | RPC方法名 |
| rpc_params_hash | string | 否 | RPC参数哈希 |
| request_timestamp | string | 否 | 请求时间戳（ISO格式） |
| response_time_ms | integer | 否 | 响应时间（毫秒） |
| response_status | integer | 否 | HTTP状态码 |
| response_size_bytes | integer | 否 | 响应大小（字节） |
| ip_address_hash | string | 否 | IP地址哈希 |
| user_agent | string | 否 | 用户代理 |

---

## 3. 分析统计 (Analytics & Statistics)

### 3.1 获取摘要统计 (Get Summary Statistics)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/summary
```

#### 功能说明 (Function Description)
**概述**：获取整体摘要统计信息

**功能描述**：
- 统总会话总数（按状态分类）
- 统计流量记录总数
- 统计隐私泄露事件总数
- 统计风险评估总数
- 计算平均风险评分

**核心算法**：
- 聚合查询：使用SQL的COUNT、AVG等聚合函数
- 数据库索引优化：加速统计查询
- 实时计算：每次请求实时生成统计数据

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "total_sessions": 13,
    "total_traffic": 900,
    "total_leaks": 0,
    "total_assessments": 2,
    "average_risk_score": 24.5,
    "sessions_by_status": {
      "active": 13
    }
  },
  "metadata": {
    "request_id": "72656393-6fed-418f-849b-7eb63cf41d9f",
    "timestamp": "2026-03-02T04:13:58.730365+00:00"
  }
}
```

---

### 3.2 获取趋势分析 (Get Trends)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/trends
```

#### 功能说明 (Function Description)
**概述**：获取趋势分析数据

**功能描述**：
- 分析会话数量趋势
- 分析泄露事件趋势
- 分析风险评分趋势
- 支持自定义时间范围

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|--------|------|------|--------|------|------|
| days | integer | 否 | 7 | 1-90 | 分析天数 |

**核心算法**：
- 时间序列分析：按日期分组统计
- 趋势计算：计算环比增长率
- 移动平均：平滑短期波动

---

### 3.3 获取方法频率 (Get Method Frequency)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/methods/frequency
```

#### 功能说明 (Function Description)
**概述**：获取最常用的RPC方法统计

**功能描述**：
- 统计RPC方法调用频率
- 识别高频方法
- 支持自定义返回数量

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|--------|------|------|--------|------|------|
| limit | integer | 否 | 10 | 1-50 | 返回方法数量 |

**核心算法**：
- 频率统计：GROUP BY + COUNT
- 排序：按调用次数降序
- 限制返回数量

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "frequencies": [
      {
        "method": "eth_blockNumber",
        "count": 445
      },
      {
        "method": "eth_call",
        "count": 442
      },
      {
        "method": "eth_getBlockByNumber",
        "count": 1
      }
    ]
  },
  "metadata": {
    "request_id": "2977e92f-d667-479b-89e0-e5fdd7d3427f",
    "timestamp": "2026-03-02T04:10:03.644341+00:00"
  }
}
```

---

### 3.4 获取响应时间统计 (Get Response Time Stats)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/response-times
```

#### 功能说明 (Function Description)
**概述**：获取RPC响应时间统计

**功能描述**：
- 计算最小、最大、平均响应时间
- 计算中位数和标准差
- 计算百分位数（P50, P95, P99）
- 识别性能瓶颈

**核心算法**：
- 统计算法：计算五个数（最小、最大、中位数、Q1、Q3）
- 百分位数算法：线性插值计算精确百分位数
- 标准差计算：总体标准差公式

**返回示例**：
```json
{
  "success": true,
  "data": {
    "min": 45.2,
    "max": 1250.8,
    "mean": 187.5,
    "median": 156.3,
    "std_dev": 98.4,
    "p50": 156.3,
    "p95": 385.2,
    "p99": 625.7,
    "total_requests": 25000
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-02T04:10:00.000000+00:00"
  }
}
```

---

## 功能模块二：隐私泄露检测与分类
## Module 2: Privacy Leak Detection & Classification

### 模块概述 (Module Overview)

**功能描述**：自动化检测通信中的隐私泄露事件并分类

**核心技术**：
- 基于规则的检测引擎（Rule-Based Detection Engine）
- YAML规则配置（灵活的规则定义）
- 置信度评分系统（Confidence Scoring）
- 多维度分类体系（Multi-dimensional Classification）

**原理解释**：
1. **规则引擎**：加载YAML规则文件，匹配流量模式
2. **模式匹配**：检查RPC方法、参数、频率等模式
3. **泄露分类**：按类型（身份、资产、行为、位置）分类
4. **置信度评估**：基于规则权重计算置信度

**检测向量**：
- 直接数据泄露：明确泄露敏感数据
- 模式泄露：可推断的调用模式
- 时序泄露：基于时间序列的行为模式
- 元数据泄露：HTTP头信息泄露

---

## 4. 检测规则 (Detection Rules)

### 4.1 列出规则 (List Rules)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/rules
```

#### 功能说明 (Function Description)
**概述**：列出所有检测规则，支持过滤

**功能描述**：
- 加载YAML规则文件
- 返回所有检测规则
- 支持按类别、是否启用过滤

**规则分类系统**：
- **IDENTITY（身份）**：地址、账户、身份信息泄露
- **ASSET（资产）**：余额、交易、资产信息泄露
- **BEHAVIOR（行为）**：行为模式、使用习惯泄露
- **LOCATION（位置）**：时区、网络指纹泄露

**优先级系统**：
- **CRITICAL（严重）**：高风险泄露
- **HIGH（高）**：高风险泄露
- **MEDIUM（中）**：中风险泄露
- **LOW（低）**：低风险泄露

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| category | string | 否 | - | 按类别过滤（identity, asset, behavior, location） |
| enabled_only | boolean | 否 | false | 只返回启用的规则 |

**核心算法**：
- 规则加载：解析YAML文件为规则对象
- 规则过滤：基于类别和状态过滤
- 规则排序：按优先级排序

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "rules": [
      {
        "rule_id": "DR-BE-2",
        "name": "Bot Behavior Detection",
        "category": "behavior",
        "enabled": true,
        "priority": "HIGH",
        "description": "Identify timing patterns indicative of automated bots (fixed intervals, burst patterns)"
      },
      {
        "rule_id": "DR-BE-4",
        "name": "High Frequency Activity",
        "category": "behavior",
        "enabled": true,
        "priority": "MEDIUM",
        "description": "Detect unusually high request frequency patterns"
      }
    ],
    "total": 12
  },
  "metadata": {
    "request_id": "bc2aaa11-ac17-4389-81e1-41443bd354d0",
    "timestamp": "2026-03-02T04:08:14.134762+00:00"
  }
}
```

---

### 4.2 获取规则摘要 (Get Rules Summary)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/rules/summary
```

#### 功能说明 (Function Description)
**概述**：获取检测规则摘要统计

**功能描述**：
- 统计总规则数
- 按类别统计规则数
- 按优先级统计规则数
- 统计启用/禁用状态

**核心算法**：
- 聚合统计：按类别、优先级分组计数
- 实时计算：每次请求重新计算

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "total": 12,
    "enabled": 12,
    "disabled": 0,
    "by_category": {
      "behavior": {
        "total": 4,
        "enabled": 4
      },
      "identity": {
        "total": 4,
        "enabled": 4
      },
      "asset": {
        "total": 2,
        "enabled": 2
      },
      "location": {
        "total": 2,
        "enabled": 2
      }
    }
  },
  "metadata": {
    "request_id": "b7b0464c-ecf6-46ca-bc2d-f27df46408ba",
    "timestamp": "2026-03-02T04:08:21.398961+00:00"
  }
}
```

---

### 4.3 获取规则详情 (Get Rule Details)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/rules/{rule_id}
```

#### 功能说明 (Function Description)
**概述**：获取指定规则的详细信息

**功能描述**：
- 返回规则的完整配置
- 显示规则条件和动作
- 展示规则优先级和状态

**核心算法**：
- 规则查找：按rule_id查找规则对象
- 规则解析：解析规则的条件和动作

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "id": "DR-AS-1",
    "name": "Asset Holding Inference",
    "category": "asset",
    "priority": "HIGH",
    "enabled": true,
    "description": "Infer asset holdings from repeated asset metadata queries",
    "conditions": [
      {
        "type": "method_pattern",
        "methods": [
          "erc20_balanceOf",
          "eth_getBalance"
        ],
        "min_frequency": 10
      }
    ],
    "actions": [
      {
        "type": "create_leak_event",
        "leak_type": "ASSET",
        "confidence_base": 0.8
      }
    ],
    "version": 1
  },
  "metadata": {
    "request_id": "124a7c4e-2801-4094-ab0d-c9819f211292",
    "timestamp": "2026-03-02T04:09:03.961123+00:00"
  }
}
```

---

## 5. 隐私泄露事件 (Privacy Leak Events)

### 5.1 获取会话泄露 (Get Session Leaks)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/sessions/{session_id}/leaks
```

#### 功能说明 (Function Description)
**概述**：获取指定会话的隐私泄露事件

**功能描述**：
- 获取会话所有泄露事件
- 支持按泄露类型过滤
- 支持按最小置信度过滤
- 支持按规则ID过滤
- 返回详细泄露分析数据

**分类体系**：
- **IDENTITY（身份）**：地址、账户、身份
- **ASSET（资产）**：余额、交易、资产
- **BEHAVIOR（行为）**：行为模式、使用习惯
- **LOCATION（位置）**：时区、网络指纹

**置信度评估算法**：
- 基于规则权重计算基础置信度
- 考虑频率因素（高频提升置信度）
- 考虑时间一致性（一致行为提升置信度）
- 计算置信区间（下限、上限）

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| leak_type | enum | 否 | - | 按泄露类型过滤（IDENTITY, ASSET, BEHAVIOR, LOCATION） |
| min_confidence | float | 否 | - | 按最小置信度过滤（0.0-1.0） |
| rule_id | string | 否 | - | 按规则ID过滤 |
| limit | integer | 否 | 100 | 返回记录数（1-1000） |
| offset | integer | 否 | 0 | 跳过记录数 |

**核心数据结构**：
```json
{
  "leaks": [
    {
      "id": "string",
      "session_id": "string",
      "leak_type": "ASSET",
      "method_name": "eth_getBalance",
      "description": "Asset/Balance Tracking",
      "confidence": 0.9,
      "confidence_interval_low": 0.85,
      "confidence_interval_high": 0.95,
      "details": {},
      "timestamp": "ISO-8601",
      "address_hash": "string",
      "rule_id": "DR-AS-1"
    }
  ]
}
```

---

### 5.2 列出所有泄露 (List All Leaks)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/leaks
```

#### 功能说明 (Function Description)
**概述**：列出所有会话的隐私泄露事件

**功能描述**：
- 跨会话查询所有泄露事件
- 支持多维度过滤
- 支持分页查询

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| leak_type | enum | 否 | - | 按泄露类型过滤 |
| min_confidence | float | 否 | - | 按最小置信度过滤 |
| skip | integer | 否 | 0 | 跳过记录数 |
| limit | integer | 否 | 50 | 返回记录数（1-100） |

---

## 功能模块三：风险量化评估
## Module 3: Risk Quantitative Assessment

### 模块概述 (Module Overview)

**功能描述**：建立多维度隐私风险量化指标体系

**核心技术**：
- 多维度风险评估模型（Multi-dimensional Risk Assessment Model）
- 统计学指标计算（Statistical Metrics Calculation）
- 机器学习增强评估（ML-Enhanced Assessment）
- 基线对比分析（Baseline Comparison Analysis）

**四个核心维度**：

1. **信息熵指标（Entropy Score）**
   - 衡量信息的可预测性
   - 熵越高，随机性越大，隐私保护越好
   - 算法：Shannon熵公式 H(X) = -Σ p(x)log₂p(x)

2. **唯一性指标（Uniqueness Score）**
   - 衡量用户身份的可区分性
   - 唯一性越低，用户越难被识别
   - 算法：计算唯一行为特征占比

3. **关联性指标（Correlation Score）**
   - 衡量跨会话行为的一致性
   - 关联性越高，行为模式越容易被追踪
   - 算法：皮尔逊相关系数

4. **时效性指标（Temporal Score）**
   - 衡量信息的时效性价值
   - 时效性越高，信息泄露风险越大
   - 算法：时间戳分布分析

**原理解释**：
1. **数据预处理**：清洗、标准化流量数据
2. **特征提取**：提取统计特征（频率、时间间隔等）
3. **指标计算**：应用算法计算四个核心指标
4. **综合评分**：加权平均生成总体评分（0-100）
5. **置信区间**：计算评分的置信区间（bootstrap方法）

**评分系统**：
- **总体评分（Overall Score）**：0-100，综合四个维度
- **风险等级（Risk Level）**：
  - LOW（低风险）：0-30
  - MEDIUM（中风险）：31-50
  - HIGH（高风险）：51-70
  - CRITICAL（严重风险）：71-100

---

## 6. 风险评估 (Risk Assessment)

### 6.1 运行风险评估 (Run Risk Assessment)

#### 接口地址 (Endpoint Address)
```
POST /api/v1/sessions/{session_id}/assess
```

#### 功能说明 (Function Description)
**概述**：对指定会话运行综合风险评估

**功能描述**：
- 提取会话流量数据
- 计算四个核心指标
- 执行基线对比
- 生成风险评估报告
- 提供改进建议

**核心算法详解**：

**1. 信息熵算法（Entropy Calculation）**
```
H = -Σ (p_i × log₂(p_i))

其中：
- p_i：RPC方法i的调用频率
- H：信息熵，单位为比特
```
应用场景：检测是否过度依赖某几个方法

**2. 唯一性算法（Uniqueness Calculation）**
```
U = 1 - (n_unique / n_total)

其中：
- n_unique：唯一行为特征数
- n_total：总行为特征数
```
应用场景：评估行为模式的可区分性

**3. 关联性算法（Correlation Calculation）**
```
ρ = Cov(X,Y) / (σ_X × σ_Y)

其中：
- Cov(X,Y)：协方差
- σ_X, σ_Y：标准差
```
应用场景：检测跨会话行为的一致性

**4. 时效性算法（Temporal Calculation）**
```
T = 1 - (time_span / total_duration)

其中：
- time_span：活动时间跨度
- total_duration：总持续时间
```
应用场景：评估信息的时效性价值

**综合评分算法**：
```
Overall = Σ (w_i × Score_i)

权重分配：
- w_entropy = 0.25
- w_uniqueness = 0.25
- w_correlation = 0.25
- w_temporal = 0.25

Score_i = score_i × (1 - confidence_i)
```

**置信度计算**：
- 使用Bootstrap方法重采样1000次
- 计算评分的95%置信区间
- 置信区间宽度反映不确定性

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "id": "7e3cd0ef-ac13-42fb-880d-5d31616339e9",
    "session_id": "ca6ffa93-8069-4a8f-abda-f0b4179059e1",
    "overall_score": 37,
    "risk_level": "medium",
    "entropy_score": 1.0,
    "uniqueness_score": 0.5,
    "correlation_score": 0.0,
    "temporal_score": 0.0,
    "confidence": 0.85,
    "confidence_interval_low": 0.77,
    "confidence_interval_high": 0.93,
    "recommendations": [
      "Review privacy settings and follow blockchain best practices"
    ],
    "baseline_comparison": {
      "risk_level": "medium",
      "ideal_score": 0,
      "worst_score": 100,
      "overall_score": 37
    },
    "assessed_at": "2026-03-02T04:12:21",
    "created_at": "2026-03-02T04:12:21"
  },
  "metadata": {
    "request_id": "945af675-5249-46c5-a35c-ec149e523c2e",
    "timestamp": "2026-03-02T04:12:20.885028+00:00"
  }
}
```

---

### 6.2 获取评估结果 (Get Assessment)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/sessions/{session_id}/assessment
```

#### 功能说明 (Function Description)
**概述**：获取指定会话的最新风险评估结果

**功能描述**：
- 获取最新评估记录
- 返回完整的评估数据
- 包含推荐建议和基线对比

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "id": "ab61898a-0bd7-4177-9982-20fba86ed2f1",
    "session_id": "8b23962f-a75a-4349-8d7b-82ac0a7df4db",
    "overall_score": 12,
    "risk_level": "low",
    "assessed_at": "2026-03-02T04:13:32",
    "created_at": "2026-03-02T04:13:32"
  },
  "metadata": {
    "request_id": "96292404-1660-424e-ba83-3a1afc2a2010",
    "timestamp": "2026-03-02T04:12:31.163003+00:00"
  }
}
```

---

### 6.3 列出所有评估 (List Assessments)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/assessments
```

#### 功能说明 (Function Description)
**概述**：列出所有风险评估，支持过滤和分页

**功能描述**：
- 跨会话查询所有评估记录
- 支持按风险等级过滤
- 支持分页查询

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| skip | integer | 否 | 0 | 跳过记录数 |
| limit | integer | 否 | 50 | 返回记录数（1-100） |
| risk_level | string | 否 | - | 按风险等级过滤（LOW, MEDIUM, HIGH, CRITICAL） |

**返回示例（基于真实数据）**：
```json
{
  "success": true,
  "data": {
    "assessments": [
      {
        "id": "ab61898a-0bd7-4177-9982-20fba86ed2f1",
        "session_id": "8b23962f-a75a-4349-8d7b-82ac0a7df4db",
        "overall_score": 12,
        "risk_level": "low",
        "assessed_at": "2026-03-02T04:13:32",
        "created_at": "2026-03-02T04:13:32"
      }
    ],
    "total": 2,
    "skip": 0,
    "limit": 5
  },
  "metadata": {
    "request_id": "b462539d-e275-4c3b-bde9-fb0d69e12916",
    "timestamp": "2026-03-02T04:13:47.718931+00:00"
  }
}
```

---

## 7. 风险分析 (Risk Analysis)

### 7.1 获取泄露分布 (Get Leak Distribution)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/leaks/distribution
```

#### 功能说明 (Function Description)
**概述**：获取隐私泄露类型分布统计

**功能描述**：
- 按泄露类型统计泄露数量
- 计算各类别占比
- 识别主要泄露类型

**核心算法**：
- 分组统计：GROUP BY leak_type
- 百分比计算：计算各类别占比

**返回示例**：
```json
{
  "success": true,
  "data": {
    "distribution": {
      "IDENTITY": 125,
      "ASSET": 450,
      "BEHAVIOR": 320,
      "LOCATION": 355
    },
    "total": 1250
  },
  "metadata": {
    "request_id": "03af42e4-f7ef-45df-a1e8-ee64d02aabb2",
    "timestamp": "2026-03-02T04:10:11.064000+00:00"
  }
}
```

---

### 7.2 获取风险分布 (Get Risk Distribution)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/risk/distribution
```

#### 功能说明 (Function Description)
**概述**：获取风险等级分布统计

**功能描述**：
- 按风险等级统计评估数量
- 计算各类等级占比
- 识别高风险会话

**返回示例**：
```json
{
  "success": true,
  "data": {
    "distribution": {
      "LOW": 15,
      "MEDIUM": 20,
      "HIGH": 12,
      "CRITICAL": 3
    },
    "total": 50
  },
  "metadata": {
    "request_id": "35af13c3-8597-49cb-83bc-764dbe807749",
    "timestamp": "2026-03-02T04:10:19.561000+00:00"
  }
}
```

---

### 7.3 获取高风险会话 (Get Top Risk Sessions)

#### 接口地址 (Endpoint Address)
```
GET /api/v1/analytics/sessions/top-risk
```

#### 功能说明 (Function Description)
**概述**：获取风险评分最高的会话列表

**功能描述**：
- 按风险评分降序排列
- 返回Top N高风险会话
- 用于风险监控和预警

**查询参数**：

| 参数名 | 类型 | 必填 | 默认值 | 范围 | 说明 |
|--------|------|------|--------|------|------|
| limit | integer | 否 | 10 | 1-50 | 返回会话数量 |

**核心算法**：
- 排序算法：ORDER BY overall_score DESC
- 限制返回数量：LIMIT N

---

## 公共错误响应 (Common Error Responses)

### 404 Not Found
资源未找到。

```json
{
  "detail": {
    "code": "NOT_FOUND",
    "message": "Session {session_id} not found"
  }
}
```

### 400 Bad Request
无效的请求输入。

```json
{
  "detail": {
    "code": "INVALID_INPUT",
    "message": "Session is not active"
  }
}
```

### 422 Validation Error
请求验证失败。

```json
{
  "detail": [
    {
      "loc": ["body", "wallet_type"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 限流策略 (Rate Limiting)

所有API端点都有速率限制以防止滥用：

- **默认限制**：每IP地址每分钟100个请求
- **响应头包含**：`X-RateLimit-Limit`、`X-RateLimit-Remaining`、`X-RateLimit-Reset`

超过速率限制时：

```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later."
  }
}
```

---

## 认证与授权 (Authentication & Authorization)

当前实现不需要认证（开发环境）。生产部署建议：

- API密钥认证（API Key Authentication）
- OAuth 2.0令牌认证（OAuth 2.0 Token-based Authentication）
- 基于角色的访问控制（RBAC）

---

## API版本管理 (API Versioning)

当前API版本为 `v1`。所有端点的基础URL为：

```
http://localhost:8000/api/v1
```

新版本将以 `v2`、`v3` 等形式发布。

---

## 支持与联系 (Support & Contact)

- **项目主页**：https://github.com/compass-rose/wallet-rpc-privacy
- **问题报告**：https://github.com/compass-rose/wallet-rpc-privacy/issues

---

**文档版本**：2.0.0
**最后更新**：2026-03-02
**语言**：中英双语（Bilingual Chinese & English）
