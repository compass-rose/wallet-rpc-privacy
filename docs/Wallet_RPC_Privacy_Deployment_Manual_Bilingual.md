# Wallet / RPC Privacy Leakage Measurement System  
# Deployment Manual

**Version:** 2.0  
**Format Note:** This document presents the complete English version first, followed by the complete Chinese version.

---

## English Version

### 1. Purpose

This deployment manual explains how to install, configure, run, validate, and maintain the **Wallet / RPC Privacy Leakage Measurement System** in development and production-like environments. It consolidates the original deployment notes, quick-start guidance, real-traffic capture instructions, and technical assumptions into one structured document.

### 2. Deployment Scope

This manual covers:

- local development deployment
- Docker-based deployment
- database setup
- environment configuration
- mock traffic mode
- real traffic mode with mitmproxy
- service validation
- basic operations, monitoring, and troubleshooting

This manual does **not** replace organization-specific security policy, firewall policy, or cloud hardening standards.

### 3. System Architecture Summary

A typical deployment consists of the following components:

- **FastAPI backend**
- **traffic provider layer** (`mock` or `mitm`)
- **rule engine**
- **risk scoring service**
- **analytics and dashboard services**
- **MySQL database**
- optional **Docker / Docker Compose**
- optional **mitmproxy** for real traffic capture

Logical flow:

```text
Wallet / Test Client
        |
        v
Capture Path (mock or mitm)
        |
        v
FastAPI Application
        |
        v
Services Layer
        |
        v
MySQL Storage
        |
        v
Analytics / Dashboard / API Consumers
```

### 4. Recommended Environment

#### 4.1 Minimum Software Requirements

- Python 3.10+
- pip
- MySQL 8.0+ or Docker Engine
- Git
- Linux, macOS, or Windows
- mitmproxy for real capture mode

#### 4.2 Recommended Development Environment

- Python virtual environment
- Docker Compose for MySQL
- terminal access for API testing
- curl, HTTPie, or Postman
- browser access to Swagger or ReDoc

#### 4.3 Recommended Production-Like Environment

- Linux host
- systemd or container orchestrator
- reverse proxy such as Nginx
- environment secrets stored outside source control
- encrypted storage for captured artifacts
- backup policy for MySQL and capture files

### 5. Source Code Preparation

Clone the repository:

```bash
git clone https://github.com/compass-rose/wallet-rpc-privacy.git
cd wallet-rpc-privacy
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 6. Environment Configuration

Create the runtime configuration file:

```bash
cp .env.example .env
```

A practical example:

```bash
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/wallet_privacy
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
LOG_LEVEL=INFO
CORS_ORIGINS=*
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
PRIVACY_API_URL=http://localhost:8000
PCAP_ENCRYPTION_KEY=replace_with_strong_key
```

#### 6.1 Important Variables

| Variable | Meaning | Typical Value |
|---|---|---|
| `DATABASE_URL` | database connection string | `mysql+aiomysql://root:password@localhost:3306/wallet_privacy` |
| `TRAFFIC_PROVIDER` | traffic source mode | `mock` or `mitm` |
| `MOCK_TRAFFIC_COUNT` | generated mock records | `500` |
| `LOG_LEVEL` | backend log verbosity | `INFO` / `DEBUG` |
| `CORS_ORIGINS` | frontend access policy | `*` or explicit origins |
| `REAL_RPC_URL` | upstream real RPC endpoint | provider URL |
| `PRIVACY_API_URL` | backend URL used by helper scripts | `http://localhost:8000` |
| `PCAP_ENCRYPTION_KEY` | encryption key for capture artifacts | strong secret |

### 7. Database Deployment

#### 7.1 Option A: Run MySQL with Docker

```bash
docker-compose up -d mysql
```

Typical local defaults:

- Host: `localhost`
- Port: `3306`
- Database: `wallet_privacy`
- Username: `root`
- Password: `password`

#### 7.2 Option B: Use an Existing MySQL Instance

Create the database manually if needed:

```sql
CREATE DATABASE wallet_privacy;
```

Then update `.env` so `DATABASE_URL` points to the correct host and credentials.

#### 7.3 Database Validation

Confirm that the database is reachable before starting the backend. Validate:

- host and port
- username and password
- selected database name
- privileges for table creation or migration

### 8. Local Backend Deployment

Run the backend directly with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Alternative:

```bash
python -m app.main
```

After startup, validate:

```bash
curl http://localhost:8000/health
```

Also confirm that documentation pages are reachable:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### 9. Docker-Based Deployment

If the project includes a top-level Docker or Compose configuration, you can start the stack with:

```bash
docker-compose up
```

For a more production-like separation, a deployment may use two services:

- `mysql`
- `app`

An example Compose structure:

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: wallet_privacy
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backups:/backups

  app:
    build: .
    environment:
      DATABASE_URL: mysql+aiomysql://root:${DB_PASSWORD}@mysql:3306/wallet_privacy
      TRAFFIC_PROVIDER: ${TRAFFIC_PROVIDER}
      REAL_RPC_URL: ${REAL_RPC_URL}
      PCAP_ENCRYPTION_KEY: ${PCAP_ENCRYPTION_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    volumes:
      - ./pcap_captures:/data/captures
      - ./certs:/app/certs

volumes:
  mysql_data:
```

Bring the stack up:

```bash
docker-compose up -d
```

### 10. Running in Mock Mode

Mock mode is the easiest deployment target and should be the default during development.

#### 10.1 Configuration

```bash
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
```

#### 10.2 Validation Checklist

After startup:

1. create a session
2. start traffic capture
3. retrieve traffic
4. retrieve leaks
5. run an assessment

If all four stages work, the backend, database, and rule engine are most likely configured correctly.

### 11. Real Traffic Deployment with mitmproxy

Real capture mode requires more setup and should be treated as an advanced deployment path.

#### 11.1 Purpose

Use this mode only for controlled testing where you have authorization to observe the traffic path.

#### 11.2 Required Components

- mitmproxy installed
- trusted local CA certificate
- upstream RPC URL
- wallet or client configured to use the local interception path
- storage policy for capture artifacts

#### 11.3 Switch to Real Mode

In `.env`:

```bash
TRAFFIC_PROVIDER=mitm
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

#### 11.4 Certificate Setup

A typical workflow is:

- start mitmproxy once
- generate its CA
- install the CA certificate into the local trust store
- verify that the operating system and the wallet environment trust it

Examples from the original notes include commands such as:

```bash
mitmproxy
```

or helper-based certificate installation on supported systems.

#### 11.5 Starting the Backend

```bash
uvicorn app.main:app --reload --port 8000
```

#### 11.6 Starting the Capture Path

A reverse-proxy style example from the original material is:

```bash
mitmproxy --mode reverse:https://mainnet.infura.io/v3/YOUR_API_KEY@mitm.it:8080 --insecure
```

In practice, adapt the upstream address and local port to your environment.

#### 11.7 Wallet Configuration

A common controlled setup is:

- wallet points to local RPC endpoint `http://localhost:8545` or another local capture port
- local capture layer forwards requests to the real upstream provider
- backend records normalized metadata associated with the active session

#### 11.8 Validation in Real Mode

After configuration:

1. create a session
2. use the wallet normally
3. call `GET /api/v1/sessions/{session_id}/traffic`
4. verify that real method names and real timestamps appear
5. call `POST /api/v1/sessions/{session_id}/assess`

### 12. MetaMask / Custom RPC Example

A sample custom network configuration for MetaMask-like testing:

| Field | Value |
|---|---|
| Network Name | `Ethereum (Privacy Analysis)` |
| RPC URL | `http://localhost:8545` |
| Chain ID | `1` |
| Currency Symbol | `ETH` |

This lets the local capture path sit between the wallet and the upstream Ethereum node.

### 13. Reverse Proxy and External Exposure

If you need to expose the backend beyond localhost, place a reverse proxy such as Nginx in front of the FastAPI service.

Recommended proxy responsibilities:

- TLS termination
- request size limits
- timeout management
- access logging
- IP filtering or firewall integration

Do **not** expose test endpoints or raw capture storage without access control.

### 14. Security Hardening Recommendations

#### 14.1 Secrets

- never commit `.env` with live secrets
- store database passwords and encryption keys securely
- rotate secrets in shared environments

#### 14.2 Capture Data Protection

- encrypt raw capture artifacts at rest
- limit filesystem permissions on capture directories
- separate test data from production-like data
- define retention and deletion policy

#### 14.3 Access Control

Current documentation indicates that the present API version may operate without authentication. If deployed beyond a local lab environment, add:

- API gateway authentication
- network-level restriction
- reverse-proxy access control
- audit logging

#### 14.4 Logging

- avoid logging raw sensitive payloads
- mask or hash addresses and identifiers where possible
- use `INFO` in normal mode and `DEBUG` only during troubleshooting

### 15. Monitoring and Operations

#### 15.1 Health Checking

Use:

```bash
curl http://localhost:8000/health
```

#### 15.2 Log Monitoring

Watch the backend logs for:

- startup failures
- database connection errors
- certificate or proxy errors
- parsing errors
- rule engine exceptions

#### 15.3 Dashboard Endpoints for Runtime Monitoring

Useful endpoints include:

- `GET /api/v1/dashboard/monitor/status`
- `GET /api/v1/dashboard/monitor/leaks/stream`
- `GET /api/v1/dashboard/monitor/risk/metrics`

These can also serve as integration checks for frontend environments.

### 16. Backup and Recovery

At minimum, back up:

- MySQL data
- rule configurations
- certificates and trust-store deployment records
- captured artifacts if they are needed for reproducibility

Suggested recovery priorities:

1. restore database
2. restore runtime secrets
3. restore certificates
4. restore application container or virtual environment
5. rerun health and smoke tests

### 17. Upgrade and Change Management

When changing versions or switching environments:

- back up MySQL first
- record the current `.env`
- note the active `TRAFFIC_PROVIDER`
- verify compatibility of database schema and rules
- run smoke tests after upgrade

### 18. Validation Checklist After Deployment

A deployment should be considered successful only if all of the following pass:

- backend health endpoint responds correctly
- session creation works
- traffic start works
- traffic records can be retrieved
- leak events can be retrieved
- risk assessment runs successfully
- analytics summary endpoint responds
- dashboard status endpoint responds
- data can be removed or reset cleanly

### 19. Common Problems and Fixes

#### 19.1 MySQL Is Not Reachable

Check:

```bash
docker ps | grep mysql
docker-compose logs mysql
```

#### 19.2 Port 8000 Is Already in Use

Check:

```bash
lsof -i :8000
```

Then stop the conflicting process or change the port.

#### 19.3 Permission Denied on Capture Directory

Fix permissions on the capture directory, for example:

```bash
chmod 755 ./pcap_captures
```

Then ensure the running user owns the directory where appropriate.

#### 19.4 Certificate Errors in Real Mode

- regenerate or reinstall the CA
- verify that the wallet trusts the CA
- verify that the proxy path is actually being used

#### 19.5 No Data Appears in Dashboard Reports

Check whether the minimum data requirements are met:

- at least one session
- traffic records stored
- leak and assessment generation completed

### 20. Operational Notes

- use **mock mode** for normal development
- use **mitm mode** only for controlled experiments
- separate demo data from research data
- document provider URLs and network assumptions
- retain only the minimum capture data needed for analysis

### 21. End of English Version

---

## 中文版本

### 1. 文档目的

本部署手册用于说明如何在开发环境和类生产环境中安装、配置、运行、验证和维护 **Wallet / RPC Privacy Leakage Measurement System（钱包 / RPC 隐私泄露测量系统）**。本手册将原有的部署说明、快速开始文档、真实流量捕获指引以及技术假设整合为一份结构化文档。

### 2. 部署范围

本手册覆盖以下内容：

- 本地开发部署
- 基于 Docker 的部署
- 数据库初始化
- 环境变量配置
- mock 流量模式
- 基于 mitmproxy 的真实流量模式
- 服务验证
- 基础运维、监控与故障排查

本手册**不**替代组织内部的安全策略、防火墙策略或云环境加固规范。

### 3. 系统架构概述

一个典型部署通常包含以下组件：

- **FastAPI backend**
- **traffic provider layer**（`mock` 或 `mitm`）
- **rule engine**
- **risk scoring service**
- **analytics and dashboard services**
- **MySQL database**
- 可选的 **Docker / Docker Compose**
- 用于真实流量捕获的可选 **mitmproxy**

逻辑流程如下：

```text
Wallet / Test Client
        |
        v
Capture Path (mock or mitm)
        |
        v
FastAPI Application
        |
        v
Services Layer
        |
        v
MySQL Storage
        |
        v
Analytics / Dashboard / API Consumers
```

### 4. 推荐运行环境

#### 4.1 最低软件要求

- Python 3.10+
- pip
- MySQL 8.0+ 或 Docker Engine
- Git
- Linux、macOS 或 Windows
- 真实捕获模式下需要 mitmproxy

#### 4.2 推荐开发环境

- Python 虚拟环境
- 使用 Docker Compose 启动 MySQL
- 可进行接口测试的终端
- curl、HTTPie 或 Postman
- 可访问 Swagger 或 ReDoc 的浏览器

#### 4.3 推荐类生产环境

- Linux 主机
- systemd 或容器编排环境
- Nginx 等反向代理
- 配置秘密信息不进入源码仓库
- 捕获文件使用加密存储
- 为 MySQL 与捕获文件建立备份策略

### 5. 准备源码

克隆仓库：

```bash
git clone https://github.com/compass-rose/wallet-rpc-privacy.git
cd wallet-rpc-privacy
```

创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

### 6. 环境配置

创建运行配置文件：

```bash
cp .env.example .env
```

一个实用示例如下：

```bash
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/wallet_privacy
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
LOG_LEVEL=INFO
CORS_ORIGINS=*
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
PRIVACY_API_URL=http://localhost:8000
PCAP_ENCRYPTION_KEY=replace_with_strong_key
```

#### 6.1 关键变量说明

| 变量 | 含义 | 常见值 |
|---|---|---|
| `DATABASE_URL` | 数据库连接串 | `mysql+aiomysql://root:password@localhost:3306/wallet_privacy` |
| `TRAFFIC_PROVIDER` | 流量来源模式 | `mock` 或 `mitm` |
| `MOCK_TRAFFIC_COUNT` | mock 生成记录数量 | `500` |
| `LOG_LEVEL` | 日志级别 | `INFO` / `DEBUG` |
| `CORS_ORIGINS` | 前端跨域访问策略 | `*` 或指定来源 |
| `REAL_RPC_URL` | 真实上游 RPC 地址 | provider URL |
| `PRIVACY_API_URL` | 辅助脚本使用的后端地址 | `http://localhost:8000` |
| `PCAP_ENCRYPTION_KEY` | 捕获文件加密密钥 | 强随机秘密值 |

### 7. 数据库部署

#### 7.1 方案 A：使用 Docker 启动 MySQL

```bash
docker-compose up -d mysql
```

常见本地默认配置：

- Host：`localhost`
- Port：`3306`
- Database：`wallet_privacy`
- Username：`root`
- Password：`password`

#### 7.2 方案 B：使用现有 MySQL 实例

如果需要手动建库，可执行：

```sql
CREATE DATABASE wallet_privacy;
```

然后在 `.env` 中将 `DATABASE_URL` 修改为实际主机和账号信息。

#### 7.3 数据库验证

在启动后端前，应确认数据库可达，并检查：

- 主机和端口
- 用户名和密码
- 数据库名
- 当前账号是否具备建表或迁移权限

### 8. 本地后端部署

使用 Uvicorn 直接运行后端：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或者：

```bash
python -m app.main
```

启动后，执行：

```bash
curl http://localhost:8000/health
```

同时确认文档页面可以访问：

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

### 9. 基于 Docker 的部署

如果项目已经提供顶层 Docker 或 Compose 配置，可以直接运行：

```bash
docker-compose up
```

一个更接近生产的结构通常分为两个服务：

- `mysql`
- `app`

示例 Compose 结构如下：

```yaml
version: "3.8"

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASSWORD}
      MYSQL_DATABASE: wallet_privacy
    volumes:
      - mysql_data:/var/lib/mysql
      - ./backups:/backups

  app:
    build: .
    environment:
      DATABASE_URL: mysql+aiomysql://root:${DB_PASSWORD}@mysql:3306/wallet_privacy
      TRAFFIC_PROVIDER: ${TRAFFIC_PROVIDER}
      REAL_RPC_URL: ${REAL_RPC_URL}
      PCAP_ENCRYPTION_KEY: ${PCAP_ENCRYPTION_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    volumes:
      - ./pcap_captures:/data/captures
      - ./certs:/app/certs

volumes:
  mysql_data:
```

启动命令：

```bash
docker-compose up -d
```

### 10. 使用 Mock 模式运行

Mock 模式是最简单的部署目标，开发阶段建议默认使用它。

#### 10.1 配置

```bash
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
```

#### 10.2 验证清单

服务启动后，请依次完成：

1. 创建会话
2. 启动流量捕获
3. 获取流量
4. 获取泄露事件
5. 运行风险评估

如果这些步骤都正常，则说明后端、数据库和规则引擎大体配置正确。

### 11. 基于 mitmproxy 的真实流量部署

真实捕获模式需要更多准备，应该视为高级部署路径。

#### 11.1 用途

该模式应只用于你有权限控制的测试环境与受控研究场景。

#### 11.2 所需组件

- 已安装 mitmproxy
- 本地已信任的 CA 证书
- 真实上游 RPC 地址
- 已配置为使用本地拦截链路的钱包或客户端
- 捕获文件的存储策略

#### 11.3 切换到真实模式

在 `.env` 中设置：

```bash
TRAFFIC_PROVIDER=mitm
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

#### 11.4 证书配置

典型流程如下：

- 先启动一次 mitmproxy
- 生成本地 CA
- 将 CA 证书安装到本机信任库
- 验证操作系统和钱包环境都信任该证书

原始材料中给出的示例命令包括：

```bash
mitmproxy
```

或系统支持的证书安装辅助方式。

#### 11.5 启动后端

```bash
uvicorn app.main:app --reload --port 8000
```

#### 11.6 启动捕获链路

原始文档中的一个反向代理示例如下：

```bash
mitmproxy --mode reverse:https://mainnet.infura.io/v3/YOUR_API_KEY@mitm.it:8080 --insecure
```

实际使用时，应按你的真实环境调整上游地址和本地端口。

#### 11.7 钱包配置

常见的受控实验方式是：

- 钱包指向本地 RPC 地址 `http://localhost:8545` 或其他本地捕获端口
- 本地捕获层将请求转发给真实上游提供商
- 后端将标准化元数据与当前会话关联后入库

#### 11.8 真实模式验证

配置完成后，请执行：

1. 创建会话
2. 正常使用钱包
3. 调用 `GET /api/v1/sessions/{session_id}/traffic`
4. 确认已出现真实方法名和真实时间戳
5. 调用 `POST /api/v1/sessions/{session_id}/assess`

### 12. MetaMask / Custom RPC 示例

一个适用于 MetaMask 类实验的自定义网络配置如下：

| 字段 | 值 |
|---|---|
| Network Name | `Ethereum (Privacy Analysis)` |
| RPC URL | `http://localhost:8545` |
| Chain ID | `1` |
| Currency Symbol | `ETH` |

这样可以使本地捕获层位于钱包与真实以太坊节点之间。

### 13. 反向代理与外部暴露

如果需要让服务不只在本机访问，建议在 FastAPI 前面增加 Nginx 等反向代理。

推荐代理层承担以下职责：

- TLS 终止
- 请求体大小限制
- 超时控制
- 访问日志
- IP 过滤或防火墙集成

不要在没有访问控制的情况下暴露测试接口或原始捕获目录。

### 14. 安全加固建议

#### 14.1 密钥与秘密信息

- 不要把含有真实密钥的 `.env` 提交到仓库
- 数据库密码与加密密钥要安全存储
- 多人环境下要定期轮换敏感信息

#### 14.2 捕获数据保护

- 原始捕获文件建议静态加密
- 限制捕获目录文件权限
- 区分演示数据与研究数据
- 建立数据保留与删除策略

#### 14.3 访问控制

当前文档显示，现版本 API 可能默认不需要认证。如果要部署到本地实验室之外，应增加：

- API 网关认证
- 网络层访问限制
- 反向代理访问控制
- 审计日志

#### 14.4 日志

- 避免记录原始敏感载荷
- 地址和标识尽量做哈希或遮蔽
- 正常运行使用 `INFO`
- 仅在排障时临时切换到 `DEBUG`

### 15. 监控与运维

#### 15.1 健康检查

使用：

```bash
curl http://localhost:8000/health
```

#### 15.2 日志监控

重点关注以下日志：

- 启动失败
- 数据库连接错误
- 证书或代理错误
- 解析错误
- 规则引擎异常

#### 15.3 使用 Dashboard 接口做运行监控

常用运行时检查接口包括：

- `GET /api/v1/dashboard/monitor/status`
- `GET /api/v1/dashboard/monitor/leaks/stream`
- `GET /api/v1/dashboard/monitor/risk/metrics`

这些接口也可以作为前端环境的集成检查项。

### 16. 备份与恢复

至少应备份以下内容：

- MySQL 数据
- 规则配置
- 证书及其部署记录
- 如需复现实验，则还应保留捕获文件

建议的恢复优先级如下：

1. 恢复数据库
2. 恢复运行所需秘密信息
3. 恢复证书
4. 恢复应用容器或虚拟环境
5. 重新执行健康检查与冒烟测试

### 17. 升级与变更管理

当切换版本或环境时，建议执行以下步骤：

- 先备份 MySQL
- 保存当前 `.env`
- 记录当前 `TRAFFIC_PROVIDER`
- 确认数据库结构与规则配置兼容
- 升级后重新跑一遍冒烟测试

### 18. 部署成功验证清单

只有以下项目全部通过，才能认为部署成功：

- 健康检查接口正常返回
- 创建会话成功
- 启动流量捕获成功
- 能获取流量记录
- 能获取泄露事件
- 能成功运行风险评估
- analytics summary 接口正常
- dashboard status 接口正常
- 数据能被清理或重置

### 19. 常见问题与修复

#### 19.1 MySQL 不可达

检查：

```bash
docker ps | grep mysql
docker-compose logs mysql
```

#### 19.2 8000 端口已被占用

检查：

```bash
lsof -i :8000
```

然后关闭冲突进程，或者改用其他端口。

#### 19.3 捕获目录权限不足

修正捕获目录权限，例如：

```bash
chmod 755 ./pcap_captures
```

然后确认运行进程对该目录具有所有权或可写权限。

#### 19.4 真实模式证书报错

- 重新生成或重新安装 CA
- 确认钱包信任该 CA
- 确认流量确实经过了本地代理链路

#### 19.5 Dashboard 报告没有数据

请检查是否满足最低数据要求：

- 至少存在一个 session
- 已写入 traffic records
- 已完成 leak 与 assessment 生成

### 20. 运维说明

- 开发阶段优先使用 **mock mode**
- 真实模式 **mitm mode** 只用于受控实验
- 演示数据与研究数据应分开管理
- 需要记录 provider URL 与网络假设
- 只保留分析所需的最小捕获数据集

### 21. 中文版结束
