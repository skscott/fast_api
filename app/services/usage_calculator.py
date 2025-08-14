# app/services/usage_calculator.py
from __future__ import annotations
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, Literal, Iterable, Optional
from sqlalchemy import and_, func, desc
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.db.models.reading import Reading
from app.db.models.utility import Utility

TariffFrequency = Literal["DAY", "MONTH", "YEAR", "M3", "KWH"]
# 👇 Add canonical type groups
ELECTRIC_TYPES = {"NORMAL", "REDUCED"}
GAS_TYPES = {"GAS"}

def _unit_for_type(util_type: str) -> str:
    return "m3" if util_type in GAS_TYPES else "kWh"
def _to_dt(d: date, end: bool = False) -> datetime:
    # start: 00:00 inclusive, end: treat as open interval by using the next midnight (we'll query < end_dt)
    return datetime.combine(d, time.min)

def _to_decimal(x) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x))

def _end_open(dt_date: date) -> datetime:
    # open interval endpoint: midnight of the *next* day
    return datetime.combine(dt_date + timedelta(days=1), time.min)

def _sum_unit_filter(q, unit: str | None):
    if unit:
        # case-insensitive compare
        return q.filter(func.lower(Reading.unit) == unit.lower())
    return q

def _delta_usage_for_utility(db: Session, utility_id: int, start_dt: datetime, end_dt: datetime, unit: str | None) -> Decimal:
    # Baseline: latest reading strictly before start
    q_base = db.query(Reading.value).filter(
        Reading.utility_id == utility_id,
        Reading.timestamp < start_dt,
    )
    q_base = _sum_unit_filter(q_base, unit)
    baseline = q_base.order_by(Reading.timestamp.desc()).limit(1).scalar()

    # Fallback baseline: first inside window
    if baseline is None:
        q_first = db.query(Reading.value).filter(
            Reading.utility_id == utility_id,
            Reading.timestamp >= start_dt,
            Reading.timestamp <  end_dt,
        )
        q_first = _sum_unit_filter(q_first, unit)
        baseline = q_first.order_by(Reading.timestamp.asc()).limit(1).scalar()

    # Final: latest reading before end (end is open -> includes entire end date)
    q_final = db.query(Reading.value).filter(
        Reading.utility_id == utility_id,
        Reading.timestamp < end_dt,
    )
    q_final = _sum_unit_filter(q_final, unit)
    final = q_final.order_by(Reading.timestamp.desc()).limit(1).scalar()

    if baseline is None or final is None:
        return Decimal("0")

    usage = _to_decimal(final) - _to_decimal(baseline)
    return usage if usage >= 0 else Decimal("0")

def get_usage_for_period(
    db: Session,
    contract_id: int | None,
    utility_id: int | None,
    start: date,
    end: date,
    for_contract_scope: bool,
) -> Dict[TariffFrequency, Decimal]:
    start_dt = datetime.combine(start, time.min)
    end_dt   = datetime.combine(end + timedelta(days=1), time.min)  # open interval → include end date

    days = (end - start).days
    out: Dict[TariffFrequency, Decimal] = {
        "DAY":   _to_decimal(days),
        "MONTH": _to_decimal(days) / Decimal("30"),
        "YEAR":  _to_decimal(days) / Decimal("365"),
        "M3":    Decimal("0"),
        "KWH":   Decimal("0"),
    }

    if for_contract_scope and contract_id is not None:
        # ✅ Treat NON-GAS as electric
        elec_ids = [uid for (uid,) in db.query(Utility.id)
            .filter(Utility.contract_id == contract_id, Utility.type != "GAS")]
        gas_ids = [uid for (uid,) in db.query(Utility.id)
            .filter(Utility.contract_id == contract_id, Utility.type == "GAS")]

        if elec_ids:
            out["KWH"] = sum(
                (_delta_usage_for_utility(db, uid, start_dt, end_dt, "kWh") for uid in elec_ids),
                Decimal("0"),
            )
        if gas_ids:
            out["M3"] = sum(
                (_delta_usage_for_utility(db, uid, start_dt, end_dt, "m3") for uid in gas_ids),
                Decimal("0"),
            )

    elif utility_id is not None:
        util = db.get(Utility, utility_id)
        if util:
            if util.type in GAS_TYPES:
                out["M3"]  = _delta_usage_for_utility(db, utility_id, start_dt, end_dt, "m3")
            else:  # ✅ NORMAL/REDUCED/etc. count as electric
                out["KWH"] = _delta_usage_for_utility(db, utility_id, start_dt, end_dt, "kWh")

    return out