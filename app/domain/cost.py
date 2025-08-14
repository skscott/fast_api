# app/domain/cost.py
from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Literal, Optional
from datetime import date

SpecFreq = Literal["DAY","MONTH","YEAR","M3","KWH"]

@dataclass
class SpecLine:
    sort: str
    description: str
    tariff_cost: Decimal
    start_date: date
    end_date: date
    amount_used: Decimal
    frequency: SpecFreq

@dataclass
class Cost:
    # buckets to keep parity with your legacy version
    gas: Decimal = Decimal("0")
    stand_i: Decimal = Decimal("0")    # “reduced” bucket (night) in your legacy mapping
    stand_ii: Decimal = Decimal("0")   # “normal” bucket (day)   in your legacy mapping
    single: Decimal = Decimal("0")
    fixed: Decimal = Decimal("0")
    variable: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    network: Decimal = Decimal("0")
    discount: Decimal = Decimal("0")   # percentage → put the computed discount here
    tariff_specification: List[SpecLine] = field(default_factory=list)

    @property
    def total(self) -> Decimal:
        return (
            self.gas + self.stand_i + self.stand_ii + self.single
            + self.fixed + self.variable + self.tax + self.network + self.discount
        )
