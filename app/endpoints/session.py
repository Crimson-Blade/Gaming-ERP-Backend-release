from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from .. import crud
from ..database import get_db

router = APIRouter()

@router.post("/sessions/{user_id}/end/")
def end_session(user_id: UUID, db: Session = Depends(get_db)):
    registration = crud.end_session(db, user_id)
    return {'message': 'Session ended', 'registration': registration}