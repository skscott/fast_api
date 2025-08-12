from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Contract(Base):
    __tablename__ = "contract"  # table name can be singular; that's fine

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    monthly_payment = Column(Numeric(5, 2), default=0)
    settlement_pdf = Column(Text, default="")
    contract_pdf = Column(Text, default="")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    # 👇 singular, lower-case — MUST match Supplier.contracts
    supplier  = relationship("Supplier", back_populates="contracts")

    # children
    utilities = relationship("Utility", back_populates="contract", cascade="all, delete-orphan")
    tariffs   = relationship("Tariff",  back_populates="contract", cascade="all, delete-orphan")
