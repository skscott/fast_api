# app/routes/reading.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas.reading import ReadingCreate, ReadingRead
from app.crud import reading as crud

router = APIRouter(prefix="/readings", tags=["Readings"])

@router.post("/", response_model=ReadingRead)
def create(data: ReadingCreate, db: Session = Depends(get_db)):
    return crud.create_reading(db, data)

@router.get("/", response_model=list[ReadingRead])
def list_all(db: Session = Depends(get_db)):
    return crud.get_all_readings(db)

@router.get("/utility/{utility_id}", response_model=list[ReadingRead])
def list_by_utility(utility_id: int, db: Session = Depends(get_db)):
    return crud.get_readings_by_utility(db, utility_id)

@router.get("/{reading_id}", response_model=ReadingRead)
def get_one(reading_id: int, db: Session = Depends(get_db)):
    reading = crud.get_reading(db, reading_id)
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    return reading
