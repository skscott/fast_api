# app/routes/import_readings.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.reading import Reading
from app.db.models.utility import Utility
import csv
from io import StringIO
from datetime import datetime
from decimal import Decimal
from app.db.models.contract import Contract

router = APIRouter(prefix="/import", tags=["import"])

# Utility type constants
GAS = "GAS"
GREY = "GREY"  # stand_i (electricity day)
NIGHT = "NIGHT"  # stand_ii (electricity night)

# Utility lookup by timestamp and type
def resolve_utility_id(db: Session, reading_time: datetime, utility_type: str) -> int:
    utilities = db.query(Utility).join(Utility.contract).filter(
        Utility.type == utility_type,

        Utility.contract.has(Contract.start_date <= reading_time),
        Utility.contract.has(Contract.end_date >= reading_time),
    ).all()

    if not utilities:
        raise HTTPException(status_code=404, detail=f"No utility found for {utility_type} on {reading_time.date()}")

    # Use the first matching utility
    return utilities[0].id

@router.post("/meter-readings")
def import_meter_readings(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(contents))
    count = 0
    skipped = 0

    for row in csv_reader:
        try:
            timestamp = datetime.fromisoformat(row["consumption_date"].strip())
            gas_val = Decimal(row["gas"])
            stand_i_val = Decimal(row["stand_i"])
            stand_ii_val = Decimal(row["stand_ii"])

            readings = []

            for value, ut_type in [
                (gas_val, GAS),
                (stand_i_val, GREY),
                (stand_ii_val, NIGHT)
            ]:
                utility_id = resolve_utility_id(db, timestamp, ut_type)
                reading = Reading(
                    timestamp=timestamp,
                    value=value,
                    unit="kWh" if ut_type in [GREY, NIGHT] else "m3",
                    utility_id=utility_id
                )
                readings.append(reading)

            db.add_all(readings)
            count += len(readings)

        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipped row {row.get('id', '?')}: {e}")
            continue

    db.commit()
    return {"imported": count, "skipped": skipped}
