from pydantic import BaseModel
from datetime import datetime

class Reading(BaseModel):
    node: str
    temperature: float
    timestamp: datetime

    class Config:
        from_attributes = True
