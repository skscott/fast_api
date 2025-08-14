from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Utility(Base):
    __tablename__ = "utilities"

    id = Column(Integer, primary_key=True)
    type = Column(String(20))
    text = Column(String(255))
    description = Column(String(255))
    start_reading = Column(Numeric(10, 3))
    end_reading = Column(Numeric(10, 3))
    start_reading_reduced = Column(Numeric(10, 3))
    end_reading_reduced = Column(Numeric(10, 3))
    estimated_use = Column(Numeric(10, 3))
    
    contract_id = Column(Integer, ForeignKey("contract.id"))

    # parent
    contract = relationship("Contract", back_populates="utilities")

    # children (optional in your app)
    readings = relationship("Reading", back_populates="utility", cascade="all, delete-orphan")

    # tariffs that are scoped to this utility
    tariffs  = relationship("Tariff",  back_populates="utility",  cascade="all, delete-orphan")
