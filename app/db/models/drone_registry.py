# drone_registry.py
# -*- coding: utf-8 -*-
# This file is part of the etracker v3 project.

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime

from app.db.database import Base

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

class DroneRegistry(Base):
    __tablename__ = "drone_registry"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    drone_name: Mapped[str] = mapped_column(String, unique=True, index=True)
    mac_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    port: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    host_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    os_version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)  # e.g. "drone", "queen", "voice"
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc)
