from sqlalchemy import Column, Integer, String, Date, Numeric, Boolean, Enum, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.models.enums import TariffSort, Frequency

class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String(100), nullable=False)
    amount = Column(Numeric(12, 4), nullable=False)
    tariff_sort = Column(Enum(TariffSort, name="tariff_sort_enum"), nullable=False)
    frequency   = Column(Enum(Frequency,   name="tariff_freq_enum"),  nullable=False)
    start_date = Column(Date)
    end_date   = Column(Date)
    is_active  = Column(Boolean, nullable=False, default=True)

    # scope: exactly one must be set
    contract_id = Column(Integer, ForeignKey("contract.id"),  nullable=True)
    utility_id  = Column(Integer, ForeignKey("utilities.id"), nullable=True)

    # parents — MUST match names on the other side
    contract = relationship("Contract", back_populates="tariffs")
    utility  = relationship("Utility",  back_populates="tariffs")

    __table_args__ = (
        CheckConstraint("(contract_id IS NOT NULL) <> (utility_id IS NOT NULL)",
                        name="ck_tariff_exactly_one_scope"),
    )
