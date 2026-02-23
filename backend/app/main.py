from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from .database import init_db
from .serial_reader import SerialReader
from .sop import router as sop_router
from .sop_execution import router as execution_router

load_dotenv()

app = FastAPI(title="DQA Lab Digital Twin API")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 加入記錄請求來源的中介軟體（已修正）
@app.middleware("http")
async def log_request_source(request: Request, call_next):
    # 只記錄我們感興趣的路徑，避免日誌過多
    if request.url.path in ["/", "/api/latest"]:
        client_host = request.client.host
        client_port = request.client.port
        print(f"🔍 收到來自 {client_host}:{client_port} 的請求: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# 註冊路由
app.include_router(sop_router)
app.include_router(execution_router)

# 其餘程式碼...