from __future__ import annotations
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.db.models.utility import Utility
from app.db.models.tariff import Tariff
from app.services.tariff_calculators import Cost, TariffCalculatorFactory
from app.services.usage_calculator import get_usage_for_period

def _clip_period(req_start: date, req_end: date, t_start: date | None, t_end: date | None):
    eff_start = max(req_start, t_start) if t_start else req_start
    eff_end = min(req_end, (t_end + timedelta(days=1)) if t_end else req_end)  # treat tariff end as inclusive
    return (eff_start, eff_end) if eff_start < eff_end else None

def compute_utility_cost(
    db: Session,
    utility_id: int,
    start: date,
    end: date,
    include_contract_tariffs: bool = True,
) -> Cost:
    util = db.get(Utility, utility_id)
    if not util:
        raise ValueError("Utility not found")

    # clip end to today (optional)
    today = date.today()
    if end > today:
        end = today

    # collect tariffs
    tariffs = list(
        db.query(Tariff).filter(
            Tariff.is_active == True,
            Tariff.utility_id == utility_id
        )
    )
    if include_contract_tariffs and util.contract_id is not None:
        tariffs += list(
            db.query(Tariff).filter(
                Tariff.is_active == True,
                Tariff.contract_id == util.contract_id,
                Tariff.utility_id == None
            )
        )

    cost = Cost()

    for t in tariffs:
        clipped = _clip_period(start, end, t.start_date, t.end_date)
        if not clipped:
            continue
        p_start, p_end = clipped

        is_contract_scope = (t.utility_id is None)

        usage = get_usage_for_period(
            db=db,
            contract_id=util.contract_id if is_contract_scope else None,
            utility_id=None if is_contract_scope else util.id,
            start=p_start,
            end=p_end,
            for_contract_scope=is_contract_scope,
        )

        calc = TariffCalculatorFactory.get_calculator(t.tariff_sort)
        calc.calculate(t, cost, usage, p_start, p_end)

    return cost  # IMPORTANT: return ONLY the Cost object
