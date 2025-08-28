from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.db.database import get_db
from app.db.models.reading import Reading
from app.db.models.solar import SolarReading
from app.db.models.utility import Utility
from app.db.models.contract import Contract
import csv
from io import StringIO
from datetime import datetime, time
from decimal import Decimal, InvalidOperation
from collections import defaultdict

router = APIRouter(prefix="/import", tags=["import"])

# ---------- helpers ----------

def _parse_decimal(raw: str | None) -> Decimal | None:
    if raw is None:
        return None
    s = raw.strip()
    if s == "":
        return None
    # tolerate 1,234.56 style input
    s = s.replace(" ", "").replace(",", "")
    try:
        return Decimal(s)
    except InvalidOperation:
        return None

def _get_contract_for_timestamp(db: Session, ts: datetime) -> Contract | None:
    return (
        db.query(Contract)
        .filter(Contract.start_date <= ts, Contract.end_date >= ts)
        .order_by(Contract.start_date.desc())
        .first()
    )

def _get_utility_for_timestamp(db: Session, ts: datetime, type_: str) -> Utility | None:
    """
    Return the utility of given type that is active at timestamp ts.
    Filters by the parent contract date window to avoid SOLAR vs meter mix-ups.
    """
    return (
        db.query(Utility)
        .join(Contract, Contract.id == Utility.contract_id)
        .filter(
            func.upper(Utility.type) == func.upper(type_),
            Contract.start_date <= ts,
            Contract.end_date >= ts,
        )
        .order_by(Contract.start_date.desc())  # newest first if multiple match
        .first()
    )

def _get_utility(db: Session, contract_id: int, type_: str) -> Utility | None:
    # case-sensitive in DB, but we normalize here just in case
    return (
        db.query(Utility)
        .filter(Utility.contract_id == contract_id, func.upper(Utility.type) == func.upper(type_))
        .first()
    )

def _last_before(db: Session, utility_id: int, ts: datetime) -> Reading | None:
    return (
        db.query(Reading)
        .filter(Reading.utility_id == utility_id, Reading.timestamp < ts)
        .order_by(Reading.timestamp.desc())
        .first()
    )

def _get_existing(db: Session, utility_id: int, ts: datetime) -> Reading | None:
    return (
        db.query(Reading)
        .filter(Reading.utility_id == utility_id, Reading.timestamp == ts)
        .first()
    )

def _upsert_reading(
    db: Session,
    utility: Utility,
    ts: datetime,
    value: Decimal,
) -> tuple[bool, str]:
    """
    Insert or update a reading for (utility, ts).
    Returns (inserted, msg). Skips if non-monotonic (value < last).
    """
    unit = "m3" if utility.type == "GAS" else "kWh"

    # monotonic guard (stands must not go backwards)
    prev = _last_before(db, utility.id, ts)
    if prev and value < prev.value:
        return (False, f"non-monotonic for util {utility.id}: {value} < {prev.value} at {ts}")

    existing = _get_existing(db, utility.id, ts)
    if existing:
        existing.value = value
        existing.unit = unit
        existing.source = existing.source or "import"
        db.add(existing)
        return (False, "updated existing")

    db.add(Reading(timestamp=ts, value=value, unit=unit, source="import", utility_id=utility.id))
    return (True, "inserted")

from datetime import date

REDUCED_CUTOFF = date(2022, 1, 18)  # last valid day for night-rate readings

# ---------- meter readings importer ----------
@router.post("/meter-readings")
def import_meter_readings(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = file.file.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(contents))

    inserted = updated = skipped = 0

    for row in reader:
        try:
            raw_ts = (row.get("consumption_date") or "").strip()
            ts = datetime.fromisoformat(raw_ts) if "T" in raw_ts else datetime.combine(datetime.fromisoformat(raw_ts).date(), time.min)

            contract = _get_contract_for_timestamp(db, ts)
            if not contract:
                skipped += 1
                print(f"❌ No contract covering {ts.date()}")
                continue

            # Utilities active at ts (avoids SOLAR contract completely)
            normal  = _get_utility_for_timestamp(db, ts, "NORMAL")
            reduced = _get_utility_for_timestamp(db, ts, "REDUCED")
            gas     = _get_utility_for_timestamp(db, ts, "GAS")

            # Parse values (no 'stand' single-column anymore)
            v_stand_i  = _parse_decimal(row.get("stand_i"))     # → REDUCED
            v_stand_ii = _parse_decimal(row.get("stand_ii"))    # → NORMAL
            v_gas      = _parse_decimal(row.get("gas"))         # → GAS

            # REDUCED
            if v_stand_i is not None:
                if reduced is not None:
                    ok, _ = _upsert_reading(db, reduced, ts, v_stand_i)
                    inserted += 1 if ok else 0; updated += 0 if ok else 1
                else:
                    skipped += 1; print(f"⚠️ No REDUCED utility active at {ts} (row={row})")

            # NORMAL
            if v_stand_ii is not None:
                if normal is not None:
                    ok, _ = _upsert_reading(db, normal, ts, v_stand_ii)
                    inserted += 1 if ok else 0; updated += 0 if ok else 1
                else:
                    skipped += 1; print(f"⚠️ No NORMAL utility active at {ts} (row={row})")

            # GAS
            if v_gas is not None:
                if gas is not None:
                    ok, _ = _upsert_reading(db, gas, ts, v_gas)
                    inserted += 1 if ok else 0; updated += 0 if ok else 1
                else:
                    skipped += 1; print(f"⚠️ No GAS utility active at {ts} (row={row})")


        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipped row (parse error): {e}; row={row}")

    db.commit()
    return {"inserted": inserted, "updated": updated, "skipped": skipped}

# ---------- solar readings importer (unchanged except tiny hardening) ----------

@router.post("/solar-readings")
def import_solar_readings(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = file.file.read().decode("utf-8", errors="replace")
    reader = csv.DictReader(StringIO(contents))

    totals_by_date = defaultdict(Decimal)
    count_rows = 0
    skipped = 0

    for row in reader:
        try:
            raw_ts = row["production_date"].strip()
            ts = datetime.fromisoformat(raw_ts) if "T" in raw_ts else datetime.combine(datetime.fromisoformat(raw_ts).date(), time.min)
            panel_serial = row.get("panel_serial_nbr", "").strip()
            energy = _parse_decimal(row.get("energy_produced"))
            if energy is None:
                skipped += 1
                continue

            utility = (
                db.query(Utility)
                .join(Contract, Contract.id == Utility.contract_id)
                .filter(Utility.type == "SOLAR", Contract.start_date <= ts, Contract.end_date >= ts)
                .first()
            )

            if not utility:
                skipped += 1
                print(f"❌ No SOLAR utility for {ts.date()}")
                continue

            db.add(SolarReading(
                production_date=ts,
                energy_produced=energy,
                unit="kWh",
                panel_serial_nbr=panel_serial
            ))
            totals_by_date[(ts.date(), utility.id)] += energy
            count_rows += 1
        except Exception as e:
            skipped += 1
            print(f"⚠️ Skipped solar row: {e}; row={row}")

    # aggregate daily solar into Reading for the utility
    for (day, utility_id), total in totals_by_date.items():
        ts = datetime.combine(day, time.min)
        existing = _get_existing(db, utility_id, ts)
        if existing:
            existing.value = total
            existing.unit = "kWh"
            existing.source = "solar"
            db.add(existing)
        else:
            db.add(Reading(timestamp=ts, value=total, unit="kWh", source="solar", utility_id=utility_id))

    db.commit()
    return {"solar_rows": count_rows, "aggregated_days": len(totals_by_date), "skipped": skipped}
