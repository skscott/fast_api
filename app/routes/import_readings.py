from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models.reading import Reading
from app.db.models.solar import SolarReading
from app.db.models.utility import Utility
from app.db.models.contract import Contract
import csv
from io import StringIO
from datetime import datetime
from decimal import Decimal
from collections import defaultdict

router = APIRouter(prefix="/import", tags=["import"])

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
            # timestamp = datetime.strptime(row["consumption_date"].strip(), "%Y-%m-%d").date()
            timestamp = datetime.fromisoformat(row["consumption_date"].strip())

            # Find contract for the reading date
            contract = db.query(Contract).filter(
                Contract.start_date <= timestamp,
                Contract.end_date >= timestamp
            ).first()

            if not contract:
                skipped += 1
                print(f"❌ No contract for {timestamp}")
                continue

            # Check for ELECTRIC and GAS utilities
            normal = db.query(Utility).filter_by(
                contract_id=contract.id,
                type="NORMAL"
            ).first()

            reduced = db.query(Utility).filter_by(
                contract_id=contract.id,
                type="REDUCED"
            ).first()

            gas_utility = db.query(Utility).filter_by(
                contract_id=contract.id,
                type="GAS"
            ).first()

            if not normal and not reduced and not gas_utility:
                skipped += 1
                print(f"⚠️ Missing utilities for {timestamp} in contract {contract.name}")
                continue

            readings = []

            if row.get("stand_i"):
                readings.append(Reading(
                    timestamp=timestamp,
                    value=Decimal(row["stand_i"]),
                    unit="kWh",
                    utility_id=normal.id
                ))

            if row.get("stand_ii"):
                readings.append(Reading(
                    timestamp=timestamp,
                    value=Decimal(row["stand_ii"]),
                    unit="kWh",
                    utility_id=reduced.id
                ))

            if row.get("gas"):
                readings.append(Reading(
                    timestamp=timestamp,
                    value=Decimal(row["gas"]),
                    unit="m3",
                    utility_id=gas_utility.id
                ))

            db.add_all(readings)
            count += len(readings)

        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipped row {row.get('id', '?')}: {e}")
            continue

    db.commit()
    return {"imported": count, "skipped": skipped}

@router.post("/solar-readings")
def import_solar_readings(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(contents))

    totals_by_date = defaultdict(Decimal)
    count = 0
    skipped = 0

    for row in csv_reader:
        try:
            production_date = datetime.fromisoformat(row["production_date"].strip())
            panel_serial = row["panel_serial_nbr"].strip()
            energy = Decimal(row["energy_produced"].strip())

            utility = db.query(Utility).join(Contract).filter(
                Utility.type == "SOLAR",
                Contract.start_date <= production_date,
                Contract.end_date >= production_date,
                Utility.contract_id == Contract.id
            ).first()

            if not utility:
                skipped += 1
                print(f"❌ No solar utility for {production_date.date()}")
                continue

            solar = SolarReading(
                production_date=production_date,
                energy_produced=energy,
                unit="kWh",
                panel_serial_nbr=panel_serial
            )
            db.add(solar)
            totals_by_date[(production_date.date(), utility.id)] += energy
            count += 1

        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipped solar row {row.get('id', '?')}: {e}")
            continue

    # Insert total readings per day per utility
    for (day, utility_id), total in totals_by_date.items():
        reading = Reading(
            timestamp=datetime.combine(day, datetime.min.time()),
            value=total,
            unit="kWh",
            source="solar",
            utility_id=utility_id
        )
        db.add(reading)

    db.commit()
    return {"solar_readings": count, "aggregated_days": len(totals_by_date), "skipped": skipped}
