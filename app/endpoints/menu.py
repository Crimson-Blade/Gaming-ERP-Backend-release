from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, crud
from ..database import get_db

router = APIRouter()

@router.post("/menu/", response_model=schemas.Menu)
def create_menu_item(menu_item: schemas.MenuCreate, db: Session = Depends(get_db)):
    return crud.create_menu_item(db, menu_item)

@router.get("/menu/", response_model=List[schemas.Menu])
def get_menu(db: Session = Depends(get_db)):
    return crud.get_menu(db)