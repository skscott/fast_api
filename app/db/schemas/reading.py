# app/db/schemas/reading.py
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class ReadingBase(BaseModel):
    timestamp: datetime
    value: Decimal
    unit: str = "kWh"
    source: str = "manual"

class ReadingCreate(ReadingBase):
    utility_id: int

class ReadingRead(ReadingBase):
    id: int
    utility_id: int

    class Config:
        orm_mode = True
