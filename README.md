# Wallet / RPC Privacy Leakage Measurement System
# 钱包与RPC隐私泄露测量系统

构建一个能够测量和量化区块链钱包（如MetaMask、WalletConnect）与RPC节点通信过程中隐私泄露程度的系统，通过实际网络通信分析和实验验证，识别攻击向量，评估隐私风险等级，并提供可操作的改进建议。

---

## 项目概述 (Project Overview)

### 核心功能 (Core Features)

1. **网络流量捕获与分析** (Network Traffic Capture & Analysis)
   - 支持模拟数据（开发）
   - 预留真实流量捕获（生产，使用mitmproxy）
   - 协议：HTTP/HTTPS, WebSocket

2. **隐私泄露检测与分类** (Privacy Leak Detection)
   - 10+ 基于YAML规则的检测规则
   - 分类：身份、资产、行为、位置
   - 置信度评分系统

3. **风险量化评估** (Risk Quantification)
   - 4维度指标：信息熵、唯一性、关联性、时效性
   - 风险评分（0-100）
   - 可操作的建议

4. **可视化分析** (Analytics & Reporting)
   - 统计摘要
   - 趋势分析
   - 分布统计

---

## 技术栈 (Technology Stack)

**后端**:
- Python 3.10+
- FastAPI 0.104+ (异步高性能 Web 框架)
- SQLAlchemy 2.0 (ORM, 异步)
- MySQL 8.0+ (结构化数据存储)
- aiomysql (MySQL(asyncio驱动))

**网络流量分析**:
- mitmproxy (TLS流量解密 - 生产环境)
- scapy (网络包捕获 - 预留)

**数据处理**:
- scikit-learn (机器学习基础)

**测试**:
- pytest, pytest-asyncio, pytest-cov

开发环境: Docker, Docker Compose

---

## 快速开始 (Quick Start)

### 前置要求 (Prerequisites)

- Python 3.10+
- MySQL 8.0+ 或 Docker
- Git

### 安装步骤 (Installation)

1. **克隆仓库**
```bash
git clone https://github.com/compass-rose/wallet-rpc-privacy.git
cd wallet-rpc-privacy
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **启动 MySQL (使用 Docker)**
```bash
docker-compose up -d mysql
```

4. **配置环境变量**
```bash
cp .env.example .env
```

5. **启动应用**
```bash
# 方法1: 使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 方法2: 使用 Docker (包含 MySQL)
docker-compose up
```

6. **访问 API 文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## 使用模式 (Usage Modes)

### 开发模式 (Mock Data)

使用模拟数据进行开发和测试：

```bash
# .env
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
```

无需额外配置即可使用。

### 生产模式 (Real Data Capture)

使用真实钱包流量进行分析：

```bash
# .env
TRAFFIC_PROVIDER=mitm
```

**详细配置步骤**请参考：[用户手册](docs/USER_MANUAL.md#using-real-data-capture-production)

---

## 项目结构 (Project Structure)

```
wallet-rpc-privacy/
├── app/                           # 主应用代码
│   ├── api/                       # API 路由
│   │   ├── deps.py                # 依赖注入
│   │   └── v1/                    # API v1 端点
│   │       ├── sessions.py        # 会话管理
│   │       ├── traffic.py         # 流量管理
│   │       ├── leaks.py           # 隐私泄露事件
│   │       ├── assessments.py     # 风险评估
│   │       ├── analytics.py       # 分析统计
│   │       └── rules.py           # 检测规则
│   ├── core/                      # 配置和工具
│   │   ├── config.py              # 应用配置
│   │   ├── database.py            # 数据库连接
│   │   └── logging.py             # 日志配置
│   ├── models/                    # 数据模型
│   │   ├── base.py                # 基础模型
│   │   ├── session.py             # 会话模型
│   │   ├── traffic.py             # 流量模型
│   │   ├── detection.py           # 检测模型
│   │   ├── risk.py                # 风险模型
│   │   └── common.py              # Pydantic 模型
│   ├── services/                  # 业务逻辑
│   │   ├── traffic/               # 流量捕获服务
│   │   │   ├── base.py            # 提供者接口
│   │   │   ├── mock_provider.py   # 模拟提供者
│   │   │   ├── mitm_provider.py   # Mitm提供者（预留）
│   │   │   └── factory.py         # 工厂函数
│   │   ├── detection/             # 隐私检测服务
│   │   │   ├── loader.py          # 规则加载器
│   │   │   └── engine.py          # 规则引擎
│   │   ├── risk/                  # 风险评估服务
│   │   │   ├── metrics.py         # 指标计算
│   │   │   ├── recommendations.py  # 推荐生成
│   │   │   └── assessment.py      # 评估计算
│   │   └── analytics.py           # 分析服务
│   ├── config/                    # 配置文件
│   │   └── rules/                 # 检测规则 (YAML)
│   ├── main.py                    # 应用入口
│   └── __init__.py
├── tests/                         # 测试代码
│   ├── unit/                      # 单元测试
│   │   ├── test_config.py
│   │   ├── test_privacy_utils.py
│   │   ├── test_traffic_service.py
│   │   ├── test_risk_assessment.py
│   │   └── test_detection_engine.py
│   └── integration/               # 集成测试
│       └── test_api.py
├── docs/                          # 文档
│   ├── plans/                     # 实施计划
│   ├── Initial-Specification.md
│   ├── Wallet-RPC-Privacy-Project-Summary.md
│   ├── threat-model.md
│   └── USER_MANUAL.md             # 用户手册 (完整配置指南)
├── docker-compose.yml             # Docker 编排
├── Dockerfile                     # Docker 镜像
├── requirements.txt               # Python 依赖
├── pytest.ini                     # pytest 配置
├── run_tests.py                   # 测试运行脚本
├── README.md                      # 本文件
└── AGENTS.md                      # Agent 行为规范
```

---

## 核心API端点 (Core API Endpoints)

### 会话管理 (Session Management)
- `POST /api/v1/sessions` - 创建新会话
- `GET /api/v1/sessions/{id}` - 获取会话详情
- `GET /api/v1/sessions` - 列出会话（支持筛选、分页）
- `DELETE /api/v1/sessions/{id}` - 删除会话

### 流量管理 (Traffic Management)
- `POST /api/v1/sessions/{id}/traffic/start` - 开始流量捕获
- `POST /api/v1/sessions/{id}/traffic/stop` - 停止流量捕获
- `GET /api/v1/sessions/{id}/traffic` - 获取流量记录

### 隐私泄露 (Privacy Leaks)
- `GET /api/v1/sessions/{id}/leaks` - 获取会话的泄露事件
- `GET /api/v1/leaks` - 列出所有泄露事件

### 风险评估 (Risk Assessment)
- `POST /api/v1/sessions/{id}/assess` - 运行风险评估
- `GET /api/v1/sessions/{id}/assessment` - 获取风险评估结果

### 分析统计 (Analytics)
- `GET /api/v1/analytics/summary` - 摘要统计
- `GET /api/v1/analytics/trends` - 趋势分析
- `GET /api/v1/analytics/leaks/distribution` - 泄露分布
- `GET /api/v1/analytics/risk/distribution` - 风险分布

---

## 运行测试 (Running Tests)

### 运行所有测试
```bash
# 方法1: 使用测试脚本
python3 run_tests.py

# 方法2: 直接使用 pytest
pytest tests/ -v --cov=app --cov-report=html
```

### 查看覆盖率报告
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 测试要求
- 单元测试覆盖率：> 70%
- 所有API端点都有集成测试
- 所有检测规则都有单元测试

---

## 配置详解 (Configuration Details)

### 环境变量

```bash
# 数据库配置
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/wallet_privacy

# 流量提供者 (mock: 模拟, mitm: 真实流量)
TRAFFIC_PROVIDER=mock

# 模拟流量配置
MOCK_TRAFFIC_COUNT=500

# 日志级别
LOG_LEVEL=INFO

# CORS 配置
CORS_ORIGINS=*
```

### 切换到真实数据捕获

请参考完整的用户手册获取详细步骤：

[docs/USER_MANUAL.md - Real Data Capture Guide](docs/USER_MANUAL.md#using-real-data-capture-production)

---

## 文档 (Documentation)

- **[用户手册 (User Manual)](docs/USER_MANUAL.md)** - 完整使用指南，包括真实数据捕获配置
- **[系统架构设计](docs/plans/2026-02-26-backend-architecture.md)** - 详细架构文档
- **[实施计划](docs/plans/2026-02-26-implementation-plan.md)** - 实施任务清单
- **[需求规格](docs/Initial-Specification.md)** - 完整需求文档
- **[威胁模型](docs/threat-model.md)** - 威胁分析

---

## 隐私承诺 (Privacy Commitment)

本系统严格保护用户隐私：

1. **敏感数据匿名化**: 所有地址、IP、交易哈希在存储前都会被哈希化
2. **无日志泄露**: 不记录原始地址、私钥或交易内容
3. **会话隔离**: 每个会话使用加密随机UUID
4. **本地分析**: 所有数据处理在本地进行，不上传外部服务器
5. **加密存储**: PCAP文件在生产环境中使用AES-256加密

---

## 许可证 (License)

MIT License

---

## 联系方式 (Contact)

项目主页: https://github.com/compass-rose/wallet-rpc-privacy

---

**注意**: 本项目遵循 AGENTS.md 中定义的所有开发规范和隐私要求。
