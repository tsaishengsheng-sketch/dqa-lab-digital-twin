from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import threading
import os
from dotenv import load_dotenv

from .database import init_db
from .serial_reader import SerialReader
from .sop import router as sop_router
from .sop_execution import router as execution_router
from .models import SessionLocal, DeviceData

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

# 記錄請求來源的中介軟體（只記錄特定路徑）
@app.middleware("http")
async def log_request_source(request: Request, call_next):
    if request.url.path in ["/", "/api/latest"]:
        client_host = request.client.host
        client_port = request.client.port
        print(f"🔍 收到來自 {client_host}:{client_port} 的請求: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# 啟動 SerialReader 執行緒（請根據實際情況修改 port 和 device_id）
serial_reader = SerialReader(port='/dev/ttys000', device_id="CHAMBER_01")
serial_reader.start()

# 註冊路由
app.include_router(sop_router)
app.include_router(execution_router)

# ✅ 提供真實數據的 /api/latest 端點
@app.get("/api/latest")
@app.get("/api/latest/")
async def latest_data():
    db = SessionLocal()
    latest = db.query(DeviceData).order_by(DeviceData.timestamp.desc()).first()
    db.close()
    if latest:
        return {
            "device_id": latest.device_id,
            "temperature": latest.temperature,
            "humidity": latest.humidity,
            "timestamp": latest.timestamp.isoformat()
        }
    return {"message": "No data yet", "data": []}

# 應用關閉時停止 SerialReader
@app.on_event("shutdown")
def shutdown_event():
    serial_reader.stop()
    print("SerialReader 已停止")