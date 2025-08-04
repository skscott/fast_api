from fastapi import APIRouter
from app.db import supplier
from app.db.schemas import UIComponentCreate

router = APIRouter()

@router.get("/supplier")
def list_supplier():
    return supplier.get_all_uicomponents()

@router.post("/supplier")
def add_supplier(data: UIComponentCreate):
    return supplier.create_uicomponent(data)
