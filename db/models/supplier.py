from sqlalchemy import Column, Integer, String, Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(String(100))
    client_number = Column(String(10))
    monthly_payment = Column(Decimal(5, 2), default=0)

    # Define relationship to ContractCombination, if necessary
    # contract_combinations = relationship("ContractCombination", back_populates="supplier")

    def __repr__(self):
        return f"{self.name} {self.address}"
