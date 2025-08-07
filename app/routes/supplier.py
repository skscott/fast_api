from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models, schemas
from app.db.database import SessionLocal  # Make sure to configure a database session
from typing import List

from app.db.models.contract import Contract
from app.db.schemas.contract import ContractRead

router = APIRouter()

# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# List suppliers
@router.get("/suppliers", response_model=List[schemas.Supplier])
def get_suppliers(db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).all()
    return suppliers

# Get individual supplier by ID
@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

# Create a new supplier
@router.post("/suppliers", response_model=schemas.Supplier)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.get("/suppliers/{supplier_id}/contracts", response_model=List[ContractRead])
def get_contracts_for_supplier(supplier_id: int, db: Session = Depends(get_db)):
    # Assuming the Contract model has a supplier_id foreign key to link contracts to suppliers
    contracts = db.query(Contract).filter(Contract.supplier_id == supplier_id).all()
    if not contracts:
        raise HTTPException(status_code=404, detail="Contracts not found for this supplier")
    return contracts
