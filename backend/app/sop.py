from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
from datetime import datetime
from .models import SessionLocal, SopTemplate

router = APIRouter(prefix="/api/sop", tags=["sop"])

class StepSchema(BaseModel):
    step_id: int
    name: str
    description: str
    requires_photo: bool = False
    requires_parameters: bool = False
    optional: bool = False
    parameters_schema: Optional[dict] = None

class SopCreate(BaseModel):
    sop_id: str
    name: str
    test_type: str
    version: str
    steps: List[StepSchema]

class SopResponse(BaseModel):
    sop_id: str
    name: str
    test_type: str
    version: str
    steps: List[StepSchema]

@router.post("/", response_model=SopResponse)
def create_sop(sop: SopCreate):
    db = SessionLocal()
    existing = db.query(SopTemplate).filter(SopTemplate.sop_id == sop.sop_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="sop_id already exists")
    
    steps_json = json.dumps([step.dict() for step in sop.steps])
    db_sop = SopTemplate(
        sop_id=sop.sop_id,
        name=sop.name,
        test_type=sop.test_type,
        version=sop.version,
        steps_json=steps_json
    )
    db.add(db_sop)
    db.commit()
    db.refresh(db_sop)
    db.close()
    return SopResponse(
        sop_id=db_sop.sop_id,  # type: ignore
        name=db_sop.name,      # type: ignore
        test_type=db_sop.test_type,  # type: ignore
        version=db_sop.version,  # type: ignore
        steps=json.loads(db_sop.steps_json)
    )

@router.get("/{sop_id}", response_model=SopResponse)
def get_sop(sop_id: str):
    db = SessionLocal()
    sop = db.query(SopTemplate).filter(SopTemplate.sop_id == sop_id).first()
    db.close()
    if not sop:
        raise HTTPException(status_code=404, detail="SOP not found")
    return SopResponse(
        sop_id=sop.sop_id,  # type: ignore
        name=sop.name,      # type: ignore
        test_type=sop.test_type,  # type: ignore
        version=sop.version,  # type: ignore
        steps=json.loads(sop.steps_json)
    )

@router.get("/", response_model=List[SopResponse])
def list_sops(test_type: Optional[str] = None):
    db = SessionLocal()
    query = db.query(SopTemplate)
    if test_type:
        query = query.filter(SopTemplate.test_type == test_type)
    sops = query.all()
    db.close()
    return [
        SopResponse(
            sop_id=s.sop_id,  # type: ignore
            name=s.name,      # type: ignore
            test_type=s.test_type,  # type: ignore
            version=s.version,  # type: ignore
            steps=json.loads(s.steps_json)
        ) for s in sops
    ]