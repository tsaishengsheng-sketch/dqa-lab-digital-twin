from fastapi import APIRouter, HTTPException, Body, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from .models import SessionLocal, SopTemplate
from .standards import STANDARDS_AND_SOPS, get_sop_by_standard, get_standard_tree

router = APIRouter()


class SopResponse(BaseModel):
    sop_id: str
    name: str
    test_type: str
    version: str
    steps: List[dict]
    description: Optional[str] = ""


@router.get("/standards/tree")
def get_standards_tree():
    """
    取得完整三層標準樹：法規 → 版本 → 測試條件
    供前端 UI 三步驟選擇使用
    """
    tree = get_standard_tree()
    result = {}
    for std_key, std_data in tree.items():
        result[std_key] = {
            "label": std_data["label"],
            "description": std_data["description"],
            "versions": {},
        }
        for ver_key, ver_data in std_data["versions"].items():
            result[std_key]["versions"][ver_key] = {
                "label": ver_data["label"],
                "description": ver_data["description"],
                "tests": {},
            }
            for test_key, test_data in ver_data["tests"].items():
                result[std_key]["versions"][ver_key]["tests"][test_key] = {
                    "sop_id": test_data["sop_id"],
                    "name": test_data["name"],
                    "description": test_data.get("description", ""),
                    "high_temperature": test_data.get("high_temperature"),
                    "low_temperature": test_data.get("low_temperature"),
                    "target_temperature": test_data.get("target_temperature"),
                    "ramp_rate": test_data.get("ramp_rate"),
                    "dwell_time_hours": test_data.get("dwell_time_hours"),
                    "cycles": test_data.get("cycles"),
                    "humidity_rh_percent": test_data.get("humidity_rh_percent"),
                    "humidity_control": test_data.get("humidity_control", False),
                    "power_on": test_data.get("power_on", False),
                    "reference": test_data.get("reference", ""),
                    "temp_tolerance": test_data.get("temp_tolerance", 2.0),
                    "humi_tolerance": test_data.get("humi_tolerance", 5.0),
                }
    return result


@router.get("/", response_model=List[SopResponse])
def list_sops():
    """
    取得所有 SOP 列表（向後相容）
    從 STANDARDS_AND_SOPS（由 STANDARD_TREE 自動展開）讀取
    """
    sops: List[SopResponse] = []

    for sop_id, std_data in STANDARDS_AND_SOPS.items():
        steps = std_data.get("steps", [])
        sop = SopResponse(
            sop_id=std_data.get("sop_id", sop_id),
            name=std_data.get("name", ""),
            test_type=std_data.get("test_type", "chamber"),
            version=std_data.get("version", ""),
            description=std_data.get("description", ""),
            steps=steps if isinstance(steps, list) else [],
        )
        sops.append(sop)

    # 再從資料庫取客製 SOP（避免重複）
    db = SessionLocal()
    try:
        db_sops = db.query(SopTemplate).all()
        existing_ids = {s.sop_id for s in sops}
        for s in db_sops:
            if s.sop_id not in existing_ids:
                sops.append(
                    SopResponse(
                        sop_id=s.sop_id,
                        name=s.name,
                        test_type=s.test_type,
                        version=s.version,
                        steps=json.loads(s.steps_json) if s.steps_json else [],
                    )
                )
    finally:
        db.close()

    return sops


@router.post("/start")
async def start_sop(request: Request, payload: Dict[str, Any] = Body(...)):
    """啟動 SOP 測試"""
    sop_id: str = payload.get("sop_id", "")
    device_key: str = "KSON_CH01"

    if not sop_id:
        raise HTTPException(status_code=400, detail="sop_id 不能為空")

    cache = request.app.state.AICM_CACHE

    if device_key in cache and cache[device_key].get("status") == "RUNNING":
        raise HTTPException(
            status_code=400, detail="機台正在執行中，請先停止目前程序。"
        )

    if device_key not in cache:
        cache[device_key] = {"temperature": 25.0, "humidity": 55.0, "status": "IDLE"}

    # 從 STANDARDS_AND_SOPS 取得名稱與標準參數
    std_data = STANDARDS_AND_SOPS.get(sop_id, {})
    sop_name = std_data.get("name", sop_id)

    # 如果 standards 沒有，查資料庫
    if sop_name == sop_id:
        db = SessionLocal()
        try:
            sop = db.query(SopTemplate).filter(SopTemplate.sop_id == sop_id).first()
            if sop:
                sop_name = sop.name
        finally:
            db.close()

    cache[device_key]["status"] = "RUNNING"
    cache[device_key]["running_sop_id"] = sop_id
    cache[device_key]["running_sop_name"] = sop_name
    cache[device_key]["standard_id"] = sop_id  # sop_id 即 standard_id

    print(f"🔥 Started SOP: {sop_id} ({sop_name})")
    return {"status": "success", "message": f"SOP {sop_name} 已啟動"}
