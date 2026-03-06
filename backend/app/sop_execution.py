from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from .models import SessionLocal, SopExecution, StepRecord

router = APIRouter(prefix="/api/sop-executions", tags=["sop-executions"])


# ---------- Pydantic Schemas ----------
class StepRecordSchema(BaseModel):
    step_id: int
    completed: bool
    parameters: Optional[Dict[str, Any]] = None
    photos: Optional[List[str]] = None


class ExecutionCreate(BaseModel):
    sop_id: str
    device_id: Optional[str] = None
    # ISO/IEC 17025:2017 §7.5.1：技術記錄應包含責任人
    operator: Optional[str] = None
    # §7.5.2：記錄實際測試開始與結束時間，供報告查詢原始數據使用
    test_started_at: Optional[datetime] = None
    test_ended_at: Optional[datetime] = None
    steps: List[StepRecordSchema]


class ExecutionResponse(BaseModel):
    id: int
    sop_id: str
    device_id: Optional[str] = None
    operator: Optional[str] = None
    test_started_at: Optional[datetime] = None
    test_ended_at: Optional[datetime] = None
    created_at: datetime
    steps: List[StepRecordSchema]


# ---------- API Endpoints ----------
@router.post("/", response_model=ExecutionResponse)
def create_execution(data: ExecutionCreate):
    db = SessionLocal()
    try:
        execution = SopExecution(
            sop_id=data.sop_id,
            device_id=data.device_id,
            operator=data.operator,
            test_started_at=data.test_started_at,
            test_ended_at=data.test_ended_at,
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)

        steps_response = []
        for step in data.steps:
            record = StepRecord(
                execution_id=execution.id,
                step_id=step.step_id,
                completed=1 if step.completed else 0,
                parameters=json.dumps(step.parameters, ensure_ascii=False)
                if step.parameters
                else None,
                photos=json.dumps(step.photos, ensure_ascii=False)
                if step.photos
                else None,
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            steps_response.append(
                StepRecordSchema(
                    step_id=record.step_id,
                    completed=bool(record.completed),
                    parameters=json.loads(record.parameters)
                    if record.parameters
                    else None,
                    photos=json.loads(record.photos) if record.photos else None,
                )
            )

        return ExecutionResponse(
            id=execution.id,
            sop_id=execution.sop_id,
            device_id=execution.device_id,
            operator=execution.operator,
            test_started_at=execution.test_started_at,
            test_ended_at=execution.test_ended_at,
            created_at=execution.created_at,
            steps=steps_response,
        )
    finally:
        db.close()


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: int):
    db = SessionLocal()
    try:
        execution = (
            db.query(SopExecution).filter(SopExecution.id == execution_id).first()
        )
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")

        records = (
            db.query(StepRecord).filter(StepRecord.execution_id == execution_id).all()
        )
        steps = [
            StepRecordSchema(
                step_id=r.step_id,
                completed=bool(r.completed),
                parameters=json.loads(r.parameters) if r.parameters else None,
                photos=json.loads(r.photos) if r.photos else None,
            )
            for r in records
        ]
        return ExecutionResponse(
            id=execution.id,
            sop_id=execution.sop_id,
            device_id=execution.device_id,
            operator=execution.operator,
            test_started_at=execution.test_started_at,
            test_ended_at=execution.test_ended_at,
            created_at=execution.created_at,
            steps=steps,
        )
    finally:
        db.close()
