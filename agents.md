# Agents.md - Wallet RPC Privacy Project

This file serves as a persistent behavioral memory system for OpenCode agents working on this project.

## Project-Specific Constraints

### Architecture & Design

RULE 1: **Follow FastAPI Async Patterns**
- All API endpoints must use `async def` to maximize performance
- Database operations must use async SQLAlchemy with `async_sessionmaker`
- Avoid blocking I/O in endpoints - delegate to background tasks if needed

RULE 2: **Privacy-First Development**
- All captured network traffic must be anonymized before storage
- Never log or store raw wallet addresses, private keys, or transaction hashes
- All user sessions must be identified by random UUIDs, not traceable identifiers

RULE 3: **Type Safety is Non-Negotiable**
- Use Pydantic v2 models for all request/response validation
- Never use `Any`, `Optional[Any]`, or type hints that bypass validation
- All database models must use SQLAlchemy 2.0 style with proper type annotations

### Code Organization

RULE 4: **Layered Architecture Strict Separation**
- `app/api/` - HTTP routes only, no business logic
- `app/services/` - Business logic only, no HTTP concerns
- `app/models/` - Data models only (Pydantic + SQLAlchemy)
- `app/core/` - Configuration and utilities only

VIOLATION: Putting business logic in API routers or HTTP concerns in services

### Data Handling

RULE 5: **Network Traffic Storage Protocol**
1. Raw packets stored in filesystem (encrypted at rest)
2. Structured metadata in PostgreSQL
3. PII must be hashed before database insertion
4. Session identifiers must be cryptographic random UUIDs

RULE 6: **Risk Assessment Scoring**
- Overall scores must be integers 0-100
- Sub-scores (entropy, uniqueness, correlation, temporal) must be floats 0.0-1.0
- All scores must include confidence intervals
- Never return NaN or infinite values to API clients

### Testing & Quality

RULE 7: **Test Coverage Requirements**
- All API endpoints must have integration tests
- All privacy detection rules must have unit tests with known leak samples
- ML models must have accuracy/bias tests before deployment
- Minimum 70% code coverage required for PRs

RULE 8: **Error Handling Standards**
- Use FastAPI's exception handlers for consistent error responses
- Never expose internal error details to API clients
- Log all errors with structured JSON format
- All 4xx/5xx responses must have `error_code` and `message` fields

### Performance Constraints

RULE 9: **Response Time Limits**
- API endpoints: < 500ms P95
- Health check: < 50ms P99
- Real-time traffic ingestion: < 100ms per packet
- Risk assessment: < 2s for single session analysis

RULE 10: **Memory Usage**
- Traffic capture buffer: max 1GB
- Session analysis: max 500MB per concurrent session
- Total process: max 2GB per worker

### Security Rules

RULE 11: **Input Validation**
- Never trust client-provided IP addresses or timestamps
- Validate all JSON-RPC method calls against allowed whitelist
- Sanitize all strings before database insertion
- Rate limit all API endpoints (default: 100 requests/minute)

RULE 12: **TLS & Encryption**
- All API endpoints must enforce HTTPS in production
- Database connections must use TLS
- Stored packets must be encrypted at rest (AES-256)
- Sensitive configuration must use environment variables

## Common Mistakes & Prevention

### Mistake 1: Sync Database Calls in Async Context
WRONG:
```python
result = db.query(User).filter(User.id == user_id).first()
```

CORRECT:
```python
result = await session.execute(select(User).where(User.id == user_id))
```

### Mistake 2: Exposing Raw Addresses in Logs
WRONG:
```python
logger.info(f"Analyzing wallet {wallet_address}")
```

CORRECT:
```python
hashed_addr = hashlib.sha256(wallet_address.encode()).hexdigest()[:8]
logger.info(f"Analyzing wallet {hashed_addr}...")
```

### Mistake 3: Skipping Confidence Scoring
WRONG:
```python
return {"risk_level": "high"}
```

CORRECT:
```python
return {
    "risk_level": "high",
    "confidence": 0.87,
    "confidence_interval": [0.82, 0.92]
}
```

### Mistake 4: Blocking Operations in API Routes
WRONG:
```python
@app.post("/analyze")
def analyze_traffic(traffic: TrafficData):
    heavy_computation(traffic)  # Blocks event loop!
    return {"result": "done"}
```

CORRECT:
```python
@app.post("/analyze")
async def analyze_traffic(traffic: TrafficData):
    result = await background_task_queue.enqueue(heavy_computation, traffic)
    return {"task_id": result.id}
```

### Mistake 5: Missing Type Annotations
WRONG:
```python
def calculate_risk(leak_events):
    # ...
```

CORRECT:
```python
def calculate_risk(leak_events: List[PrivacyLeakEvent]) -> RiskAssessment:
    # ...
```

## Before Any Output

Agents working on this project must verify:

1. [ ] Does this change violate any RULE above?
2. [ ] Are all types properly annotated with Pydantic v2?
3. [ ] Is sensitive data properly anonymized or hashed?
4. [ ] Are async operations truly non-blocking?
5. [ ] Are error messages consistent and non-exposing?
6. [ ] Is performance within defined limits?
7. [ ] Are tests included for new functionality?
8. [ ] Does this follow the layered architecture separation?

## Git Commit Rules (Mandatory)

RULE 13: **Prohibit AI Attribution in Commits**
- NEVER add "Co-authored-by: Sisyphus" to any commit
- NEVER add "Co-authored-by: sisyphus-dev-ai" to any commit
- NEVER add "Ultraworked with [Sisyphus]" footer to any commit
- NEVER add any AI attribution whatsoever to commit messages
- All commits must be clean with NO AI co-authoring credit

**Violations:**
```bash
# WRONG - DON'T DO THIS
git commit -m "Add feature" -m "Co-authored-by: Sisyphus <...>"
git commit -m "Add feature" -m "Ultraworked with [Sisyphus](...)"

# CORRECT - DO THIS
git commit -m "Add feature"
```

**Reasoning**: The project should not contain AI attribution in its commit history. All commits must appear as human-authored work.

## Project-Specific Patterns

### API Response Standard
```python
return {
    "success": True,
    "data": {...},
    "metadata": {
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
}
```

### Error Response Standard
```python
return JSONResponse(
    status_code=400,
    content={
        "success": False,
        "error": {
            "code": "INVALID_INPUT",
            "message": "Wallet address format is invalid",
            "request_id": request_id
        },
        "metadata": {
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }
)
```

### Database Session Pattern
```python
async with async_session_maker() as session:
    try:
        # Database operations
        await session.commit()
    except Exception as e:
        await session.rollback()
        raise
```

---

Last updated: 2026-02-03
Project: Wallet / RPC Privacy Leakage Measurement
Repository: https://github.com/compass-rose/wallet-rpc-privacy
