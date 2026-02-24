# Getting Started & Deployment Guide

## English Version

### 1. Prerequisites
Before setting up the project, ensure your environment meets the following requirements:
* **Python**: Version 3.10 or higher.
* **Package Manager**: `pip` (standard with Python).
* **Internet Connection**: Required for Web3.py to perform certain blockchain-related validation logic.

### 2. Installation
First, clone the repository to your local machine and install the necessary dependencies.
```bash
# Clone the repository
git clone [https://github.com/compass-rose/wallet-rpc-privacy.git](https://github.com/compass-rose/wallet-rpc-privacy.git)

# Enter the project directory
cd wallet-rpc-privacy

# Install dependencies from requirements.txt
pip install -r requirements.txt
3. Running the Service
Launch the FastAPI server using Uvicorn. The --reload flag is recommended for development as it automatically restarts the server when code changes are detected.

Bash
uvicorn app.main:app --reload
Once started, the server will be active at: http://127.0.0.1:8000

4. Testing the API
The system provides a built-in interactive documentation interface (Swagger UI) for quick testing.

Open your web browser and navigate to http://127.0.0.1:8000/docs.

Locate the POST /api/v1/analyze endpoint and click to expand it.

Click the "Try it out" button on the right.

Replace the default JSON in the Request Body with a sample RPC payload (e.g., containing a wallet address or eth_getBalance method).

：
{
  "session_id": "METAMASK-SEPOLIA-SCAN-001",
  "rpc_method": "eth_getBalance",
  "request_body": "Querying balance for 0xd6f755FAF7C7D79Bc9149C435f94869a80E67824. System call: eth_getTransactionCount. Note: handle with care.",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MetaMask/11.0.0",
  "request_timestamp": "2024-02-24T14:00:00Z"
}

Click the large blue "Execute" button.

Scroll down to "Server response" to view the structured privacy leakage report (JSON format).

启动与部署指南
中文版
1. 环境要求
在部署项目之前，请确保您的环境满足以下要求：

Python: 3.10 或更高版本。

包管理器: pip（Python 自带）。

网络连接: 必须联网，以便 Web3.py 执行特定的区块链相关校验逻辑。

2. 安装步骤
首先，将仓库克隆到本地并安装所需的依赖项。

Bash
# 克隆仓库
git clone [https://github.com/compass-rose/wallet-rpc-privacy.git](https://github.com/compass-rose/wallet-rpc-privacy.git)

# 进入项目目录
cd wallet-rpc-privacy

# 从 requirements.txt 安装依赖
pip install -r requirements.txt
3. 运行服务
使用 Uvicorn 启动 FastAPI 服务器。建议在开发环境下使用 --reload 标志，以便在检测到代码更改时自动重启服务器。

Bash
uvicorn app.main:app --reload
启动后，服务器将运行在：http://127.0.0.1:8000

4. 测试接口
系统提供了一个内置的交互式文档界面（Swagger UI）用于快速测试。

打开浏览器并访问 http://127.0.0.1:8000/docs。

找到 POST /api/v1/analyze 接口并点击展开。

点击右侧的 "Try it out"（开始测试）按钮。

将请求体（Request Body）中的默认 JSON 替换为示例 RPC 数据（例如包含钱包地址或 eth_getBalance 方法的内容）。

：
{
  "session_id": "METAMASK-SEPOLIA-SCAN-001",
  "rpc_method": "eth_getBalance",
  "request_body": "Querying balance for 0xd6f755FAF7C7D79Bc9149C435f94869a80E67824. System call: eth_getTransactionCount. Note: handle with care.",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MetaMask/11.0.0",
  "request_timestamp": "2024-02-24T14:00:00Z"
}

点击蓝色的 "Execute"（执行）按钮。

向下滚动到 "Server response"（服务器响应）部分，即可查看生成的结构化隐私泄露报告（JSON 格式）。