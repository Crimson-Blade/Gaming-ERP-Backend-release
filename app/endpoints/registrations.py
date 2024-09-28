from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from pytz import timezone
from typing import List, Optional
import os
from dotenv import load_dotenv
from uuid import UUID
from .. import schemas, crud, models
from ..database import get_db
load_dotenv()
router = APIRouter()

LOUNGE_PRICE_PER_HOUR = float(os.getenv("LOUNGE_PRICE_PER_HOUR", 50.0))

@router.post("/registrations/", response_model=schemas.Registration)
def create_registration(registration: schemas.RegistrationCreate, db: Session = Depends(get_db)):
    db_registration = crud.create_registration(db, registration)
    # Create a lounge system entry
    system = schemas.SystemCreate(
        name="lounge",
        amount=LOUNGE_PRICE_PER_HOUR,
        start_time=datetime.now(timezone('UTC'))
    )
    crud.create_system(db, db_registration.user_id, system)
    return db_registration

# Endpoint to get user details by userID
@router.get("/registrations/{user_id}", response_model=schemas.Registration)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    user = crud.get_registration(db, str(user_id))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/registrations/search/", response_model=List[schemas.Registration])
def search_registrations(
    date: Optional[date] = None,
    name: Optional[str] = None,
    phone_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    registrations = crud.search_registrations(db, date, name, phone_number)
    return registrations

@router.get("/registrations/today/", response_model=List[schemas.Registration])
def get_today_registrations(db: Session = Depends(get_db), onlyActive: Optional[bool] = None):
    today = datetime.now(timezone('UTC')).date()
    registrations = crud.search_registrations(db, date=today, onlyActive=onlyActive)
    return registrations