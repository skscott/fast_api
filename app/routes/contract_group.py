from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.contract_group import ContractGroupCreate, ContractGroupRead
from app.db.database import get_db
from app.db.models.contract_group import ContractGroup
from app.crud import contract_group as crud

router = APIRouter(prefix="/contract-groups", tags=["Contract Groups"])

@router.post("/", response_model=ContractGroupRead)
def create_contract_group(group: ContractGroupCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_contract_group(db, group)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ContractGroupRead])
def list_contract_groups(db: Session = Depends(get_db)):
    return db.query(ContractGroup).all()
