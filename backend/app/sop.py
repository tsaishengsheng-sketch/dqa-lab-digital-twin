from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from .models import SessionLocal, SopTemplate
from .standards import STANDARDS_AND_SOPS, get_sop_by_standard

router = APIRouter()

class SopResponse(BaseModel):
    sop_id: str
    name: str
    test_type: str
    version: str
    steps: List[dict]

@router.get("/", response_model=List[SopResponse])
def list_sops():
    """
    獲取所有 SOP 列表
    優先從 standards.py 獲取，其次從資料庫獲取
    """
    sops: List[SopResponse] = []
    
    # 1. 先從 standards.py 獲取標準 SOP
    for standard_id, standard_data in STANDARDS_AND_SOPS.items():
        steps = standard_data.get("steps", [])
        sop = SopResponse(
            sop_id=standard_data.get("sop_id", ""),
            name=standard_data.get("name", ""),
            test_type=standard_data.get("test_type", ""),
            version=standard_data.get("version", ""),
            steps=steps if isinstance(steps, list) else []
        )
        sops.append(sop)
        print(f"✅ Loaded from standards.py: {standard_data.get('name')}")
    
    # 2. 再從資料庫獲取其他 SOP（避免重複）
    db = SessionLocal()
    try:
        db_sops = db.query(SopTemplate).all()
        for s in db_sops:
            # 避免重複
            if not any(sop.sop_id == s.sop_id for sop in sops):
                sop = SopResponse(
                    sop_id=s.sop_id,
                    name=s.name,
                    test_type=s.test_type,
                    version=s.version,
                    steps=json.loads(s.steps_json) if s.steps_json else []
                )
                sops.append(sop)
                print(f"✅ Loaded from database: {s.name}")
    finally:
        db.close()
    
    print(f"📊 Total SOPs loaded: {len(sops)}")
    return sops

@router.post("/start")
async def start_sop(request: Request, payload: Dict[str, Any] = Body(...)):
    """啟動 SOP 測試"""
    print(f"📥 Received payload: {payload}")
    
    sop_id: str = payload.get("sop_id", "")
    device_key: str = "KSON_CH01"
    
    # 從 standards.py 查找標準 ID
    standard_id: str = "IEC60068_CYCLE"
    for std_id, std_data in STANDARDS_AND_SOPS.items():
        if std_data.get("sop_id") == sop_id:
            standard_id = std_id
            break
    
    # 如果沒找到，用預設值
    if standard_id == "IEC60068_CYCLE":
        standard_id = payload.get("standard_id", "IEC60068_CYCLE")

    if not sop_id:
        raise HTTPException(status_code=400, detail="sop_id 不能為空")

    cache = request.app.state.AICM_CACHE
    
    # 檢查是否已在運行
    if device_key in cache and cache[device_key].get("status") == "RUNNING":
        raise HTTPException(status_code=400, detail="機台正在執行中，請先停止目前程序。")

    # 初始化快取
    if device_key not in cache:
        cache[device_key] = {
            "temperature": 25.0,
            "humidity": 55.0,
            "status": "IDLE"
        }
    
    # 獲取 SOP 名稱
    sop_name: str = sop_id
    
    # 優先從 standards 獲取
    for std_id, std_data in STANDARDS_AND_SOPS.items():
        if std_data.get("sop_id") == sop_id:
            sop_name = std_data.get("name", sop_id)
            break
    
    # 如果沒找到，再從資料庫找
    if sop_name == sop_id:
        db = SessionLocal()
        try:
            sop = db.query(SopTemplate).filter(SopTemplate.sop_id == sop_id).first()
            if sop:
                sop_name = sop.name
        finally:
            db.close()
    
    # 更新狀態
    cache[device_key]["status"] = "RUNNING"
    cache[device_key]["running_sop_id"] = sop_id
    cache[device_key]["running_sop_name"] = sop_name
    cache[device_key]["standard_id"] = standard_id
    
    print(f"🔥 Started SOP: {sop_id} ({sop_name}) with standard: {standard_id}")
    return {"status": "success", "message": f"SOP {sop_name} 已啟動"}