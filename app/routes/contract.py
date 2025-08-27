# app/routes/contract.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.contract import Contract
from app.db.models.tariff import Tariff
from app.db.models.utility import Utility
from app.db.schemas.contract import ContractCreate, ContractRead, ContractUpdate
from app.db.schemas.tariff import TariffCreate, TariffRead
from app.crud import contract as crud
from app.db.schemas.utility import UtilityOut, UtilityRead

router = APIRouter(prefix="/contracts", tags=["Contracts"])

@router.post("/", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def create_contract(group: ContractCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_contract(db, group)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{contract_id}", response_model=ContractRead)
def update_contract(contract_id: int, body: ContractUpdate, db: Session = Depends(get_db)):
    db_contract = db.query(Contract).get(contract_id)
    if not db_contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(db_contract, field, value)
    
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@router.get("/", response_model=List[ContractRead])
def list_contracts(db: Session = Depends(get_db)):
    return db.query(Contract).all()

@router.get("/{contract_id}/tariffs", response_model=List[TariffRead])
def list_tariffs_for_contract(contract_id: int, db: Session = Depends(get_db)):
    if not db.get(Contract, contract_id):
        raise HTTPException(status_code=404, detail="Contract not found")
    return db.query(Tariff).filter(Tariff.contract_id == contract_id).all()

@router.post("/{contract_id}/tariffs", response_model=TariffRead, status_code=status.HTTP_201_CREATED)
def create_tariff_for_contract(contract_id: int, body: TariffCreate, db: Session = Depends(get_db)):
    if not db.get(Contract, contract_id):
        raise HTTPException(status_code=404, detail="Contract not found")

    payload = body.model_dump(exclude={"utility_id", "contract_id"}, exclude_unset=True)
    tariff = Tariff(**payload, contract_id=contract_id)

    db.add(tariff)
    db.commit()
    db.refresh(tariff)
    return tariff

@router.get(
    "/{contract_id}/utilities",
    response_model=list[UtilityOut],            # or List[UtilityOut]
    response_model_exclude_none=True            # omit nulls like end_reading=None
)
def list_utilities_for_contract(contract_id: int, db: Session = Depends(get_db)):
    # SQLAlchemy 2.x style get (avoids deprecated .query(...).get)
    contract_obj = db.get(Contract, contract_id)
    if contract_obj is None:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Return ORM rows; Pydantic v2 needs model_config.from_attributes = True on UtilityOut
    return (
        db.query(Utility)
          .filter(Utility.contract_id == contract_id)
          .order_by(Utility.type)  # optional nicety
          .all()
    )