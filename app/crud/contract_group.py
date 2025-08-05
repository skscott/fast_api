from sqlalchemy.orm import Session
from app.db.models.contract_group import ContractGroup
from app.schemas.contract_group import ContractGroupCreate
from sqlalchemy import and_

def create_contract_group(db: Session, data: ContractGroupCreate):
    # Check for overlaps
    overlaps = db.query(ContractGroup).filter(
        ContractGroup.supplier_id == data.supplier_id,
        ContractGroup.start_date < data.end_date,
        ContractGroup.end_date > data.start_date
    ).all()

    if overlaps:
        raise ValueError("Overlapping contract group exists for this supplier.")

    new_group = ContractGroup(**data.dict())
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group
