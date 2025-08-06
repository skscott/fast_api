# app/schemas/utility.py
from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class UtilityBase(BaseModel):
    type: str
    text: str
    description: str
    start_reading: Decimal
    end_reading: Decimal
    start_reading_reduced: Decimal
    end_reading_reduced: Decimal
    estimated_use: Decimal

class UtilityCreate(UtilityBase):
    contract_id: int

class UtilityRead(UtilityBase):
    id: int
    contract_id: int

    class Config:
        orm_mode = True


