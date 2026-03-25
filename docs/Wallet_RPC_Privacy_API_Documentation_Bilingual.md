# Wallet / RPC Privacy Leakage Measurement System  
# API Documentation

**Version:** 2.0  
**Format Note:** This document presents the complete English version first, followed by the complete Chinese version.

---

## English Version

### 1. Introduction

This document defines the API surface for the **Wallet / RPC Privacy Leakage Measurement System**. It merges the previously separated core backend API, risk-analysis API, and dashboard API into one consolidated reference.

### 2. Conventions

#### 2.1 Base URL

```text
http://localhost:8000/api/v1
```

#### 2.2 API Version

Current documented version: `v1`

#### 2.3 Content Type

Most request and response bodies use:

```text
application/json
```

#### 2.4 Authentication

According to the current project documents, the present version does **not** require authentication by default. If the system is deployed outside a local or classroom environment, add authentication and access control externally.

### 3. Standard Response Format

#### 3.1 Success Response

```json
{
  "success": true,
  "data": {},
  "metadata": {
    "request_id": "uuid",
    "timestamp": "2026-03-09T04:00:00.000Z"
  }
}
```

#### 3.2 Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  },
  "metadata": {
    "request_id": "uuid",
    "timestamp": "2026-03-09T04:00:00.000Z"
  }
}
```

### 4. Endpoint Groups

This document organizes endpoints into two levels.

#### 4.1 Core Stable Endpoints

These form the main usage path:

- session management
- traffic capture and traffic records
- privacy leak retrieval
- risk assessment
- analytics
- detection rules
- health check

#### 4.2 Extended / Research / Visualization Endpoints

These are documented as supported modules or project extensions:

- baseline comparison
- simulated attack
- adversarial testing
- dashboard monitoring
- dashboard reports
- comprehensive report generation
- optional config and report-generation endpoints from the initial specification

### 5. Quick Endpoint Index

| Group | Method | Path | Purpose |
|---|---|---|---|
| Session | POST | `/sessions` | create a session |
| Session | GET | `/sessions/{session_id}` | get one session |
| Session | GET | `/sessions` | list sessions |
| Session | PUT | `/sessions/{session_id}` | update session |
| Session | DELETE | `/sessions/{session_id}` | delete session |
| Traffic | POST | `/sessions/{session_id}/traffic/start` | start capture |
| Traffic | POST | `/sessions/{session_id}/traffic/stop` | stop capture |
| Traffic | GET | `/sessions/{session_id}/traffic` | get traffic records |
| Traffic | POST | `/sessions/{session_id}/traffic/record` | record one traffic item |
| Leaks | GET | `/sessions/{session_id}/leaks` | get leaks for a session |
| Leaks | GET | `/leaks` | list all leaks |
| Assessment | POST | `/sessions/{session_id}/assess` | run risk assessment |
| Assessment | GET | `/sessions/{session_id}/assessment` | get assessment for a session |
| Assessment | GET | `/assessments` | list assessments |
| Analytics | GET | `/analytics/summary` | overall summary |
| Analytics | GET | `/analytics/trends` | trends over time |
| Analytics | GET | `/analytics/leaks/distribution` | leak-type distribution |
| Analytics | GET | `/analytics/risk/distribution` | risk-level distribution |
| Analytics | GET | `/analytics/methods/frequency` | method frequency statistics |
| Analytics | GET | `/analytics/sessions/top-risk` | top-risk sessions |
| Analytics | GET | `/analytics/response-times` | response-time statistics |
| Rules | GET | `/rules` | list rules |
| Rules | GET | `/rules/summary` | summarize rules |
| Rules | GET | `/rules/{rule_id}` | get rule details |
| Research | POST | `/sessions/{session_id}/baseline-compare` | compare with baselines |
| Research | POST | `/sessions/{session_id}/simulate-attack` | simulate attack effectiveness |
| Research | POST | `/sessions/{session_id}/adversarial-test` | evaluate defenses |
| Dashboard | GET | `/dashboard/monitor/status` | current monitoring status |
| Dashboard | GET | `/dashboard/monitor/leaks/stream` | leak event stream |
| Dashboard | GET | `/dashboard/monitor/risk/metrics` | real-time risk metrics |
| Dashboard | GET | `/dashboard/reports/timeline` | timeline report |
| Dashboard | GET | `/dashboard/reports/heatmap` | heatmap report |
| Dashboard | GET | `/dashboard/charts` | aggregated chart bundle |
| Dashboard | GET | `/dashboard/charts/{chart_type}` | single chart |
| Dashboard | POST | `/dashboard/comprehensive-report` | full combined report |
| Utility | GET | `/health` | health check |

### 6. Session Management

#### 6.1 Create Session

**Method:** `POST`  
**Path:** `/sessions`

**Purpose:**  
Create a new capture session for a wallet and RPC provider pair.

**Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `wallet_type` | string | yes | wallet name or type, such as `MetaMask` |
| `rpc_provider` | string | yes | RPC provider URL or logical provider name |

**Example Request**

```http
POST /api/v1/sessions
Content-Type: application/json
```

```json
{
  "wallet_type": "MetaMask",
  "rpc_provider": "https://mainnet.infura.io/v3/test"
}
```

**Typical Success Fields**

| Field | Description |
|---|---|
| `data.id` | session UUID |
| `data.wallet_type` | wallet type |
| `data.rpc_provider` | provider used |
| `data.status` | session state |
| `data.created_at` | creation timestamp |

---

#### 6.2 Get Session Details

**Method:** `GET`  
**Path:** `/sessions/{session_id}`

**Purpose:**  
Retrieve one session by UUID.

**Path Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | yes | session UUID |

---

#### 6.3 List Sessions

**Method:** `GET`  
**Path:** `/sessions`

**Purpose:**  
List sessions with pagination and optional filters.

**Common Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | no | number of records to skip |
| `limit` | integer | no | maximum returned records |
| `wallet_type` | string | no | filter by wallet type |

---

#### 6.4 Update Session

**Method:** `PUT`  
**Path:** `/sessions/{session_id}`

**Purpose:**  
Update mutable session fields when supported by the implementation.

**Notes:**  
This endpoint appears in the specification document and should be treated as supported only if implemented in the current codebase.

---

#### 6.5 Delete Session

**Method:** `DELETE`  
**Path:** `/sessions/{session_id}`

**Purpose:**  
Delete a session and its associated derived data, according to implementation policy.

### 7. Traffic Capture and Traffic Records

#### 7.1 Start Traffic Capture

**Method:** `POST`  
**Path:** `/sessions/{session_id}/traffic/start`

**Purpose:**  
Start traffic capture for the selected session.

**Path Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | yes | target session UUID |

**Expected Result:**  
Session capture state becomes active.

---

#### 7.2 Stop Traffic Capture

**Method:** `POST`  
**Path:** `/sessions/{session_id}/traffic/stop`

**Purpose:**  
Stop capture for the selected session.

---

#### 7.3 Get Traffic Records

**Method:** `GET`  
**Path:** `/sessions/{session_id}/traffic`

**Purpose:**  
Return normalized traffic records for a session.

**Common Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | no | pagination offset |
| `limit` | integer | no | pagination size |
| `method_name` | string | no | filter by RPC method |

**Typical Record Fields**

| Field | Description |
|---|---|
| `id` | traffic record ID |
| `session_id` | related session |
| `method_name` | RPC method |
| `timestamp` | observed time |
| `response_time_ms` | latency |
| `address_hash` | anonymized address identifier |

---

#### 7.4 Record Single Traffic

**Method:** `POST`  
**Path:** `/sessions/{session_id}/traffic/record`

**Purpose:**  
Insert one traffic record manually or from a testing source.

**Typical Request Body**

| Field | Type | Required | Description |
|---|---|---|---|
| `method_name` | string | yes | RPC method |
| `timestamp` | string | no | ISO timestamp |
| `response_time_ms` | number | no | response latency |
| `address_hash` | string | no | hashed address |
| `metadata` | object | no | additional normalized metadata |

### 8. Privacy Leak Endpoints

#### 8.1 Get Session Leaks

**Method:** `GET`  
**Path:** `/sessions/{session_id}/leaks`

**Purpose:**  
Return all detected privacy leaks for one session.

**Common Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | no | pagination offset |
| `limit` | integer | no | pagination size |
| `leak_type` | string | no | filter by leak category |

**Typical Leak Fields**

| Field | Description |
|---|---|
| `id` | leak-event ID |
| `session_id` | session UUID |
| `leak_type` | IDENTITY / ASSET / BEHAVIOR / LOCATION |
| `method_name` | related RPC method |
| `description` | human-readable explanation |
| `confidence` | confidence score |
| `confidence_interval_low` | lower CI bound |
| `confidence_interval_high` | upper CI bound |
| `rule_id` | triggering rule |

---

#### 8.2 List All Leaks

**Method:** `GET`  
**Path:** `/leaks`

**Purpose:**  
Return privacy leak events across sessions.

**Common Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | no | pagination offset |
| `limit` | integer | no | pagination size |
| `leak_type` | string | no | leak category |
| `session_id` | string | no | specific session filter |

### 9. Risk Assessment Endpoints

#### 9.1 Run Risk Assessment

**Method:** `POST`  
**Path:** `/sessions/{session_id}/assess`

**Purpose:**  
Compute privacy-risk metrics for a session.

**Path Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | yes | target session UUID |

**Typical Result Fields**

| Field | Description |
|---|---|
| `overall_score` | overall score from 0 to 100 |
| `risk_level` | `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL` |
| `entropy_score` | entropy metric |
| `uniqueness_score` | uniqueness metric |
| `correlation_score` | correlation metric |
| `temporal_score` | temporal metric |
| `confidence` | result confidence |
| `recommendations` | privacy improvement suggestions |
| `assessed_at` | evaluation time |

**Typical Risk-Level Interpretation**

| Level | Score Range |
|---|---|
| `LOW` | 0–30 |
| `MEDIUM` | 31–50 |
| `HIGH` | 51–70 |
| `CRITICAL` | 71–100 |

---

#### 9.2 Get Assessment

**Method:** `GET`  
**Path:** `/sessions/{session_id}/assessment`

**Purpose:**  
Return the most recent or stored risk assessment for a session.

---

#### 9.3 List Assessments

**Method:** `GET`  
**Path:** `/assessments`

**Purpose:**  
List assessments across sessions.

**Common Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `skip` | integer | no | pagination offset |
| `limit` | integer | no | pagination size |
| `risk_level` | string | no | filter by risk level |

### 10. Analytics Endpoints

#### 10.1 Summary Statistics

**Method:** `GET`  
**Path:** `/analytics/summary`

**Purpose:**  
Return overall statistics across all sessions.

**Typical Fields**

| Field | Description |
|---|---|
| `total_sessions` | total sessions |
| `active_sessions` | currently active sessions |
| `completed_sessions` | completed sessions |
| `total_traffic_records` | total traffic count |
| `total_leaks` | total leak count |
| `average_risk_score` | average risk score |
| `high_risk_sessions` | number of high or critical sessions |

---

#### 10.2 Trends

**Method:** `GET`  
**Path:** `/analytics/trends`

**Purpose:**  
Return trend data over a selected time window.

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `days` | integer | no | number of days, often `1–90` |

**Typical Result Structure**

- `dates`
- `session_counts`
- `leak_counts`
- `average_risk_scores`

---

#### 10.3 Leak Distribution

**Method:** `GET`  
**Path:** `/analytics/leaks/distribution`

**Purpose:**  
Return counts by leak type.

---

#### 10.4 Risk Distribution

**Method:** `GET`  
**Path:** `/analytics/risk/distribution`

**Purpose:**  
Return counts by risk level.

---

#### 10.5 Method Frequency

**Method:** `GET`  
**Path:** `/analytics/methods/frequency`

**Purpose:**  
Return the most frequent RPC methods.

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | no | number of methods to return |

---

#### 10.6 Top Risk Sessions

**Method:** `GET`  
**Path:** `/analytics/sessions/top-risk`

**Purpose:**  
Return sessions with the highest risk scores.

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | no | number of sessions to return |

---

#### 10.7 Response-Time Statistics

**Method:** `GET`  
**Path:** `/analytics/response-times`

**Purpose:**  
Return response-time metrics.

**Typical Fields**

| Field | Description |
|---|---|
| `min` | minimum response time |
| `max` | maximum response time |
| `mean` | average response time |
| `median` | median response time |
| `std_dev` | standard deviation |
| `p50` | 50th percentile |
| `p95` | 95th percentile |
| `p99` | 99th percentile |
| `total_requests` | request count |

### 11. Detection Rules Endpoints

#### 11.1 List Rules

**Method:** `GET`  
**Path:** `/rules`

**Purpose:**  
Return detection rules, optionally filtered.

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `category` | string | no | rule category |
| `enabled_only` | boolean | no | whether to return only enabled rules |

**Typical Rule Fields**

| Field | Description |
|---|---|
| `rule_id` | rule identifier |
| `name` | rule name |
| `category` | IDENTITY / ASSET / BEHAVIOR / LOCATION |
| `priority` | LOW / MEDIUM / HIGH / CRITICAL |
| `enabled` | enabled status |
| `description` | rule description |

---

#### 11.2 Rules Summary

**Method:** `GET`  
**Path:** `/rules/summary`

**Purpose:**  
Return aggregate statistics for detection rules.

**Typical Fields**

- `total_rules`
- `enabled_rules`
- `by_category`
- `by_priority`

---

#### 11.3 Rule Details

**Method:** `GET`  
**Path:** `/rules/{rule_id}`

**Purpose:**  
Return detailed information for one rule.

### 12. Research and Extended Analysis Endpoints

#### 12.1 Baseline Comparison

**Method:** `POST`  
**Path:** `/sessions/{session_id}/baseline-compare`

**Purpose:**  
Compare the assessed session with reference baselines.

**Precondition:**  
The session should already have a completed assessment.

**Typical Result Sections**

- `baseline_comparison.actual`
- `baseline_comparison.random_baseline`
- `baseline_comparison.ideal_baseline`
- `baseline_comparison.overall_privacy_score`
- `baseline_comparison.privacy_level`
- `industry_comparison.session_metrics`
- `industry_comparison.industry_mean`
- `industry_comparison.overall_industry_ranking`

---

#### 12.2 Simulated Attack

**Method:** `POST`  
**Path:** `/sessions/{session_id}/simulate-attack`

**Purpose:**  
Estimate distinguishability of sessions using classifier-based or clustering-based attack simulation.

**Precondition:**  
The project notes indicate that this usually needs data from at least two sessions.

**Typical Result Sections**

- `attack_type`
- `num_sessions`
- `classifiers.random_forest`
- `classifiers.naive_bayes`
- `clustering.silhouette_score`
- `clustering.cluster_purity`
- `overall_attack_effectiveness`

---

#### 12.3 Adversarial Test

**Method:** `POST`  
**Path:** `/sessions/{session_id}/adversarial-test`

**Purpose:**  
Evaluate the expected effectiveness of defense strategies.

**Typical Defense Strategies**

- `padding`
- `timing_jitter`
- `method_randomization`

**Typical Result Sections**

- `defense_strategies`
- `recommendations`
- `best_strategy`
- `overall_improvement`

### 13. Dashboard Monitoring Endpoints

#### 13.1 Monitoring Status

**Method:** `GET`  
**Path:** `/dashboard/monitor/status`

**Purpose:**  
Return the current runtime status of capture and overall counts.

**Typical Fields**

| Field | Description |
|---|---|
| `active_sessions` | active session count |
| `total_sessions` | total session count |
| `capturing` | whether capture is active |
| `today_packets` | packets captured today |
| `today_leaks` | leaks detected today |
| `capture_rate` | packets per second or similar |
| `last_capture_time` | last capture timestamp |

---

#### 13.2 Leak Stream

**Method:** `GET`  
**Path:** `/dashboard/monitor/leaks/stream`

**Purpose:**  
Return recent leak events for monitoring panels.

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | no | records to return |
| `offset` | integer | no | pagination offset |

**Typical Result Sections**

- `leaks`
- `stream_position`
- `has_more`
- `leak_rate`

---

#### 13.3 Real-Time Risk Metrics

**Method:** `GET`  
**Path:** `/dashboard/monitor/risk/metrics`

**Purpose:**  
Return high-level real-time risk indicators.

**Typical Fields**

| Field | Description |
|---|---|
| `current_risk_level` | current aggregate risk level |
| `average_risk_score` | current average score |
| `high_risk_sessions` | count of high-risk sessions |
| `risk_trend` | stable / increasing / decreasing |
| `confidence` | confidence estimate |
| `last_updated` | last update time |

### 14. Dashboard Reports and Charts

#### 14.1 Timeline Report

**Method:** `GET`  
**Path:** `/dashboard/reports/timeline`

**Purpose:**  
Return event timeline data for reports.

**Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `time_range` | string | no | `last_hour`, `last_24h`, `last_7d`, `last_30d` |

---

#### 14.2 Heatmap Report

**Method:** `GET`  
**Path:** `/dashboard/reports/heatmap`

**Purpose:**  
Return heatmap-ready matrix data.

**Typical Query Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `time_range` | string | no | selected period |
| `heatmap_type` | string | no | heatmap dimension type |

---

#### 14.3 Get All Charts

**Method:** `GET`  
**Path:** `/dashboard/charts`

**Purpose:**  
Return all chart data needed by the frontend in a single bundle.

**Typical Use Case:**  
ECharts integration or dashboard bootstrapping.

---

#### 14.4 Get a Specific Chart

**Method:** `GET`  
**Path:** `/dashboard/charts/{chart_type}`

**Purpose:**  
Return a single chart payload.

**Path Parameters**

| Field | Type | Required | Description |
|---|---|---|---|
| `chart_type` | string | yes | chart name or chart family |

### 15. Comprehensive Report Endpoint

#### 15.1 Generate Comprehensive Report

**Method:** `POST`  
**Path:** `/dashboard/comprehensive-report`

**Purpose:**  
Generate a combined JSON report that may include:

- tested sessions
- individual assessments
- baseline comparison
- simulated attack results
- adversarial test results
- high-level recommendations

**Typical Characteristics**

- may use parallel processing internally
- useful for course demos and final presentations
- response time in the original note is around one second under sample conditions

### 16. Utility Endpoint

#### 16.1 Health Check

**Method:** `GET`  
**Path:** `/health`

**Purpose:**  
Return service health status.

**Example Response**

```json
{
  "status": "healthy",
  "service": "wallet-privacy-backend"
}
```

### 17. Optional Specification-Level Endpoints

The initial specification also references some endpoints that may be part of future or partial implementation. Treat these as **conditional** unless confirmed in the running backend.

| Method | Path | Notes |
|---|---|---|
| POST | `/api/v1/leaks/simulate` | testing-oriented detection simulation |
| POST | `/api/v1/assessments/evaluate` | evaluate custom data |
| POST | `/api/v1/rules` | create rule |
| PUT | `/api/v1/rules/{rule_id}` | update rule |
| DELETE | `/api/v1/rules/{rule_id}` | delete rule |
| POST | `/api/v1/reports/generate` | generate downloadable report |
| GET | `/api/v1/reports/download/{report_id}` | download generated report |
| GET | `/api/v1/config` | get runtime configuration |
| PUT | `/api/v1/config` | update runtime configuration |

### 18. Common Error Codes

The merged project documents reference the following typical error codes:

| Error Code | Meaning | Typical HTTP Status |
|---|---|---|
| `SESSION_NOT_FOUND` | session does not exist | `404` |
| `ASSESSMENT_NOT_FOUND` | no assessment found | `404` |
| `NO_SESSIONS_FOUND` | no sessions found for the selected range | `404` |
| `CHART_NOT_FOUND` | requested chart does not exist | `404` |
| `INSUFFICIENT_DATA` | not enough data for the requested analysis | `400` |
| `INVALID_INPUT` | invalid input parameters | `400` |
| `INVALID_PARAMETER` | invalid query or path parameter | `400` |
| `INTERNAL_ERROR` | server-side failure | `500` |

### 19. Sample cURL Commands

#### 19.1 Create Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

#### 19.2 Start Capture

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/start
```

#### 19.3 Get Traffic

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

#### 19.4 Get Leaks

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

#### 19.5 Run Assessment

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

#### 19.6 Get Summary Analytics

```bash
curl http://localhost:8000/api/v1/analytics/summary
```

#### 19.7 Get Dashboard Status

```bash
curl http://localhost:8000/api/v1/dashboard/monitor/status
```

#### 19.8 Generate Comprehensive Report

```bash
curl -X POST "http://localhost:8000/api/v1/dashboard/comprehensive-report?time_range=last_24h"
```

### 20. End of English Version

---

## 中文版本

### 1. 简介

本文件定义 **Wallet / RPC Privacy Leakage Measurement System（钱包 / RPC 隐私泄露测量系统）** 的 API 接口集合。本文档将原先分散的核心后端 API、风险分析 API 和 dashboard API 合并为一份统一参考文档。

### 2. 基本约定

#### 2.1 基础 URL

```text
http://localhost:8000/api/v1
```

#### 2.2 API 版本

当前文档版本：`v1`

#### 2.3 内容类型

大多数请求与响应体使用：

```text
application/json
```

#### 2.4 认证

根据当前项目文档，现版本默认**不要求认证**。如果系统部署在本地实验环境之外，建议额外增加认证和访问控制。

### 3. 统一响应格式

#### 3.1 成功响应

```json
{
  "success": true,
  "data": {},
  "metadata": {
    "request_id": "uuid",
    "timestamp": "2026-03-09T04:00:00.000Z"
  }
}
```

#### 3.2 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  },
  "metadata": {
    "request_id": "uuid",
    "timestamp": "2026-03-09T04:00:00.000Z"
  }
}
```

### 4. 接口分组

本文档将接口划分为两层。

#### 4.1 核心稳定接口

这些接口构成系统的主使用流程：

- session 管理
- 流量捕获与流量记录
- 隐私泄露事件查询
- 风险评估
- 统计分析
- 检测规则
- 健康检查

#### 4.2 扩展 / 研究 / 可视化接口

这些接口来自项目扩展模块或研究模块：

- 基线对比
- 模拟攻击
- 对抗测试
- dashboard 监控
- dashboard 报告
- 综合报告生成
- 初始规格中提到的可选 config / report 接口

### 5. 接口总览

| 分组 | 方法 | 路径 | 作用 |
|---|---|---|---|
| Session | POST | `/sessions` | 创建会话 |
| Session | GET | `/sessions/{session_id}` | 获取单个会话 |
| Session | GET | `/sessions` | 获取会话列表 |
| Session | PUT | `/sessions/{session_id}` | 更新会话 |
| Session | DELETE | `/sessions/{session_id}` | 删除会话 |
| Traffic | POST | `/sessions/{session_id}/traffic/start` | 启动捕获 |
| Traffic | POST | `/sessions/{session_id}/traffic/stop` | 停止捕获 |
| Traffic | GET | `/sessions/{session_id}/traffic` | 获取流量记录 |
| Traffic | POST | `/sessions/{session_id}/traffic/record` | 手动写入一条流量记录 |
| Leaks | GET | `/sessions/{session_id}/leaks` | 获取某会话的泄露事件 |
| Leaks | GET | `/leaks` | 获取所有泄露事件 |
| Assessment | POST | `/sessions/{session_id}/assess` | 运行风险评估 |
| Assessment | GET | `/sessions/{session_id}/assessment` | 获取某会话评估结果 |
| Assessment | GET | `/assessments` | 获取评估列表 |
| Analytics | GET | `/analytics/summary` | 总体统计 |
| Analytics | GET | `/analytics/trends` | 时间趋势 |
| Analytics | GET | `/analytics/leaks/distribution` | 泄露类型分布 |
| Analytics | GET | `/analytics/risk/distribution` | 风险等级分布 |
| Analytics | GET | `/analytics/methods/frequency` | 方法频率统计 |
| Analytics | GET | `/analytics/sessions/top-risk` | 高风险会话排行 |
| Analytics | GET | `/analytics/response-times` | 响应时间统计 |
| Rules | GET | `/rules` | 获取规则列表 |
| Rules | GET | `/rules/summary` | 获取规则摘要 |
| Rules | GET | `/rules/{rule_id}` | 获取单条规则详情 |
| Research | POST | `/sessions/{session_id}/baseline-compare` | 与基线进行比较 |
| Research | POST | `/sessions/{session_id}/simulate-attack` | 运行模拟攻击 |
| Research | POST | `/sessions/{session_id}/adversarial-test` | 评估防御策略 |
| Dashboard | GET | `/dashboard/monitor/status` | 获取当前监控状态 |
| Dashboard | GET | `/dashboard/monitor/leaks/stream` | 获取泄露流 |
| Dashboard | GET | `/dashboard/monitor/risk/metrics` | 获取实时风险指标 |
| Dashboard | GET | `/dashboard/reports/timeline` | 获取时间线报告 |
| Dashboard | GET | `/dashboard/reports/heatmap` | 获取热力图报告 |
| Dashboard | GET | `/dashboard/charts` | 获取全部图表数据 |
| Dashboard | GET | `/dashboard/charts/{chart_type}` | 获取单个图表 |
| Dashboard | POST | `/dashboard/comprehensive-report` | 生成综合报告 |
| Utility | GET | `/health` | 健康检查 |

### 6. Session 管理接口

#### 6.1 创建会话

**方法：** `POST`  
**路径：** `/sessions`

**作用：**  
为某个钱包与 RPC 提供商组合创建新的捕获会话。

**请求体**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `wallet_type` | string | 是 | 钱包名称或类型，如 `MetaMask` |
| `rpc_provider` | string | 是 | RPC 提供商 URL 或逻辑名称 |

**请求示例**

```http
POST /api/v1/sessions
Content-Type: application/json
```

```json
{
  "wallet_type": "MetaMask",
  "rpc_provider": "https://mainnet.infura.io/v3/test"
}
```

**常见返回字段**

| 字段 | 说明 |
|---|---|
| `data.id` | session UUID |
| `data.wallet_type` | 钱包类型 |
| `data.rpc_provider` | 使用的 RPC 提供商 |
| `data.status` | 会话状态 |
| `data.created_at` | 创建时间 |

---

#### 6.2 获取单个会话

**方法：** `GET`  
**路径：** `/sessions/{session_id}`

**作用：**  
根据 UUID 获取单个会话。

**路径参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `session_id` | string | 是 | 会话 UUID |

---

#### 6.3 获取会话列表

**方法：** `GET`  
**路径：** `/sessions`

**作用：**  
分页列出会话，并支持基础筛选。

**常见查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skip` | integer | 否 | 跳过多少条记录 |
| `limit` | integer | 否 | 最多返回多少条 |
| `wallet_type` | string | 否 | 按钱包类型筛选 |

---

#### 6.4 更新会话

**方法：** `PUT`  
**路径：** `/sessions/{session_id}`

**作用：**  
在实现支持的情况下，更新可变的会话字段。

**说明：**  
该接口出现在规格文档中，是否可用应以当前代码实现为准。

---

#### 6.5 删除会话

**方法：** `DELETE`  
**路径：** `/sessions/{session_id}`

**作用：**  
删除会话以及与之关联的衍生数据，具体行为以实现逻辑为准。

### 7. 流量捕获与流量记录接口

#### 7.1 启动流量捕获

**方法：** `POST`  
**路径：** `/sessions/{session_id}/traffic/start`

**作用：**  
为指定会话启动流量捕获。

**路径参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `session_id` | string | 是 | 目标会话 UUID |

**预期结果：**  
对应会话进入 active/capturing 状态。

---

#### 7.2 停止流量捕获

**方法：** `POST`  
**路径：** `/sessions/{session_id}/traffic/stop`

**作用：**  
停止该会话的流量捕获。

---

#### 7.3 获取流量记录

**方法：** `GET`  
**路径：** `/sessions/{session_id}/traffic`

**作用：**  
返回某个会话的标准化流量记录。

**常见查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skip` | integer | 否 | 分页偏移 |
| `limit` | integer | 否 | 分页大小 |
| `method_name` | string | 否 | 按 RPC 方法名筛选 |

**常见记录字段**

| 字段 | 说明 |
|---|---|
| `id` | 流量记录 ID |
| `session_id` | 所属会话 |
| `method_name` | RPC 方法名 |
| `timestamp` | 观测时间 |
| `response_time_ms` | 响应延迟 |
| `address_hash` | 匿名化地址标识 |

---

#### 7.4 手动写入单条流量

**方法：** `POST`  
**路径：** `/sessions/{session_id}/traffic/record`

**作用：**  
手动写入一条流量记录，适合测试或外部采集器接入。

**常见请求体字段**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `method_name` | string | 是 | RPC 方法名 |
| `timestamp` | string | 否 | ISO 时间戳 |
| `response_time_ms` | number | 否 | 响应延迟 |
| `address_hash` | string | 否 | 哈希地址 |
| `metadata` | object | 否 | 其他标准化元数据 |

### 8. 隐私泄露接口

#### 8.1 获取某会话的泄露事件

**方法：** `GET`  
**路径：** `/sessions/{session_id}/leaks`

**作用：**  
返回某个会话检测出的全部隐私泄露事件。

**常见查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skip` | integer | 否 | 分页偏移 |
| `limit` | integer | 否 | 分页大小 |
| `leak_type` | string | 否 | 按泄露类型筛选 |

**常见泄露字段**

| 字段 | 说明 |
|---|---|
| `id` | 泄露事件 ID |
| `session_id` | 所属会话 UUID |
| `leak_type` | IDENTITY / ASSET / BEHAVIOR / LOCATION |
| `method_name` | 相关 RPC 方法 |
| `description` | 可读解释 |
| `confidence` | 置信度 |
| `confidence_interval_low` | 置信区间下界 |
| `confidence_interval_high` | 置信区间上界 |
| `rule_id` | 触发规则 ID |

---

#### 8.2 获取所有泄露事件

**方法：** `GET`  
**路径：** `/leaks`

**作用：**  
跨会话返回泄露事件列表。

**常见查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skip` | integer | 否 | 分页偏移 |
| `limit` | integer | 否 | 分页大小 |
| `leak_type` | string | 否 | 泄露类型 |
| `session_id` | string | 否 | 指定会话过滤 |

### 9. 风险评估接口

#### 9.1 运行风险评估

**方法：** `POST`  
**路径：** `/sessions/{session_id}/assess`

**作用：**  
为某个会话计算隐私风险指标。

**路径参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `session_id` | string | 是 | 目标会话 UUID |

**常见返回字段**

| 字段 | 说明 |
|---|---|
| `overall_score` | 0 到 100 的总体分数 |
| `risk_level` | `LOW`、`MEDIUM`、`HIGH` 或 `CRITICAL` |
| `entropy_score` | 信息熵维度分数 |
| `uniqueness_score` | 唯一性维度分数 |
| `correlation_score` | 关联性维度分数 |
| `temporal_score` | 时序维度分数 |
| `confidence` | 评估置信度 |
| `recommendations` | 建议项 |
| `assessed_at` | 评估时间 |

**风险等级常见解释**

| 等级 | 分数区间 |
|---|---|
| `LOW` | 0–30 |
| `MEDIUM` | 31–50 |
| `HIGH` | 51–70 |
| `CRITICAL` | 71–100 |

---

#### 9.2 获取评估结果

**方法：** `GET`  
**路径：** `/sessions/{session_id}/assessment`

**作用：**  
返回某个会话最近一次或已保存的风险评估结果。

---

#### 9.3 获取评估列表

**方法：** `GET`  
**路径：** `/assessments`

**作用：**  
跨会话列出评估结果。

**常见查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `skip` | integer | 否 | 分页偏移 |
| `limit` | integer | 否 | 分页大小 |
| `risk_level` | string | 否 | 按风险等级筛选 |

### 10. 统计分析接口

#### 10.1 总体统计

**方法：** `GET`  
**路径：** `/analytics/summary`

**作用：**  
返回全局统计信息。

**常见字段**

| 字段 | 说明 |
|---|---|
| `total_sessions` | 总会话数 |
| `active_sessions` | 当前活跃会话数 |
| `completed_sessions` | 已完成会话数 |
| `total_traffic_records` | 总流量条数 |
| `total_leaks` | 总泄露事件数 |
| `average_risk_score` | 平均风险分数 |
| `high_risk_sessions` | 高风险或严重风险会话数 |

---

#### 10.2 时间趋势

**方法：** `GET`  
**路径：** `/analytics/trends`

**作用：**  
返回某个时间窗口内的趋势数据。

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `days` | integer | 否 | 分析天数，常见范围 `1–90` |

**常见结果结构**

- `dates`
- `session_counts`
- `leak_counts`
- `average_risk_scores`

---

#### 10.3 泄露类型分布

**方法：** `GET`  
**路径：** `/analytics/leaks/distribution`

**作用：**  
返回不同泄露类型的数量分布。

---

#### 10.4 风险等级分布

**方法：** `GET`  
**路径：** `/analytics/risk/distribution`

**作用：**  
返回不同风险等级的数量分布。

---

#### 10.5 方法频率统计

**方法：** `GET`  
**路径：** `/analytics/methods/frequency`

**作用：**  
返回最常见的 RPC 方法。

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer | 否 | 返回方法条数 |

---

#### 10.6 高风险会话排行

**方法：** `GET`  
**路径：** `/analytics/sessions/top-risk`

**作用：**  
返回风险分数最高的一批会话。

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer | 否 | 返回会话条数 |

---

#### 10.7 响应时间统计

**方法：** `GET`  
**路径：** `/analytics/response-times`

**作用：**  
返回响应时间相关统计值。

**常见字段**

| 字段 | 说明 |
|---|---|
| `min` | 最小响应时间 |
| `max` | 最大响应时间 |
| `mean` | 平均响应时间 |
| `median` | 中位数 |
| `std_dev` | 标准差 |
| `p50` | 50 分位 |
| `p95` | 95 分位 |
| `p99` | 99 分位 |
| `total_requests` | 请求总数 |

### 11. 检测规则接口

#### 11.1 获取规则列表

**方法：** `GET`  
**路径：** `/rules`

**作用：**  
返回检测规则列表，并支持基础过滤。

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `category` | string | 否 | 规则分类 |
| `enabled_only` | boolean | 否 | 是否只返回启用规则 |

**常见规则字段**

| 字段 | 说明 |
|---|---|
| `rule_id` | 规则标识 |
| `name` | 规则名称 |
| `category` | IDENTITY / ASSET / BEHAVIOR / LOCATION |
| `priority` | LOW / MEDIUM / HIGH / CRITICAL |
| `enabled` | 是否启用 |
| `description` | 规则描述 |

---

#### 11.2 获取规则摘要

**方法：** `GET`  
**路径：** `/rules/summary`

**作用：**  
返回规则的聚合统计信息。

**常见字段**

- `total_rules`
- `enabled_rules`
- `by_category`
- `by_priority`

---

#### 11.3 获取单条规则详情

**方法：** `GET`  
**路径：** `/rules/{rule_id}`

**作用：**  
返回指定规则的详细信息。

### 12. 研究与扩展分析接口

#### 12.1 基线对比

**方法：** `POST`  
**路径：** `/sessions/{session_id}/baseline-compare`

**作用：**  
将当前会话与参考基线进行比较。

**前置条件：**  
通常要求该会话已经完成风险评估。

**常见结果结构**

- `baseline_comparison.actual`
- `baseline_comparison.random_baseline`
- `baseline_comparison.ideal_baseline`
- `baseline_comparison.overall_privacy_score`
- `baseline_comparison.privacy_level`
- `industry_comparison.session_metrics`
- `industry_comparison.industry_mean`
- `industry_comparison.overall_industry_ranking`

---

#### 12.2 模拟攻击

**方法：** `POST`  
**路径：** `/sessions/{session_id}/simulate-attack`

**作用：**  
通过分类器或聚类方法估计会话区分难度。

**前置条件：**  
项目文档指出，这类分析一般至少需要两个会话的数据。

**常见结果结构**

- `attack_type`
- `num_sessions`
- `classifiers.random_forest`
- `classifiers.naive_bayes`
- `clustering.silhouette_score`
- `clustering.cluster_purity`
- `overall_attack_effectiveness`

---

#### 12.3 对抗测试

**方法：** `POST`  
**路径：** `/sessions/{session_id}/adversarial-test`

**作用：**  
评估不同防御策略的预期效果。

**常见策略**

- `padding`
- `timing_jitter`
- `method_randomization`

**常见结果结构**

- `defense_strategies`
- `recommendations`
- `best_strategy`
- `overall_improvement`

### 13. Dashboard 监控接口

#### 13.1 监控状态

**方法：** `GET`  
**路径：** `/dashboard/monitor/status`

**作用：**  
返回当前捕获运行状态和整体数量信息。

**常见字段**

| 字段 | 说明 |
|---|---|
| `active_sessions` | 活跃会话数 |
| `total_sessions` | 总会话数 |
| `capturing` | 当前是否在捕获 |
| `today_packets` | 今日捕获包数 |
| `today_leaks` | 今日泄露事件数 |
| `capture_rate` | 捕获速率 |
| `last_capture_time` | 最近捕获时间 |

---

#### 13.2 泄露流接口

**方法：** `GET`  
**路径：** `/dashboard/monitor/leaks/stream`

**作用：**  
为监控面板返回最近泄露事件流。

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `limit` | integer | 否 | 返回记录数 |
| `offset` | integer | 否 | 分页偏移 |

**常见结果结构**

- `leaks`
- `stream_position`
- `has_more`
- `leak_rate`

---

#### 13.3 实时风险指标

**方法：** `GET`  
**路径：** `/dashboard/monitor/risk/metrics`

**作用：**  
返回高层级实时风险指标。

**常见字段**

| 字段 | 说明 |
|---|---|
| `current_risk_level` | 当前总体风险等级 |
| `average_risk_score` | 当前平均分数 |
| `high_risk_sessions` | 高风险会话数量 |
| `risk_trend` | stable / increasing / decreasing |
| `confidence` | 置信度估计 |
| `last_updated` | 最近更新时间 |

### 14. Dashboard 报告与图表接口

#### 14.1 时间线报告

**方法：** `GET`  
**路径：** `/dashboard/reports/timeline`

**作用：**  
返回可用于报告展示的事件时间线数据。

**查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `time_range` | string | 否 | `last_hour`、`last_24h`、`last_7d`、`last_30d` |

---

#### 14.2 热力图报告

**方法：** `GET`  
**路径：** `/dashboard/reports/heatmap`

**作用：**  
返回适合热力图渲染的矩阵数据。

**常见查询参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `time_range` | string | 否 | 时间范围 |
| `heatmap_type` | string | 否 | 热力图维度类型 |

---

#### 14.3 获取全部图表数据

**方法：** `GET`  
**路径：** `/dashboard/charts`

**作用：**  
一次性返回前端需要的全部图表数据。

**典型用途：**  
用于 ECharts 集成或 dashboard 首次加载。

---

#### 14.4 获取单个图表

**方法：** `GET`  
**路径：** `/dashboard/charts/{chart_type}`

**作用：**  
返回指定图表的单独数据。

**路径参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `chart_type` | string | 是 | 图表名称或图表类型 |

### 15. 综合报告接口

#### 15.1 生成综合报告

**方法：** `POST`  
**路径：** `/dashboard/comprehensive-report`

**作用：**  
生成一份综合 JSON 报告，内容可能包括：

- 测试会话列表
- 各会话风险评估
- 基线对比
- 模拟攻击结果
- 对抗测试结果
- 高层建议

**常见特点**

- 可能内部并发执行多个分析任务
- 适合课程展示或最终演示
- 原始说明中提到在示例条件下响应时间约为 1 秒

### 16. 工具接口

#### 16.1 健康检查

**方法：** `GET`  
**路径：** `/health`

**作用：**  
返回服务健康状态。

**示例响应**

```json
{
  "status": "healthy",
  "service": "wallet-privacy-backend"
}
```

### 17. 规格级可选接口

初始规格文档还提到了一些可能属于未来实现或部分实现的接口。除非在运行中的后端中确认存在，否则应将它们视为**条件性接口**。

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/leaks/simulate` | 测试型泄露检测模拟 |
| POST | `/api/v1/assessments/evaluate` | 对自定义数据进行评估 |
| POST | `/api/v1/rules` | 创建规则 |
| PUT | `/api/v1/rules/{rule_id}` | 更新规则 |
| DELETE | `/api/v1/rules/{rule_id}` | 删除规则 |
| POST | `/api/v1/reports/generate` | 生成可下载报告 |
| GET | `/api/v1/reports/download/{report_id}` | 下载已生成报告 |
| GET | `/api/v1/config` | 获取运行配置 |
| PUT | `/api/v1/config` | 更新运行配置 |

### 18. 常见错误码

合并后的项目文档中，常见错误码包括：

| 错误码 | 含义 | 常见 HTTP 状态码 |
|---|---|---|
| `SESSION_NOT_FOUND` | 会话不存在 | `404` |
| `ASSESSMENT_NOT_FOUND` | 未找到评估结果 | `404` |
| `NO_SESSIONS_FOUND` | 所选范围内没有会话 | `404` |
| `CHART_NOT_FOUND` | 指定图表不存在 | `404` |
| `INSUFFICIENT_DATA` | 数据不足，无法完成分析 | `400` |
| `INVALID_INPUT` | 输入参数无效 | `400` |
| `INVALID_PARAMETER` | 查询参数或路径参数无效 | `400` |
| `INTERNAL_ERROR` | 服务端内部错误 | `500` |

### 19. cURL 示例

#### 19.1 创建会话

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

#### 19.2 启动捕获

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/start
```

#### 19.3 获取流量

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

#### 19.4 获取泄露事件

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

#### 19.5 运行风险评估

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

#### 19.6 获取总体统计

```bash
curl http://localhost:8000/api/v1/analytics/summary
```

#### 19.7 获取 Dashboard 状态

```bash
curl http://localhost:8000/api/v1/dashboard/monitor/status
```

#### 19.8 生成综合报告

```bash
curl -X POST "http://localhost:8000/api/v1/dashboard/comprehensive-report?time_range=last_24h"
```

### 20. 中文版结束
