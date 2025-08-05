from sqlalchemy import Column, Integer, String, Date, Numeric, Text, ForeignKey
from sqlalchemy.orm import relationship, validates
from app.db.database import Base
from decimal import Decimal

class ContractGroup(Base):
    __tablename__ = "contract_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    description = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    monthly_payment = Column(Numeric(5, 2), default=0)
    settlement_pdf = Column(Text, default="")
    contract_pdf = Column(Text, default="")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))

    supplier = relationship("Supplier", back_populates="contract_groups")

    # Optional: add reverse relationship from related contracts if needed
    # contracts = relationship("Contract", back_populates="contract_group")

    def __str__(self):
        return f"{self.description} {self.start_date} {self.end_date} {self.monthly_payment}"
