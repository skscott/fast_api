# app/crud/reading.py
from sqlalchemy.orm import Session
from app.db.models.reading import Reading
from app.db.schemas.reading import ReadingCreate

def create_reading(db: Session, data: ReadingCreate):
    reading = Reading(**data.dict())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading

def get_all_readings(db: Session):
    return db.query(Reading).order_by(Reading.timestamp).all()

def get_readings_by_utility(db: Session, utility_id: int):
    return db.query(Reading).filter(Reading.utility_id == utility_id).order_by(Reading.timestamp).all()

def get_reading(db: Session, reading_id: int):
    return db.query(Reading).filter(Reading.id == reading_id).first()
