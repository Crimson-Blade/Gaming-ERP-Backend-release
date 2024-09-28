from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud
from ..database import get_db

router = APIRouter()

@router.get("/billing/{user_id}/")
def generate_bill(user_id: UUID, db: Session = Depends(get_db)):
    return crud.calculate_total(db, user_id)

@router.post("/billing/{user_id}/finalize/")
def finalize_bill(user_id: UUID, discount_percentage: float = 0.0, db: Session = Depends(get_db)):
    bill_info = crud.calculate_total(db, user_id)
    total_cost = bill_info['total_cost']
    final_amount = total_cost * (1 - discount_percentage / 100)
    registration = crud.finalize_bill(db, user_id, final_amount)
    return {
        'total_cost': total_cost,
        'discount_percentage': discount_percentage,
        'final_amount': final_amount,
        'registration': registration
    }