from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class SolarReading(Base):
    __tablename__ = "solar_readings"

    id = Column(Integer, primary_key=True, index=True)
    production_date = Column(Date, nullable=False)
    panel_serial_nbr = Column(String, nullable=False, index=True)
    energy_produced = Column(DECIMAL(scale=3), nullable=False)
    unit = Column(String, nullable=False)