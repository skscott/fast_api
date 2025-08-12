from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models, schemas
from app.db.database import SessionLocal  # Make sure to configure a database session
from typing import List

from app.db.models.contract import Contract
from app.db.schemas.contract import ContractRead
from app.db.schemas.supplier import SupplierBase

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

@router.put("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def update_supplier(
    supplier_id: int,
    supplier_update: schemas.SupplierUpdate,  # You'll need this schema
    db: Session = Depends(get_db)
):
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if not db_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    for key, value in supplier_update.dict(exclude_unset=True).items():
        setattr(db_supplier, key, value)

    db.commit()
    db.refresh(db_supplier)
    return db_supplier

@router.patch("/suppliers/{supplier_id}", response_model=schemas.Supplier)
def patch_supplier(supplier_id: int, updates: SupplierBase, db: Session = Depends(get_db)):
    supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    data = updates.dict(exclude_unset=True)  # only provided fields
    for key, value in data.items():
        setattr(supplier, key, value)

    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier