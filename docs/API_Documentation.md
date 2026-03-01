# Wallet RPC Privacy Leakage Measurement API

---

## 1. Upload Traffic File

### 接口地址

POST /api/v1/upload

### 接口描述

上传网络流量文件（LDJSON 格式，每行一个 JSON 对象）。系统逐行解析文件内容，对每条 flow 执行隐私泄露检测规则，并返回风险评分、统计信息、生成的报告文件名以及部分隐私事件样例。

---

## 请求参数

### 请求格式

multipart/form-data

### 参数说明

| 参数名 | 类型 | 是否必填 | 描述 |
|--------|------|----------|------|
| file | File | 是 | UTF-8 编码文本文件，每行一个 JSON 对象 |

---

### 请求示例

上传文件内容示例（LDJSON）：

    {"flow_id":"flow_001","request":{"method":"POST","host":"example.com","path":"/rpc","headers":"MetaMask","content":"eth_getBalance"},"response":{"content":"0x0"}}
    {"flow_id":"flow_002","request":{"method":"GET","host":"phishing-detection.example","path":"/phishing-detection","headers":"","content":""},"response":{"content":""}}

---

## 返回结果

### 返回格式

application/json

---

### 200 Successful Response

返回风险评估结果对象。

#### 返回参数说明

| 参数名 | 类型 | 描述 |
|--------|------|------|
| m2_assessment | object | 风险评分结果 |
| stats | object | 统计信息 |
| report_file | string | 生成的报告文件名 |
| sample | array | 隐私泄露事件样例（最多 3 条） |

---

#### m2_assessment 结构

| 参数名 | 类型 | 描述 |
|--------|------|------|
| score | number | 风险评分（0~100） |
| risk_level | string | 风险等级（LOW / MEDIUM / CRITICAL） |

风险等级判定规则：

- score > 70 → CRITICAL  
- score > 35 → MEDIUM  
- 其他 → LOW  

---

#### stats 结构

| 参数名 | 类型 | 描述 |
|--------|------|------|
| processed | integer | 成功解析的 flow 数量 |
| leaks | integer | 检测到的隐私泄露事件数量 |

---

#### sample 数组中单个事件结构（PrivacyLeakEventSchema）

| 参数名 | 类型 | 描述 |
|--------|------|------|
| session_id | string | 来源于 flow.flow_id |
| leak_type | string | 泄露类型（IDENTITY / LOCATION / ASSET / BEHAVIOR） |
| method_name | string | 请求方法 |
| description | string | 泄露描述 |
| confidence | number | 置信度 |
| details | object | 规则附加信息 |
| timestamp | string | 事件时间（ISO 格式） |
| address_hash | string | 地址哈希 |
| rule_id | string | 规则 ID |

---

### 返回示例

    {
      "m2_assessment": {
        "score": 42.3,
        "risk_level": "MEDIUM"
      },
      "stats": {
        "processed": 2,
        "leaks": 3
      },
      "report_file": "full_report_153012.json",
      "sample": [
        {
          "session_id": "flow_001",
          "leak_type": "ASSET",
          "method_name": "POST",
          "description": "Asset/Balance Tracking",
          "confidence": 0.9,
          "details": {},
          "timestamp": "2026-02-27T15:30:12.123456",
          "address_hash": "N/A",
          "rule_id": "DR-AS-1"
        }
      ]
    }

---

### 422 Validation Error

当文件参数缺失时返回。

    {
      "detail": [
        {
          "loc": ["body", "file"],
          "msg": "field required",
          "type": "value_error.missing"
        }
      ]
    }
