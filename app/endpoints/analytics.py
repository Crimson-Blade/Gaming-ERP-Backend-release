from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from ..database import get_db
from .. import crud
from pydantic import BaseModel
from typing import List

class RegistrationStatsResponse(BaseModel):
    labels: List[str]  # List of labels, e.g., dates or months
    values: List[int]  # List of registration counts

router = APIRouter()


@router.get("/analytics/registrations", response_model=RegistrationStatsResponse)
def get_registrations(
    start_date: date,
    end_date: date,
    period: str = "daily",
    db: Session = Depends(get_db)
):  
    if start_date > end_date:
      raise HTTPException(status_code=400, detail="start date cannot be after end date")
    if period not in ["daily", "weekly", "monthly"]:
      raise HTTPException(status_code=400, detail="Invalid period specified")

    return crud.get_registration_stats(db, period, start_date, end_date)
    
  
@router.get("/analytics/activity", response_model=List[dict])
def get_active_inactive_users(db: Session = Depends(get_db)):
    return crud.get_active_inactive_users(db)
  
@router.get("/analytics/income", response_model=List[dict])
def get_income(
    start_date: date,
    end_date: date,
    period: str = "daily",
    db: Session = Depends(get_db)
):
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid period specified")

    return crud.get_income_stats(db, period, start_date, end_date)