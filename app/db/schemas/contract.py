from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContractBase(BaseModel):
    name: str
    description: str
    start_date: date
    end_date: date
    monthly_payment: float
    settlement_pdf: Optional[str] = ""
    contract_pdf: Optional[str] = ""

class ContractUpdate(ContractBase):
    name: Optional[str] = None
    description: str
    start_date: date
    end_date: date
    monthly_payment: float
    settlement_pdf: Optional[str] = ""
    contract_pdf: Optional[str] = ""

class ContractCreate(ContractBase):
    supplier_id: int

class ContractRead(ContractBase):
    id: int
    supplier_id: int

    class Config:
        orm_mode = True
