# 🚀 MetaMask 真实流量捕获 - 快速参考

## ⚡ 一键启动

```bash
# 确保已配置 .env 文件中的 REAL_RPC_URL
./start_real_capture.sh
```

## 📋 快速配置步骤

### 1. 获取免费 RPC URL

| 提供商 | URL | 说明 |
|--------|-----|------|
| **Infura** | https://infura.io | 推荐，免费额度大 |
| **Alchemy** | https://www.alchemy.com | 免费，稳定 |
| **Ankr** | https://rpc.ankr.com/eth | 完全免费公链 |

### 2. 编辑 .env 文件

```bash
nano .env

# 修改这一行
REAL_RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

### 3. 配置 MetaMask

```
网络名称:   Ethereum (隐私分析)
RPC URL:    http://localhost:8545
链 ID:      1
货币符号:   ETH
```

### 4. 开始使用

切换到新网络 → 正常使用 MetaMask → 自动捕获流量

---

## 📊 查看分析结果

### 获取会话列表
```bash
curl http://localhost:8000/api/v1/sessions
```

### 获取流量数据
```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/traffic
```

### 检测隐私泄露
```bash
curl http://localhost:8000/api/v1/sessions/{SESSION_ID}/leaks
```

### 运行风险评估
```bash
curl -X POST http://localhost:8000/api/v1/sessions/{SESSION_ID}/assess
```

### 查看完整 API 文档
```
http://localhost:8000/docs
```

---

## 🎯 测试流程示例

```bash
# 1. 启动服务
./start_real_capture.sh

# 2. 在 MetaMask 中添加自定义网络并切换

# 3. 执行一些操作（查看余额、转账等）

# 4. 获取会话 ID
SESSION_ID=$(curl -s http://localhost:8000/api/v1/sessions | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['sessions'][0]['id'])")

# 5. 查看捕获的流量
curl http://localhost:8000/api/v1/sessions/$SESSION_ID/traffic

# 6. 运行风险分析
curl -X POST http://localhost:8000/api/v1/sessions/$SESSION_ID/assess | python3 -m json.tool
```

---

## ⚠️ 注意事项

✅ **安全**:
- 代理只转发请求，不存储私钥
- 本地运行，不暴露到公网

✅ **不影响配置**:
- 只是添加新的 RPC 端点
- 可以随时切换回原来的网络

⚠️ **使用时**:
- 需要一直运行代理服务
- 操作完成后记得停止
- 不要在公共网络使用此代理

---

## 🔧 手动启动（如果脚本失败）

```bash
# 终端 1: 启动后端
source venv/bin/activate
uvicorn app.main:app --port 8000

# 终端 2: 启动代理
source venv/bin/activate
python rpc_proxy.py --port 8545 --real-rpc "YOUR_RPC_URL"
```

---

## 📖 相关文档

- 完整指南: [DOCS/REAL_TRAFFIC_GUIDE.md](REAL_TRAFFIC_GUIDE.md)
- 用户手册: [USER_MANUAL.md](USER_MANUAL.md)
- API 文档: http://localhost:8000/docs

---

## 🆘 常见问题

**Q: 没有反应？**
→ 确保两个终端都在运行，端口 8000 和 8545 都在监听

**Q: MetaMask 显示网络错误？**
→ 检查代理服务是否运行，确认 REAL_RPC_URL 正确

**Q: 如何停止？**
→ Ctrl+C 或关闭终端

**Q: 会影响其他操作吗？**
→ 不会，只是捕获流量，不影响正常使用

---

## 🎉 开始使用

```bash
# 1. 获取免费 RPC URL
# 访问: https://infura.io 注册

# 2. 编辑配置
nano .env
# 设置 REAL_RPC_URL

# 3. 启动
./start_real_capture.sh

# 4. 配置 MetaMask 并使用

# 5. 查看结果
curl http://localhost:8000/docs
```

**就这么简单！🚀**
