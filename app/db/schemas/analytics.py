# app/db/schemas/analytics.py
from pydantic import BaseModel
from typing import List

class ChartData(BaseModel):
    labels: List[str]
    gas: List[float]
    stand_i: List[float]   # reduced electricity
    stand_ii: List[float]  # normal electricity
    solar: List[float]
