# app/db/schemas/cost.py
from datetime import date
from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional

class TariffSpecItem(BaseModel):
    sort: str
    description: str
    tariff_cost: Decimal
    start_date: date             # was str
    end_date: date               # was str
    amount_used: Decimal
    frequency: str

class CostRead(BaseModel):
    gas: Decimal
    stand_i: Decimal
    stand_ii: Decimal
    single: Decimal
    fixed: Decimal
    variable: Decimal
    tax: Decimal
    network: Decimal
    discount: Decimal
    total: Decimal
    specification: List[TariffSpecItem]
