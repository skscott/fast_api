# app/crud/utility.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.utility import Utility
from app.db.schemas.utility import UtilityCreate, UtilityUpdate

def create_utility(db: Session, data: UtilityCreate) -> Utility:
    u = Utility(**data.model_dump())
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def get_utilities(db: Session):
    return db.query(Utility).all()

def update_utility(db: Session, utility_id: int, data: UtilityUpdate) -> Utility:
    u = db.get(Utility, utility_id)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utility not found")

    payload = data.model_dump(exclude_unset=True)
    for field, value in payload.items():
        setattr(u, field, value)

    db.add(u)
    db.commit()
    db.refresh(u)
    return u
