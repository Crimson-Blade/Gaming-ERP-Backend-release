from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/orders/{user_id}/", response_model=schemas.Order)
def create_order(user_id: UUID, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db, user_id, order)

@router.get("/orders/{user_id}/", response_model=List[schemas.Order])
def get_orders(user_id: UUID, db: Session = Depends(get_db)):
    return crud.get_orders_by_user(db, user_id)