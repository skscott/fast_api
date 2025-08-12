# app/api/routes/tariffs.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import SessionLocal
from app.db.models.tariff import Tariff
from app.db.schemas.tariff import TariffCreate, TariffUpdate, TariffRead

router = APIRouter(prefix="/tariffs", tags=["tariffs"])

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

@router.get("", response_model=List[TariffRead])
def list_tariffs(db: Session = Depends(get_db)):
  return db.query(Tariff).all()

@router.post("", response_model=TariffRead)
def create_tariff(body: TariffCreate, db: Session = Depends(get_db)):
  t = Tariff(**body.model_dump(exclude_unset=True))
  db.add(t); db.commit(); db.refresh(t)
  return t

@router.get("/by-contract/{contract_id}", response_model=List[TariffRead])
def list_by_contract(contract_id: int, db: Session = Depends(get_db)):
  return db.query(Tariff).where(Tariff.contract_id == contract_id).all()

@router.get("/by-utility/{utility_id}", response_model=List[TariffRead])
def list_by_utility(utility_id: int, db: Session = Depends(get_db)):
  return db.query(Tariff).where(Tariff.utility_id == utility_id).all()

@router.patch("/{tariff_id}", response_model=TariffRead)
def update_tariff(tariff_id: int, updates: TariffUpdate, db: Session = Depends(get_db)):
  t = db.query(Tariff).get(tariff_id)
  if not t: raise HTTPException(status_code=404, detail="Tariff not found")
  for k, v in updates.model_dump(exclude_unset=True).items(): setattr(t, k, v)
  db.commit(); db.refresh(t); return t

@router.delete("/{tariff_id}", status_code=204)
def delete_tariff(tariff_id: int, db: Session = Depends(get_db)):
  t = db.query(Tariff).get(tariff_id)
  if not t: raise HTTPException(status_code=404, detail="Tariff not found")
  db.delete(t); db.commit()
