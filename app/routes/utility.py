
# app/routes/utility.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas.utility import UtilityCreate, UtilityRead
from app.crud import utility as crud

router = APIRouter(prefix="/utilities", tags=["Utilities"])

@router.post("/", response_model=UtilityRead)
def create(data: UtilityCreate, db: Session = Depends(get_db)):
    return crud.create_utility(db, data)

@router.get("/", response_model=list[UtilityRead])
def list_utilities(db: Session = Depends(get_db)):
    return crud.get_utilities(db)

@router.get("/{utility_id}", response_model=UtilityRead)
def get_one(utility_id: int, db: Session = Depends(get_db)):
    utility = crud.get_utility(db, utility_id)
    if not utility:
        raise HTTPException(status_code=404, detail="Utility not found")
    return utility
