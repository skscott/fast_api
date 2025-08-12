# app/db/schemas/tariff.py
from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date
from decimal import Decimal
from app.db.models.enums import TariffSort, Frequency

class TariffBase(BaseModel):
  description: str
  amount: Decimal
  tariff_sort: TariffSort
  frequency: Frequency
  start_date: Optional[date] = None
  end_date: Optional[date] = None
  is_active: bool = True

  contract_id: Optional[int] = None
  utility_id:  Optional[int] = None

  @field_validator("utility_id")
  @classmethod
  def check_scope(cls, v, info):
    data = info.data
    # exactly one of utility_id / contract_id must be set
    if (v is None) == (data.get("contract_id") is None):
      raise ValueError("Provide exactly one of utility_id or contract_id")
    return v

class TariffCreate(TariffBase):
  pass

class TariffUpdate(BaseModel):
  description: Optional[str] = None
  amount: Optional[Decimal] = None
  tariff_sort: Optional[TariffSort] = None
  frequency: Optional[Frequency] = None
  start_date: Optional[date] = None
  end_date: Optional[date] = None
  is_active: Optional[bool] = None
  contract_id: Optional[int] = None
  utility_id:  Optional[int] = None

class TariffRead(TariffBase):
  id: int
  class Config:
    from_attributes = True
