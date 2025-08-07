from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.schemas.contract import ContractCreate, ContractRead
from app.db.database import get_db
from app.db.models.contract import Contract
from app.crud import contract as crud

router = APIRouter(prefix="/contract", tags=["Contract"])

@router.post("/", response_model=ContractRead)
def create_contract(group: ContractCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_contract(db, group)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ContractRead])
def list_contract(db: Session = Depends(get_db)):
    return db.query(Contract).all()

