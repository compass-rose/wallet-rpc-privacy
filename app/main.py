"""
Wallet / RPC Privacy Leakage Measurement System
钱包与RPC隐私泄露测量系统

Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(
    title="Wallet / RPC Privacy Leakage Measurement",
    description="A system to measure and quantify privacy leakage in wallet-RPC communications",
    version="0.1.0"
)


@app.get("/")
async def root() -> JSONResponse:
    """
    Root endpoint - Hello World

    Returns:
        JSONResponse: Welcome message
    """
    return JSONResponse({
        "message": "Welcome to Wallet / RPC Privacy Leakage Measurement System",
        "version": "0.1.0",
        "status": "healthy"
    })


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint

    Returns:
        JSONResponse: Health status
    """
    return JSONResponse({
        "status": "healthy",
        "service": "wallet-rpc-privacy"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
