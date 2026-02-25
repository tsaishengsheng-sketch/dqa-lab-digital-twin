import os
import asyncio
import datetime
import random
import json
from fastapi import FastAPI, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from .serial_reader import AsyncSerialReader
from .sop import router as sop_router
from .models import SessionLocal, SopTemplate

app = FastAPI(title="KSON AICM Digital Twin Server")
app.state.AICM_CACHE = {} 
background_tasks = set()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 核心控制接口 ---

@app.post("/api/stop/emergency")
async def emergency_stop():
    """🚨 緊急停止：立即歸零，解除所有鎖定"""
    cache = app.state.AICM_CACHE
    for device_id in cache:
        cache[device_id]["status"] = "IDLE"
        cache[device_id]["running_sop_id"] = None
        cache[device_id]["running_sop_name"] = "None"
    print("\n🚨 [SYSTEM] EMERGENCY STOP EXECUTED.")
    return {"status": "success"}

@app.post("/api/stop/pause")
async def pause_test():
    """⏸️ 暫停切換：保留數值但解開前端啟動按鈕鎖定"""
    cache = app.state.AICM_CACHE
    for device_id in cache:
        cache[device_id]["status"] = "PAUSED"
    print("\n⏸️ [SYSTEM] TEST PAUSED. WAITING FOR NEW COMMAND.")
    return {"status": "success"}

@app.post("/api/stop/normal")
async def normal_stop():
    """⏹️ 正常停止：標記結束，模擬器會開始引導溫度回歸室溫"""
    cache = app.state.AICM_CACHE
    for device_id in cache:
        cache[device_id]["status"] = "FINISHING"
        cache[device_id]["running_sop_id"] = None
        cache[device_id]["running_sop_name"] = "Finishing..."
    print("\n⏹️ [SYSTEM] NORMAL STOP. RETURNING TO AMBIENT.")
    return {"status": "success"}

@app.get("/api/latest")
async def get_latest():
    cache = app.state.AICM_CACHE
    if not cache:
        return {"status": "IDLE", "temperature": 25.0, "humidity": 55.0, "running_sop_name": "None", "timestamp": "--:--:--"}
    return list(cache.values())[0]

# --- 物理模擬引擎 ---

async def data_simulator():
    while True:
        cache = app.state.AICM_CACHE
        db = SessionLocal()
        try:
            for device_id in cache:
                item = cache[device_id]
                status = item.get("status")
                
                # 運作邏輯
                if status == "RUNNING" and item.get("running_sop_id"):
                    sop = db.query(SopTemplate).filter(SopTemplate.sop_id == item["running_sop_id"]).first()
                    if sop:
                        target_temp = 85.0 if "高溫" in sop.name else -40.0 if "低溫" in sop.name else 25.0
                        diff = target_temp - item["temperature"]
                        item["temperature"] += (0.8 if diff > 0 else -0.8) + random.uniform(-0.1, 0.1) if abs(diff) > 0.1 else random.uniform(-0.02, 0.02)
                        print(f"\r📊 [RUN] {sop.name} | 目標: {target_temp}°C | 當前: {item['temperature']:.2f}°C", end="")
                
                elif status == "PAUSED":
                    print(f"\r⏸️ [PAUSE] 保持在 {item['temperature']:.2f}°C", end="")
                
                else: # IDLE 或 FINISHING
                    diff = 25.0 - item["temperature"]
                    if abs(diff) > 0.5:
                        item["temperature"] += (0.3 if diff > 0 else -0.3)
                    print(f"\r💤 [IDLE/FINISH] 回歸室溫中: {item['temperature']:.2f}°C", end="")

                item["timestamp"] = datetime.datetime.now().strftime("%H:%M:%S")
            await asyncio.sleep(1)
        finally:
            db.close()

@app.on_event("startup")
async def startup_event():
    # 串口與模擬器啟動
    sim_task = asyncio.create_task(data_simulator())
    background_tasks.add(sim_task)

app.include_router(sop_router, prefix="/api/sop")