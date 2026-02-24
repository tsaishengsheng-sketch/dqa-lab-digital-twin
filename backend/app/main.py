import os  # 確保導入 os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import threading
from dotenv import load_dotenv

from .database import init_db
from .serial_reader import SerialReader
from .sop import router as sop_router
from .sop_execution import router as execution_router
from .models import SessionLocal, DeviceData

# 載入 .env 檔案中的設定
load_dotenv()

app = FastAPI(title="DQA Lab Digital Twin API")

# CORS 設定 (維持原樣)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 記錄請求來源的中介軟體 (維持原樣)
@app.middleware("http")
async def log_request_source(request: Request, call_next):
    # 只針對特定路徑記錄日誌，避免日誌太雜
    if request.url.path in ["/", "/api/latest"]:
        # 安全讀取 client，如果抓不到則顯示 unknown
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else 0
        print(f"🔍 收到來自 {client_host}:{client_port} 的請求: {request.method} {request.url.path}")
    
    response = await call_next(request)
    return response

# --- 修改點：動態取得 Port ---
# os.getenv("SERIAL_PORTS") 會讀取 dev_start.sh 傳進來的 /dev/ttys007
# 如果沒有環境變數，則預設回退到 '/dev/ttys000'，保證不崩潰
target_port = os.getenv("SERIAL_PORTS", "/dev/ttys000")
device_id = os.getenv("DEVICE_NAMES", "CHAMBER_01")

print(f"📡 [Backend] SerialReader 正在嘗試連接: {target_port}")

serial_reader = SerialReader(port=target_port, device_id=device_id)
serial_reader.start()

# 註冊路由 (維持原樣)
app.include_router(sop_router)
app.include_router(execution_router)

# ✅ 提供真實數據的 /api/latest 端點 (維持原樣)
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

# 應用關閉時停止 SerialReader (維持原樣)
@app.on_event("shutdown")
def shutdown_event():
    serial_reader.stop()
    print("SerialReader 已停止")