from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.solar import SolarReading
import csv
from io import StringIO
from datetime import datetime
from decimal import Decimal

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/solar-readings")
def import_solar_readings(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(contents))
    count = 0
    skipped = 0

    for row in csv_reader:
        try:
            production_date = datetime.fromisoformat(row["production_date"]).date()
            serial = row["panel_serial_nbr"]
            produced = Decimal(row["energy_produced"])

            db.add(SolarReading(
                production_date=production_date,
                panel_serial_nbr=serial,
                energy_produced=produced
            ))
            count += 1

        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipped row {row.get('id', '?')}: {e}")
            continue

    db.commit()
    return {"imported": count, "skipped": skipped}
