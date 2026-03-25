# Wallet / RPC Privacy Leakage Measurement System  
# User Manual

**Version:** 2.0  
**Format Note:** This document presents the complete English version first, followed by the complete Chinese version.

---

## English Version

### 1. Purpose

This user manual explains how to use the **Wallet / RPC Privacy Leakage Measurement System** as an end user, tester, researcher, or evaluator. It focuses on day-to-day usage rather than infrastructure deployment. The system is designed to measure privacy leakage at the wallet–RPC communication layer by capturing traffic, detecting leak patterns, computing risk scores, and presenting the results through APIs and dashboard-ready endpoints.

### 2. What the System Does

The system analyzes communication between blockchain wallets and RPC providers such as Infura, Alchemy, QuickNode, or self-hosted nodes. It does **not** break encryption or inspect wallet private keys. Instead, it studies privacy-sensitive metadata that an honest-but-curious RPC provider could observe, including:

- RPC method names
- request timing and frequency
- address-level correlation patterns
- response latency and temporal signatures
- session-level behavior

### 3. Main Capabilities

#### 3.1 Traffic Capture
The system can capture either:

- **mock traffic**, for development and demonstration
- **real traffic**, through a mitmproxy-based capture path for controlled experiments

#### 3.2 Privacy Leak Detection
The rule engine evaluates captured traffic against predefined privacy rules. Leak events are grouped into four major categories:

- **Identity**
- **Asset**
- **Behavior**
- **Location**

#### 3.3 Risk Assessment
Each session can be scored on four dimensions:

- **entropy score**
- **uniqueness score**
- **correlation score**
- **temporal score**

These are combined into an **overall score** from 0 to 100.

#### 3.4 Analytics and Visualization
The system provides aggregated views such as:

- overall summary statistics
- trend data over time
- leak type distribution
- risk level distribution
- method frequency statistics
- top-risk sessions
- dashboard monitoring and reports

### 4. Typical User Workflow

A normal usage flow looks like this:

1. Create a session.
2. Start traffic capture.
3. Use the wallet normally or generate mock traffic.
4. Retrieve traffic records.
5. Detect privacy leaks.
6. Run a risk assessment.
7. Review analytics, dashboard outputs, and recommendations.
8. Export or compare results if needed.

### 5. Quick Start

#### 5.1 Prerequisites

Before using the system, make sure you have:

- Python 3.10 or above
- MySQL 8.0 or a Docker-based MySQL container
- the project dependencies installed
- access to the backend service on port `8000` by default

#### 5.2 Start the Backend

Example startup commands:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

or

```bash
python -m app.main
```

If Docker Compose is configured:

```bash
docker-compose up
```

#### 5.3 Verify That the Service Is Running

```bash
curl http://localhost:8000/health
```

Expected healthy response:

```json
{
  "status": "healthy",
  "service": "wallet-privacy-backend"
}
```

#### 5.4 Open the Interactive API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 6. Using Mock Traffic

Mock traffic is the simplest way to learn the system and test the analysis pipeline without touching a real wallet.

#### 6.1 When to Use Mock Mode

Use mock mode when you want to:

- test the backend quickly
- demonstrate the platform in class or a presentation
- verify rule matching and scoring behavior
- run the system without certificate or proxy setup

#### 6.2 Required Configuration

In `.env`:

```bash
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
```

#### 6.3 Example Workflow in Mock Mode

Create a session:

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

Start capture:

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/start
```

Check traffic:

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

Get detected leaks:

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

Run assessment:

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

### 7. Using Real Traffic Capture

Real traffic mode is intended for controlled experiments. It uses a local interception path based on **mitmproxy**.

#### 7.1 Important Safety Notes

- The system is intended for **your own testing environment** and controlled research.
- Private keys are not meant to be captured or stored.
- Sensitive identifiers should be anonymized or hashed before storage.
- PCAP or raw capture data should be protected and, where applicable, encrypted at rest.

#### 7.2 When to Use Real Capture

Use real capture when you want to:

- study actual wallet–RPC behavior
- compare real-world providers
- evaluate privacy leakage under realistic timing and method patterns
- produce empirical measurements for a report or experiment

#### 7.3 Basic Setup Idea

A typical real-capture setup is:

```text
Wallet -> Local proxy / capture layer -> Real RPC provider
```

The user configures the wallet to use a controlled local endpoint, while the backend records normalized metadata.

#### 7.4 Core Requirements for Real Capture

- mitmproxy installed
- certificate trusted locally
- a real upstream RPC endpoint such as Infura, Alchemy, or Ankr
- a local environment where proxying is allowed
- proper authorization to test the wallet and traffic path

#### 7.5 Example `.env` Switch

```bash
TRAFFIC_PROVIDER=mitm
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
PRIVACY_API_URL=http://localhost:8000
```

#### 7.6 Typical Wallet Configuration Example

For a custom wallet network or a controlled MetaMask test network, the wallet can point to a local RPC endpoint such as:

- Network Name: `Ethereum (Privacy Analysis)`
- RPC URL: `http://localhost:8545`
- Chain ID: `1`
- Symbol: `ETH`

### 8. Session Management

A **session** is the basic unit of analysis. Each session represents one capture-and-analysis run for a selected wallet and RPC provider combination.

#### 8.1 Create a Session
Use this before traffic capture starts. The session stores metadata such as wallet type, RPC provider, current status, and timestamps.

#### 8.2 Get Session Details
Use this to inspect one specific session.

#### 8.3 List Sessions
Use this when you want to review historical tests, filter by wallet type, or paginate through records.

#### 8.4 Delete a Session
Use this to remove a session and its associated analysis data when cleanup is required.

### 9. Traffic Records

Traffic records are normalized request/response observations captured for each session.

Typical fields include:

- session ID
- method name
- timestamp
- response time
- address hash or anonymized identifier
- request/response size or metadata fields

Use traffic records when you want to inspect whether a session shows repetitive, unique, or highly linkable behavior.

### 10. Privacy Leak Events

Leak events are created when traffic matches one or more privacy detection rules.

Typical leak-event information includes:

- leak type
- description
- confidence score
- confidence interval
- method name
- related rule ID
- event timestamp

#### 10.1 Leak Categories

**Identity leaks**  
These suggest that a user or wallet can be linked or re-identified.

**Asset leaks**  
These reveal balance-related or holdings-related behavior.

**Behavior leaks**  
These show highly distinguishable patterns in method usage or timing.

**Location leaks**  
These indicate network- or route-level patterns that may help infer a user’s environment or origin.

### 11. Understanding Risk Scores

The overall score is typically interpreted as:

- **0–30**: low risk
- **31–50**: medium risk
- **51–70**: high risk
- **71–100**: critical risk

#### 11.1 Entropy Score
Measures diversity and unpredictability in request patterns. Lower diversity can increase linkability.

#### 11.2 Uniqueness Score
Measures how distinctive a session is compared with others. Highly unique traffic can be easier to identify.

#### 11.3 Correlation Score
Measures whether multiple addresses or repeated behaviors appear statistically linkable.

#### 11.4 Temporal Score
Measures the strength of timing patterns such as fixed intervals, bursts, or repeated routines.

#### 11.5 Confidence
Confidence indicates how reliable the risk result is, based on the amount and quality of observed data.

### 12. Recommendations and How to Read Them

After an assessment, the system may suggest actions such as:

- increase method diversity
- reduce fixed polling frequency
- avoid repeated timing signatures
- use privacy-preserving routing or provider separation
- reduce cross-address behavioral coupling

These recommendations should be treated as **privacy engineering suggestions**, not absolute guarantees.

### 13. Baseline Comparison, Attack Simulation, and Adversarial Testing

Some builds or modules expose additional research-oriented endpoints.

#### 13.1 Baseline Comparison
Compares a session against:

- a random baseline
- an ideal privacy baseline
- an industry or sample average

This helps users understand whether a session is better or worse than common patterns.

#### 13.2 Simulated Attack
Runs a classifier- or clustering-based test to estimate how easily sessions can be distinguished.

Typical indicators:

- attack success rate
- clustering purity
- silhouette score
- overall attack effectiveness

#### 13.3 Adversarial Test
Evaluates the expected benefit of defense strategies such as:

- padding
- timing jitter
- method randomization

This is useful for experimentation and design exploration.

### 14. Dashboard and Reporting Functions

Dashboard-related endpoints support frontend visualization, especially for ECharts or similar charting libraries.

They can provide:

- monitoring status
- leak streams
- live risk metrics
- timeline reports
- heatmap data
- aggregated chart bundles
- comprehensive reports

These endpoints are especially useful for presentations, demos, and monitoring panels.

### 15. Detection Rules

The rule engine is typically YAML-based or configuration-driven. Rules may contain:

- rule ID
- category
- priority
- enable/disable status
- matching conditions
- event generation actions

Rule categories usually include Identity, Asset, Behavior, and Location.

### 16. Data Privacy and Safety

This system is built to measure privacy leakage while minimizing unnecessary exposure. Operational expectations include:

- no logging of private keys
- no storage of raw wallet secrets
- hashing or anonymizing sensitive identifiers
- local analysis whenever possible
- secure storage and deletion policies for captured artifacts

### 17. Common Commands

#### 17.1 Create a Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

#### 17.2 Start Capture

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/start
```

#### 17.3 Stop Capture

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/stop
```

#### 17.4 Get Traffic

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

#### 17.5 Get Leaks

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

#### 17.6 Run Assessment

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

#### 17.7 Get Dashboard Status

```bash
curl http://localhost:8000/api/v1/dashboard/monitor/status
```

### 18. Troubleshooting

#### 18.1 The Backend Does Not Start

Check:

- whether Python 3.10+ is installed
- whether dependencies were installed
- whether the configured database is reachable
- whether port `8000` is already occupied

#### 18.2 MySQL Connection Failed

Check:

- database host, port, username, and password
- whether Docker MySQL is running
- whether the database schema has been initialized

#### 18.3 No Traffic Appears in a Session

Check:

- whether capture was started
- whether `TRAFFIC_PROVIDER` is set correctly
- whether the wallet or traffic generator actually produced requests
- whether the local proxy path is working in real-capture mode

#### 18.4 SSL or Certificate Errors in Real Mode

Check:

- whether the mitmproxy certificate is installed and trusted
- whether the wallet is using the intended proxy or local endpoint
- whether the operating system certificate store accepted the CA

### 19. FAQ

#### Q1. Can I use this system without a real wallet?
Yes. Mock mode is designed exactly for that purpose.

#### Q2. Does the system capture private keys?
It is not intended to. The design goal is to analyze metadata, not secrets.

#### Q3. Can I compare two different RPC providers?
Yes. Create separate sessions for each provider and compare the results.

#### Q4. Can I export the results?
Yes. Most results can be obtained in JSON form through the API.

#### Q5. Is the score absolute?
No. The score is best interpreted comparatively across sessions, scenarios, or baselines.

### 20. End of English Version

---

## 中文版本

### 1. 文档目的

本用户手册面向系统的日常使用者、测试者、研究人员和评估人员，重点说明如何使用 **Wallet / RPC Privacy Leakage Measurement System（钱包 / RPC 隐私泄露测量系统）**。本手册主要介绍使用流程，不以部署细节为重点。系统的目标是在钱包与 RPC 提供商通信这一层面上测量隐私泄露，通过流量捕获、规则检测、风险评分和可视化接口输出分析结果。

### 2. 系统作用

本系统用于分析区块链钱包与 RPC 提供商（如 Infura、Alchemy、QuickNode 或自建节点）之间的通信行为。系统**不会**破解加密，也不会读取钱包私钥。它关注的是一个“诚实但好奇”的 RPC 提供商能够观察到的元数据，例如：

- RPC 方法名
- 请求的时间与频率
- 地址层面的关联模式
- 响应延迟与时序特征
- 会话级别的行为特征

### 3. 主要能力

#### 3.1 流量捕获
系统支持两类流量来源：

- **mock traffic**：用于开发、测试和演示
- **real traffic**：通过基于 mitmproxy 的真实捕获链路获取实验数据

#### 3.2 隐私泄露检测
规则引擎会依据预定义的隐私规则对捕获到的流量进行检测。泄露事件主要分为四类：

- **Identity**
- **Asset**
- **Behavior**
- **Location**

#### 3.3 风险评估
每个会话都可以从四个维度计算分数：

- **entropy score**
- **uniqueness score**
- **correlation score**
- **temporal score**

最后会合成为一个 **0 到 100 的 overall score**。

#### 3.4 分析与可视化
系统支持以下聚合分析结果：

- 总体统计信息
- 时间趋势数据
- 泄露类型分布
- 风险等级分布
- RPC 方法频率统计
- 高风险会话排行
- dashboard 监控与报告接口

### 4. 典型使用流程

标准流程如下：

1. 创建会话。
2. 启动流量捕获。
3. 正常使用钱包，或者生成 mock 流量。
4. 获取流量记录。
5. 检测隐私泄露事件。
6. 运行风险评估。
7. 查看统计结果、dashboard 输出和建议。
8. 按需要导出或比较结果。

### 5. 快速开始

#### 5.1 前置条件

在使用系统前，请确保具备以下条件：

- Python 3.10 或以上版本
- MySQL 8.0，或者使用 Docker 启动的 MySQL
- 已安装项目依赖
- 可访问默认运行在 `8000` 端口的后端服务

#### 5.2 启动后端

示例启动命令：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

或者：

```bash
python -m app.main
```

如果已经配置 Docker Compose，也可以使用：

```bash
docker-compose up
```

#### 5.3 验证服务是否正常运行

```bash
curl http://localhost:8000/health
```

正常情况下会返回：

```json
{
  "status": "healthy",
  "service": "wallet-privacy-backend"
}
```

#### 5.4 打开交互式 API 文档

- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

### 6. 使用 Mock 流量

Mock 流量是学习系统和验证分析链路最简单的方式，不需要真实钱包参与。

#### 6.1 适用场景

建议在以下情况下使用 mock 模式：

- 需要快速测试后端
- 课堂展示或演示
- 验证规则命中与评分逻辑
- 当前机器不方便配置证书或代理

#### 6.2 所需配置

在 `.env` 中设置：

```bash
TRAFFIC_PROVIDER=mock
MOCK_TRAFFIC_COUNT=500
```

#### 6.3 Mock 模式示例流程

创建会话：

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

启动捕获：

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/start
```

查看流量：

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

查看泄露事件：

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

运行风险评估：

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

### 7. 使用真实流量捕获

真实流量模式用于受控实验，底层一般基于 **mitmproxy** 实现本地拦截与转发。

#### 7.1 重要安全说明

- 该系统应当只用于**自己的测试环境**和受控研究场景。
- 系统设计目标不是捕获或存储私钥。
- 敏感标识应在入库前匿名化或哈希化。
- PCAP 或原始流量文件应妥善保护，必要时进行静态加密。

#### 7.2 适用场景

建议在以下情况下使用真实捕获模式：

- 研究真实钱包与 RPC 的交互行为
- 比较不同 RPC 提供商
- 评估真实环境下的时序与调用模式隐私风险
- 为课程报告或实验生成实证数据

#### 7.3 基本结构

典型的真实捕获链路如下：

```text
Wallet -> Local proxy / capture layer -> Real RPC provider
```

用户将钱包配置为走本地受控入口，后端只记录标准化后的元数据。

#### 7.4 真实捕获的核心要求

- 已安装 mitmproxy
- 本机已信任证书
- 已准备真实上游 RPC 地址，例如 Infura、Alchemy 或 Ankr
- 本地环境允许代理和转发
- 对被测试的钱包和流量路径具有合法控制权

#### 7.5 `.env` 切换示例

```bash
TRAFFIC_PROVIDER=mitm
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
PRIVACY_API_URL=http://localhost:8000
```

#### 7.6 钱包侧配置示例

以自定义网络或受控 MetaMask 网络为例，可设置为：

- Network Name：`Ethereum (Privacy Analysis)`
- RPC URL：`http://localhost:8545`
- Chain ID：`1`
- Symbol：`ETH`

### 8. 会话管理

**Session** 是系统最基本的分析单位。每个会话都代表一次独立的捕获与分析过程，对应某种钱包类型与某个 RPC 提供商组合。

#### 8.1 创建会话
在流量捕获前必须先创建会话。会话会记录钱包类型、RPC 提供商、当前状态和时间戳等元数据。

#### 8.2 查看单个会话
当你需要查看某次实验的详细信息时，使用单会话查询。

#### 8.3 列出会话
当你需要查看历史记录、按钱包类型筛选、或分页浏览实验数据时，使用会话列表接口。

#### 8.4 删除会话
当你需要清理测试数据时，可以删除会话以及关联分析结果。

### 9. 流量记录

Traffic Record 是针对某个会话捕获到的标准化请求/响应观察结果。

常见字段包括：

- session ID
- method name
- timestamp
- response time
- address hash 或匿名标识
- 请求/响应大小或其他元数据字段

如果你想判断一个会话是否存在重复、独特或高度可关联的行为模式，就需要查看这些流量记录。

### 10. 隐私泄露事件

当某条流量命中隐私规则时，系统会生成 Leak Event。

常见字段包括：

- leak type
- description
- confidence
- confidence interval
- method name
- rule ID
- event timestamp

#### 10.1 泄露类别

**Identity leaks**  
表示用户或钱包可能被识别或重新关联。

**Asset leaks**  
表示余额、资产持有或资产查询行为暴露明显。

**Behavior leaks**  
表示方法调用模式或时序模式过于独特，容易区分。

**Location leaks**  
表示网络层或路由层特征可能帮助推断用户所处环境。

### 11. 风险评分解释

总体评分通常按如下方式理解：

- **0–30**：低风险
- **31–50**：中风险
- **51–70**：高风险
- **71–100**：严重风险

#### 11.1 Entropy Score
用于衡量请求模式的多样性与不可预测性。多样性越低，通常越容易被关联。

#### 11.2 Uniqueness Score
用于衡量当前会话与其他会话相比有多独特。越独特，越容易被识别。

#### 11.3 Correlation Score
用于衡量多个地址或行为之间是否存在可统计识别的关联。

#### 11.4 Temporal Score
用于衡量固定间隔、突发模式和重复时序等时间特征强弱。

#### 11.5 Confidence
表示当前风险结果的可靠程度，通常与观测到的数据量和质量有关。

### 12. 如何理解建议项

完成评估后，系统可能会给出如下建议：

- 增加方法调用多样性
- 减少固定频率轮询
- 避免重复的时间特征
- 使用更有隐私保护能力的路由或不同提供商隔离
- 降低跨地址行为耦合

这些建议应理解为**隐私工程层面的改进方向**，而不是绝对保证。

### 13. 基线对比、模拟攻击与对抗测试

某些构建版本或扩展模块中会提供研究型接口。

#### 13.1 基线对比
将会话与以下对象进行比较：

- 随机基线
- 理想隐私基线
- 行业平均或样本均值

这样可以帮助用户判断某个会话比常见模式更好还是更差。

#### 13.2 模拟攻击
通过分类器或聚类方法估计会话有多容易被区分。

典型指标包括：

- attack success rate
- clustering purity
- silhouette score
- overall attack effectiveness

#### 13.3 对抗测试
用于评估以下防御策略可能带来的效果：

- padding
- timing jitter
- method randomization

这类接口适合实验分析和设计探索。

### 14. Dashboard 与报告功能

Dashboard 相关接口主要服务于前端可视化，特别适合 ECharts 等图表库。

可提供的数据包括：

- 监控状态
- 实时泄露流
- 实时风险指标
- 时间线报告
- 热力图数据
- 聚合图表数据
- 综合报告

这些接口非常适合做演示页面、课程展示和监控面板。

### 15. 检测规则

规则引擎一般采用 YAML 或配置驱动形式。每条规则通常包含：

- 规则 ID
- 分类
- 优先级
- 启用/禁用状态
- 匹配条件
- 事件生成动作

规则通常分属 Identity、Asset、Behavior、Location 这四大类。

### 16. 数据隐私与安全

本系统的目标是在测量隐私泄露的同时，尽量降低不必要的敏感信息暴露。使用时应满足如下预期：

- 不记录私钥
- 不存储原始钱包秘密信息
- 对敏感标识做哈希或匿名化
- 尽量在本地完成分析
- 对捕获文件建立安全存储与删除策略

### 17. 常用命令

#### 17.1 创建会话

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask",
    "rpc_provider": "https://mainnet.infura.io/v3/test"
  }'
```

#### 17.2 启动捕获

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/start
```

#### 17.3 停止捕获

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic/stop
```

#### 17.4 获取流量

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

#### 17.5 获取泄露事件

```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

#### 17.6 运行风险评估

```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

#### 17.7 获取 Dashboard 状态

```bash
curl http://localhost:8000/api/v1/dashboard/monitor/status
```

### 18. 故障排查

#### 18.1 后端无法启动

请检查：

- Python 版本是否为 3.10 以上
- 依赖是否已正确安装
- 数据库配置是否可连接
- `8000` 端口是否被占用

#### 18.2 MySQL 连接失败

请检查：

- 数据库主机、端口、用户名、密码是否正确
- Docker 中的 MySQL 是否正常运行
- 数据表结构是否已经初始化

#### 18.3 会话中没有流量数据

请检查：

- 是否已经调用启动捕获接口
- `TRAFFIC_PROVIDER` 配置是否正确
- 钱包或流量生成器是否真的发出了请求
- 在真实模式下，本地代理链路是否正常

#### 18.4 真实模式出现 SSL 或证书错误

请检查：

- mitmproxy 证书是否安装并信任
- 钱包是否真正走了预期的代理或本地端点
- 操作系统证书库是否接受该 CA

### 19. 常见问题

#### Q1. 没有真实钱包能不能使用？
可以。mock 模式就是为这种场景设计的。

#### Q2. 系统会不会捕获私钥？
设计目标不是捕获私钥，而是分析元数据。

#### Q3. 能不能比较两个不同的 RPC 提供商？
可以。分别建立不同会话，再对结果进行比较即可。

#### Q4. 能不能导出结果？
可以。大部分结果都可以通过 API 以 JSON 形式导出。

#### Q5. 风险分数是不是绝对值？
不是。它更适合用于不同会话、不同场景、不同基线之间的相对比较。

### 20. 中文版结束
