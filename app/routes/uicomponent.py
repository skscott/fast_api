from fastapi import APIRouter
from app.db import uicomponent
from app.db.schemas import UIComponentCreate

router = APIRouter()

@router.get("/uicomponent")
def list_uicomponents():
    return uicomponent.get_all_uicomponents()

@router.post("/uicomponent")
def add_uicomponent(data: UIComponentCreate):
    return uicomponent.create_uicomponent(data)
