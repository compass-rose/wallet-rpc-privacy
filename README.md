# Wallet / RPC Privacy Leakage Measurement
钱包与RPC隐私泄露测量系统

## 项目概述

构建一个能够测量和量化区块链钱包（如MetaMask、WalletConnect）与RPC节点通信过程中隐私泄露程度的系统，通过实际网络通信分析和实验验证，识别攻击向量，评估隐私风险等级，并提供可操作的改进建议。

## 技术栈

**后端**:
- Python 3.10+
- FastAPI (异步高性能 Web 框架)
- SQLAlchemy (ORM)
- PostgreSQL (结构化数据存储)
- Redis (实时缓存)

**网络流量分析**:
- mitmproxy (HTTPS/TLS 流量解密)
- scapy (网络包捕获)
- pyshark (网络协议分析)

**数据处理**:
- pandas
- numpy
- scikit-learn

**前端**:
- React + TypeScript
- D3.js / ECharts (数据可视化)

## 项目结构

```
wallet-rpc-privacy/
├── app/                    # 主应用代码
│   ├── api/               # API 路由
│   ├── core/              # 配置和工具
│   ├── models/            # 数据模型
│   └── services/          # 业务逻辑
├── tests/                 # 测试代码
├── README.md
└── requirements.txt
```

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行开发服务器

```bash
cd app/ && uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或者直接运行：

```bash
python app/main.py
```

### 访问 API 文档

启动服务后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 核心功能

### 1. 网络流量捕获与分析
- 捕获钱包与 RPC 节点之间的网络通信
- 解析 JSON-RPC 方法调用
- 支持多种协议（HTTP/HTTPS, WebSocket, HTTP/2）

### 2. 隐私泄露检测与分类
- 自动化检测隐私泄露事件
- 分类：身份/资产/行为/位置
- 置信度评分系统

### 3. 风险量化评估
- 多维度指标体系（信息熵、唯一性、关联性、时效性）
- 风险评分（0-100）
- 与行业平均水平对比

### 4. 可视化仪表板
- 实时监控面板
- 分析报告生成
- 多种图表类型展示

## 开发指南

### 运行测试

```bash
pytest
```

### 代码风格

项目遵循 PEP 8 Python 代码风格规范。

## 许可证

MIT License

## 联系方式

项目主页: https://github.com/compass-rose/wallet-rpc-privacy
