from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import Dict, Literal, Any

TariffFrequency = Literal["DAY", "MONTH", "YEAR", "M3", "KWH"]

class Cost:
    def __init__(self):
        self.tariff_specification: list[dict[str, Any]] = []
        self.gas = Decimal("0")
        self.stand_i = Decimal("0")      # reduced bucket
        self.stand_ii = Decimal("0")     # normal bucket
        self.single = Decimal("0")
        self.fixed = Decimal("0")
        self.variable = Decimal("0")
        self.tax = Decimal("0")
        self.network = Decimal("0")
        self.discount = Decimal("0")

    @property
    def total(self) -> Decimal:
        total = (
            self.gas + self.stand_i + self.stand_ii + self.single +
            self.fixed + self.variable + self.tax + self.network + self.discount
        )
        return total.quantize(Decimal("0.01"))

class TariffCalculator(ABC):
    @abstractmethod
    def calculate(self, tariff, cost: Cost, usage: Dict[TariffFrequency, Decimal], p_start: date, p_end: date) -> None: ...

class BaseTariffCalculator(TariffCalculator):
    def calculate(self, tariff, cost: Cost, usage: Dict[TariffFrequency, Decimal], p_start: date, p_end: date):
        days = Decimal((p_end - p_start).days)
        tariff_cost = Decimal("0")
        amount_used = Decimal("0")

        if tariff.frequency == "DAY":
            amount_used = days
            tariff_cost = Decimal(tariff.amount) * days
        elif tariff.frequency == "MONTH":
            amount_used = days / Decimal("30")
            tariff_cost = Decimal(tariff.amount) * amount_used
        elif tariff.frequency == "YEAR":
            amount_used = days
            tariff_cost = Decimal(tariff.amount) * (days / Decimal("365"))
        elif tariff.frequency in ("M3", "KWH"):
            amount_used = usage.get(tariff.frequency, Decimal("0"))
            tariff_cost = Decimal(tariff.amount) * amount_used
        else:
            raise ValueError(f"Unsupported frequency: {tariff.frequency}")

        self._apply(cost, tariff_cost)

        self._append_spec(cost, tariff, tariff_cost, p_start, p_end, amount_used)

    def _append_spec(self, cost: Cost, tariff, tariff_cost: Decimal, p_start: date, p_end: date, amount_used: Decimal):
        cost.tariff_specification.append({
            "sort": tariff.tariff_sort,
            "description": tariff.description,
            "tariff_cost": tariff_cost.quantize(Decimal("0.01")),
            "start_date": p_start,
            "end_date": p_end,
            "amount_used": amount_used,
            "frequency": tariff.frequency,
        })

    @abstractmethod
    def _apply(self, cost: Cost, amount: Decimal) -> None: ...

class NormalTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.stand_ii += amount

class ReducedTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.stand_i += amount

class SingleTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.single += amount

class FixedTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.fixed += amount

class VariableTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.variable += amount

class TaxTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.tax += amount

class NetworkTariffCalculator(BaseTariffCalculator):
    def _apply(self, cost: Cost, amount: Decimal) -> None:
        cost.network += amount

class PercentageTariffCalculator(TariffCalculator):
    def calculate(self, tariff, cost: Cost, usage: Dict[TariffFrequency, Decimal], p_start: date, p_end: date) -> None:
        base = cost.gas + cost.stand_i + cost.stand_ii + cost.single + cost.fixed + cost.variable
        amount = (base * Decimal(tariff.amount) / Decimal("100"))
        cost.discount += amount
        cost.tariff_specification.append({
            "sort": tariff.tariff_sort,
            "description": tariff.description,
            "tariff_cost": amount.quantize(Decimal("0.01")),
            "start_date": p_start,
            "end_date": p_end,
            "amount_used": Decimal(tariff.amount),
            "frequency": "PERCENT",
        })

class TariffCalculatorFactory:
    MAP = {
        "NORMAL":     NormalTariffCalculator(),
        "REDUCED":    ReducedTariffCalculator(),
        "SINGLE":     SingleTariffCalculator(),
        "FIXED":      FixedTariffCalculator(),
        "VARIABLE":   VariableTariffCalculator(),
        "TAX":        TaxTariffCalculator(),
        "NETWORK":    NetworkTariffCalculator(),
        "PERCENTAGE": PercentageTariffCalculator(),
    }

    @staticmethod
    def get_calculator(tariff_sort: str) -> TariffCalculator:
        calc = TariffCalculatorFactory.MAP.get(tariff_sort)
        if not calc:
            raise ValueError(f"No calculator for sort {tariff_sort}")
        return calc
