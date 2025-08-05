from sqlalchemy import Column, Integer, String, Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

Base = declarative_base()

class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(String(100))
    client_number = Column(String(10))
    monthly_payment = Column(Decimal(5, 2), default=0)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    client_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    monthly_payment: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Define relationship to ContractCombination, if necessary
    # contract_combinations = relationship("ContractCombination", back_populates="supplier")

    def __repr__(self):
        return f"{self.name} {self.address}"
