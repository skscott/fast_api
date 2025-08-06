from sqlalchemy.orm import Session
from app.db.models.contract import Contract
from app.db.schemas.contract import ContractCreate
from sqlalchemy import and_

def create_contract(db: Session, data: ContractCreate):
    # Check for overlaps
    overlaps = db.query(Contract).filter(
        Contract.supplier_id == data.supplier_id,
        Contract.start_date < data.end_date,
        Contract.end_date > data.start_date
    ).all()

    if overlaps:
        raise ValueError("Overlapping contract group exists for this supplier.")

    new_contract = Contract(**data.dict())
    db.add(new_contract)
    db.commit()
    db.refresh(new_contract)
    return new_contract
