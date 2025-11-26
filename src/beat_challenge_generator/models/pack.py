from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    BigInteger,
    DateTime,
    func,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from beat_challenge_generator.db.base import Base

class Pack(Base):
    __tablename__ = "packs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    date: Mapped[str] = mapped_column(String(20), unique=True)
    seed: Mapped[str] = mapped_column(String(64))
    zip_path: Mapped[str] = mapped_column(String(1024))
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    items: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), index=True, default="pending")
    generated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        return f"<Pack(id={self.id} name={self.name} date={self.date})>"
