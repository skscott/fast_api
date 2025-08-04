from sqlalchemy import Column, Integer, String, Boolean
from app.db.database import Base

class UIComponent(Base):
    __tablename__ = "ui_components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_visible = Column(Boolean, default=True)
