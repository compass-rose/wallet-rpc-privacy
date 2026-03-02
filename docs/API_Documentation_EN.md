# Wallet RPC Privacy Leakage Measurement API Documentation

---

## Table of Contents

1. [Session Management](#1-session-management)
2. [Traffic Capture](#2-traffic-capture)
3. [Privacy Leak Events](#3-privacy-leak-events)
4. [Risk Assessment](#4-risk-assessment)
5. [Analytics & Statistics](#5-analytics--statistics)
6. [Detection Rules](#6-detection-rules)

---

## 1. Session Management

### 1.1 Create Session

#### Endpoint Address

POST /api/v1/sessions

#### Interface Description

Create a new capture session for analyzing wallet-RPC communication.

---

#### Request Parameters

##### Request Format

application/json

##### Parameter Description

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| wallet_type | string | Yes | Type of wallet (e.g., "metamask", "walletconnect") |
| rpc_provider | string | Yes | RPC provider (e.g., "infura", "alchemy", "quicknode") |

#### Request Example

```json
{
  "wallet_type": "metamask",
  "rpc_provider": "infura"
}
```

---

#### Return Result

##### Return Format

application/json

##### 201 Created Response

Returns created session information.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| success | boolean | Request success status |
| data.id | string | Session UUID |
| data.wallet_type | string | Wallet type |
| data.rpc_provider | string | RPC provider |
| data.status | string | Session status (active, completed) |
| data.created_at | string | Creation timestamp (ISO format) |
| metadata.request_id | string | Request ID for tracking |
| metadata.timestamp | string | Response timestamp (ISO format) |

#### Return Example

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "wallet_type": "metamask",
    "rpc_provider": "infura",
    "status": "active",
    "created_at": "2026-03-01T12:00:00.000000"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:00:00.000000"
  }
}
```

---

### 1.2 Get Session Details

#### Endpoint Address

GET /api/v1/sessions/{session_id}

#### Interface Description

Retrieve detailed information about a specific session.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

---

#### Return Result

##### 200 OK Response

Returns detailed session information.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.id | string | Session UUID |
| data.wallet_type | string | Wallet type |
| data.rpc_provider | string | RPC provider |
| data.start_time | string | Capture start time (ISO format) |
| data.end_time | string | Capture end time (ISO format) |
| data.packet_count | integer | Total packets captured |
| data.duration_seconds | integer | Duration in seconds |
| data.status | string | Session status |
| data.session_metadata | object | Additional session metadata |

#### Return Example

```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "wallet_type": "metamask",
    "rpc_provider": "infura",
    "start_time": "2026-03-01T12:00:00.000000",
    "end_time": "2026-03-01T12:05:00.000000",
    "packet_count": 500,
    "duration_seconds": 300,
    "status": "completed",
    "session_metadata": null,
    "created_at": "2026-03-01T12:00:00.000000",
    "updated_at": "2026-03-01T12:05:00.000000"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:05:00.000000"
  }
}
```

---

### 1.3 List Sessions

#### Endpoint Address

GET /api/v1/sessions

#### Interface Description

List all sessions with optional filtering and pagination.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 50 | Number of records to return (1-100) |
| wallet_type | string | No | - | Filter by wallet type |
| rpc_provider | string | No | - | Filter by RPC provider |
| status | string | No | - | Filter by status (active, completed) |

---

#### Return Result

##### 200 OK Response

Returns list of sessions.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.sessions | array | List of session objects |
| data.sessions[].id | string | Session UUID |
| data.sessions[].wallet_type | string | Wallet type |
| data.sessions[].rpc_provider | string | RPC provider |
| data.sessions[].status | string | Session status |
| data.sessions[].packet_count | integer | Total packets captured |
| data.sessions[].created_at | string | Creation timestamp |
| data.total | integer | Total number of sessions |
| data.limit | integer | Page limit |
| data.offset | integer | Starting offset |

#### Return Example

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "wallet_type": "metamask",
        "rpc_provider": "infura",
        "status": "completed",
        "packet_count": 500,
        "created_at": "2026-03-01T12:00:00.000000"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:05:00.000000"
  }
}
```

---

### 1.4 Update Session

#### Endpoint Address

PUT /api/v1/sessions/{session_id}

#### Interface Description

Update session details such as status, end time, or packet count.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

##### Query Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| status | string | No | New status (active, completed) |
| end_time | string | No | End time in ISO format |
| packet_count | integer | No | Total packet count |

---

### 1.5 Delete Session

#### Endpoint Address

DELETE /api/v1/sessions/{session_id}

#### Interface Description

Delete a session and all associated data (traffic, leaks, assessments).

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

---

#### Return Result

##### 200 OK Response

Returns deletion confirmation.

#### Return Example

```json
{
  "success": true,
  "data": {
    "message": "Session deleted successfully"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

## 2. Traffic Capture

### 2.1 Start Traffic Capture

#### Endpoint Address

POST /api/v1/sessions/{session_id}/traffic/start

#### Interface Description

Start capturing network traffic for a specific session.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

##### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| packet_count | integer | No | 500 | Number of packets to capture (1-10000) |
| duration_seconds | integer | No | null | Capture duration in seconds (1-3600) |

---

#### Return Result

##### 200 OK Response

Returns capture status.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.active | boolean | Capture active status |
| data.packets_captured | integer | Number of packets captured |
| data.session_id | string | Session UUID |

#### Return Example

```json
{
  "success": true,
  "data": {
    "active": true,
    "packets_captured": 500,
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:05:00.000000"
  }
}
```

---

### 2.2 Stop Traffic Capture

#### Endpoint Address

POST /api/v1/sessions/{session_id}/traffic/stop

#### Interface Description

Stop capturing traffic for a session and finalize the session.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

---

#### Return Result

##### 200 OK Response

Returns final capture status.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.packets_captured | integer | Total packets captured |
| data.active | boolean | Capture active status |

#### Return Example

```json
{
  "success": true,
  "data": {
    "packets_captured": 500,
    "active": false
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 2.3 Get Traffic Records

#### Endpoint Address

GET /api/v1/sessions/{session_id}/traffic

#### Interface Description

Retrieve traffic records for a specific session with optional filtering.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

##### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| method | string | No | - | Filter by HTTP method (GET, POST, etc.) |
| rpc_method | string | No | - | Filter by RPC method name |
| limit | integer | No | 100 | Number of records to return (1-1000) |
| offset | integer | No | 0 | Number of records to skip |

---

#### Return Result

##### 200 OK Response

Returns traffic records.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.traffic | array | List of traffic records |
| data.traffic[].id | string | Traffic record ID |
| data.traffic[].session_id | string | Session UUID |
| data.traffic[].method | string | HTTP method |
| data.traffic[].endpoint | string | Request endpoint/URL |
| data.traffic[].rpc_method | string | RPC method name |
| data.traffic[].request_timestamp | string | Request timestamp (ISO format) |
| data.traffic[].response_time_ms | integer | Response time in milliseconds |
| data.traffic[].response_status | integer | HTTP status code |
| data.traffic[].response_size_bytes | integer | Response size in bytes |
| data.traffic[].user_agent | string | User agent string |
| data.total | integer | Total number of records |
| data.limit | integer | Page limit |
| data.offset | integer | Starting offset |

#### Return Example

```json
{
  "success": true,
  "data": {
    "traffic": [
      {
        "id": "traffic-001",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "method": "POST",
        "endpoint": "https://mainnet.infura.io/v3/",
        "rpc_method": "eth_getBalance",
        "request_timestamp": "2026-03-01T12:01:00.000000",
        "response_time_ms": 150,
        "response_status": 200,
        "response_size_bytes": 512,
        "user_agent": "MetaMask"
      }
    ],
    "total": 500,
    "limit": 100,
    "offset": 0
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 2.4 Record Single Traffic

#### Endpoint Address

POST /api/v1/sessions/{session_id}/traffic/record

#### Interface Description

Record a single traffic record (for RPC proxy integration).

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

##### Request Body

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| method | string | No | HTTP method (default: POST) |
| endpoint | string | No | Request endpoint |
| request_body | string | No | Request body |
| rpc_method | string | No | RPC method name |
| rpc_params_hash | string | No | Hash of RPC parameters |
| request_timestamp | string | No | Request timestamp (ISO format) |
| response_time_ms | integer | No | Response time in milliseconds |
| response_status | integer | No | HTTP status code |
| response_size_bytes | integer | No | Response size in bytes |
| ip_address_hash | string | No | Hash of IP address |
| user_agent | string | No | User agent string |

#### Request Example

```json
{
  "method": "POST",
  "endpoint": "https://mainnet.infura.io/v3/",
  "rpc_method": "eth_getBalance",
  "request_timestamp": "2026-03-01T12:01:00.000000",
  "response_time_ms": 150,
  "response_status": 200,
  "response_size_bytes": 512,
  "ip_address_hash": "a3f5...",
  "user_agent": "MetaMask"
}
```

---

## 3. Privacy Leak Events

### 3.1 Get Session Leaks

#### Endpoint Address

GET /api/v1/sessions/{session_id}/leaks

#### Interface Description

Retrieve privacy leak events for a specific session.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

##### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| leak_type | enum | No | - | Filter by leak type (IDENTITY, ASSET, BEHAVIOR, LOCATION) |
| min_confidence | float | No | - | Filter by minimum confidence (0.0-1.0) |
| rule_id | string | No | - | Filter by rule ID |
| limit | integer | No | 100 | Number of records to return (1-1000) |
| offset | integer | No | 0 | Number of records to skip |

---

#### Return Result

##### 200 OK Response

Returns privacy leak events.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.leaks | array | List of leak events |
| data.leaks[].id | string | Leak event ID |
| data.leaks[].session_id | string | Session UUID |
| data.leaks[].leak_type | string | Leak type enum value |
| data.leaks[].method_name | string | RPC method name |
| data.leaks[].description | string | Leak description |
| data.leaks[].confidence | float | Confidence score (0.0-1.0) |
| data.leaks[].confidence_interval_low | float | Lower confidence bound |
| data.leaks[].confidence_interval_high | float | Upper confidence bound |
| data.leaks[].details | object | Additional rule details |
| data.leaks[].timestamp | string | Event timestamp (ISO format) |
| data.leaks[].address_hash | string | Hashed wallet address |
| data.leaks[].rule_id | string | Detection rule ID |
| data.leaks[].created_at | string | Creation timestamp (ISO format) |
| data.total | integer | Total number of leaks |
| data.limit | integer | Page limit |
| data.offset | integer | Starting offset |

#### Return Example

```json
{
  "success": true,
  "data": {
    "leaks": [
      {
        "id": "leak-001",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "leak_type": "ASSET",
        "method_name": "eth_getBalance",
        "description": "Asset/Balance Tracking",
        "confidence": 0.9,
        "confidence_interval_low": 0.85,
        "confidence_interval_high": 0.95,
        "details": {},
        "timestamp": "2026-03-01T12:01:00.000000",
        "address_hash": "a3f5...",
        "rule_id": "DR-AS-1",
        "created_at": "2026-03-01T12:01:00.000000"
      }
    ],
    "total": 10,
    "limit": 100,
    "offset": 0
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 3.2 List All Leaks

#### Endpoint Address

GET /api/v1/leaks

#### Interface Description

List all privacy leak events across all sessions.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| leak_type | enum | No | - | Filter by leak type (IDENTITY, ASSET, BEHAVIOR, LOCATION) |
| min_confidence | float | No | - | Filter by minimum confidence (0.0-1.0) |
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 50 | Number of records to return (1-100) |

---

#### Return Result

##### 200 OK Response

Returns all privacy leak events.

#### Return Example

```json
{
  "success": true,
  "data": {
    "leaks": [
      {
        "id": "leak-001",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "leak_type": "ASSET",
        "method_name": "eth_getBalance",
        "description": "Asset/Balance Tracking",
        "confidence": 0.9,
        "timestamp": "2026-03-01T12:01:00.000000"
      }
    ],
    "total": 100,
    "skip": 0,
    "limit": 50
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

## 4. Risk Assessment

### 4.1 Run Risk Assessment

#### Endpoint Address

POST /api/v1/sessions/{session_id}/assess

#### Interface Description

Run a comprehensive privacy risk assessment for a session based on captured traffic.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

---

#### Return Result

##### 200 OK Response

Returns risk assessment results.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.id | string | Assessment ID |
| data.session_id | string | Session UUID |
| data.overall_score | integer | Overall risk score (0-100) |
| data.risk_level | string | Risk level (LOW, MEDIUM, HIGH, CRITICAL) |
| data.entropy_score | float | Entropy score (0.0-1.0) |
| data.uniqueness_score | float | Uniqueness score (0.0-1.0) |
| data.correlation_score | float | Correlation score (0.0-1.0) |
| data.temporal_score | float | Temporal score (0.0-1.0) |
| data.confidence | float | Assessment confidence (0.0-1.0) |
| data.confidence_interval_low | float | Lower confidence bound |
| data.confidence_interval_high | float | Upper confidence bound |
| data.recommendations | array | List of improvement recommendations |
| data.baseline_comparison | object | Comparison to baseline metrics |
| data.assessed_at | string | Assessment timestamp (ISO format) |
| data.created_at | string | Creation timestamp (ISO format) |

#### Risk Level Classification

| Score Range | Risk Level |
|-------------|------------|
| 0-30 | LOW |
| 31-50 | MEDIUM |
| 51-70 | HIGH |
| 71-100 | CRITICAL |

#### Return Example

```json
{
  "success": true,
  "data": {
    "id": "assessment-001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "overall_score": 65,
    "risk_level": "HIGH",
    "entropy_score": 0.75,
    "uniqueness_score": 0.82,
    "correlation_score": 0.68,
    "temporal_score": 0.55,
    "confidence": 0.89,
    "confidence_interval_low": 0.82,
    "confidence_interval_high": 0.96,
    "recommendations": [
      "Reduce frequency of balance polling",
      "Use batch requests for multiple queries"
    ],
    "baseline_comparison": {
      "above_baseline": ["temporal"],
      "at_baseline": ["uniqueness"],
      "below_baseline": ["entropy", "correlation"]
    },
    "assessed_at": "2026-03-01T12:10:00.000000",
    "created_at": "2026-03-01T12:10:00.000000"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 4.2 Get Assessment

#### Endpoint Address

GET /api/v1/sessions/{session_id}/assessment

#### Interface Description

Retrieve the latest risk assessment for a specific session.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| session_id | string | Yes | Session UUID |

---

#### Return Result

##### 200 OK Response

Returns risk assessment if available, or null if no assessment exists.

#### Return Example

```json
{
  "success": true,
  "data": {
    "id": "assessment-001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "overall_score": 65,
    "risk_level": "HIGH",
    "entropy_score": 0.75,
    "uniqueness_score": 0.82,
    "correlation_score": 0.68,
    "temporal_score": 0.55,
    "confidence": 0.89,
    "recommendations": [
      "Reduce frequency of balance polling"
    ],
    "baseline_comparison": {
      "above_baseline": ["temporal"],
      "at_baseline": ["uniqueness"],
      "below_baseline": ["entropy", "correlation"]
    },
    "assessed_at": "2026-03-01T12:10:00.000000",
    "created_at": "2026-03-01T12:10:00.000000"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 4.3 List Assessments

#### Endpoint Address

GET /api/v1/assessments

#### Interface Description

List all risk assessments with optional filtering.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of records to skip |
| limit | integer | No | 50 | Number of records to return (1-100) |
| risk_level | string | No | - | Filter by risk level (LOW, MEDIUM, HIGH, CRITICAL) |

---

#### Return Result

##### 200 OK Response

Returns list of risk assessments.

#### Return Example

```json
{
  "success": true,
  "data": {
    "assessments": [
      {
        "id": "assessment-001",
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "overall_score": 65,
        "risk_level": "HIGH",
        "assessed_at": "2026-03-01T12:10:00.000000",
        "created_at": "2026-03-01T12:10:00.000000"
      }
    ],
    "total": 10,
    "skip": 0,
    "limit": 50
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

## 5. Analytics & Statistics

### 5.1 Get Summary Statistics

#### Endpoint Address

GET /api/v1/analytics/summary

#### Interface Description

Get overall summary statistics across all sessions.

---

#### Return Result

##### 200 OK Response

Returns summary statistics.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.total_sessions | integer | Total number of sessions |
| data.active_sessions | integer | Number of active sessions |
| data.completed_sessions | integer | Number of completed sessions |
| data.total_traffic_records | integer | Total traffic records captured |
| data.total_leaks | integer | Total privacy leaks detected |
| data.average_risk_score | float | Average risk score across all assessments |
| data.high_risk_sessions | integer | Number of sessions with HIGH or CRITICAL risk |

#### Return Example

```json
{
  "success": true,
  "data": {
    "total_sessions": 50,
    "active_sessions": 5,
    "completed_sessions": 45,
    "total_traffic_records": 25000,
    "total_leaks": 1250,
    "average_risk_score": 52.3,
    "high_risk_sessions": 18
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 5.2 Get Trends

#### Endpoint Address

GET /api/v1/analytics/trends

#### Interface Description

Get trend analysis over a specified number of days.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Range | Description |
|----------------|------|----------|---------|-------|-------------|
| days | integer | No | 7 | 1-90 | Number of days to analyze |

---

#### Return Result

##### 200 OK Response

Returns trend data.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.dates | array | Array of dates (ISO format) |
| data.session_counts | array | Daily session counts |
| data.leak_counts | array | Daily leak counts |
| data.average_risk_scores | array | Daily average risk scores |

#### Return Example

```json
{
  "success": true,
  "data": {
    "dates": [
      "2026-02-22",
      "2026-02-23",
      "2026-02-24",
      "2026-02-25",
      "2026-02-26",
      "2026-02-27",
      "2026-02-28"
    ],
    "session_counts": [10, 12, 8, 15, 11, 9, 13],
    "leak_counts": [250, 300, 200, 375, 275, 225, 325],
    "average_risk_scores": [48.5, 52.3, 45.2, 58.7, 51.3, 47.6, 55.8]
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 5.3 Get Leak Distribution

#### Endpoint Address

GET /api/v1/analytics/leaks/distribution

#### Interface Description

Get distribution of privacy leaks by type.

---

#### Return Result

##### 200 OK Response

Returns leak type distribution.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.distribution | object | Leak counts by type |
| data.distribution.IDENTITY | integer | Identity-related leaks |
| data.distribution.ASSET | integer | Asset-related leaks |
| data.distribution.BEHAVIOR | integer | Behavior-related leaks |
| data.distribution.LOCATION | integer | Location-related leaks |
| data.total | integer | Total leak count |

#### Return Example

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
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 5.4 Get Risk Distribution

#### Endpoint Address

GET /api/v1/analytics/risk/distribution

#### Interface Description

Get distribution of risk levels across all assessments.

---

#### Return Result

##### 200 OK Response

Returns risk level distribution.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.distribution | object | Count by risk level |
| data.distribution.LOW | integer | Low risk assessments |
| data.distribution.MEDIUM | integer | Medium risk assessments |
| data.distribution.HIGH | integer | High risk assessments |
| data.distribution.CRITICAL | integer | Critical risk assessments |
| data.total | integer | Total assessment count |

#### Return Example

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
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 5.5 Get Method Frequency

#### Endpoint Address

GET /api/v1/analytics/methods/frequency

#### Interface Description

Get most frequently used RPC methods.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Range | Description |
|----------------|------|----------|---------|-------|-------------|
| limit | integer | No | 10 | 1-50 | Number of methods to return |

---

#### Return Result

##### 200 OK Response

Returns method frequencies.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.frequencies | array | Array of method-frequency pairs |
| data.frequencies[].method | string | RPC method name |
| data.frequencies[].count | integer | Usage count |

#### Return Example

```json
{
  "success": true,
  "data": {
    "frequencies": [
      {"method": "eth_getBalance", "count": 15000},
      {"method": "eth_blockNumber", "count": 5000},
      {"method": "eth_getTransactionCount", "count": 2500},
      {"method": "eth_getCode", "count": 1200},
      {"method": "eth_call", "count": 800}
    ]
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 5.6 Get Top Risk Sessions

#### Endpoint Address

GET /api/v1/analytics/sessions/top-risk

#### Interface Description

Get sessions with highest risk scores.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Range | Description |
|----------------|------|----------|---------|-------|-------------|
| limit | integer | No | 10 | 1-50 | Number of sessions to return |

---

#### Return Result

##### 200 OK Response

Returns top risk sessions.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.sessions | array | Array of session-risk pairs |
| data.sessions[].session_id | string | Session UUID |
| data.sessions[].risk_level | string | Risk level |
| data.sessions[].overall_score | integer | Overall risk score |
| data.sessions[].assessed_at | string | Assessment timestamp (ISO format) |

#### Return Example

```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "risk_level": "CRITICAL",
        "overall_score": 85,
        "assessed_at": "2026-03-01T12:10:00.000000"
      },
      {
        "session_id": "550e8400-e29b-41d4-a716-446655440001",
        "risk_level": "HIGH",
        "overall_score": 78,
        "assessed_at": "2026-03-01T11:50:00.000000"
      }
    ]
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440002",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 5.7 Get Response Time Statistics

#### Endpoint Address

GET /api/v1/analytics/response-times

#### Interface Description

Get RPC response time statistics.

---

#### Return Result

##### 200 OK Response

Returns response time statistics.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.min | float | Minimum response time (ms) |
| data.max | float | Maximum response time (ms) |
| data.mean | float | Average response time (ms) |
| data.median | float | Median response time (ms) |
| data.std_dev | float | Standard deviation (ms) |
| data.p50 | float | 50th percentile (ms) |
| data.p95 | float | 95th percentile (ms) |
| data.p99 | float | 99th percentile (ms) |
| data.total_requests | integer | Total number of requests |

#### Return Example

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
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

## 6. Detection Rules

### 6.1 List Rules

#### Endpoint Address

GET /api/v1/rules

#### Interface Description

List all detection rules with optional filtering.

---

#### Query Parameters

| Parameter Name | Type | Required | Default | Description |
|----------------|------|----------|---------|-------------|
| category | string | No | - | Filter by rule category |
| enabled_only | boolean | No | false | Return only enabled rules |

---

#### Return Result

##### 200 OK Response

Returns list of detection rules.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.rules | array | Array of rule objects |
| data.rules[].rule_id | string | Rule ID |
| data.rules[].name | string | Rule name |
| data.rules[].category | string | Rule category |
| data.rules[].priority | string | Rule priority (LOW, MEDIUM, HIGH, CRITICAL) |
| data.rules[].enabled | boolean | Rule enabled status |
| data.rules[].description | string | Rule description |
| data.total | integer | Total number of rules |

#### Return Example

```json
{
  "success": true,
  "data": {
    "rules": [
      {
        "rule_id": "DR-AS-1",
        "name": "Balance Polling",
        "category": "ASSET",
        "priority": "MEDIUM",
        "enabled": true,
        "description": "Detects frequent balance polling"
      },
      {
        "rule_id": "DR-ID-1",
        "name": "Wallet Address Exposure",
        "category": "IDENTITY",
        "priority": "CRITICAL",
        "enabled": true,
        "description": "Detects wallet address in request parameters"
      }
    ],
    "total": 12
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 6.2 Get Rules Summary

#### Endpoint Address

GET /api/v1/rules/summary

#### Interface Description

Get summary statistics for detection rules.

---

#### Return Result

##### 200 OK Response

Returns rules summary.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.total_rules | integer | Total number of rules |
| data.enabled_rules | integer | Number of enabled rules |
| data.by_category | object | Rule counts by category |
| data.by_priority | object | Rule counts by priority |

#### Return Example

```json
{
  "success": true,
  "data": {
    "total_rules": 12,
    "enabled_rules": 12,
    "by_category": {
      "IDENTITY": 3,
      "ASSET": 4,
      "BEHAVIOR": 3,
      "LOCATION": 2
    },
    "by_priority": {
      "LOW": 2,
      "MEDIUM": 5,
      "HIGH": 3,
      "CRITICAL": 2
    }
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

### 6.3 Get Rule Details

#### Endpoint Address

GET /api/v1/rules/{rule_id}

#### Interface Description

Get detailed information about a specific detection rule.

---

#### Path Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| rule_id | string | Yes | Rule ID |

---

#### Return Result

##### 200 OK Response

Returns rule details.

#### Return Parameter Description

| Parameter Name | Type | Description |
|----------------|------|-------------|
| data.id | string | Rule ID |
| data.name | string | Rule name |
| data.category | string | Rule category |
| data.priority | string | Rule priority |
| data.enabled | boolean | Rule enabled status |
| data.description | string | Rule description |
| data.conditions | array | Rule conditions |
| data.actions | array | Rule actions |
| data.version | string | Rule version |

#### Return Example

```json
{
  "success": true,
  "data": {
    "id": "DR-AS-1",
    "name": "Balance Polling",
    "category": "ASSET",
    "priority": "MEDIUM",
    "enabled": true,
    "description": "Detects frequent balance polling requests to the same address",
    "conditions": [
      {
        "field": "rpc_method",
        "operator": "equals",
        "value": "eth_getBalance"
      },
      {
        "field": "frequency",
        "operator": "greater_than",
        "value": 5
      }
    ],
    "actions": [
      {
        "type": "log_leak",
        "leak_type": "ASSET",
        "confidence": 0.9
      }
    ],
    "version": "1.0"
  },
  "metadata": {
    "request_id": "550e8400-e29b-41d4-a716-446655440001",
    "timestamp": "2026-03-01T12:10:00.000000"
  }
}
```

---

## Common Error Responses

### 404 Not Found

Resource not found.

```json
{
  "detail": {
    "code": "NOT_FOUND",
    "message": "Session {session_id} not found"
  }
}
```

### 400 Bad Request

Invalid request input.

```json
{
  "detail": {
    "code": "INVALID_INPUT",
    "message": "Session is not active"
  }
}
```

### 422 Validation Error

Request validation failed.

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

## Rate Limiting

All API endpoints are rate-limited to prevent abuse:

- **Default Limit**: 100 requests per minute per IP address
- **Response Header Included**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

When rate limit is exceeded:

```json
{
  "detail": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later."
  }
}
```

---

## Authentication & Authorization

Current implementation does not require authentication for development purposes. For production deployment, consider implementing:

- API Key authentication
- OAuth 2.0 token-based authentication
- Role-based access control (RBAC)

---

## API Versioning

The current API version is `v1`. The base URL for all endpoints is:

```
http://localhost:8000/api/v1
```

For updates and breaking changes, new versions will be released as `v2`, `v3`, etc.

---

## Support & Contact

- **Project Homepage**: https://github.com/compass-rose/wallet-rpc-privacy
- **Issues**: https://github.com/compass-rose/wallet-rpc-privacy/issues

---

**Document Version**: 1.0.0
**Last Updated**: 2026-03-01
