# Milestone 1 Individual Evidence Package
## Section 1: Summary

During Milestone 1, my primary role as Project Architect was to establish the overall system architecture, technical framework, and detailed specifications for the Wallet / RPC Privacy Leakage Measurement System. I successfully delivered a comprehensive Initial Specification document that forms the foundation for all subsequent development work. The document defines the complete technical vision, from system architecture through API specifications, development standards, and validation methodology. I also established the project's version control infrastructure and worked with the team to align on development standards and AI usage guidelines.

Key achievements include designing a four-layered architecture (Frontend, API Gateway, Business Logic, Data Layer), selecting an appropriate technology stack (Python/FastAPI backend, MySQL database, React/TypeScript frontend), defining 60+ functional and non-functional requirements, specifying complete data models with Pydantic validation, implementing a comprehensive API specification with 20+ endpoints, and establishing detailed development standards including coding guidelines, security practices, and testing requirements.

---

## Section 2: Personal Contributions

### 2.1 System Architecture Design
- **Four-Layer Architecture**: Designed the system with Frontend (React), API Gateway (FastAPI), Business Logic (Traffic Capture, Privacy Detection, Risk Assessment, Analytics), and Data Layer (MySQL, File Storage, Rules Engine, Metrics Engine)
- **Data Flow Definition**: Established clear data flow from packet capture through parsing, anonymization, detection, scoring, and visualization
- **Service Decomposition**: Separated concerns into distinct services with well-defined responsibilities and interactions

### 2.2 Technology Stack Selection
- **Backend Framework**: Chose FastAPI 0.104+ for async performance, automatic API documentation, and Pydantic v2 integration
- **Database**: Selected MySQL 8.0+ for ACID compliance and mature tooling.
- **Network Analysis**: Evaluated mitmproxy, scapy, and TLS interception tools; designed traffic capture pipeline

### 2.3 API Interface Specifications
- **RESTful Design**: Defined complete API following REST conventions with versioned endpoints (/api/v1/)
- **Standardized Responses**: Created consistent success/error response formats with metadata
- **20+ Endpoints**: Specified CRUD operations for sessions, traffic, leaks, assessments, rules, analytics, reports, and configuration
- **Documentation**: Designed auto-generated Swagger/ReDoc documentation structure
- **Rate Limiting**: Established 100 requests/minute per IP address limit

### 2.4 Data Models and Database Schema
- **6 Core Entities**: Sessions, NetworkTraffic, PrivacyLeakEvent, RiskAssessment, DetectionRule, Configuration
- **MySQL-Specific Schema**: CHAR(36) for UUIDs, proper indexes for performance, foreign key constraints
- **Pydantic Models**: Defined request/response models with validation, constraints, and type hints
- **Entity Relationships**: Established one-to-many relationships with cascade deletes where appropriate

### 2.5 GitHub Repository Setup
- **Repository Structure**: Created app/ with api/, core/, models/, services/ organized by layer
- **Initial Codebase**: Set up FastAPI main.py with health endpoints, core __init__.py modules
- **Configuration**: Created requirements.txt with 23 dependencies, environment variables template
- **Documentation**: Initialized README.md with project overview, tech stack, and quick start guide

### 2.6 AI Agent Usage Guidelines
- **Established in AGENTS.md**: Defined project-specific rules for AI collaboration

## Section 3: Final Deliverables

### 3.1 Initial Specification Document

**Document Location**: `/docs/Initial-Specification.md`

**Document Statistics**:
- Length: 2,536 lines (~24,000 words)
- 17 chapters covering all aspects of the system
- 60+ functional requirements
- 60+ non-functional requirements
- Complete data models with 6 entities
- 20+ API endpoints fully specified
- 10 core detection rules defined
- 4 core algorithms with Python implementations
- Comprehensive development standards

**Chapter Overview**:

1. **Executive Summary**: Project overview, key highlights, target metrics
2. **Problem Statement**: Background on RPC privacy risks, threat characterization, research gap
3. **Project Goals**: Primary objectives, stakeholder value, project differentiators
4. **Scope and Boundaries**: In-scope components, out-of-scope items (ML excluded), assumptions
5. **Threat Model**: Honest-but-curious adversary, capabilities, limitations, goals
6. **System Architecture**: Four-layer design, component responsibilities, data flow
7. **Functional Requirements**: 60+ detailed requirements across 6 categories
8. **Non-Functional Requirements**: Performance, security, privacy, testing standards
9. **Data Models**: 6 MySQL tables with full schema, Pydantic models with validation
10. **API Specifications**: Complete REST API with request/response examples
11. **Core Algorithms**: Entropy, uniqueness, correlation, temporal score implementations
12. **Development Standards**: Python standards, security guidelines, testing framework
13. **Validation Experiments**: 3 experimental designs (Address Linkability, Behavioral Fingerprinting, Risk Scoring)
14. **Technical Stack**: Complete technology catalog with versions
15. **Success Metrics**: Quantitative targets and acceptance criteria
16. **Deliverables**: Software, documentation, research, presentation artifacts
17. **Appendices**: Glossary of terms

---

### 3.2 Project Repository

**Repository**: https://github.com/compass-rose/wallet-rpc-privacy

**Initial Structure**: Established with:
- `app/main.py`: FastAPI application with health check endpoints
- `app/api/`: API route module
- `app/core/`: Configuration module
- `app/models/`: Data model module
- `app/services/`: Business logic module
- `docs/Initial-Specification.md`: Complete specification document
- `README.md`: Project overview
- `requirements.txt`: 23 dependencies listed
- `AGENTS.md`: AI collaboration guidelines

![image-20260209101713136](/Users/shenghao/Library/Application Support/typora-user-images/image-20260209101713136.png)

---

### 3.3 Development Standards Documentation

**Included in Initial Specification Chapter 12**:

- **Python Development Standards**:
  - PEP 8 compliance
  - Type annotations for all functions
  - Google-style docstrings with examples
  - Error handling patterns with specific exceptions
  - Structured logging
  - Async database query patterns

- **Security Guidelines**:
  - Input validation with Pydantic
  - Hashing/anonymization functions
  - AES-256 encryption for data at rest

- **Testing Standards**:
  - Unit test structure with pytest
  - Integration test examples
  - Parameterized tests

- **Git Workflow**:
  - Conventional Commits format
  - Branch naming conventions

---

## Section 4: AI Usage Record

### 4.1 AI Suggestions Accepted

**Suggestion**: Use FastAPI instead of Django or Flask for the backend framework

**AI Reasoning**: FastAPI provides native async/await support, automatic API documentation with Swagger/ReDoc, built-in request validation with Pydantic, and superior performance (on par with Node.js and Go). It also follows modern Python type hints and is well-suited for the asynchronous nature of network traffic capture and analysis.

**Decision**: **ACCEPTED**

**My Verification**:
- Reviewed FastAPI documentation for async capabilities
- Confirmed Pydantic v2 integration for robust validation
- Benchmarked basic async route performance
- Verified auto-generated Swagger docs work out-of-box
- Confirmed compatibility with required networking libraries (scapy, mitmproxy)

**Outcome**: Adopted FastAPI 0.104+ as outlined in Section 14.1. This enables scalable async traffic capture, automatically generated API docs, and type-safe request validation. The decision has been validated by the team and integrated into the development standards.

---

### 4.2 AI Suggestions Rejected

**Suggestion**: Use PostgreSQL with Redis caching instead of MySQL alone

**AI Reasoning**: PostgreSQL is more feature-rich with advanced indexing, JSONB support, full-text search, and extensions. Redis provides in-memory caching for frequently accessed data, improving API response times. This combination has been battle-tested in production at scale.

**Decision**: **REJECTED**

**My Analysis**:
- **Additional Complexity**: Adding Redis increases operational complexity—additional service to monitor, cache invalidation logic to implement, and distributed state management to handle
- **Team Learning Curve**: The team consists of 4 students with limited database experience. MySQL is simpler to administer and has more learning resources. PostgreSQL's advanced features would likely go unused while adding confusion
- **Project Scope**: This is a 10-week course project, not a production system at internet scale. MySQL's capabilities are more than sufficient for the target storage (100GB+) and concurrent operations (50 connections)
- **Cache Tradeoff**: Caching introduces complexity without clear benefit in this use case. Session analysis happens once per assessment and can be memoized in MySQL. Real-time dashboard updates can use HTTP polling which is sufficient for academic/development purposes
- **Maintenance Overhead**: Redis requires memory management, eviction policies, persistence configuration, and monitoring—all overhead that distracts from core privacy research objectives

**Outcome**: Selected MySQL 8.0+ alone as the primary data store (Section 14.3). This reduces system complexity, lowers the learning curve for the team, and focuses resources on core privacy analysis functionality rather than infrastructure optimization. The simpler architecture is more appropriate for a 10-week timeline and academic context.
