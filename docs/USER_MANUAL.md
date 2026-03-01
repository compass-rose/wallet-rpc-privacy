# Wallet / RPC Privacy Leakage Measurement System
## User Manual

---

**Version:** 1.0.0
**Last Updated:** 2026-02-26

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [System Architecture](#system-architecture)
4. [Configuration](#configuration)
5. [Using Mock Data (Development)](#using-mock-data-development)
6. [Using Real Data Capture (Production)](#using-real-data-capture-production)
7. [API Reference](#api-reference)
8. [Understanding Risk Assessments](#understanding-risk-assessments)
9. [Detection Rules](#detection-rules)
10. [Troubleshooting](#troubleshooting)
11. [FAQ](#faq)

---

## Introduction

The Wallet / RPC Privacy Leakage Measurement System is a research-driven tool that measures and quantifies privacy leakage risks in the communication between blockchain wallets (e.g., MetaMask, WalletConnect) and RPC providers.

### Key Features

- **Traffic Capture**: Capture and analyze real or simulated wallet-RPC traffic
- **Privacy Detection**: YAML-based rule engine with 10+ detection rules
- **Risk Assessment**: 4-dimensional scoring (entropy, uniqueness, correlation, temporal)
- **Analytics**: Comprehensive statistics and trend analysis
- **Flexible Deployment**: Switch easily between mock data (development) and real capture (production)

### Privacy Mission

This system helps identify privacy leaks WITHOUT compromising your actual privacy:
- All sensitive data is anonymized/hashed before storage
- No raw wallet addresses, private keys, or transaction hashes are logged
- Session IDs are cryptographic random UUIDs
- PCAP files are encrypted at rest (AES-256)

---

## Quick Start

### Prerequisites

- Python 3.10+
- MySQL 8.0+ or Docker
- Git

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/compass-rose/wallet-rpc-privacy.git
cd wallet-rpc-privacy
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Start MySQL using Docker**

```bash
docker-compose up -d mysql
```

This will start MySQL on port `localhost:3306` with:
- Database: `wallet_privacy`
- Username: `root`
- Password: `password`

4. **Configure environment**

```bash
cp .env.example .env
```

Edit `.env` if needed (defaults should work for local development).

5. **Start the application**

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m app.main

# Option 3: Using Docker (includes MySQL)
docker-compose up
```

6. **Access the API**

- API Root: http://localhost:8000
- Interactive Docs (Swagger): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

7. **Verify installation**

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "wallet-privacy-backend"
}
```

---

## System Architecture

### Layered Architecture

```
┌─────────────────────────────────────┐
│          API Layer (FastAPI)        │
│  - Request/Response validation       │
│  - Error handling, rate limiting      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Services Layer                │
│  ├── TrafficService (mock/mitm)     │
│  ├── DetectionService (rules)       │
│  ├── RiskService (4-dim metrics)    │
│  └── AnalyticsService               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│        Data Layer                   │
│  ├── Async SQLAlchemy 2.0           │
│  └── MySQL (metadata storage)       │
└─────────────────────────────────────┘
```

### Data Flow

1. **Create Session** → Generate unique session UUID
2. **Start Capture** → Provider starts capturing traffic (mock or real)
3. **Parse & Store** → Traffic records anonymized and stored in MySQL
4. **Privacy Detection** → YAML rules evaluated, leak events created
5. **Risk Assessment** → 4-dimensional metrics computed
6. **Analytics** → Statistics aggregated and returned

---

## Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database Configuration
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/wallet_privacy

# Traffic Provider (mock for dev, mitm for real)
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500

# Logging
LOG_LEVEL=INFO

# CORS (for frontend access)
CORS_ORIGINS=*
```

### Provider Configuration

The `TRAFFIC_PROVIDER` environment variable controls data source:

| Value | Provider | Use Case |
|-------|----------|----------|
| `mock` | MockTrafficProvider | Development, testing, demos |
| `mitm` | MitmTrafficProvider | Production, real wallet analysis |

---

## Using Mock Data (Development)

Mock data is perfect for:
- Development and testing
- Demonstrations without real wallets
- Understanding the system
- Running on machines without network access

### Creating a Test Session with Mock Data

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test",
    "status": "active"
  }
}
```

### Starting Mock Capture

```bash
SESSION_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X POST "http://localhost:8000/api/v1/sessions/$SESSION_ID/traffic/start?packet_count=100"
```

This generates 100 realistic JSON-RPC requests.

### Captured Traffic Preview

```bash
curl "http://localhost:8000/api/v1/sessions/$SESSION_ID/traffic?limit=5"
```

Response:
```json
{
  "success": true,
  "data": {
    "traffic": [
      {
        "id": "traffic-uuid",
        "rpc_method": "eth_getBalance",
        "request_timestamp": "2026-02-26T12:00:00Z",
        "response_time_ms": 125,
        "response_status": 200
      },
      ...
    ],
    "total": 100
  }
}
```

---

## Using Real Data Capture (Production)

### Overview

Real data capture uses **mitmproxy** to intercept and decrypt TLS traffic between your wallet and RPC provider. This provides actual privacy measurements from real usage.

### ⚠️ Security & Privacy Notice

- **Your private keys are NEVER exposed**: We only capture encrypted TLS traffic
- **Local analysis only**: Traffic analysis happens locally on your machine
- **Anonymization enforced**: All addresses are hashed before storage
- **Encrypted storage**: PCAP files encrypted with AES-256

### Prerequisites

1. **mitmproxy**: Already installed via requirements.txt
2. **Root/Admin access**: Required for SSL interception
3. **Wallet with custom RPC**: Must be configured to use mitmproxy as proxy

### Step-by-Step Setup

#### Step 1: Switch to Real Data Capture

Edit `.env`:
```bash
TRAFFIC_PROVIDER=mitm
```

#### Step 2: Generate and Install mitmproxy CA Certificate

**For macOS/Linux:**

```bash
# Generate mitmproxy CA certificate (if not exists)
mitmproxy-ca --install-cert-app
```

This command:
- Generates mitmproxy's CA certificate
- Installs it into your system's trusted certificate store
- Enables TLS interception

**For Windows:**

1. Run mitmproxy: `mitmproxy`
2. Follow on-screen instructions to install CA certificate
3. Trust the certificate in Windows settings

#### Step 3: Start Mitmproxy Traffic Capture

The MitmTrafficProvider is reserved for production. Here's how to integrate it:

```python
# The provider is already implemented in:
# app/services/traffic/mitm_provider.py

# It requires these production-only components:
# - CA certificate setup
# - PCAP encryption keys
# - mitmproxy addon configuration
```

**Current status**: The mitm provider is an interface. To enable real capture:

1. Install required system packages:
   - `libpcap-dev` (Ubuntu/Debian)
   - `libpcap` (macOS via Homebrew)
   - `Npcap` (Windows, included with Wireshark)

2. Configure wallet to use mitmproxy:
   - **MetaMask**: Settings → Networks → Custom RPC → Set HTTP proxy to `localhost:8080`
   - **WalletConnect**: Configure provider's proxy settings

3. Start capture (requires root):
   ```bash
   # Run mitmproxy in reverse proxy mode
   mitmproxy --mode reverse:https://mainnet.infura.io/v3/YOUR_API_KEY@mitm.it:8080 --insecure

   # Or use the integrated provider (once implemented)
   ```

#### Step 4: Production Deployment with Docker

For production deployment:

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: wallet_privacy
    volumes:
      - mysql_prod:/var/lib/mysql
      - ./backups:/backups

  app:
    build: .
    environment:
      - DATABASE_URL=mysql+aiomysql://root:${DB_PASSWORD}@mysql:3306/wallet_privacy
      - TRAFFIC_PROVIDER=mitm
      - PCAP_ENCRYPTION_KEY=${PCAP_KEY}
    volumes:
      - ./pcap_captures:/data/captures
      - ./certs:/app/certs
    depends_on:
      - mysql

volumes:
  mysql_prod:
```

```bash
# Deploy with production configuration
docker-compose -f docker-compose.production.yml up -d
```

### Verifying Real Data Capture

After configuring your wallet to use mitmproxy:

1. **Create session** as before
2. **Use wallet normally** - perform transactions, check balances, etc.
3. **View captured traffic**:
   ```bash
   curl "http://localhost:8000/api/v1/sessions/$SESSION_ID/traffic"
   ```

Captured traffic will show:
- **Real methods** you actually called
- **Actual timestamps** of your interactions
- **Real response times** from your RPC provider

### Switching Between Mock and Real Data

No code changes needed - just update `.env`:

```bash
# Development (fast, no setup required)
TRAFFIC_PROVIDER=mock

# Production (real traffic analysis)
TRAFFIC_PROVIDER=mitm
```

Then restart the application:
```bash
# Stop and restart
pkill -f "uvicorn app.main:app"
python -m app.main
```

---

## API Reference

All endpoints follow REST conventions and return standardized responses.

### Base URL
```
http://localhost:8000/api/v1
```

### Standard Response Format

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "request_id": "uuid",
    "timestamp": "2026-02-26T12:00:00Z"
  }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource not found"
  },
  "metadata": { ... }
}
```

### Session Management

#### Create Session
```http
POST /api/v1/sessions
Content-Type: application/json

{
  "wallet_type": "MetaMask",
  "rpc_provider": "https://mainnet.infura.io/v3/test"
}
```

#### Get Session
```http
GET /api/v1/sessions/{session_id}
```

#### List Sessions
```http
GET /api/v1/sessions?skip=0&limit=50&wallet_type=MetaMask
```

#### Delete Session
```http
DELETE /api/v1/sessions/{session_id}
```

### Traffic Management

#### Start Capture
```http
POST /api/v1/sessions/{session_id}/traffic/start?packet_count=500
```

#### Stop Capture
```http
POST /api/v1/sessions/{session_id}/traffic/stop
```

#### Get Traffic
```http
GET /api/v1/sessions/{session_id}/traffic?method=POST&limit=100&offset=0
```

### Privacy Leaks

#### Get Session Leaks
```http
GET /api/v1/sessions/{session_id}/leaks?leak_type=identity&min_confidence=0.5
```

#### List All Leaks
```http
GET /api/v1/leaks?leak_type=asset&skip=0&limit=50
```

### Risk Assessment

#### Run Assessment
```http
POST /api/v1/sessions/{session_id}/assess
```

#### Get Assessment
```http
GET /api/v1/sessions/{session_id}/assessment
```

#### List Assessments
```http
GET /api/v1/assessments?risk_level=high&skip=0&limit=50
```

### Analytics

#### Summary Statistics
```http
GET /api/v1/analytics/summary
```

Returns:
```json
{
  "total_sessions": 42,
  "total_traffic": 15847,
  "total_leaks": 134,
  "average_risk_score": 45.7,
  "sessions_by_status": {
    "active": 5,
    "completed": 35,
    "failed": 2
  }
}
```

#### Trends
```http
GET /api/v1/analytics/trends?days=7
```

#### Leak Distribution
```http
GET /api/v1/analytics/leaks/distribution
```

#### Risk Distribution
```http
GET /api/v1/analytics/risk/distribution
```

#### Method Frequencies
```http
GET /api/v1/analytics/methods/frequency?limit=10
```

#### Top Risk Sessions
```http
GET /api/v1/analytics/sessions/top-risk?limit=10
```

#### Response Time Statistics
```http
GET /api/v1/analytics/response-times
```

### Detection Rules

#### List Rules
```http
GET /api/v1/rules?category=identity&enabled_only=true
```

#### Get Rules Summary
```http
GET /api/v1/rules/summary
```

#### Get Rule Details
```http
GET /api/v1/rules/{rule_id}
```

---

## Understanding Risk Assessments

### 4-Dimensional Scoring

Our privacy risk assessment uses 4 complementary metrics:

| Dimension | Range | Interpretation |
|-----------|-------|---------------|
| **Entropy** | 0.0-1.0 | Method diversity. Higher = more distinct methods = better privacy |
| **Uniqueness** | 0.0-1.0 | How distinct your behavior is vs. baseline. Lower = better (blends in) |
| **Correlation** | 0.0-1.0 | Address linkability. Lower = less correlation = better privacy |
| **Temporal** | 0.0-1.0 | Timing patterns. Lower = less predictable = better privacy |

### Overall Risk Score

**Calculation:**
```
overall_score = (
    0.25 * entropy_score +
    0.25 * uniqueness_score +
    0.25 * correlation_score +
    0.25 * temporal_score
) * 100
```

**Classification:**

| Score Range | Risk Level | Meaning |
|-------------|------------|---------|
| 0-30 | LOW | Minimal privacy leakage |
| 31-50 | MEDIUM | Moderate privacy concerns |
| 51-70 | HIGH | Significant privacy risks detected |
| 71-100 | CRITICAL | Severe privacy leakage - immediate attention needed |

### Example Assessment

**Request:**
```bash
curl -X POST http://localhost:8000/api/v1/sessions/$SESSION_ID/assess
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "assessment-uuid",
    "overall_score": 67,
    "risk_level": "HIGH",
    "entropy_score": 0.35,
    "uniqueness_score": 0.72,
    "correlation_score": 0.65,
    "temporal_score": 0.45,
    "confidence": 0.87,
    "confidence_interval_low": 0.79,
    "confidence_interval_high": 0.95,
    "recommendations": [
      "Use address rotation: generate fresh addresses for new sessions",
      "Separate activities: use different addresses for different transaction types",
      "Add random timing jitter between requests to obfuscate patterns"
    ],
    "assessed_at": "2026-02-26T12:00:00Z"
  }
}
```

### Interpreting Recommendations

The system generates actionable recommendations based on your risk scores:

| Metric Issue | Recommendation |
|-------------|----------------|
| Low entropy | "Increase request method diversity to reduce predictability" |
| High correlation | "Use address rotation: generate fresh addresses" |
| High temporal score | "Add random timing jitter between requests" |
| High uniqueness | "Use common DApps to blend in with typical users" |

---

## Detection Rules

### Rule Categories

1. **IDENTITY** - Rules detecting user identity linkability
2. **ASSET** - Rules inferring asset holdings and transfers
3. **BEHAVIOR** - Rules identifying behavioral patterns
4. **LOCATION** - Rules inferring location and timezone

### 10+ Core Rules

#### Identity Rules (3)

1. **DR-ID-1: Address Reuse Detection**
   - Detects frequent queries to same address across sessions

2. **DR-ID-2: Address Correlation**
   - Identifies multiple addresses with correlated behavior

3. **DR-ID-3: Account Discovery**
   - Detects enumeration of account indices (0, 1, 2...)

#### Asset Rules (2)

4. **DR-AS-1: Asset Holding Inference**
   - Infers holdings from balance queries

5. **DR-AS-2: Transfer Signature Detection**
   - Identifies transfer patterns from nonce/gas data

#### Behavior Rules (4)

6. **DR-BE-1: DApp Usage Pattern**
   - Detects DApp-specific call sequences (e.g., Uniswap)

7. **DR-BE-2: Bot Behavior Detection**
   - Identifies automated bot timing patterns

8. **DR-BE-3: Active Session Inference**
   - Detects active vs idle periods

9. **DR-BE-4: High Frequency Activity**
   - Identifies unusually high request rates

#### Location Rules (2)

10. **DR-LO-1: Timezone Inference**
    - Infers user timezone from activity patterns

11. **DR-LO-2: Network Fingerprinting**
    - Detects consistent network-level signatures

### Listing Rules

```bash
# Get all rules
curl http://localhost:8000/api/v1/rules

# Get rules summary
curl http://localhost:8000/api/v1/rules/summary

# Get specific rule
curl http://localhost:8000/api/v1/rules/dr-id-1
```

### Custom Rules

Rules are defined as YAML files in `app/config/rules/{category}/`. To add a custom rule:

1. Create a new YAML file:
   ```yaml
   rule_id: "custom-001"
   name: "My Custom Rule"
   category: "IDENTITY"
   priority: "MEDIUM"
   enabled: true
   description: "My custom detection logic"
   version: 1

   conditions:
     - type: "method_pattern"
       methods: ["eth_getBalance"]
       min_frequency: 10

   actions:
     - type: "create_leak_event"
       leak_type: "IDENTITY"
       confidence_base: 0.75
   ```

2. Place in `app/config/rules/{category}/`

3. Restart application to load new rule

---

## Troubleshooting

### Database Issues

**Problem:** "Can't connect to MySQL server"

```bash
# Check if MySQL is running
docker ps | grep mysql

# Start MySQL
docker-compose up -d mysql

# Check logs
docker-compose logs mysql
```

**Problem:** "Table already exists"

```bash
# Drop and recreate tables (WARNING: deletes data)
docker-compose exec mysql mysql -uroot -ppassword wallet_privacy
DROP DATABASE wallet_privacy;
CREATE DATABASE wallet_privacy;
```

### Permission Issues

**Problem:** "Permission denied" on PCAP files

```bash
# PCAP directory needs correct permissions
chmod 755 ./pcap_captures
sudo chown $USER:$USER ./pcap_captures
```

### Port Conflicts

**Problem:** "Address already in use" (port 8000)

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Import Errors

**Problem:** "Module not found"

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python version (requires 3.10+)
python --version
```

### Mitmproxy Issues

**Problem:** "SSL certificate error"

1. Regenerate certificate:
   ```bash
   mitmproxy --mode reverse:https://example.com@8080 --insecure
   ```

2. Install certificate system-wide:
   - macOS: `mitmproxy-ca --install-cert-app`
   - Linux: `mitmproxy-ca --install-cert-util`
   - Windows: Manual trust in certificate manager

### Debugging Mode

Enable detailed logging:

```bash
# .env
LOG_LEVEL=DEBUG

# Restart application
```

View all logs in console output.

---

## FAQ

### Q: Can I use this without revealing my actual transactions?

**A:** Yes! The system is designed for privacy:
- Only metadata is captured (methods, timestamps, sizes)
- No transaction content, payloads, or private keys
- All addresses are hashed before storage
- Analysis happens locally on your machine

### Q: How do I switch from mock to real data?

**A:** Just change one line in `.env`:
```bash
# From:
TRAFFIC_PROVIDER=mock

# To:
TRAFFIC_PROVIDER=mitm
```

Then restart the application.

### Q: Will using this slow down my RPC calls?

**A:** Minimal impact with mock data. With mitmproxy:
- ~10-100ms overhead per request (TLS decryption)
- Only applies when capture is active
- Similar to using any proxy

### Q: Can I analyze historical traffic?

**A:** Not directly. The system is designed for real-time capture. To analyze historical PCAPs:
1. Replay PCAP through mitmproxy
2. Or extend the MitmTrafficProvider to parse existing PCAPs

### Q: How accurate is the risk scoring?

**A:** The scoring is:
- **Quantitative**: Uses mathematically-defined metrics (Shannon entropy, Jaccard similarity, etc.)
- **Compared to baseline**: Scores are relative to typical user behavior
- **Confidence intervals**: Each score includes 95% CI bounds

The system is designed for **comparative** analysis (e.g., "Session A is riskier than Session B"), not absolute statements.

### Q: Can I use this with custom RPC providers?

**A:** Yes! Specify any RPC endpoint when creating a session:
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MyWallet",
    "rpc_provider": "https://my-custom-rpc.com/endpoint"
  }'
```

### Q: What happens to my captured data?

**A:** All data is stored locally in MySQL:
- No data is sent to external servers
- You can delete sessions anytime
- PCAP files are encrypted at rest (production mode)

### Q: Can I export the results?

**A:** Yes, via API:
```bash
# Export all traffic for a session
curl http://localhost:8000/api/v1/sessions/$SESSION_ID/traffic > traffic.json

# Export assessment
curl http://localhost:8000/api/v1/sessions/$SESSION_ID/assessment > assessment.json
```

### Q: How do I reset the system?

**A:** Delete database and start fresh:
```bash
# Stop application
docker-compose down

# Delete MySQL volume
docker volume rm wallet-rpc-privacy_mysql_data

# Restart
docker-compose up -d
```

---

## Getting Help

### Resources

- **Documentation**: `/docs` directory
- **API Docs**: http://localhost:8000/docs
- **Source Code**: https://github.com/compass-rose/wallet-rpc-privacy

### Reporting Issues

When reporting issues, include:
1. Python version (`python --version`)
2. Full error message or traceback
3. Steps to reproduce
4. Your `.env` configuration (sensitive info redacted)

---

**End of User Manual**

© 2026 Wallet / RPC Privacy Leakage Measurement Project
