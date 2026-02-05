# Wallet / RPC Privacy Leakage Measurement System
## Initial Specification Document

**Document Version:** 2.0
**Creation Date:** February 5, 2026
**Project Status:** Planning Phase
**Project Duration:** 10 weeks

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement](#problem-statement)
3. [Project Goals and Value Proposition](#project-goals-and-value-proposition)
4. [Scope and Boundaries](#scope-and-boundaries)
5. [Threat Model](#threat-model)
6. [System Architecture](#system-architecture)
7. [Functional Requirements](#functional-requirements)
8. [Non-Functional Requirements](#non-functional-requirements)
9. [Data Models](#data-models)
10. [API Specifications](#api-specifications)
11. [Core Algorithms and Detection Rules](#core-algorithms-and-detection-rules)
12. [Development Standards and Guidelines](#development-standards-and-guidelines)
13. [Validation and Experiments](#validation-and-experiments)
14. [Technical Stack](#technical-stack)
15. [Success Metrics and Acceptance Criteria](#success-metrics-and-acceptance-criteria)
16. [Deliverables](#deliverables)
17. [Appendices](#appendices)

---

## 1. Executive Summary

The **Wallet / RPC Privacy Leakage Measurement System** is a research-driven software development project that aims to measure and quantify privacy leakage risks in the communication between blockchain wallets (e.g., MetaMask, WalletConnect) and RPC (Remote Procedure Call) providers. This system will capture real network traffic, analyze privacy-sensitive metadata using rule-based detection, and provide actionable risk assessments for wallet developers, RPC providers, and end users.

### Key Highlights

- **Empirical Approach**: Uses real-world network traffic data for measurement
- **Rule-Based Detection**: Implements comprehensive detection rules to identify privacy leakage patterns
- **Quantitative Metrics**: Provides multi-dimensional scoring (entropy, uniqueness, correlation, temporal) with confidence intervals
- **Actionable Insights**: Delivers specific privacy protection recommendations based on empirical evidence
- **Academic Value**: Establishes a methodology for quantifying blockchain privacy leakage
- **Industry Impact**: Informs wallet and DApp developers on privacy-enhancing practices

### Project Statistics

| Metric | Target Value |
|--------|-------------|
| Real traffic samples captured | ≥ 5,000 |
| Privacy leakage patterns identified | ≥ 15 |
| Wallet privacy risk assessments | ≥ 3 |
| Detection rules implemented | ≥ 10 |
| Code test coverage | > 70% |
| API availability uptime | > 99% |
| API response time (P95) | < 500ms |

---

## 2. Problem Statement

### 2.1 Background

In modern blockchain ecosystems, users interact with blockchain networks primarily through wallet applications, which depend on RPC providers to query blockchain state and submit transactions. While blockchain's transparency is a design principle, privacy risks introduced at the **wallet-RPC communication layer** are often overlooked in practice.

### 2.2 Privacy Risks in Wallet-RPC Communication

Even when cryptographic protections (private keys, encryption) are intact, RPC communication channels leak sensitive metadata:

- **Query patterns and call frequency**: Reveals user activity patterns and usage intensity
- **Temporal behavior signatures**: Time-based patterns can identify users even across different sessions
- **Address usage correlations**: Links multiple addresses belonging to the same user
- **Network-level indicators**: IP addresses, session IDs, and routing information enable location inference

### 2.3 The Threat

An **honest-but-curious RPC provider** can leverage this metadata to:
- Link user addresses across different sessions
- Infer behavioral patterns (e.g., trading strategies, DApp usage patterns)
- Reduce user anonymity without modifying blockchain state or breaking cryptographic protections
- Perform longitudinal tracking and correlation analysis

### 2.4 The Gap

Existing discussions of RPC privacy risks lack:
1. **Standardized measurement methodologies**
2. **Empirical quantitative analysis**
3. **Actionable risk assessments**
4. **Real-world validation experiments**

---

## 3. Project Goals and Value Proposition

### 3.1 Primary Goals

1. **Quantify Privacy Leakage**: Develop metrics to measure the extent of privacy exposure in wallet-RPC communications
2. **Identify Attack Vectors**: Catalog specific patterns and behaviors that enable privacy violations
3. **Validate Empirical Findings**: Conduct controlled experiments to confirm theoretical assumptions
4. **Provide Actionable Recommendations**: Deliver concrete guidance for privacy improvement

### 3.2 Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Wallet Developers** | Privacy benchmarking, vulnerability identification, implementation guidelines |
| **RPC Providers** | Privacy auditing, trust transparency, service differentiation |
| **End Users** | Privacy awareness, informed wallet selection, configuration guidance |
| **Academic/Research** | Methodological foundation, dataset contribution, publishable findings |
| **Regulatory Bodies** | Privacy standards evidence, compliance assessment tools |

### 3.3 Differentiators

| Feature | This Project | Existing Solutions |
|---------|--------------|-------------------|
| Real-time measurement | ✔ | ✗ |
| Multi-dimensional scoring | ✔ (4 dimensions) | Limited |
| Actionable insights | ✔ | Often theoretical |
| Empirical validation | ✔ | Rare |
| Rule-based detection | ✔, comprehensive rules | Limited rule coverage |
| Open-source | ✔ | Commercial tools only |

---

## 4. Scope and Boundaries

### 4.1 In-Scope Components

This project focuses on:

✅ **JSON-RPC Request Metadata**
- Method types (e.g., `eth_getBalance`, `eth_call`, `eth_blockNumber`)
- Request timing, frequency, and ordering
- Request parameters (hashed/anonymized where appropriate)
- Response sizes and processing times

✅ **Session-Level Behavior Patterns**
- Sequences of RPC calls within a session
- Inter-request time intervals
- Request clustering and batching behavior
- Session duration and activity patterns

✅ **Address-Level Interaction Traces**
- Multi-address usage within sessions
- Cross-address correlation patterns
- Asset transfer signatures
- Smart contract interaction patterns

✅ **Quantitative Privacy Metrics**
- Information entropy calculation
- User uniqueness scoring
- Temporal correlation analysis
- Spatial inference detection

✅ **Real-World Usage Scenarios**
- Mainnet interactions with popular wallets
- Multiple RPC providers (5 providers planned)
- Various transaction types (transfers, swaps, contract calls)
- Different network conditions

### 4.2 Out-of-Scope Components

To maintain a realistic and bounded threat model, the following are excluded:

❌ **Machine Learning Models**
- ML-based privacy leak classification
- Neural network or deep learning approaches
- Training and model deployment pipelines

❌ **Wallet Software Compromise**
- Private key extraction
- Malicious code injection
- Browser extension exploits

❌ **Cryptographic Breaks**
- Breaking TLS/SSL encryption
- Cracking private keys or seed phrases

❌ **On-Chain Analysis**
- Transaction graph analysis on-chain
- Chain analytic techniques

### 4.3 Assumptions

Throughout this project, we assume:

1. **RPC Provider Visibility**: RPC providers have full visibility into all RPC request metadata
2. **User Behavior**: Users do not actively implement traffic obfuscation (e.g., request padding, timing randomization)
3. **Blockchain Trust**: Blockchain execution and consensus mechanisms operate correctly
4. **Network Reliability**: Network connectivity is stable during measurement periods
5. **Rule-Based Detection**: Privacy leaks will be identified through well-defined detection rules

---

## 5. Threat Model

### 5.1 Adversary Definition

**Adversary Type:** Honest-But-Curious RPC Provider

The RPC provider correctly executes all RPC requests and returns valid responses, but passively observes and records RPC communication metadata for analysis purposes.

### 5.2 Adversary Capabilities

Under this threat model, the adversary can observe:

| Observable | What It Reveals | Privacy Impact |
|------------|-----------------|----------------|
| **JSON-RPC Method Names** | User intentions (balance checks, transactions, contract calls) | Behavioral profiling |
| **Request Timing & Ordering** | Activity patterns, workflows, bot detection signatures | Fingerprinting |
| **Call Frequency** | Usage intensity, application engagement levels | Linkage across sessions |
| **Session Patterns** | Duration, intervals, clustering | Behavioral uniqueness |
| **Address Correlation** | Multi-address ownership | Identity linkage |
| **Network Identifiers** | IP addresses, session IDs | Location inference |

### 5.3 Adversary Limitations

The adversary **cannot**:

- ❌ Access wallet-internal state or private keys
- ❌ Break TLS/SSL encryption or cryptographic primitives
- ❌ Modify blockchain state or transaction execution
- ❌ Execute arbitrary code on user devices

### 5.4 Adversary Goals

1. **User Linkage**: Link multiple addresses to the same user across different sessions
2. **Behavioral Fingerprinting**: Identify unique behavioral patterns that distinguish users
3. **Longitudinal Tracking**: Monitor user behavior over extended time periods
4. **Location Inference**: Infer geographic location from network-level metadata

---

## 6. System Architecture

### 6.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Layer                              │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Real-time   │   Analysis   │    Risk      │  Reports &   │  │
│  │  Dashboard   │   Panels     │ Assessment   │  Export      │  │
│  └──────┬───────┴──────┬───────┴──────┬───────┴──────┬───────┘  │
└─────────┼───────────────┼───────────────┼───────────────┼─────────┘
          │ HTTP REST API │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
│                    (FastAPI - Python)                           │
├─────────────────────────────────────────────────────────────────┤
│  Routes: • Traffic Capture  • Privacy Detection                │
│          • Risk Assessment   • Analytics                       │
│          • Reports          • Configuration                   │
└─────────────────────────────────────────────────────────────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Traffic     │  │  Privacy     │  │    Risk      │  │  Analytics   │
│  Capture     │  │  Detection   │  │  Assessment  │  │  Service     │
│  Service     │  │  Service     │  │  Service     │  │              │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                │                │                │
       ▼                ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Data Layer                                 │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │   MySQL      │    File      │   Detection  │   Metrics    │  │
│  │ (Metadata)   │   Storage    │    Rules     │   Engine     │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Network Capture Layer                         │
│  ┌──────────────┬──────────────┐                               │
│  │  mitmproxy   │   scapy      │                               │
│  │  (TLS Proxy) │  (Sniffing)  │                               │
│  └──────────────┴──────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Layered Architecture

#### Layer 1: Frontend (React + TypeScript)

**Responsibilities:**
- Provide user interface for visualization and interaction
- Real-time data updates via HTTP polling
- Generate analytics charts using D3.js and ECharts
- Export reports in various formats (PDF, CSV, JSON)

#### Layer 2: API Gateway (FastAPI)

**Responsibilities:**
- RESTful API endpoints for all system operations
- Request validation using Pydantic v2
- Response formatting and error handling
- Rate limiting

#### Layer 3: Business Logic Services

**Service 1: Traffic Capture Service**
- Configure and manage mitmproxy/scapy instances
- Parse captured network packets
- Extract JSON-RPC payloads
- Normalize and anonymize sensitive data

**Service 2: Privacy Detection Service**
- Apply privacy leak detection rules
- Classify leak types (identity, asset, behavior, location)
- Calculate confidence scores

**Service 3: Risk Assessment Service**
- Compute multi-dimensional metrics (entropy, uniqueness, correlation, temporal)
- Aggregate scores into overall risk rating (0-100)
- Generate risk reports with recommendations

**Service 4: Analytics Service**
- Statistical analysis of captured data
- Trend analysis and anomaly detection
- Generate visualizable datasets

#### Layer 4: Data Layer

**Component 1: MySQL (Structured Storage)**
- Store metadata from captured traffic
- Index for efficient querying
- User sessions and analysis results
- Risk assessment history
- Detection rules configuration

**Component 2: File Storage (Binary Data)**
- Raw packet captures (PCAP format, encrypted at rest)
- Exported reports

**Component 3: Detection Rules Engine**
- Rule definitions and metadata
- Rule evaluation pipeline

**Component 4: Metrics Engine**
- Statistical computation modules
- Scoring algorithms

### 6.3 Data Flow

```
1. Traffic Capture Phase:
   Wallet → RPC Provider → mitmproxy/scapy → Raw PCAP → Encrypted File Storage

2. Parsing Phase:
   Raw PCAP → scapy → Structured Metadata → MySQL

3. Anonymization Phase:
   Sensitive Fields → Hashing → Anonymized Data → Database

4. Analysis Phase:
   Metadata → Privacy Detection Service → Detection Rules → PrivacyLeakEvent Table

5. Scoring Phase:
   PrivacyLeakEvents → Risk Assessment Service → Multi-dimensional Metrics → RiskAssessment Table

6. Visualization Phase:
   RiskAssessments + Analytics Service → API → Frontend → Dashboard Charts
```

---

## 7. Functional Requirements

### 7.1 Network Traffic Capture

#### FR-1: Traffic Capture Configuration

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-1.1 | **Capture Session Management** | System must support creating, starting, stopping, and deleting capture sessions |
| FR-1.2 | **Multi-Protocol Support** | Capture traffic over HTTP, HTTPS, WebSocket, and HTTP/2 protocols |
| FR-1.3 | **TLS Interception** | Configure mitmproxy to intercept and decrypt TLS traffic with certificate installation |
| FR-1.4 | **Packet-Level Metadata** | Capture request headers (User-Agent, Accept, Content-Type), timestamps, sizes |
| FR-1.5 | **Payload Capture** | Capture JSON-RPC request and response bodies (with optional truncation) |
| FR-1.6 | **Flow-Based Capture** | Store complete request-response pairs with correlation IDs |
| FR-1.7 | **Performance Requirements** | Support sustained capture rate of 1000+ packets/second |
| FR-1.8 | **Session Persistence** | Maintain session state across service restarts (via MySQL) |
| FR-1.9 | **Capture Status Monitoring** | Real-time monitoring of capture session status (active, idle, error) |

#### FR-2: Traffic Parsing and Normalization

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-2.1 | **JSON-RPC Parsing** | Extract method name, parameters, result/error from JSON-RPC payloads |
| FR-2.2 | **Timestamp Normalization** | Convert all timestamps to UTC timezone |
| FR-2.3 | **Parameter Hashing** | Hash sensitive parameters (addresses, amounts) before storage |
| FR-2.4 | **Request-Response Correlation** | Link requests to responses using flow IDs or sequence numbers |
| FR-2.5 | **Error Handling** | Gracefully handle malformed JSON-RPC messages with logged warnings |
| FR-2.6 | **Response Time Calculation** | Compute latency between request send and response receive |
| FR-2.7 | **Batch Request Handling** | Parse JSON-RPC batch requests (array of requests) |

#### FR-3: Data Storage

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-3.1 | **PCAP File Storage** | Store raw packets in PCAP format with AES-256 encryption |
| FR-3.2 | **Structured Metadata** | Store normalized metadata in MySQL with proper indexing |
| FR-3.3 | **Data Retention Policy** | Implement configurable data retention (default: 30 days) |
| FR-3.4 | **File Cleanup** | Automated cleanup of expired PCAP files |
| FR-3.5 | **Storage Optimization** | Compress stored PCAP files (optional) |
| FR-3.6 | **Integrity Verification** | Checksum verification of stored files |

---

### 7.2 Privacy Leak Detection

#### FR-4: Detection Rules Engine

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-4.1 | **Rule Definition Format** | YAML/JSON format for detection rules with metadata fields |
| FR-4.2 | **Rule Categories** | Support classification: IDENTITY, ASSET, BEHAVIOR, LOCATION |
| FR-4.3 | **Rule Conditions** | Support conditions based on: method name, parameters, timing, patterns |
| FR-4.4 | **Rule Actions** | Trigger actions: create leak event, log warning, calculate score |
| FR-4.5 | **Rule Priority** | Support priority levels (critical, high, medium, low) |
| FR-4.6 | **Rule Enable/Disable** | Runtime toggle of individual rules without restart |
| FR-4.7 | **Rule Versioning** | Store rule versions with change history |
| FR-4.8 | **Rule Testing Framework** | Test rules against sample traffic before deployment |

#### FR-5: Core Detection Rules

MUST implement at least 10 detection rules:

**Identity-Related Rules** (3 rules)

| Rule ID | Name | Description |
|---------|------|-------------|
| DR-ID-1 | **Address Reuse Detection** | Detect frequent balance checks or queries to same address across multiple sessions |
| DR-ID-2 | **Address Correlation** | Identify multiple addresses used in same session with correlated behavior |
| DR-ID-3 | **Account Discovery** | Detect patterns of enumerating account indices (e.g., checking eth_getBalance for indices 0, 1, 2...) |

**Asset-Related Rules** (2 rules)

| Rule ID | Name | Description |
|---------|------|-------------|
| DR-AS-1 | **Asset Holding Inference** | Infer asset holdings from repeated asset metadata queries (e.g., erc20_balanceOf) |
| DR-AS-2 | **Transfer Signature Detection** | Identify transfer patterns from nonce sequences and gas price patterns |

**Behavior-Related Rules** (3 rules)

| Rule ID | Name | Description |
|---------|------|-------------|
| DR-BE-1 | **DApp Usage Pattern** | Detect characteristic sequences of calls specific to DApps (e.g., Uniswap swap sequence) |
| DR-BE-2 | **Bot Behavior Detection** | Identify timing patterns indicative of automated bots (fixed intervals, burst patterns) |
| DR-BE-3 | **Active Session Inference** | Detect active vs idle periods based on request frequency thresholds |

**Location-Related Rules** (2 rules)

| Rule ID | Name | Description |
|---------|------|-------------|
| DR-LO-1 | **Timezone Inference** | Infer user timezone from request timing patterns (circadian patterns) |
| DR-LO-2 | **Network Fingerprinting** | Detect consistent network-level signatures (TLS handshake timing) |

#### FR-6: Detection Execution

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-6.1 | **Real-Time Detection** | Execute detection rules as traffic is captured (streaming mode) |
| FR-6.2 | **Batch Detection** | Support re-running detection on historical sessions |
| FR-6.3 | **Event Aggregation** | Aggregate multiple detections occurring in short time window |
| FR-6.4 | **Confidence Scoring** | Calculate confidence score (0.0-1.0) based on rule strength and evidence count |
| FR-6.5 | **Confidence Intervals** | Compute 95% confidence intervals for confidence scores (bootstrap method) |
| FR-6.6 | **Event Deduplication** | Prevent duplicate leak events from same rule within threshold |
| FR-6.7 | **Detection Performance** | Process detection within 100ms of packet capture |

---

### 7.3 Risk Assessment

#### FR-7: Metric Computation

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-7.1 | **Entropy Score** | Calculate Shannon entropy of request method distribution (0.0-1.0) |
| FR-7.2 | **Uniqueness Score** | Measure uniqueness of behavioral patterns compared to baseline (0.0-1.0) |
| FR-7.3 | **Correlation Score** | Compute address and session correlation strength (0.0-1.0) |
| FR-7.4 | **Temporal Score** | Analyze timing patterns for distinguishability (0.0-1.0) |
| FR-7.5 | **Overall Score** | Weighted combination of sub-scores (integer 0-100) |

**Entropy Calculation (FR-7.1)**

```
Given request method frequencies f[1..n] for n methods:
- Normalize: p[i] = f[i] / sum(f)
- Entropy H = -sum(p[i] * log2(p[i]) for i in 1..n)
- Normalize to [0,1]: entropy_score = H / log2(n)
```

**Uniqueness Score (FR-7.2)**

```
For target session T and reference sessions R[1..m]:
- Extract feature vector v_T (method distribution, timing stats)
- Compute cosine similarity to each reference: sim[R_i] = cos(v_T, v_Ri)
- Uniqueness score = 1 - max(sim[R_i])
```

**Correlation Score (FR-7.3)**

```
For session with multiple addresses A[1..k]:
- Compute Jaccard similarity of method sets for all address pairs
- Correlation score = max Jaccard_similarity(A_i, A_j) for all i≠j
```

**Temporal Score (FR-7.4)**

```
- Extract inter-request intervals: intervals[i] = timestamp[i+1] - timestamp[i]
- Compute coefficient of variation (CV = std / mean)
- Normalize CV to [0,1]: temporal_score = min(1.0, CV / threshold)
```

**Overall Risk Score (FR-7.5)**

```
overall_score = w_entropy * entropy_score * 100
             + w_uniqueness * uniqueness_score * 100
             + w_correlation * correlation_score * 100
             + w_temporal * temporal_score * 100

Default weights: w_entropy = 0.25, w_uniqueness = 0.25, w_correlation = 0.25, w_temporal = 0.25
```

#### FR-8: Risk Level Classification

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-8.1 | **Risk Level Thresholds** | Define configurable thresholds: LOW (0-30), MEDIUM (31-50), HIGH (51-70), CRITICAL (71-100) |
| FR-8.2 | **Baseline Comparison** | Compare scores against ideal privacy baseline and worst-case baseline |
| FR-8.3 | **Trend Analysis** | Identify risk score trends across multiple sessions for same user |

#### FR-9: Recommendations Generation

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-9.1 | **Recommendation Templates** | Pre-configured recommendations based on risk level and dominant contributing metrics |
| FR-9.2 | **Specific Recommendations** | Provide at least 3 actionable recommendations per assessment |
| FR-9.3 | **Recommendation Prioritization** | Order recommendations by impact and feasibility |
| FR-9.4 | **Dynamic Recommendations** | Include specific metric values (e.g., "Reduce address correlation: current score 0.82") |

**Recommendation Templates Examples**

```python
RECOMMENDATION_TEMPLATES = {
    "low_entropy": [
        "Increase request method diversity to reduce predictability",
        "Explore multiple DApps to diversify behavioral profile"
    ],
    "high_correlation": [
        "Use address rotation: generate fresh addresses for new sessions",
        "Separate activities: use different addresses for different transaction types"
    ],
    "high_temporal": [
        "Add random timing jitter between requests to obfuscate patterns",
        "Batch requests to reduce timing granularity"
    ],
    "high_uniqueness": [
        "Use common DApps and methods similar to typical users to blend in",
        "Maintain consistent usage patterns across sessions"
    ]
}
```

---

### 7.4 Analytics and Visualization

#### FR-10: Query and Filtering

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-10.1 | **Session Filtering** | Filter by wallet type, RPC provider, date range, status |
| FR-10.2 | **Leak Event Filtering** | Filter by leak type, confidence level, method name |
| FR-10.3 | **Search Functionality** | Full-text search on descriptions and metadata |
| FR-10.4 | **Pagination** | Cursor-based pagination with configurable page size (default: 100) |
| FR-10.5 | **Sorting** | Sort results by any field with ascending/descending order |

#### FR-11: Analytics Queries

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-11.1 | **Summary Statistics** | Aggregate counts for sessions, leaks, addresses |
| FR-11.2 | **Trend Analysis** | Compute metrics over time (hourly, daily, weekly) |
| FR-11.3 | **Comparative Analysis** | Compare metrics across wallets, providers, leak types |
| FR-11.4 | **Correlation Analysis** | Identify correlations between metrics (e.g., entropy vs uniqueness) |
| FR-11.5 | **Percentile Calculations** | Compute P50, P95, P99 for response times, intervals |

#### FR-12: Visualization Requirements

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-12.1 | **Dashboard Charts** | Line charts (trends), bar charts (comparisons), pie charts (distributions) |
| FR-12.2 | **Heatmaps** | Visualize request patterns over time (methods vs hour-of-day) |
| FR-12.3 | **Network Graphs** | Visualize address correlations and session relationships |
| FR-12.4 | **Score Distribution** | Histogram of risk scores with quartile markers |
| FR-12.5 | **Interactive Charts** | Zoom, pan, tooltip details on hover, click-to-filter |

#### FR-13: Report Generation

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-13.1 | **PDF Reports** | Generate printable reports with charts, tables, and narrative |
| FR-13.2 | **CSV Export** | Export tabular data (sessions, leaks, assessments) as CSV |
| FR-13.3 | **JSON Export** | Export complete datasets including raw data |
| FR-13.4 | **Report Templates** | Pre-configured templates for different audiences (technical, executive) |
| FR-13.5 | **Report Customization** | Allow customization of included sections and charts |

---

### 7.5 API Interface

#### FR-14: API Design

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-14.1 | **RESTful Endpoints** | All CRUD operations follow REST conventions (GET, POST, PUT, DELETE) |
| FR-14.2 | **Response Format** | Standardized format with success/error indicators |
| FR-14.3 | **Versioning** | API versioned in URL path (e.g., /api/v1/) |
| FR-14.4 | **Pagination** | Cursor-based pagination with next_cursor in response |
| FR-14.5 | **Filtering** | Query parameters for filtering (e.g., ?leak_type=identity&min_confidence=0.5) |
| FR-14.6 | **Sorting** | sort_by and sort_order query parameters |
| FR-14.7 | **Field Selection** | Partial field selection via fields parameter |
| FR-14.8 | **Rate Limiting** | Enforce 100 requests/minute per IP address |
| FR-14.9 | **Request Validation** | Pydantic v2 models for request body validation |
| FR-14.10 | **Error Handling** | Structured error responses with codes and messages |
| FR-14.11 | **OpenAPI Documentation** | Auto-generated Swagger/ReDoc documentation |

#### FR-15: API Endpoints

Must implement all endpoints detailed in Section 10 (API Specifications).

---

### 7.6 Configuration and Management

#### FR-16: Configuration Management

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-16.1 | **Environment Variables** | Sensitive config via environment variables (database, encryption keys) |
| FR-16.2 | **Database Configuration** | Scoring weights, risk thresholds stored in MySQL |
| FR-16.3 | **Detection Rules Management** | CRUD operations for detection rules via API |
| FR-16.4 | **Configuration Versioning** | Track configuration changes with timestamps |
| FR-16.5 | **Configuration Reload** | Hot-reload configuration without service restart |
| FR-16.6 | **Default Configuration** | Ship with sensible defaults for all settings |

#### FR-17: Monitoring and Health

| ID | Requirement | Description |
|----|-------------|-------------|
| FR-17.1 | **Health Check Endpoint** | Returns service status and database connectivity |
| FR-17.2 | **Metrics Endpoint** | Expose system metrics (request counts, error rates, latency) |
| FR-17.3 | **Logging** | Structured JSON logging for all events |
| FR-17.4 | **Error Tracking** | Capture and log all errors with stack traces |
| FR-17.5 | **Status Dashboard** | Display active sessions, capture status, recent errors |

---

## 8. Non-Functional Requirements

### 8.1 Performance Requirements

| Requirement | Target Value | Measurement |
|-------------|--------------|-------------|
| **API Response Time (P95)** | < 500ms | Load testing (Locust) |
| **API Response Time (P99)** | < 100ms | Load testing |
| **Health Check Response** | < 50ms (P99) | Monitoring |
| **Traffic Capture Latency** | < 100ms per packet | Profiling |
| **Risk Assessment Computation** | < 2s per session | Performance testing |
| **Dashboard Initial Load** | < 3s | Browser performance metrics |
| **Dashboard Interaction** | < 500ms | Browser performance metrics |
| **Packet Capture Throughput** | 1000+ packets/second | Stress testing |
| **Query Response (indexed)** | < 200ms for common queries | Query profiling |
| **Report Generation (PDF)** | < 10s for 100-page report | Performance testing |

### 8.2 Scalability Requirements

| Requirement | Target Value |
|-------------|--------------|
| **Data Storage** | Support 100GB+ of captured traffic |
| **Database Connections** | Support 50+ concurrent MySQL connections |
| **Concurrent Sessions** | Support 10+ concurrent capture sessions |
| **Session Count** | Support 10,000+ sessions in database |
| **Event Count** | Support 1,000,000+ leak events |

### 8.3 Reliability and Availability

| Requirement | Target Value |
|-------------|--------------|
| **System Availability** | > 99% uptime |
| **Mean Time Between Failures (MTBF)** | > 168 hours (1 week) |
| **Mean Time To Recovery (MTTR)** | < 30 minutes for critical failures |
| **Data Durability** | No data loss (MySQL with backups) |
| **Automatic Restart** | Auto-restart on service crash (via systemd/process manager) |
| **Graceful Degradation** | Continue functioning under degraded conditions |

### 8.4 Security Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| **SR-1** | All sensitive configuration in environment variables | Critical |
| SR-2 | Database connections use TLS encryption | High |
| SR-3 | Stored raw packets encrypted at rest using AES-256 | Critical |
| SR-4 | All user input validated against allowed whitelists | Critical |
| SR-5 | Sanitize all strings before database insertion (SQL injection prevention) | Critical |
| SR-6 | Never log or store raw wallet addresses, transaction hashes | Critical |
| SR-7 | All session IDs are cryptographic random UUIDs v4 | Critical |
| SR-8 | Implement rate limiting on all API endpoints (100 req/min) | Critical |
| SR-9 | API errors do not expose internal system details | High |
| SR-10 | File upload validation (size, type) if file endpoints exist | Medium |

### 8.5 Privacy Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| **PR-1** | All captured traffic anonymized before database insertion | Critical |
| PR-2 | Wallet addresses hashed (SHA-256) and truncated to 8 characters | Critical |
| PR-3 | IP addresses hashed or anonymized before storage | Critical |
| PR-4 | Transaction hashes hashed and truncated | Critical |
| PR-5 | Exported reports contain no raw sensitive information | Critical |
| PR-6 | Analysis must not re-identify users from anonymized data | Critical |

### 8.6 Code Quality Requirements

| Requirement | Standard |
|-------------|----------|
| **Python Code Style** | PEP 8 compliance |
| **Type Annotations** | Required for all functions and classes |
| **Docstrings** | Google-style or NumPy-style docstrings for all public functions |
| **Imports** | Organized, grouped, no unused imports |
| **Naming Conventions** | snake_case for functions/variables, PascalCase for classes |
| **Line Length** | Max 120 characters (with exceptions |
| **Code Complexity** | Cyclomatic complexity < 10 per function |
| **Function Length** | Max 50 lines (with exceptions for special cases) |
| **TypeScript Code Style** | ESLint + Prettier with standard rules |

### 8.7 Testing Requirements

| Requirement | Target |
|-------------|--------|
| **Unit Test Coverage** | > 70% for all modules |
| **API Integration Tests** | All endpoints tested end-to-end |
| **Detection Rule Tests** | Each rule tested with known leak samples |
| **Risk Assessment Tests** | Validated against manually assessed cases |
| **Performance Tests** | All performance requirements validated |
| **Smoke Tests** | Critical paths tested before each deployment |
| **Regression Tests** | Test suite runs on every commit |

### 8.8 Documentation Requirements

| Requirement | Status |
|-------------|--------|
| **Source Code Documentation** | All non-trivial functions have docstrings |
| **API Documentation** | Auto-generated via Swagger/OpenAPI |
| **README** | Quick start guide, installation, architecture overview |
| **Changelog** | Document all breaking changes and major features |
| **Deployment Guide** | Step-by-step production deployment instructions |
| **User Manual** | Dashboard usage guide and report interpretation |

---

## 9. Data Models

### 9.1 Core Entities

#### Entity 1: Session (Capture Session)

**Purpose**: Represents a network traffic capture session.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | CHAR(36) | PK, NOT NULL | Session UUID (v4) |
| `wallet_type` | VARCHAR(255) | NOT NULL | Wallet application name |
| `rpc_provider` | VARCHAR(255) | NOT NULL | RPC provider name/endpoint |
| `start_time` | TIMESTAMP | NOT NULL, UTC | Session start timestamp |
| `end_time` | TIMESTAMP | NULLABLE, UTC | Session end timestamp |
| `packet_count` | INT | NOT NULL, >= 0 | Total packets captured |
| `duration_seconds` | INT | NULLABLE, >= 0 | Session duration |
| `status` | ENUM | NOT NULL | 'ACTIVE', 'COMPLETED', 'FAILED' |
| `metadata` | JSON | NULLABLE | Additional session metadata |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() ON UPDATE NOW() | Update timestamp |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX `idx_wallet_type` (`wallet_type`)
- INDEX `idx_rpc_provider` (`rpc_provider`)
- INDEX `idx_start_time` (`start_time`)
- INDEX `idx_status` (`status`)

---

#### Entity 2: NetworkTraffic (Network Traffic Records)

**Purpose**: Stores metadata for captured network traffic.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | CHAR(36) | PK, NOT NULL | Traffic UUID (v4) |
| `session_id` | CHAR(36) | FK, NOT NULL | Session FK |
| `method` | VARCHAR(16) | NOT NULL | HTTP method (GET, POST, etc.) |
| `endpoint` | VARCHAR(2048) | NOT NULL | RPC endpoint URL |
| `request_body` | TEXT | NULLABLE | JSON-RPC request (anonymized) |
| `rpc_method` | VARCHAR(255) | NULLABLE | Extracted JSON-RPC method |
| `rpc_params_hash` | VARCHAR(64) | NULLABLE | Hashed parameters |
| `request_timestamp` | TIMESTAMP | NOT NULL, UTC | Request timestamp |
| `response_time_ms` | INT | NULLABLE, >= 0 | Response time in ms |
| `response_status` | INT | NULLABLE | HTTP status code |
| `response_size_bytes` | BIGINT | NULLABLE, >= 0 | Response size |
| `ip_address_hash` | VARCHAR(64) | NULLABLE | Hashed source IP |
| `user_agent` | VARCHAR(512) | NULLABLE | User-Agent header |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX `idx_session_id` (`session_id`)
- INDEX `idx_request_timestamp` (`request_timestamp`)
- INDEX `idx_rpc_method` (`rpc_method`)
- FOREIGN KEY (`session_id`) REFERENCES `sessions`(`id`) ON DELETE CASCADE

---

#### Entity 3: PrivacyLeakEvent (Detected Privacy Leaks)

**Purpose**: Represents a detected privacy leakage event.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | CHAR(36) | PK, NOT NULL | Event UUID (v4) |
| `session_id` | CHAR(36) | FK, NOT NULL | Session FK |
| `leak_type` | ENUM | NOT NULL | 'IDENTITY', 'ASSET', 'BEHAVIOR', 'LOCATION' |
| `method_name` | VARCHAR(255) | NOT NULL | Triggering JSON-RPC method |
| `description` | VARCHAR(2048) | NOT NULL | Human-readable description |
| `confidence` | FLOAT | NOT NULL, [0.0, 1.0] | Confidence score |
| `confidence_interval_low` | FLOAT | NOT NULL, [0.0, 1.0] | Lower bound (95% CI) |
| `confidence_interval_high` | FLOAT | NOT NULL, [0.0, 1.0] | Upper bound (95% CI) |
| `details` | JSON | NULLABLE | Additional metadata |
| `timestamp` | TIMESTAMP | NOT NULL, UTC | Event timestamp |
| `address_hash` | VARCHAR(16) | NOT NULL | Hashed wallet address |
| `rule_id` | VARCHAR(64) | NOT NULL | Detection rule identifier |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX `idx_session_id` (`session_id`)
- INDEX `idx_leak_type` (`leak_type`)
- INDEX `idx_rule_id` (`rule_id`)
- INDEX `idx_timestamp` (`timestamp`)
- INDEX `idx_confidence` (`confidence`)
- FOREIGN KEY (`session_id`) REFERENCES `sessions`(`id`) ON DELETE CASCADE

---

#### Entity 4: RiskAssessment (Risk Assessments)

**Purpose**: Stores computed risk assessments.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | CHAR(36) | PK, NOT NULL | Assessment UUID (v4) |
| `session_id` | CHAR(36) | FK, NULLABLE | Session FK (NULL for address-level) |
| `address_hash` | VARCHAR(16) | NULLABLE | Hashed address |
| `overall_score` | INT | NOT NULL, [0, 100] | Overall risk score |
| `entropy_score` | FLOAT | NOT NULL, [0.0, 1.0] | Entropy score |
| `uniqueness_score` | FLOAT | NOT NULL, [0.0, 1.0] | Uniqueness score |
| `correlation_score` | FLOAT | NOT NULL, [0.0, 1.0] | Correlation score |
| `temporal_score` | FLOAT | NOT NULL, [0.0, 1.0] | Temporal score |
| `confidence` | FLOAT | NOT NULL, [0.0, 1.0] | Overall confidence |
| `confidence_interval_low` | FLOAT | NOT NULL | Lower bound CI |
| `confidence_interval_high` | FLOAT | NOT NULL | Upper bound CI |
| `risk_level` | ENUM | NOT NULL | 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL' |
| `recommendations` | JSON | NOT NULL | List of recommendations |
| `baseline_comparison` | JSON | NULLABLE | Comparison to baselines |
| `assessed_at` | TIMESTAMP | NOT NULL, UTC | Assessment timestamp |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX `idx_session_id` (`session_id`)
- INDEX `idx_address_hash` (`address_hash`)
- INDEX `idx_overall_score` (`overall_score`)
- INDEX `idx_risk_level` (`risk_level`)
- FOREIGN KEY (`session_id`) REFERENCES `sessions`(`id`) ON DELETE CASCADE

---

#### Entity 5: DetectionRule (Detection Rules)

**Purpose**: Stores detection rule definitions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | VARCHAR(64) | PK, NOT NULL | Rule unique ID |
| `name` | VARCHAR(255) | NOT NULL | Rule name |
| `category` | ENUM | NOT NULL | 'IDENTITY', 'ASSET', 'BEHAVIOR', 'LOCATION' |
| `description` | TEXT | NOT NULL | Rule description |
| `conditions` | JSON | NOT NULL | Rule conditions (logic) |
| `actions` | JSON | NOT NULL | Rule actions |
| `priority` | ENUM | NOT NULL, DEFAULT 'MEDIUM' | 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW' |
| `enabled` | BOOLEAN | NOT NULL, DEFAULT TRUE | Enable/disable flag |
| `version` | INT | NOT NULL, DEFAULT 1 | Rule version |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() ON UPDATE NOW() | Update timestamp |

**Indexes**:
- PRIMARY KEY (`id`)
- INDEX `idx_category` (`category`)
- INDEX `idx_enabled` (`enabled`)
- INDEX `idx_priority` (`priority`)

---

#### Entity 6: Configuration (Configuration)

**Purpose**: Stores system configuration.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `key` | VARCHAR(255) | PK, NOT NULL | Configuration key |
| `value` | JSON | NOT NULL | Configuration value |
| `description` | TEXT | NULLABLE | Description |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() ON UPDATE NOW() | Last update |

**Sample Configuration Keys**:
- `scoring_weights`: {"entropy": 0.25, "uniqueness": 0.25, "correlation": 0.25, "temporal": 0.25}
- `risk_thresholds`: {"low": 30, "medium": 50, "high": 70}
- `detection_rules_override`: {...}

---

### 9.2 Entity Relationships

```
Sessions (1) ──────── (*) NetworkTraffic
Sessions (1) ──────── (*) PrivacyLeakEvent
Sessions (0 or 1) ──── (1) RiskAssessment
DetectionRule (1) ──── (*) PrivacyLeakEvent
```

---

### 9.3 Pydantic Response Models

```python
from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator
from enum import Enum

class ErrorCode(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

class APIResponse(BaseModel):
    """Standard API response"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: ErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: ErrorDetail
    metadata: Optional[Dict[str, Any]] = None

class LeakType(str, Enum):
    IDENTITY = "identity"
    ASSET = "asset"
    BEHAVIOR = "behavior"
    LOCATION = "location"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"

class SessionCreate(BaseModel):
    """Create session request"""
    wallet_type: str = Field(..., min_length=1, max_length=255)
    rpc_provider: str = Field(..., min_length=1, max_length=255)

class SessionResponse(BaseModel):
    """Session response"""
    id: str
    wallet_type: str
    rpc_provider: str
    start_time: datetime
    end_time: Optional[datetime]
    packet_count: int
    duration_seconds: Optional[int]
    status: SessionStatus
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NetworkTrafficResponse(BaseModel):
    """Network traffic record response"""
    id: str
    session_id: str
    method: str
    endpoint: str
    rpc_method: Optional[str]
    request_timestamp: datetime
    response_time_ms: Optional[int]
    response_status: Optional[int]
    response_size_bytes: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class PrivacyLeakEventResponse(BaseModel):
    """Privacy leak event response"""
    id: str
    session_id: str
    leak_type: LeakType
    method_name: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_interval_low: float
    confidence_interval_high: float
    details: Optional[Dict[str, Any]]
    timestamp: datetime
    address_hash: str
    rule_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class RiskAssessmentResponse(BaseModel):
    """Risk assessment response"""
    id: str
    session_id: Optional[str]
    address_hash: Optional[str]
    overall_score: int = Field(..., ge=0, le=100)
    entropy_score: float = Field(..., ge=0.0, le=1.0)
    uniqueness_score: float = Field(..., ge=0.0, le=1.0)
    correlation_score: float = Field(..., ge=0.0, le=1.0)
    temporal_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_interval_low: float
    confidence_interval_high: float
    risk_level: RiskLevel
    recommendations: List[str] = Field(..., min_length=1)
    baseline_comparison: Optional[Dict[str, Any]]
    assessed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    limit: int
    offset: int
    next_cursor: Optional[str] = None
```

---

## 10. API Specifications

### 10.1 API Overview

- **Base URL**: `http://localhost:8000/api/v1` (development)
- **Protocol**: HTTP/2 with TLS in production
- **Content-Type**: `application/json`
- **Rate Limiting**: 100 requests/minute per IP address
- **API Documentation**: `/docs` (Swagger UI), `/redoc` (ReDoc)

### 10.2 Standard Response Format

**Success Response (200/201):**
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "request_id": "uuid-v4",
    "timestamp": "2026-02-05T15:00:00Z"
  }
}
```

**Error Response (400/404/500):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Validation failed",
    "details": { "field": "wallet_type must not be empty" }
  },
  "metadata": {
    "request_id": "uuid-v4",
    "timestamp": "2026-02-05T15:00:00Z"
  }
}
```

### 10.3 Session Management

#### `POST /api/v1/sessions` - Create Session

**Request:**
```json
{
  "wallet_type": "MetaMask",
  "rpc_provider": "Infura Mainnet"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "wallet_type": "MetaMask",
    "rpc_provider": "Infura Mainnet",
    "start_time": "2026-02-05T15:00:00Z",
    "end_time": null,
    "packet_count": 0,
    "duration_seconds": null,
    "status": "active",
    "metadata": null,
    "created_at": "2026-02-05T15:00:00Z",
    "updated_at": "2026-02-05T15:00:00Z"
  }
}
```

#### `GET /api/v1/sessions/{session_id}` - Get Session

**Response (200):**
```json
{
  "success": true,
  "data": { /* SessionResponse object */ }
}
```

#### `GET /api/v1/sessions` - List Sessions

**Query Parameters**:
- `wallet_type` (optional): Filter by wallet type
- `rpc_provider` (optional): Filter by RPC provider
- `status` (optional): Filter by status
- `limit` (optional, default 50): Maximum results
- `offset` (optional, default 0): Offset

**Response (200):**
```json
{
  "success": true,
  "data": {
    "sessions": [/* SessionResponse objects */],
    "total": 42,
    "limit": 50,
    "offset": 0
  }
}
```

#### `PUT /api/v1/sessions/{session_id}` - Update Session

**Request:**
```json
{
  "status": "completed",
  "end_time": "2026-02-05T15:05:00Z",
  "packet_count": 342
}
```

**Response (200):**
```json
{
  "success": true,
  "data": { /* Updated SessionResponse */ }
}
```

#### `DELETE /api/v1/sessions/{session_id}` - Delete Session

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Session deleted successfully"
  }
}
```

---

### 10.4 Traffic Management

#### `GET /api/v1/sessions/{session_id}/traffic` - Get Traffic

**Query Parameters**:
- `method` (optional): Filter by HTTP method
- `rpc_method` (optional): Filter by JSON-RPC method
- `start_time` (optional): Start timestamp (ISO 8601)
- `limit`/`offset`: Pagination

**Response (200):**
```json
{
  "success": true,
  "data": {
    "traffic": [/* NetworkTrafficResponse objects */],
    "total": 342,
    "limit": 100,
    "offset": 0
  }
}
```

---

### 10.5 Privacy Leak Events

#### `GET /api/v1/sessions/{session_id}/leaks` - Get Privacy Leaks

**Query Parameters**:
- `leak_type` (optional): Filter by leak type
- `min_confidence` (optional): Minimum confidence (0.0-1.0)
- `rule_id` (optional): Filter by detection rule

**Response (200):**
```json
{
  "success": true,
  "data": {
    "leaks": [/* PrivacyLeakEventResponse objects */],
    "total": 15,
    "limit": 100,
    "offset": 0
  }
}
```

#### `POST /api/v1/leaks/simulate` - Simulate Detection (Testing)

**Request:**
```json
{
  "sample_traffic": { /* Sample traffic data */ },
  "rules": ["DR-ID-1", "DR-BE-1"]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "detected_events": [/* Simulated leak events */]
  }
}
```

---

### 10.6 Risk Assessment

#### `GET /api/v1/sessions/{session_id}/assessment` - Get Risk Assessment

**Query Parameters**:
- `force_recompute` (optional, default false): Force recomputation

**Response (200):**
```json
{
  "success": true,
  "data": { /* RiskAssessmentResponse object */ }
}
```

#### `POST /api/v1/assessments/evaluate` - Evaluate Custom Data

**Request:**
```json
{
  "traffic_data": [...],
  "leak_events": [...]
}
```

**Response (200):**
```json
{
  "success": true,
  "data": { /* RiskAssessmentResponse object */ }
}
```

---

### 10.7 Detection Rules Management

#### `GET /api/v1/rules` - List Detection Rules

**Query Parameters**:
- `category` (optional): Filter by category
- `enabled` (optional): Filter by enabled status
- `priority` (optional): Filter by priority

**Response (200):**
```json
{
  "success": true,
  "data": {
    "rules": [/* DetectionRule objects */],
    "total": 10
  }
}
```

#### `POST /api/v1/rules` - Create Detection Rule

**Request:**
```json
{
  "id": "DR-CUSTOM-1",
  "name": "Custom Rule",
  "category": "identity",
  "description": "Description",
  "conditions": { "rpc_method": "eth_getBalance", "frequency": "> 5/min" },
  "actions": { "create_event": true },
  "priority": "medium",
  "enabled": true
}
```

#### `PUT /api/v1/rules/{rule_id}` - Update Detection Rule

#### `DELETE /api/v1/rules/{rule_id}` - Delete Detection Rule

---

### 10.8 Analytics

#### `GET /api/v1/analytics/summary` - Get Summary

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_sessions": 42,
    "total_packets_captured": 14258,
    "total_leaks_detected": 615,
    "leaks_by_type": {
      "identity": 234,
      "asset": 189,
      "behavior": 142,
      "location": 50
    },
    "average_risk_score": 61.2,
    "risk_distribution": {
      "low": 8,
      "medium": 18,
      "high": 12,
      "critical": 4
    }
  }
}
```

#### `GET /api/v1/analytics/trends/{metric}` - Get Trends

**Path Parameter:**
- `metric`: One of (risk_score, entropy, uniqueness, correlation, temporal, leak_count)

**Query Parameters:**
- `interval` (optional): hour, day, week, month (default: hour)
- `start_time`, `end_time` (optional): Time range

---

### 10.9 Reports

#### `POST /api/v1/reports/generate` - Generate Report

**Request:**
```json
{
  "sessions": ["uuid-1", "uuid-2"],
  "format": "pdf",
  "template": "technical"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "report_id": "report-uuid",
    "download_url": "/reports/download/report-uuid",
    "status": "processing",
    "estimated_ready": "2026-02-05T15:02:00Z"
  }
}
```

#### `GET /api/v1/reports/download/{report_id}` - Download Report

---

### 10.10 Configuration

#### `GET /api/v1/config` - Get Configuration

**Response (200):**
```json
{
  "success": true,
  "data": {
    "scoring_weights": {
      "entropy": 0.25,
      "uniqueness": 0.25,
      "correlation": 0.25,
      "temporal": 0.25
    },
    "risk_thresholds": {
      "low": 30,
      "medium": 50,
      "high": 70
    }
  }
}
```

#### `PUT /api/v1/config` - Update Configuration

---

### 10.11 Health

#### `GET /health` - Health Check

**Response (200):**
```json
{
  "status": "healthy",
  "service": "wallet-rpc-privacy",
  "timestamp": "2026-02-05T15:10:00Z",
  "database": "connected",
  "version": "2.0.0"
}
```

---

## 11. Core Algorithms and Detection Rules

### 11.1 Detection Rule Format

Each detection rule is defined in YAML/JSON format:

```yaml
id: DR-ID-1
name: Address Reuse Detection
category: IDENTITY
priority: HIGH
enabled: true
description: Detect frequent balance checks for same address across multiple sessions
version: 1

conditions:
  - type: method_pattern
    methods: ["eth_getBalance", "eth_getTransactionCount"]
  - type: frequency
    threshold: "> 5/hour"
  - type:跨session
    pattern: same_address_multiple_sessions

actions:
  - type: create_event
    confidence: 0.85
    details:
      address_hash: "{{address_hash}}"
      session_count: "{{session_count}}"
      check_frequency: "{{frequency}}/hour"
  - type: log
    level: warning
```

### 11.2 Core Detection Algorithms

#### Algorithm 1: Entropy Calculation

```python
import math
from collections import Counter
from typing import List

def calculate_entropy_score(methods: List[str]) -> float:
    """
    Calculate normalized Shannon entropy of method distribution.

    Args:
        methods: List of JSON-RPC method names

    Returns:
        Normalized entropy score [0.0, 1.0]
    """
    if not methods:
        return 0.0

    # Count frequency of each method
    freq = Counter(methods)
    total = len(methods)
    n_unique = len(freq)

    if n_unique <= 1:
        return 0.0

    # Calculate Shannon entropy
    probabilities = [count / total for count in freq.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities if p > 0)

    # Normalize to [0, 1]
    max_entropy = math.log2(n_unique)
    return entropy / max_entropy
```

#### Algorithm 2: Uniqueness Score

```python
from typing import List, Dict, Any
import numpy as np
from scipy.spatial.distance import cosine

def extract_behavioral_features(traffic_records: List[Dict[str, Any]]) -> np.array:
    """
    Extract feature vector from traffic records.

    Features:
    - Method distribution (normalized counts)
    - Average response time
    - Request frequency (requests per minute)

    Args:
        traffic_records: List of network traffic records

    Returns:
        Feature vector as numpy array
    """
    # Method distribution
    methods = [r['rpc_method'] for r in traffic_records if r.get('rpc_method')]
    method_counter = Counter(methods)
    total = len(methods)

    # Get top 20 most common methods (fixed size for similarity)
    top_methods = [m for m, _ in method_counter.most_common(20)]
    method_dist = [method_counter.get(m, 0) / total for m in top_methods]

    # Average response time
    response_times = [r['response_time_ms'] for r in traffic_records
                     if r.get('response_time_ms')]
    avg_response_time = np.mean(response_times) if response_times else 0

    # Request frequency
    if traffic_records:
        time_span = (traffic_records[-1]['request_timestamp'] -
                    traffic_records[0]['request_timestamp']).total_seconds()
        frequency = len(traffic_records) / max(time_span, 1)
    else:
        frequency = 0

    # Normalize features
    features = np.array(method_dist + [avg_response_time / 1000.0, frequency / 10.0])
    return features

def calculate_uniqueness_score(
    target_traffic: List[Dict[str, Any]],
    reference_traffics: List[List[Dict[str, Any]]]
) -> float:
    """
    Calculate uniqueness score by comparing to reference sessions.

    Args:
        target_traffic: Traffic records for target session
        reference_traffics: List of traffic record lists for reference sessions

    Returns:
        Uniqueness score [0.0, 1.0]
    """
    if not target_traffic or not reference_traffics:
        return 0.5  # Neutral value

    target_features = extract_behavioral_features(target_traffic)

    similarities = []
    for reference_traffic in reference_traffics:
        if not reference_traffic:
            continue
        ref_features = extract_behavioral_features(reference_traffic)
        similarity = 1 - cosine(target_features, ref_features)
        similarities.append(similarity)

    if not similarities:
        return 1.0  # Completely unique (no comparisons)

    max_similarity = max(similarities)
    return max(0.0, 1.0 - max_similarity)
```

#### Algorithm 3: Correlation Score

```python
from typing import List, Set, Dict, Any
from collections import defaultdict

def calculate_correlation_score(
    traffic_records: List[Dict[str, Any]]
) -> float:
    """
    Calculate address correlation score within a session.

    High score indicates strong correlation between multiple addresses
    (privacy risk).

    Args:
        traffic_records: Traffic records for a session

    Returns:
        Correlation score [0.0, 1.0]
    """
    # Group requests by address
    address_methods = defaultdict(set)
    for record in traffic_records:
        address_hash = record.get('address_hash')
        method = record.get('rpc_method')
        if address_hash and method:
            address_methods[address_hash].add(method)

    addresses = list(address_methods.keys())

    if len(addresses) < 2:
        return 0.0  # No multiple addresses to correlate

    # Calculate Jaccard similarity for all pairs
    jaccard_similarities = []
    for i in range(len(addresses)):
        for j in range(i + 1, len(addresses)):
            set_i = address_methods[addresses[i]]
            set_j = address_methods[addresses[j]]

            # Jaccard similarity
            intersection = len(set_i & set_j)
            union = len(set_i | set_j)
            similarity = intersection / union if union > 0 else 0

            jaccard_similarities.append(similarity)

    if not jaccard_similarities:
        return 0.0

    return max(jaccard_similarities)
```

#### Algorithm 4: Temporal Score

```python
from typing import List, Dict, Any
from datetime import timedelta
import numpy as np

def calculate_temporal_score(traffic_records: List[Dict[str, Any]]) -> float:
    """
    Calculate temporal pattern distinguishability score.

    High score indicates predictable, distinguishable timing patterns
    (privacy risk).

    Args:
        traffic_records: Traffic records for a session

    Returns:
        Temporal score [0.0, 1.0]
    """
    if len(traffic_records) < 2:
        return 0.0

    # Extract inter-request intervals
    intervals = []
    for i in range(1, len(traffic_records)):
        prev_time = traffic_records[i - 1]['request_timestamp']
        curr_time = traffic_records[i]['request_timestamp']
        interval = (curr_time - prev_time).total_seconds()
        if interval > 0:
            intervals.append(interval)

    if len(intervals) < 2:
        return 0.0

    # Calculate coefficient of variation (CV = std / mean)
    mean_interval = np.mean(intervals)
    std_interval = np.std(intervals)

    if mean_interval == 0:
        return 0.0

    cv = std_interval / mean_interval

    # Normalize: High CV = irregular = more private (low score)
    # Low CV = regular = less private (high score)
    # Threshold: CV < 0.5 is considered regular
    score = max(0.0, min(1.0, 1.0 - (cv / 0.5)))
    return score
```

### 11.3 Confidence Interval Calculation (Bootstrap)

```python
import numpy as np
from typing import List, Callable

def bootstrap_confidence_interval(
    data: List[float],
    stat_func: Callable = np.mean,
    n_bootstrap: int = 10000,
    ci_percentile: float = 95
) -> tuple[float, float]:
    """
    Calculate confidence interval using bootstrap resampling.

    Args:
        data: Data points
        stat_func: Statistic function (default: mean)
        n_bootstrap: Number of bootstrap iterations
        ci_percentile: Confidence interval percentile (e.g., 95)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    data = np.array(data)

    if len(data) < 2:
        # Not enough data, return bounds around observed value
        observed = stat_func(data)
        return (observed, observed)

    bootstrap_stats = []
    for _ in range(n_bootstrap):
        # Resample with replacement
        resample = np.random.choice(data, size=len(data), replace=True)
        stat = stat_func(resample)
        bootstrap_stats.append(stat)

    # Calculate percentiles
    alpha = (100 - ci_percentile) / 2
    lower_bound = np.percentile(bootstrap_stats, alpha)
    upper_bound = np.percentile(bootstrap_stats, 100 - alpha)

    return (float(lower_bound), float(upper_bound))
```

### 11.4 Overall Risk Score Calculation

```python
from typing import Dict

def calculate_overall_risk_score(
    entropy_score: float,
    uniqueness_score: float,
    correlation_score: float,
    temporal_score: float,
    weights: Dict[str, float] = None
) -> int:
    """
    Calculate overall risk score from sub-scores.

    Args:
        entropy_score: Entropy score [0.0, 1.0]
        uniqueness_score: Uniqueness score [0.0, 1.0]
        correlation_score: Correlation score [0.0, 1.0]
        temporal_score: Temporal score [0.0, 1.0]
        weights: Weight mapping (optional)

    Returns:
        Overall risk score [0, 100]
    """
    if weights is None:
        weights = {
            "entropy": 0.25,
            "uniqueness": 0.25,
            "correlation": 0.25,
            "temporal": 0.25
        }

    # Validate weights sum to 1.0
    weight_sum = sum(weights.values())
    if abs(weight_sum - 1.0) > 0.01:
        raise ValueError(f"Weights must sum to 1.0, got {weight_sum}")

    # Calculate weighted sum
    weighted_score = (
        weights.get("entropy", 0) * entropy_score +
        weights.get("uniqueness", 0) * uniqueness_score +
        weights.get("correlation", 0) * correlation_score +
        weights.get("temporal", 0) * temporal_score
    )

    # Scale to 0-100 and round
    overall_score = int(round(weighted_score * 100))
    overall_score = max(0, min(100, overall_score))

    return overall_score

def classify_risk_level(score: int) -> str:
    """Classify risk level from score."""
    if score <= 30:
        return "LOW"
    elif score <= 50:
        return "MEDIUM"
    elif score <= 70:
        return "HIGH"
    else:
        return "CRITICAL"
```

---

## 12. Development Standards and Guidelines

### 12.1 Python Development Standards

#### Code Style (PEP 8)

```python
# ✅ Correct: snake_case for functions
def calculate_entropy_score(methods: List[str]) -> float:
    pass

# ✅ Correct: PascalCase for classes
class RiskAssessmentService:
    pass

# ✅ Correct: UPPER_CASE for constants
DEFAULT_SCORING_WEIGHTS = {
    "entropy": 0.25,
    "uniqueness": 0.25,
}

# ❌ Wrong: camelCase
def calculateEntropyScore(methods):
    pass
```

#### Type Annotations

```python
# ✅ Required: Type hints for all function parameters and returns
from datetime import datetime
from typing import Optional, List, Dict, Any

def process_leak_event(
    session_id: str,
    leak_type: LeakType,
    confidence: float,
    details: Optional[Dict[str, Any]] = None
) -> PrivacyLeakEvent:
    """
    Process a privacy leak event and store in database.

    Args:
        session_id: Session UUID
        leak_type: Type of leak detected
        confidence: Confidence score [0.0, 1.0]
        details: Additional metadata

    Returns:
        Created PrivacyLeakEvent instance

    Raises:
        ValueError: If confidence not in valid range
    """
    pass
```

#### Docstrings (Google Style)

```python
def calculate_correlation_score(
    traffic_records: List[NetworkTraffic]
) -> float:
    """
    Calculate address correlation score within a session.

    High scores indicate strong correlation between multiple addresses,
    which is a privacy risk as it enables address linkage.

    Args:
        traffic_records: List of network traffic records for a session.

    Returns:
        Correlation score in range [0.0, 1.0] where:
        - 0.0: No correlation (multiple addresses unrelated)
        - 1.0: Perfect correlation (multiple addresses identical behavior)

    Raises:
        ValueError: If traffic_records is empty.

    Example:
        >>> traffic = [NetworkTraffic(...), NetworkTraffic(...)]
        >>> score = calculate_correlation_score(traffic)
        >>> print(f"Correlation score: {score:.2f}")
    """
    if not traffic_records:
        raise ValueError("traffic_records must not be empty")

    # Implementation...
    return 0.75
```

#### Error Handling

```python
# ✅ Correct: Specific exceptions with context
async def get_session(session_id: str) -> Optional[Session]:
    """
    Retrieve session by ID.

    Args:
        session_id: Session UUID

    Returns:
        Session if found, None otherwise

    Raises:
        DatabaseError: If database query fails
        ValidationError: If session_id invalid
    """
    try:
        if not is_valid_uuid(session_id):
            raise ValidationError(f"Invalid UUID: {session_id}")

        session = await db.getSession(session_id)
        return session

    except DatabaseError as e:
        logger.error(f"Database error retrieving session {session_id}: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error retrieving session {session_id}")
        raise DatabaseError(f"Failed to retrieve session: {e}")

# ❌ Wrong: Broad exception catching
async def get_session(session_id: str):
    try:
        return db.getSession(session_id)
    except:
        logger.error("Error")
        return None
```

#### Logging

```python
import structlog

logger = structlog.get_logger()

# ✅ Correct: Structured logging with context
logger.info(
    "session_created",
    session_id=session_id,
    wallet_type=wallet_type,
    rpc_provider=rpc_provider
)

logger.error(
    "traffic_capture_failed",
    session_id=session_id,
    error=str(e),
    error_type=type(e).__name__
)

logger.warning(
    "high_risk_assessment",
    session_id=session_id,
    overall_score=assessment.overall_score,
    risk_level=assessment.risk_level
)
```

#### Database Queries (SQLAlchemy Async)

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# ✅ Correct: Async session with proper error handling
async def get_leak_events_by_session(
    db: AsyncSession,
    session_id: str,
    leak_type: Optional[LeakType] = None,
    min_confidence: float = 0.0
) -> List[PrivacyLeakEvent]:
    """
    Query leak events for a session with optional filters.

    Args:
        db: Async database session
        session_id: Session UUID
        leak_type: Optional filter by leak type
        min_confidence: Minimum confidence threshold

    Returns:
        List of PrivacyLeakEvent objects
    """
    try:
        query = select(PrivacyLeakEvent).where(
            PrivacyLeakEvent.session_id == session_id,
            PrivacyLeakEvent.confidence >= min_confidence
        )

        if leak_type:
            query = query.where(PrivacyLeakEvent.leak_type == leak_type)

        result = await db.execute(query)
        return result.scalars().all()

    except Exception as e:
        logger.error(
            "database_query_failed",
            operation="get_leak_events_by_session",
            session_id=session_id,
            error=str(e)
        )
        raise DatabaseError(f"Query failed: {e}")
```

#### Configuration Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    # Database
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_database: str = "privacy_leakage"

    # Encryption
    encryption_key: str  # AES-256 encryption key (32 bytes, Base64 encoded)

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    rate_limit_per_minute: int = 100

    # Logging
    log_level: str = "INFO"

# Usage
settings = Settings()

# ❌ Wrong: Hardcoded values
DB_HOST = "localhost"
DB_PASSWORD = "password123"  # Never hardcode secrets!
```

---

### 12.2 Security Guidelines

#### Input Validation

```python
from pydantic import BaseModel, Field, validator

class SessionCreateRequest(BaseModel):
    """Request model for creating a session."""

    wallet_type: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Wallet application name"
    )
    rpc_provider: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="RPC provider name/endpoint"
    )

    @validator('wallet_type', 'rpc_provider')
    def sanitize_string(cls, v):
        """Sanitize string input to prevent injection."""
        # Only allow alphanumeric, spaces, and common punctuation
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-\.]+$', v):
            raise ValueError("Invalid characters in input")
        return v.strip()
```

#### Hashing and Anonymization

```python
import hashlib
from typing import Optional

def hash_wallet_address(address: str) -> str:
    """
    Hash wallet address for anonymized storage.

    Args:
        address: Raw wallet address (e.g., '0x1234...')

    Returns:
        Truncated hash (8 characters)
    """
    # SHA-256 hash
    full_hash = hashlib.sha256(address.encode()).hexdigest()

    # Truncate to 8 characters for display (not reversible)
    return full_hash[:8]

def anonymize_ip_address(ip: str) -> Optional[str]:
    """
    Anonymize IP address by removing last octet.

    Args:
        ip: IP address string

    Returns:
        Anonymized IP (e.g., '192.168.1.0') or None if invalid
    """
    parts = ip.split('.')
    if len(parts) != 4:
        return None

    try:
        # Validate each octet
        [int(p) for p in parts]
        # Replace last octet with 0
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0"
    except ValueError:
        return None
```

#### Data Encryption

```python
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

class EncryptionService:
    """Service for encrypting data at rest."""

    def __init__(self, encryption_key: str):
        """
        Initialize encryption service.

        Args:
            encryption_key: Base64-encoded 32-byte encryption key
        """
        self.cipher = Fernet(encryption_key.encode())

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data."""
        return self.cipher.encrypt(data)

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data)
```

---

### 12.3 Testing Standards

#### Unit Tests

```python
import pytest
from app.services.risk_assessment import calculate_overall_risk_score

class TestRiskAssessment:
    """Unit tests for risk assessment calculations."""

    @pytest.mark.parametrize(
        "entropy, uniqueness, correlation, temporal, expected",
        [
            (0.0, 0.0, 0.0, 0.0, 0),    # Minimum
            (1.0, 1.0, 1.0, 1.0, 100),  # Maximum
            (0.5, 0.5, 0.5, 0.5, 50),   # Midpoint
            (0.8, 0.2, 0.9, 0.3, 55),   # Weighted
        ]
    )
    def test_calculate_overall_score(
        self,
        entropy: float,
        uniqueness: float,
        correlation: float,
        temporal: float,
        expected: int
    ):
        """Test overall risk score calculation."""
        score = calculate_overall_risk_score(
            entropy_score=entropy,
            uniqueness_score=uniqueness,
            correlation_score=correlation,
            temporal_score=temporal
        )
        assert score == expected

    def test_score_bounds(self):
        """Test score is always within [0, 100]."""
        for _ in range(100):
            e, u, c, t = [np.random.random() for _ in range(4)]
            score = calculate_overall_risk_score(e, u, c, t)
            assert 0 <= score <= 100
```

#### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSessionAPI:
    """Integration tests for session API endpoints."""

    def test_create_session(self):
        """Test creating a new session."""
        response = client.post(
            "/api/v1/sessions",
            json={
                "wallet_type": "MetaMask",
                "rpc_provider": "Infura Mainnet"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["wallet_type"] == "MetaMask"

    def test_get_session_not_found(self):
        """Test retrieving non-existent session."""
        response = client.get("/api/v1/sessions/nonexistent-uuid")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"
```

---

### 12.4 Git Workflow Standards

#### Commit Messages (Conventional Commits)

```
✅ Correct:

feat(traffic): implement real-time packet capture with mitmproxy

Add TrafficCaptureService with support for HTTP, HTTPS, WebSocket.
Add session management and PCAP file encryption.

Closes #123

❌ Wrong:

fix bug
update code
stuff
```

#### Branch Naming

```
feature/traffic-capture-service
fix/detection-rule-validation
docs/update-api-spec
test/add-risk-assessment-tests
```

---

## 13. Validation and Experiments

### 13.1 Validation Experiments

#### Experiment 1: Address Linkability Measurement

**Objective**: Measure address linkage accuracy from RPC metadata.

**Methodology**:
1. Capture traffic from wallets with known address usage patterns
2. Analyze correlation scores for multi-address sessions
3. Validate against ground truth (known address ownership)

**Metrics**:
- Linkage success rate: Proportion of correctly linked addresses
- False positive rate: Incorrect linkages made
- Confidence interval accuracy: Compare reported CI to actual accuracy

**Success Criteria**:
- Quantify linkage success rate with 95% confidence intervals
- Identify specific behaviors that enable linkage

---

#### Experiment 2: Behavioral Fingerprinting

**Objective**: Evaluate distinguishability of user behavioral signatures.

**Methodology**:
1. Capture longitudinal traffic from distinct users
2. Calculate uniqueness scores across users
3. Measure overlap between user behavioral profiles

**Metrics**:
- Uniqueness score distribution across users
- Cross-user similarity distribution
- Temporal consistency of behavioral patterns

**Success Criteria**:
- Achieve > 70% distinguishability with confidence intervals
- Identify top features contributing to fingerprinting

---

#### Experiment 3: Risk Scoring Validation

**Objective**: Validate risk scoring against manual privacy assessments.

**Methodology**:
1. Manual privacy expert assessment of sample sessions
2. Automated risk scoring of same sessions
3. Correlation analysis between manual and automated scores

**Metrics**:
- Pearson correlation coefficient (target: r > 0.7)
- Mean absolute error (MAE) of scores
-Cohen's kappa for risk level classification

**Success Criteria**:
- Correlation r > 0.7 with statistical significance (p < 0.05)
- Risk level classification accuracy > 80%

---

### 13.2 Experimental Setup

| Component | Specification |
|-----------|---------------|
| Test Wallets | MetaMask, Trust Wallet, WalletConnect |
| RPC Providers | Infura, Alchemy, QuickNode, Ankr, Cloudflare |
| Network | Testnet (Goerli / Sepolia) |
| Capture Tool | mitmproxy with custom add-on |
| Data Duration | Minimum 7 days per experiment |
| Target Sample Size | 5,000+ RPC requests per wallet |

---

## 14. Technical Stack

### 14.1 Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.10+ |
| Web Framework | FastAPI | 0.104+ |
| ASGI Server | Uvicorn | 0.24+ |
| API Validation | Pydantic | 2.5+ |
| Settings | pydantic-settings | 2.1+ |
| Database ORM | SQLAlchemy | 2.0+ |
| Database Driver | mysql-connector-python | 8.0+ |
| Database Migrations | Alembic | 1.13+ |
| Network Analysis | scapy | 2.5+ |
| TLS Interception | mitmproxy | 10.1+ |
| Data Processing | pandas | 2.1+ |
| Numerical Computing | numpy | 1.26+ |
| HTTP Client | httpx | 0.25+ |
| JSON Parsing | orjson | 3.9+ |
| Environment Config | python-dotenv | 1.0+ |
| Testing | pytest | 7.4+ |
| Async Testing | pytest-asyncio | 0.21+ |
| Coverage | pytest-cov | 4.1+ |
| Logging | structlog | 23.0+ |
| Encryption | cryptography | 41.0+ |

### 14.2 Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | React | 18+ |
| Language | TypeScript | 5.3+ |
| Build Tool | Vite | 5.x |
| HTTP Client | axios | 1.x |
| Data Visualization | D3.js | 7+ |
| Charts | ECharts React | 6+ |
| UI Framework | TailwindCSS | 3.x |
| Testing | Jest | 29+ |
| Component Testing | React Testing Library | 14+ |

### 14.3 Infrastructure

| Component | Technology |
|-----------|-----------|
| Database | MySQL 8.0+ |
| Containerization | Docker |
| Container Orchestration | Docker Compose |
| Version Control | Git + GitHub |
| API Documentation | Swagger UI / ReDoc |

---

## 15. Success Metrics and Acceptance Criteria

### 15.1 Quantitative Metrics

| Metric | Target | Priority |
|--------|--------|----------|
| Traffic samples captured | ≥ 5,000 | Critical |
| Privacy leakage patterns | ≥ 15 | Critical |
| Detection rules implemented | ≥ 10 | Critical |
| Test coverage | > 70% | Critical |
| API uptime | > 99% | High |
| API response time (P95) | < 500ms | High |
| Detection rule precision | > 85% | High |
| Risk assessment correlation | r > 0.7 | High |


---

## 16. Deliverables

### 16.1 Software

- Backend source code (Python/FastAPI)
- Frontend source code (React/TypeScript)
- Database schema and migrations
- Docker configuration
- Test suite (> 70% coverage)

### 16.2 Documentation

- README (installation, quick start)
- API documentation (Swagger/ReDoc)
- Developer guide (architecture, coding standards)
- User manual (dashboard usage)

### 16.3 Research

- Initial Specification (this document)
- Experiment protocols and results
- Final research report with findings
- Validation analysis

### 16.4 Presentation

- Final presentation slides
- Demo video
- Live demonstration

---

---

---

## 17. Appendices

### 17.1 Glossary

| Term | Definition |
|------|------------|
| JSON-RPC | Remote Procedure Call format using JSON |
| TLS | Transport Layer Security encryption protocol |
| PEP 8 | Python style guide |
| API | Application Programming Interface |
| MySQL | Relational database management system |


---

**Document Version:** 2.0
**Date:** February 5, 2026
**Status:** Final Draft
