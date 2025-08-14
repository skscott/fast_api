# app/routes/utility.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.tariff import Tariff
from app.db.models.utility import Utility
from app.db.schemas.tariff import TariffCreate, TariffRead
from app.db.schemas.utility import UtilityCreate, UtilityRead, UtilityUpdate
from app.crud import utility as crud
from datetime import date
from fastapi import Query
from app.services.cost_calculator import compute_utility_cost
from app.db.schemas.cost import CostRead, TariffSpecItem


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

# ✅ NEW: update a utility
@router.put("/{utility_id}", response_model=UtilityRead)
def update(utility_id: int, body: UtilityUpdate, db: Session = Depends(get_db)):
    return crud.update_utility(db, utility_id, body)

@router.get("/{utility_id}/tariffs", response_model=List[TariffRead])
def list_tariffs_for_utility(
    utility_id: int,
    include_contract: bool = Query(False, description="Also include contract-level tariffs"),
    db: Session = Depends(get_db),
):
    utility = db.get(Utility, utility_id)
    if not utility:
        raise HTTPException(status_code=404, detail="Utility not found")

    q = db.query(Tariff).filter(Tariff.utility_id == utility_id)
    if not include_contract:
        return q.all()

    return q.union_all(
        db.query(Tariff).filter(Tariff.contract_id == utility.contract_id)
    ).all()

@router.post("/{utility_id}/tariffs", response_model=TariffRead, status_code=status.HTTP_201_CREATED)
def create_tariff_for_utility(utility_id: int, body: TariffCreate, db: Session = Depends(get_db)):
    if not db.get(Utility, utility_id):
        raise HTTPException(status_code=404, detail="Utility not found")

    payload = body.model_dump(exclude={"utility_id", "contract_id"}, exclude_unset=True)
    tariff = Tariff(**payload, utility_id=utility_id)
    db.add(tariff)
    db.commit()
    db.refresh(tariff)
    return tariff


@router.get("/{utility_id}/cost", response_model=CostRead)
def get_utility_cost(
    utility_id: int,
    start: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end: date = Query(..., description="End date (YYYY-MM-DD)"),
    include_contract: bool = Query(True, description="Include contract-level tariffs"),
    db: Session = Depends(get_db),
):
    # Validate utility exists
    if not db.get(Utility, utility_id):
        raise HTTPException(status_code=404, detail="Utility not found")

    cost = compute_utility_cost(db, utility_id, start, end, include_contract)

    return {
        "gas": cost.gas, "stand_i": cost.stand_i, "stand_ii": cost.stand_ii,
        "single": cost.single, "fixed": cost.fixed, "variable": cost.variable,
        "tax": cost.tax, "network": cost.network, "discount": cost.discount,
        "total": cost.total,
        "specification": cost.tariff_specification,
    }