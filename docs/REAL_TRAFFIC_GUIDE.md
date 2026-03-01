# MetaMask 真实流量捕获 - 完整指南

## 📋 目录
1. [方案概述](#方案概述)
2. [方案一：本地 RPC 代理（推荐）](#方案一本地-rpc-代理推荐)
3. [方案二：浏览器扩展捕获](#方案二浏览器扩展捕获)
4. [方案三：Chrome DevTools API](#方案三chrome-devtools-api)
5. [常见问题](#常见问题)

---

## 方案概述

由于 Chrome 插件无法直接配置代理，我们提供三种方案：

| 方案 | 难度 | 适用场景 | 优缺点 |
|------|------|----------|--------|
| **RPC 代理** | ⭐ 简单 | 所有用户 | ✅ 最简单<br>✅ 实时分析<br>❌ 需要修改网络配置 |
| **浏览器扩展** | ⭐⭐ 中等 | 开发者 | ✅ 不需要配置<br>✅ 自动捕获<br>❌ 需要安装扩展 |
| **DevTools API** | ⭐⭐⭐ 困难 | 高级用户 | ✅ 无需额外工具<br>❌ 需要编程 |

---

## 方案一：本地 RPC 代理（推荐）

### 概述

在本地运行一个 RPC 代理服务器，MetaMask 将请求发送到这个代理，代理转发到真实节点并记录流量。

```
MetaMask → 本地代理 (∅:8545) → 真实 RPC 节点
              ↓
         记录→数据库→实时分析
```

### 步骤 1: 获取真实的 RPC URL

你需要一个真实的以太坊 RPC 节点：

**免费选项**:
- Infura: https://infura.io (注册免费)
- Alchemy: https://www.alchemy.com (免费额度)
- Ankr: https://www.ankr.com (免费公链 RPC)

示例 URL:
```
https://mainnet.infura.io/v3/YOUR_PROJECT_ID
https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
https://rpc.ankr.com/eth
```

### 步骤 2: 配置环境变量

编辑 `.env` 文件：

```bash
# 你的真实 RPC 端点
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# 本地分析服务地址
PRIVACY_API_URL=http://localhost:8000
```

### 步骤 3: 启动分析服务

```bash
# 终端 1: 启动隐私分析后端
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 步骤 4: 启动 RPC 代理

```bash
# 终端 2: 启动 RPC 代理
source venv/bin/activate

python rpc_proxy.py \
  --port 8545 \
  --real-rpc "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
```

你应该看到：

```
🚀 RPC Proxy Server - MetaMask 流量捕获
============================================================
📍 监听地址: http://0.0.0.0:8545
🔄 真实 RPC: https://mainnet.infura.io/v3/YOUR_PROJECT_ID
📊 分析 API: http://localhost:8000
============================================================
```

### 步骤 5: 在 MetaMask 中配置自定义网络

1. 打开 MetaMask
2. 点击网络选择器 → 添加网络 → 手动添加网络
3. 填写以下信息：

| 字段 | 值 |
|------|---|
| **网络名称** | Ethereum (隐私分析) |
| **新的 RPC URL** | `http://localhost:8545` |
| **链 ID** | `1` |
| **货币符号** | `ETH` |
| **区块浏览器URL** | `https://etherscan.io` |

4. 保存网络

### 步骤 6: 开始捕获

1. 切换到新添加的网络 "Ethereum (隐私分析)"
2. 正常使用 MetaMask（转账、交互 DApps 等）
3. 流量会被自动捕获并记录

### 步骤 7: 查看分析结果

**创建分析会话**:
```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_type": "MetaMask-Chrome",
    "rpc_provider": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
  }'
```

**获取流量数据**:
```bash
SESSION_ID="返回的会话ID"
curl http://localhost:8000/api/v1/sessions/${SESSION_ID}/traffic
```

**运行风险评估**:
```bash
curl -X POST http://localhost:8000/api/v1/sessions/${SESSION_ID}/assess
```

### 使用示例视频

```bash
# 1. 启动服务（终端 1）
uvicorn app.main:app --reload

# 2. 启动代理（终端 2）
python rpc_proxy.py

# 3. 在 MetaMask 中切换到自定义网络

# 4. 使用 MetaMask 进行操作（例如查看余额）

# 5. 查看捕获的流量
curl http://localhost:8000/api/v1/sessions

# 6. 获取会话 ID 后查看流量
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic

# 7. 运行隐私检测
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks

# 8. 运行风险评估
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

---

## 方案二：浏览器扩展捕获

如果你觉得配置自定义网络太麻烦，可以创建一个简单的浏览器扩展。

### 概述

创建一个 Chrome 扩展，拦截 MetaMask 的网络请求并将数据发送到分析服务器。

### 步骤 1: 创建扩展目录

```bash
mkdir metamask-capture-extension
cd metamask-capture-extension
```

### 步骤 2: 创建 manifest.json

```json
{
  "manifest_version": 3,
  "name": "MetaMask Flow Capture",
  "version": "1.0.0",
  "description": "Capture MetaMask traffic for privacy analysis",
  "permissions": [
    "webRequest",
    "storage"
  ],
  "host_permissions": [
    "https://*/*", "https://rpc.*/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_popup": "popup.html"
  }
}
```

### 步骤 3: 创建 background.js

```javascript
let capturedRequests = [];
const API_URL = "http://localhost:8000";
let sessionId = null;

// 初始化会话
async function initSession() {
  try {
    const response = await fetch(`${API_URL}/api/v1/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        wallet_type: "MetaMask-Chrome-Extension",
        rpc_provider: "Captured via Extension"
      })
    });
    const data = await response.json();
    sessionId = data.data.id;
    console.log('Session created:', sessionId);
  } catch (error) {
    console.error('Failed to create session:', error);
  }
}

// 拦截请求
chrome.webRequest.onBeforeRequest.addListener(
  async (details) => {
    // 只拦截 JSON-RPC 请求
    if (details.requestBody?.raw && details.method === "POST") {
      try {
        const body = JSON.parse(
          String.fromCharCode.apply(null, 
            new Uint8Array(details.requestBody.raw[0].bytes)
          )
        );

        if (body.method && body.method.startsWith('eth_')) {
          const record = {
            method: details.method,
            endpoint: details.url,
            rpc_method: body.method,
            request_body: JSON.stringify(body.params),
            request_timestamp: new Date().toISOString()
          };

          // 发送到分析服务器
          if (sessionId) {
            fetch(`${API_URL}/api/v1/sessions/${sessionId}/traffic/record`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(record)
            }).catch(err => console.log('Failed to record:', err));
          }

          capturedRequests.push(record);
        }
      } catch (e) {
        // 忽略解析错误
      }
    }
  },
  { urls: ["<all_urls>"] },
  ["requestBody"]
);

// 扩展启动时初始化
initSession();
```

### 步骤 4: 创建 popup.html

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { width: 300px; padding: 10px; font-family: Arial; }
    .status { padding: 10px; margin-bottom: 10px; border-radius: 5px; }
    .status.success { background: #d4edda; color: #155724; }
    .button { width: 100%; padding: 10px; margin: 5px 0; cursor: pointer; }
  </style>
</head>
<body>
  <h3>MetaMask 流量捕获</h3>
  <div id="status" class="status">初始化中...</div>
  <div class="stats">
    已捕获: <span id="count">0</span> 条请求
  </div>
  <button class="button" onclick="openAnalysis()">查看分析</button>
  <button class="button" onclick="clearData()">清除数据</button>
  <script src="popup.js"></script>
</body>
</html>
```

### 步骤 5: 创建 popup.js

```javascript
// 从 background.js 获取数据
chrome.runtime.getBackgroundPage((bg) => {
  if (bg?.capturedRequests) {
    document.getElementById('count').textContent = 
      bg.capturedRequests.length;
    document.getElementById('status').textContent = '运行中';
    document.getElementById('status').classList.add('success');
  }
});

function openAnalysis() {
  chrome.tabs.create({ url: 'http://localhost:8000/docs' });
}

function clearData() {
  if (confirm('确定清除所有捕获的数据？')) {
    chrome.runtime.getBackgroundPage((bg) => {
      bg.capturedRequests = [];
      document.getElementById('count').textContent = '0';
    });
  }
}
```

### 步骤 6: 安装扩展

1. 打开 Chrome
2. 进入 `chrome://extensions/`
3. 启用"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择 `metamask-capture-extension` 目录
6. 启动后端分析和代理服务（步骤同方案一）

---

## 方案三：Chrome DevTools API

如果你不想安装扩展或修改网络配置，可以使用 Chrome DevTools Protocol。

### 使用 Selenium + Puppeteer

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

# 配置 Chrome
options = Options()
options.add_argument("--load-extension=/path/to/metamask")
options.add_argument("--remote-debugging-port=9222")

# 启动浏览器
driver = webdriver.Chrome(options=options)

# 访问 DApp
driver.get("https://uniswap.org")

# 启用网络监控
driver.execute_cdp_cmd("Network.enable", {})

# 捕获网络事件
def capture_network(params):
    if "eth_" in params.get("request", {}).get("url", ""):
        print("Captured RPC call:", params["request"]["url"])

driver.add_cdp_listener("Network.requestWillBeSent", capture_network)

# 让用户操作
input("按 Enter 开始捕获，操作完成后按 Enter 结束...")

# 关闭
driver.quit()
```

---

## 常见问题

### Q1: 配置自定义网络会影响我的 MetaMask 吗？

**A**: 不会。这只是在 Ethereum 主网络上添加了一个新的 RPC 端点，不会改变你的私钥或现有网络配置。你可以随时切换回原来的网络。

### Q2: 本地代理安全吗？

**A**: 安全。代理只是转发请求到真实的 RPC 节点，不存储私钥或敏感信息。但建议：
- 使用可信的 RPC 提供商（Infura、Alchemy 等）
- 不要在公共网络上暴露代理服务
- 使用完记得停止代理服务

### Q3: 捕获的流量包含我的私钥吗？

**A**: 不会。系统会自动：
- 匿名化钱包地址
- 不存储私钥
- 对 IP 地址进行哈希处理

### Q4: 可以捕获哪些操作的流量？

**A**: 可以捕获几乎所有 MetaMask 操作：
- 查看余额
- 转账
- 交互 DApp（Uniswap、OpenSea 等）
- 查看交易历史
- 签名消息
- 等等...

### Q5: 我需要一直运行代理服务吗？

**A**: 只有在使用 MetaMask 时需要代理运行。操作完成后可以关闭。如果停止代理，MetaMask 会显示网络错误，切换回其他网络即可。

### Q6: 如何切换回原来的网络？

**A**:
1. 在 MetaMask 中点击网络选择器
2. 选择 "Ethereum Mainnet" 或你之前使用的网络
3. 不需要删除自定义网络，以后可以直接使用

---

## 高级用法

### 自动化脚本

创建 `capture_traffic.sh`:

```bash
#!/bin/bash

# 配置
REAL_RPC="https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
PROXY_PORT=8545

# 启动后端
echo "🚀 启动隐私分析服务..."
uvicorn app.main:app --port 8000 &
BACKEND_PID=$!

# 启动代理
echo "🔄 启动 RPC 代理..."
python rpc_proxy.py --port $PROXY_PORT --real-rpc "$REAL_RPC" &
PROXY_PID=$!

echo ""
echo "✅ 服务已启动！"
echo "   后端服务: http://localhost:8000"
echo "   RPC 代理: http://localhost:$PROXY_PORT"
echo ""
echo "📝 下一步："
echo "   1. 在 MetaMask 中添加自定义网络"
echo "   2. RPC URL: http://localhost:$PROXY_PORT"
echo "   3. 开始使用 MetaMask"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断
trap "kill $BACKEND_PID $PROXY_PID" INT TERM
wait
```

运行：
```bash
chmod +x capture_traffic.sh
./capture_traffic.sh
```

### 定期分析

```python
import requests

def analyze_daily_traffic():
    """每天自动运行分析"""
    # 获取今天的会话
    response = requests.post(
        "http://localhost:8000/api/v1/sessions",
        json={
            "wallet_type": "MetaMask",
            "rpc_provider": "daily_analysis"
        }
    )
    session_id = response.json()["data"]["id"]
    
    # 运行风险评估
    response = requests.post(
        f"http://localhost:8000/api/v1/sessions/{session_id}/assess"
    )
    
    result = response.json()["data"]
    print(f"风险评分: {result['overall_score']}")
    print(f"风险等级: {result['risk_level']}")

if __name__ == "__main__":
    analyze_daily_traffic()
```

---

## 下一步

1. ✅ 测试代理服务器
2. ✅ 验证流量捕获
3. ✅ 运行隐私分析
4. ✅ 查看分析报告
5. ✅ 根据建议改进隐私

查看 API 文档: http://localhost:8000/docs
查看项目文档: [USER_MANUAL.md](USER_MANUAL.md)
