# app/db/schemas/reading.py
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal

class SolarBase(BaseModel):
    timestamp: datetime
    production_date: datetime
    panel_serial_nbr: str
    energy_produced: float

class SolarCreate(SolarBase):
    reading_id: int

class SolarRead(SolarBase):
    id: int
    reading_id: int

    class Config:
        orm_mode = True
