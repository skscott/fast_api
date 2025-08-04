from app.db.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    node = Column(String, index=True)
    temperature = Column(Float)
    create_at = Column(DateTime, default=datetime.utcnow)
