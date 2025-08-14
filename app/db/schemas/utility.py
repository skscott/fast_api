# app/db/schemas/utility.py
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

class UtilityUpdate(BaseModel):
    # all fields optional for partial update via PUT
    type: Optional[str] = None
    text: Optional[str] = None
    description: Optional[str] = None
    start_reading: Optional[Decimal] = None
    end_reading: Optional[Decimal] = None
    start_reading_reduced: Optional[Decimal] = None
    end_reading_reduced: Optional[Decimal] = None
    estimated_use: Optional[Decimal] = None
    contract_id: Optional[int] = None  # allow moving between contracts if desired

class UtilityRead(UtilityBase):
    id: int
    contract_id: int

    class Config:
        orm_mode = True
