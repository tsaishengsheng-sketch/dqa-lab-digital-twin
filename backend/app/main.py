import asyncio
import datetime
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .sop import router as sop_router
from .sop_execution import router as execution_router
from .models import SessionLocal, DeviceData
from .standards import get_ramp_rate, get_standard

app = FastAPI(title="KSON AICM Digital Twin Server")
app.state.AICM_CACHE = {}
background_tasks = set()
app.include_router(sop_router, prefix="/api/sop", tags=["sop"])
app.include_router(execution_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 核心控制接口 ---


@app.post("/api/stop/emergency")
async def emergency_stop():
    """🚨 緊急停止：中斷所有輸出"""
    cache = app.state.AICM_CACHE
    for device_id in cache:
        cache[device_id]["status"] = "EMERGENCY"
        cache[device_id]["running_sop_id"] = None
        cache[device_id]["running_sop_name"] = "🚨 緊急停止中 - 待確認安全"
    print("\n" + "!" * 60)
    print("🚨 [ALERT] EMERGENCY STOP ACTIVATED.")
    print("📢 [SYSTEM] 設備輸出已中斷，等待操作員確認降溫指令。")
    print("!" * 60 + "\n")
    return {"status": "success", "message": "Emergency activated"}


@app.post("/api/stop/pause")
async def pause_test():
    cache = app.state.AICM_CACHE
    for device_id in cache:
        # 暫停切換：RUNNING ↔ PAUSED
        if cache[device_id]["status"] == "RUNNING":
            cache[device_id]["status"] = "PAUSED"
        elif cache[device_id]["status"] == "PAUSED":
            cache[device_id]["status"] = "RUNNING"
    return {"status": "success"}


@app.post("/api/stop/normal")
async def normal_stop():
    """⏹️ 正常停止：進入收尾降溫模式"""
    cache = app.state.AICM_CACHE
    for device_id in cache:
        cache[device_id]["status"] = "FINISHING"
        cache[device_id]["running_sop_name"] = "系統自動降溫收尾中..."
    return {"status": "success"}


@app.get("/api/latest")
async def get_latest():
    cache = app.state.AICM_CACHE

    if not cache or "KSON_CH01" not in cache:
        return {
            "status": "OFFLINE",
            "temperature": 0.0,
            "humidity": 0.0,
            "running_sop_name": "未連線",
            "description": "等待模擬器啟動...",
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
        }

    data = cache["KSON_CH01"]
    status = data.get("status", "OFFLINE")

    if status == "RUNNING":
        description = f"正在執行：{data.get('running_sop_name')}。溫度按標準速率變化。"
    elif status == "PAUSED":
        description = f"已暫停：{data.get('running_sop_name')}。點擊暫停切換可繼續。"
    elif status == "EMERGENCY":
        description = "⚠️ 緊急停止已觸發，請確認設備安全後按正常停止。"
    elif status == "FINISHING":
        description = "測試已結束，正在自動降溫到 25°C，請稍候..."
    elif status == "IDLE":
        description = "系統待機中，請選擇 SOP 後點擊啟動。"
    else:
        description = "等待連線..."

    return {
        "status": status,
        "temperature": data.get("temperature", 0.0),
        "humidity": data.get("humidity", 0.0),
        "running_sop_name": data.get("running_sop_name", "STANDBY"),
        "description": description,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
    }


# --- 物理模擬引擎 ---


async def data_simulator():
    """物理模擬器 - 遵守標準的升降溫速率"""
    while True:
        cache = app.state.AICM_CACHE
        db = SessionLocal()
        try:
            for device_id, item in cache.items():
                status = item.get("status", "OFFLINE")
                current_temp = item.get("temperature", 25.0)

                if status == "RUNNING":
                    standard_id = item.get("standard_id", "IEC60068_CYCLE")
                    max_ramp_rate = get_ramp_rate(standard_id)
                    standard = get_standard(standard_id)

                    if standard:
                        target_temp = standard.get("high_temperature") or standard.get(
                            "target_temperature", 25.0
                        )
                    else:
                        target_temp = 25.0

                    temp_diff = target_temp - current_temp
                    if abs(temp_diff) > 0.1:
                        max_change_per_sec = max_ramp_rate / 60.0
                        actual_change = min(abs(temp_diff), max_change_per_sec)
                        new_temp = current_temp + (
                            actual_change if temp_diff > 0 else -actual_change
                        )
                    else:
                        new_temp = current_temp

                    new_temp += random.uniform(-0.1, 0.1)
                    item["temperature"] = round(new_temp, 2)

                elif status == "FINISHING":
                    diff = 25.0 - current_temp
                    if abs(diff) > 0.5:
                        item["temperature"] += 0.4 if diff > 0 else -0.4
                    else:
                        # ✅ 降溫完成，自動回到 IDLE
                        item["temperature"] = 25.0
                        item["status"] = "IDLE"
                        item["running_sop_name"] = "STANDBY"
                        print("✅ [SYSTEM] 降溫完成，系統回到待機狀態。")

                elif status == "EMERGENCY":
                    # 緊急停止時溫度微幅抖動（不主動降溫）
                    item["temperature"] += random.uniform(-0.05, 0.05)

                # 保存到資料庫
                if status in ["RUNNING", "FINISHING", "PAUSED", "EMERGENCY"]:
                    new_record = DeviceData(
                        device_id=device_id,
                        temperature=item["temperature"],
                        humidity=item.get("humidity", 55.0),
                        timestamp=datetime.datetime.now(),
                    )
                    db.add(new_record)
                    db.commit()

            await asyncio.sleep(1)
        except Exception as e:
            print(f"Simulator Error: {e}")
            db.rollback()
        finally:
            db.close()


@app.on_event("startup")
async def startup_event():
    from .database import init_db

    init_db()

    app.state.AICM_CACHE = {
        "KSON_CH01": {
            "temperature": 25.0,
            "humidity": 55.0,
            "status": "OFFLINE",
            "running_sop_name": "STANDBY",
            "timestamp": "00:00:00",
        }
    }

    sim_task = asyncio.create_task(data_simulator())
    background_tasks.add(sim_task)
    print("✅ System initialized")
