from fastapi import APIRouter
from .models import SessionLocal, ErrorLog

router = APIRouter(prefix="/api/errors", tags=["errors"])


@router.get("/")
def list_errors():
    """取得所有異常紀錄，最新在前"""
    db = SessionLocal()
    try:
        logs = db.query(ErrorLog).order_by(ErrorLog.created_at.desc()).all()
        return [
            {
                "id": e.id,
                "device_id": e.device_id,
                "error_type": e.error_type,
                "sop_id": e.sop_id,
                "sop_name": e.sop_name,
                "temperature": e.temperature,
                "humidity": e.humidity,
                "note": e.note,
                "created_at": e.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for e in logs
        ]
    finally:
        db.close()
