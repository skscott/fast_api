# app/routes/utility.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.tariff import Tariff
from app.db.models.utility import Utility
from app.db.schemas.tariff import TariffCreate, TariffRead
from app.db.schemas.utility import UtilityCreate, UtilityRead
from app.crud import utility as crud

router = APIRouter(prefix="/utilities", tags=["Utilities"])

@router.post("/", response_model=UtilityRead, status_code=status.HTTP_201_CREATED)
def create(data: UtilityCreate, db: Session = Depends(get_db)):
    return crud.create_utility(db, data)

@router.get("/", response_model=List[UtilityRead])
def list_utilities(db: Session = Depends(get_db)):
    return crud.get_utilities(db)

@router.get("/{utility_id}", response_model=UtilityRead)
def get_one(utility_id: int, db: Session = Depends(get_db)):
    utility = db.get(Utility, utility_id)
    if not utility:
        raise HTTPException(status_code=404, detail="Utility not found")
    return utility

@router.get("/{utility_id}/tariffs", response_model=List[TariffRead])
def list_tariffs_for_utility(
        utility_id: int,
        include_contract: bool = Query(False, description="Also include contract-level tariffs"),
        db: Session = Depends(get_db),
    ):
    utility = db.get(Utility, utility_id)
    if not utility:
        raise HTTPException(status_code=404, detail="Utility not found")

    # Always include utility-specific tariffs
    q = db.query(Tariff).filter(Tariff.utility_id == utility_id)

    if not include_contract:
        return q.all()

    # Also include the parent contract tariffs
    return (
        q.union_all(
            db.query(Tariff).filter(Tariff.contract_id == utility.contract_id)
        )
        .all()
    )

@router.post("/{utility_id}/tariffs", response_model=TariffRead, status_code=status.HTTP_201_CREATED)
def create_tariff_for_utility(utility_id: int, body: TariffCreate, db: Session = Depends(get_db)):
    if not db.get(Utility, utility_id):
        raise HTTPException(status_code=404, detail="Utility not found")

    # Ignore any utility_id/contract_id in body; scope comes from URL
    payload = body.model_dump(exclude={"utility_id", "contract_id"}, exclude_unset=True)
    tariff = Tariff(**payload, utility_id=utility_id)

    db.add(tariff)
    db.commit()
    db.refresh(tariff)
    return tariff
