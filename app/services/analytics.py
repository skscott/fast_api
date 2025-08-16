# app/services/analytics.py
from __future__ import annotations
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Tuple
from sqlalchemy.orm import Session
from app.db.models.reading import Reading
from app.db.models.utility import Utility
from app.db.models.solar import SolarReading

MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def _empty_series() -> Dict[str, List[float]]:
    return {
        "labels": MONTH_LABELS,
        "gas":      [0.0]*12,
        "stand_i":  [0.0]*12,  # NORMAL
        "stand_ii": [0.0]*12,  # REDUCED
        "solar":    [0.0]*12,
    }

def _month_idx(dt: datetime | date) -> int:
    return (dt.month - 1)  # 0..11

def _sum_deltas_by_month(
    pairs: List[Tuple[Reading, Reading]]
) -> List[Decimal]:
    """
    Given consecutive (prev, curr) reading pairs for a single utility (ordered),
    return a 12-length list of monthly consumption where each delta is added
    to the month of the *curr* reading.
    """
    per_month = [Decimal("0")] * 12
    for prev, curr in pairs:
        delta = Decimal(curr.value) - Decimal(prev.value)
        if delta < 0:
            # guard: meter rollover/correction; ignore negative
            continue
        per_month[_month_idx(curr.timestamp)] += delta
    return per_month

def _pairwise(readings: List[Reading]) -> List[Tuple[Reading, Reading]]:
    return list(zip(readings[:-1], readings[1:]))

def monthly_usage(db: Session, year: int) -> Dict[str, List[float]]:
    """
    Compute monthly usage for a given calendar year:
      - Electricity NORMAL  -> stand_i
      - Electricity REDUCED -> stand_ii
      - Gas (unit m3)       -> gas
      - Solar production    -> solar (sum, not delta)
    Bucketing rule: delta goes into the month of the *ending* reading.
    """
    result = _empty_series()

    # ---- ELECTRICITY NORMAL (stand_i) & REDUCED (stand_ii) ----
    for kind, series_key in (("NORMAL", "stand_i"), ("REDUCED", "stand_ii")):
        utils = (
            db.query(Utility.id)
              .filter(Utility.type == kind)
              .all()
        )
        utility_ids = [u.id for u in utils]
        if not utility_ids:
            continue

        # fetch all readings for these utilities within the year and unit kWh
        start_dt = datetime(year, 1, 1)
        end_dt   = datetime(year + 1, 1, 1)

        rows = (
            db.query(Reading)
              .filter(Reading.utility_id.in_(utility_ids))
              .filter(Reading.unit == "kWh")
              .filter(Reading.timestamp >= start_dt, Reading.timestamp < end_dt)
              .order_by(Reading.utility_id, Reading.timestamp)
              .all()
        )

        # group by utility, compute pairwise deltas
        by_util: Dict[int, List[Reading]] = {}
        for r in rows:
            by_util.setdefault(r.utility_id, []).append(r)

        per_month_sum = [Decimal("0")] * 12
        for lst in by_util.values():
            if len(lst) < 2:
                continue
            deltas = _sum_deltas_by_month(_pairwise(lst))
            per_month_sum = [a + b for a, b in zip(per_month_sum, deltas)]

        result[series_key] = [float(x) for x in per_month_sum]

    # ---- GAS (m3) ----
    gas_utils = db.query(Utility.id).filter(Utility.type == "GAS").all()
    gas_ids = [u.id for u in gas_utils]
    if gas_ids:
        start_dt = datetime(year, 1, 1)
        end_dt   = datetime(year + 1, 1, 1)
        rows = (
            db.query(Reading)
              .filter(Reading.utility_id.in_(gas_ids))
              .filter(Reading.unit == "m3")
              .filter(Reading.timestamp >= start_dt, Reading.timestamp < end_dt)
              .order_by(Reading.utility_id, Reading.timestamp)
              .all()
        )
        by_util: Dict[int, List[Reading]] = {}
        for r in rows:
            by_util.setdefault(r.utility_id, []).append(r)

        per_month_sum = [Decimal("0")] * 12
        for lst in by_util.values():
            if len(lst) < 2:
                continue
            deltas = _sum_deltas_by_month(_pairwise(lst))
            per_month_sum = [a + b for a, b in zip(per_month_sum, deltas)]

        result["gas"] = [float(x) for x in per_month_sum]

    # ---- SOLAR (kWh produced) ----
    # SolarReading already stores production; sum by month
    start_dt = datetime(year, 1, 1)
    end_dt   = datetime(year + 1, 1, 1)
    solar_rows = (
        db.query(SolarReading)
          .filter(SolarReading.production_date >= start_dt,
                  SolarReading.production_date < end_dt)
          .order_by(SolarReading.production_date)
          .all()
    )
    solar_per_month = [Decimal("0")] * 12
    for s in solar_rows:
        solar_per_month[_month_idx(s.production_date)] += Decimal(s.energy_produced)
    result["solar"] = [float(x) for x in solar_per_month]

    return result
