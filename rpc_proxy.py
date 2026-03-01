"""
RPC Proxy Server - 捕获 MetaMask 流量

这个代理服务器:
1. 监听本地端口 (默认 8545)
2. 接收 MetaMask 的 JSON-RPC 请求
3. 转发到真实 RPC 节点
4. 记录流量到我们的系统
5. 返回响应给 MetaMask
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional
import json
import os
from pathlib import Path

app = FastAPI()

# 真实 RPC 节点配置
REAL_RPC_URL = os.getenv("REAL_RPC_URL", "https://mainnet.infura.io/v3/YOUR_PROJECT_ID")

# 我们的隐私分析 API
PRIVACY_API_URL = os.getenv("PRIVACY_API_URL", "http://localhost:8000")

# 当前会话 ID（从 API 获取）
CURRENT_SESSION_ID: Optional[str] = None

# HTTP 客户端
http_client = httpx.AsyncClient(timeout=30.0)


async def get_or_create_session() -> str:
    """获取或创建分析会话"""
    global CURRENT_SESSION_ID

    if CURRENT_SESSION_ID:
        return CURRENT_SESSION_ID

    # 创建新会话
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PRIVACY_API_URL}/api/v1/sessions",
            json={
                "wallet_type": "MetaMask",
                "rpc_provider": REAL_RPC_URL
            },
            timeout=10.0
        )
        response.raise_for_status()
        CURRENT_SESSION_ID = response.json()["data"]["id"]

    print(f"✓ Created session: {CURRENT_SESSION_ID}")
    return CURRENT_SESSION_ID


@app.post("/")
async def proxy_rpc(request: Request):
    """
    代理 JSON-RPC 请求

    流程:
    1. 接收 MetaMask 的请求
    2. 解析 RPC 方法
    3. 记录请求信息
    4. 转发到真实 RPC 节点
    5. 记录响应信息
    6. 返回响应
    """
    try:
        # 1. 获取请求体
        body = await request.json()
        session_id = await get_or_create_session()

        # 2. 解析 RPC 信息
        method = body.get("method", "unknown")
        params = body.get("params", [])
        request_id = body.get("id")
        timestamp = datetime.now(timezone.utc)

        # 3. 记录到隐私分析系统
        try:
            record_data = {
                "method": "POST",
                "endpoint": REAL_RPC_URL,
                "rpc_method": method,
                "request_body": json.dumps(params),
                "request_timestamp": timestamp.isoformat(),
                "ip_address_hash": "127.0.0.1",  # 本地请求
            }

            # 发送到我们的系统（异步，不阻塞）
            asyncio.create_task(
                send_record_to_api(session_id, record_data)
            )
        except Exception as e:
            print(f"⚠ Warning: Failed to record traffic: {e}")

        # 4. 转发到真实 RPC 节点
        headers = {
            "Content-Type": "application/json",
            "User-Agent": request.headers.get("User-Agent", "MetaMask"),
        }

        rpc_response = await http_client.post(
            REAL_RPC_URL,
            json=body,
            headers=headers
        )

        # 5. 记录响应信息
        response_data = {
            "response_status": rpc_response.status_code,
            "response_time_ms": 0,  # 实际应该计算
        }

        # 6. 返回 JSON 响应
        if rpc_response.headers.get("content-type", "").startswith("application/json"):
            return JSONResponse(
                content=rpc_response.json(),
                status_code=rpc_response.status_code
            )
        else:
            return JSONResponse(
                content=rpc_response.text,
                status_code=rpc_response.status_code
            )

    except json.JSONDecodeError:
        return JSONResponse(
            content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}, "id": None},
            status_code=400
        )
    except httpx.HTTPError as e:
        return JSONResponse(
            content={"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": None},
            status_code=502
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        return JSONResponse(
            content={"jsonrpc": "2.0", "error": {"code": -32603, "message": "Internal error"}, "id": None},
            status_code=500
        )


async def send_record_to_api(session_id: str, record_data: Dict):
    """异步发送流量记录到分析系统"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{PRIVACY_API_URL}/api/v1/sessions/{session_id}/traffic/record",
                json=record_data,
                timeout=5.0
            )
    except Exception as e:
        print(f"⚠ Failed to send record to API: {e}")


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "rpc-proxy",
        "real_rpc": REAL_RPC_URL,
        "session_id": CURRENT_SESSION_ID
    }


@app.on_event("shutdown")
async def shutdown():
    """清理资源"""
    await http_client.aclose()


if __name__ == "__main__":
    import uvicorn
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8545, help="监听端口")
    parser.add_argument("--real-rpc", default=REAL_RPC_URL, help="真实 RPC URL")
    args = parser.parse_args()

    REAL_RPC_URL = args.real_rpc

    print("=" * 60)
    print("🚀 RPC Proxy Server - MetaMask 流量捕获")
    print("=" * 60)
    print(f"📍 监听地址: http://{args.host}:{args.port}")
    print(f"🔄 真实 RPC: {REAL_RPC_URL}")
    print(f"📊 分析 API: {PRIVACY_API_URL}")
    print("=" * 60)
    print()
    print("📝 使用方法:")
    print("   1. 启动隐私分析服务: uvicorn app.main:app --reload")
    print("   2. 启动本代理服务器: python rpc_proxy.py")
    print("   3. 在 MetaMask 中添加自定义网络:")
    print(f"      RPC URL: http://localhost:{args.port}")
    print("   4. 开始使用 MetaMask，流量将被自动捕获")
    print()
    print("=" * 60)

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
