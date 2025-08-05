from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContractGroupBase(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date
    monthly_payment: float
    settlement_pdf: Optional[str] = ""
    contract_pdf: Optional[str] = ""

class ContractGroupCreate(ContractGroupBase):
    supplier_id: int

class ContractGroupRead(ContractGroupBase):
    id: int
    supplier_id: int

    class Config:
        orm_mode = True
