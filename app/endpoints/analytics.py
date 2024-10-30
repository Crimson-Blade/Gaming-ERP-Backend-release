from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.schemas import RegistrationStatsResponse, ActiveInactiveUsersResponse, IncomeStatsResponse, AverageSessionDurationResponse
from ..database import get_db
from .. import crud
from pydantic import BaseModel
from typing import List



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
    
  
@router.get("/analytics/activity", response_model=ActiveInactiveUsersResponse)
def get_active_inactive_users(db: Session = Depends(get_db)):
    return crud.get_active_inactive_users(db)
  
@router.get("/analytics/income", response_model=IncomeStatsResponse)
def get_income(
    start_date: date,
    end_date: date,
    period: str = "daily",
    db: Session = Depends(get_db)
):
    if start_date > end_date:
      raise HTTPException(status_code=400, detail="start date cannot be after end date")
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid period specified")

    return crud.get_income_stats(db, period, start_date, end_date)

@router.get("/analytics/average-session-duration/", response_model=AverageSessionDurationResponse)
def average_session_duration(
    start_date: date,
    end_date: date,
    period: str = "daily",
    db: Session = Depends(get_db)
):
    if start_date > end_date:
      raise HTTPException(status_code=400, detail="start date cannot be after end date")
    if period not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid period specified")

    return crud.get_average_session_duration(db, period, start_date, end_date)