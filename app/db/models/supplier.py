from sqlalchemy import Column, Integer, String, Numeric
from sqlalchemy.orm import relationship
from app.db.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(String(100))
    client_number = Column(String(10))
    monthly_payment = Column(Numeric(5, 2), default=0)

    contract = relationship("Contract", back_populates="supplier", cascade="all, delete-orphan")
