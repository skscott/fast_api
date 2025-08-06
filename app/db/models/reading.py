# app/db/models/reading.py
from sqlalchemy import Column, Integer, DateTime, Numeric, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    value = Column(Numeric(10, 3), nullable=False)
    unit = Column(String(10), default="kWh")  # e.g. "kWh", "m3"
    source = Column(String(50), default="manual")

    utility_id = Column(Integer, ForeignKey("utilities.id"), nullable=False)
    utility = relationship("Utility", back_populates="readings")


# app/db/models/utility.py (extend your Utility model)
readings = relationship("Reading", back_populates="utility", cascade="all, delete-orphan")
