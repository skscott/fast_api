from pydantic import BaseModel
from typing import Optional

class SupplierBase(BaseModel):
    name: str
    address: str
    client_number: str

    class Config:
        orm_mode = True

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    client_number: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
