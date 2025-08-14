# app/services/usage_calculator.py
from __future__ import annotations
from datetime import date, datetime, time
from decimal import Decimal
from typing import Dict, Literal, Iterable, Optional
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import Session

from app.db.models.reading import Reading
from app.db.models.utility import Utility

TariffFrequency = Literal["DAY", "MONTH", "YEAR", "M3", "KWH"]

def _to_dt(d: date, end: bool = False) -> datetime:
    # start: 00:00 inclusive, end: treat as open interval by using the next midnight (we'll query < end_dt)
    return datetime.combine(d, time.min)

def _to_decimal(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))

def _delta_usage_for_utility(
    db: Session,
    utility_id: int,
    start_dt: datetime,
    end_dt: datetime,
    unit: Optional[str],   # "kWh" or "m3"
) -> Decimal:
    """
    Usage = (last reading before end_dt) - (baseline reading at or before start_dt).
    Falls back to 0 if we can't form a delta.
    """

    # Baseline: the latest reading at or before start
    baseline = (
        db.query(Reading.value)
        .filter(
            Reading.utility_id == utility_id,
            Reading.timestamp < start_dt,            # strictly before start for baseline
            *( [Reading.unit == unit] if unit else [] )
        )
        .order_by(desc(Reading.timestamp))
        .limit(1)
        .scalar()
    )

    # If no baseline before start, try the first reading inside the window as baseline
    if baseline is None:
        baseline = (
            db.query(Reading.value)
            .filter(
                Reading.utility_id == utility_id,
                Reading.timestamp >= start_dt,
                Reading.timestamp <  end_dt,
                *( [Reading.unit == unit] if unit else [] )
            )
            .order_by(Reading.timestamp.asc())
            .limit(1)
            .scalar()
        )

    # Final (end) reading: the latest reading before end_dt
    final = (
        db.query(Reading.value)
        .filter(
            Reading.utility_id == utility_id,
            Reading.timestamp < end_dt,
            *( [Reading.unit == unit] if unit else [] )
        )
        .order_by(desc(Reading.timestamp))
        .limit(1)
        .scalar()
    )

    if baseline is None or final is None:
        return Decimal("0")

    usage = _to_decimal(final) - _to_decimal(baseline)
    # Guard against clock glitches / resets
    if usage < 0:
        usage = Decimal("0")
    return usage

def get_usage_for_period(
    db: Session,
    contract_id: Optional[int],
    utility_id: Optional[int],
    start: date,
    end: date,
    for_contract_scope: bool,
) -> Dict[TariffFrequency, Decimal]:
    """
    Returns DAY/MONTH/YEAR and KWH/M3 usage over [start, end).
    Uses delta-from-baseline for meter readings.
    """
    # Convert to datetimes for querying; treat end as open interval (< end_dt)
    start_dt = _to_dt(start)
    end_dt   = _to_dt(end)

    days = (end - start).days
    out: Dict[TariffFrequency, Decimal] = {
        "DAY":   _to_decimal(days),
        "MONTH": _to_decimal(days) / Decimal("30"),
        "YEAR":  _to_decimal(days) / Decimal("365"),
        "M3":    Decimal("0"),
        "KWH":   Decimal("0"),
    }

    if for_contract_scope and contract_id is not None:
        # Sum deltas across utilities by type under this contract
        gas_ids = [u.id for u in db.query(Utility).filter(Utility.contract_id == contract_id, Utility.type == "GAS")]
        elec_ids = [u.id for u in db.query(Utility).filter(Utility.contract_id == contract_id, Utility.type == "ELECTRIC")]

        if gas_ids:
            out["M3"] = sum((_delta_usage_for_utility(db, uid, start_dt, end_dt, unit="m3") for uid in gas_ids), Decimal("0"))
        if elec_ids:
            out["KWH"] = sum((_delta_usage_for_utility(db, uid, start_dt, end_dt, unit="kWh") for uid in elec_ids), Decimal("0"))
    elif utility_id is not None:
        util = db.get(Utility, utility_id)
        if util:
            if util.type == "GAS":
                out["M3"] = _delta_usage_for_utility(db, utility_id, start_dt, end_dt, unit="m3")
            else:
                out["KWH"] = _delta_usage_for_utility(db, utility_id, start_dt, end_dt, unit="kWh")

    return out
