# app/routes/analytics.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services.analytics import monthly_usage

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/monthly-usage")
def get_monthly_usage(year: int = Query(..., ge=1900, le=9999), db: Session = Depends(get_db)):
    return monthly_usage(db, year)

@router.get("/yearly-usage")
def get_yearly_usage(db: Session = Depends(get_db)):
    """
    Optional: produce a multi-year summary.
    You can implement a simple loop that calls monthly_usage() per year and aggregates.
    """
    # Placeholder – implement as needed
    return {"labels": [], "gas": [], "stand_i": [], "stand_ii": [], "solar": []}
