from fastapi import FastAPI
from fastapi.responses import JSONResponse
from typing import List
from app.models.schemas import NetworkTrafficSchema, PrivacyLeakEventSchema
from app.core.detector import PrivacyDetector

app = FastAPI(
    title="Wallet / RPC Privacy Leakage Measurement",
    description="System to quantify privacy leakage in wallet-RPC communications",
    version="0.1.0"
)

detector = PrivacyDetector()

@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse({"status": "healthy", "message": "Welcome"})

# --- 核心任务 3.2：隐私检测分析接口 ---
@app.post("/api/v1/analyze", response_model=List[PrivacyLeakEventSchema])
async def analyze_rpc_traffic(traffic: NetworkTrafficSchema):
    """
    接收来自 3.1 模块的流量数据，输出符合 9.1 Schema 的隐私泄露事件。
    """
    return detector.analyze_traffic(traffic)

@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse({"status": "healthy"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)