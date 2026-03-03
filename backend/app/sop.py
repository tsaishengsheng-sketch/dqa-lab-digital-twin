from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import json
from .models import SessionLocal, SopTemplate
from .standards import STANDARDS_AND_SOPS

router = APIRouter()


class SopResponse(BaseModel):
    sop_id: str
    standard_id: str
    name: str
    test_type: str
    version: str
    steps: List[dict]


class StartSopRequest(BaseModel):
    sop_id: str
    device_id: str = "KSON_CH01"
    standard_id: str = "IEC60068_CYCLE"


@router.get("/", response_model=List[SopResponse])
def list_sops():
    """獲取所有 SOP 列表，優先從 standards.py，其次從資料庫"""
    sops: List[SopResponse] = []

    # 1. 從 standards.py 載入
    for standard_id, standard_data in STANDARDS_AND_SOPS.items():
        sop = SopResponse(
            standard_id=standard_id,
            sop_id=standard_data.get("sop_id", ""),
            name=standard_data.get("name", ""),
            test_type=standard_data.get("test_type", ""),
            version=standard_data.get("version", ""),
            steps=standard_data.get("steps", []),
        )
        sops.append(sop)

    # 2. 從資料庫補充（避免重複）
    db = SessionLocal()
    try:
        db_sops = db.query(SopTemplate).all()
        existing_ids = {sop.sop_id for sop in sops}
        for s in db_sops:
            if s.sop_id not in existing_ids:
                sop = SopResponse(
                    standard_id=getattr(s, "standard_id", ""),
                    sop_id=s.sop_id,
                    name=s.name,
                    test_type=s.test_type,
                    version=s.version,
                    steps=json.loads(s.steps_json) if s.steps_json else [],
                )
                sops.append(sop)
    finally:
        db.close()

    return sops


@router.post("/start")
async def start_sop(request: Request, payload: StartSopRequest):
    """啟動 SOP 測試"""
    sop_id = payload.sop_id
    standard_id = payload.standard_id  # 直接用前端傳來的，不需要重新查找
    device_key = "KSON_CH01"

    cache = request.app.state.AICM_CACHE

    # 檢查是否已在運行
    if device_key in cache and cache[device_key].get("status") == "RUNNING":
        raise HTTPException(
            status_code=400, detail="機台正在執行中，請先停止目前程序。"
        )

    # 初始化快取（如果不存在）
    if device_key not in cache:
        cache[device_key] = {"temperature": 25.0, "humidity": 55.0, "status": "IDLE"}

    # 取得 SOP 名稱，優先從 standards.py
    sop_name = sop_id
    for std_data in STANDARDS_AND_SOPS.values():
        if std_data.get("sop_id") == sop_id:
            sop_name = std_data.get("name", sop_id)
            break

    # 找不到再從資料庫查
    if sop_name == sop_id:
        db = SessionLocal()
        try:
            sop = db.query(SopTemplate).filter(SopTemplate.sop_id == sop_id).first()
            if sop:
                sop_name = sop.name
        finally:
            db.close()

    # 更新快取狀態
    cache[device_key].update(
        {
            "status": "RUNNING",
            "running_sop_id": sop_id,
            "running_sop_name": sop_name,
            "standard_id": standard_id,
        }
    )

    print(f"🔥 Started: {sop_name} (standard: {standard_id})")
    return {"status": "success", "message": f"SOP {sop_name} 已啟動"}
