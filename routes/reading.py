from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.models.reading import Reading
from app.db.database import get_db
from app.db.schemas import Reading as ReadingSchema

router = APIRouter()

@router.get("/readings/latest", response_model=list[ReadingSchema])
def get_latest_readings(limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Reading).order_by(Reading.timestamp.desc()).limit(limit).all()
