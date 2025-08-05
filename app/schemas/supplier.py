from pydantic import BaseModel

class SupplierBase(BaseModel):
    name: str
    address: str
    client_number: str
    monthly_payment: float

    class Config:
        orm_mode = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(SupplierBase):
    pass

class Supplier(SupplierBase):
    id: int
