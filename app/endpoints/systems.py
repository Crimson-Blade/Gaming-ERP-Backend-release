from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/systems/{user_id}/", response_model=schemas.System)
def create_system_entry(user_id: UUID, system: schemas.SystemCreate, db: Session = Depends(get_db)):
    return crud.create_system(db, user_id, system)

@router.get("/systems/{user_id}/", response_model=List[schemas.System])
def get_systems(user_id: UUID, db: Session = Depends(get_db)):
    return crud.get_systems_by_user(db, user_id)

@router.put("/systems/{system_id}/end/")
def update_system_end_time(system_id: int, db: Session = Depends(get_db)):
    system = crud.update_system_end_time(db, system_id)
    return system