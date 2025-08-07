# app/crud/reading.py
from sqlalchemy.orm import Session
from app.db.models.solar import SolarReading
from app.db.schemas.solar import SolarCreate

def create_solar_reading(db: Session, data: SolarCreate):
    solar = SolarReading(**data.dict())
    db.add(solar)
    db.commit()
    db.refresh(solar)
    return solar

def get_all_readings(db: Session):
    return db.query(SolarReading).order_by(SolarReading.timestamp).all()

def get_readings_by_utility(db: Session, utility_id: int):
    return db.query(SolarReading).filter(SolarReading.utility_id == utility_id).order_by(SolarReading.timestamp).all()

def get_reading(db: Session, reading_id: int):
    return db.query(SolarReading).filter(SolarReading.id == reading_id).first()
