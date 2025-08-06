# app/crud/utility.py
from sqlalchemy.orm import Session
from app.db.models.utility import Utility
from app.db.schemas.utility import UtilityCreate

def create_utility(db: Session, data: UtilityCreate):
    utility = Utility(**data.dict())
    db.add(utility)
    db.commit()
    db.refresh(utility)
    return utility

def get_utilities(db: Session):
    return db.query(Utility).all()


def get_utility(db: Session, utility_id: int):
    return db.query(Utility).filter(Utility.id == utility_id).first()
