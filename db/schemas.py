from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# ========== User Schemas ==========

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # For Pydantic v2 — replaces orm_mode


class RegisterInput(BaseModel):
    username: str
    password: str


class LoginInput(BaseModel):
    username: str
    password: str


# ========== Token Response ==========

class Token(BaseModel):
    token: str
    user: User


class Reading(BaseModel):
    node: str
    temperature: float
    timestamp: datetime

    class Config:
        from_attributes = True  # ✅ instead of orm_mode = True


class UIComponentBase(BaseModel):
    name: str
    is_visible: bool

class UIComponentCreate(UIComponentBase):
    pass

class UIComponent(UIComponentBase):
    id: int

    class Config:
        from_attributes = True  # or orm_mode = True if you're on Pydantic v1


# Assuming you also have a ContractCombination Pydantic model
# from .contract_combination import ContractCombinationBase

class SupplierBase(BaseModel):
    name: str
    address: str
    client_number: str
    monthly_payment: float

    class Config:
        orm_mode = True  # Tells Pydantic to treat SQLAlchemy models as dictionaries

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
    # contract_combinations: List[ContractCombinationBase]  # If you're returning ContractCombination data

    class Config:
        orm_mode = True
