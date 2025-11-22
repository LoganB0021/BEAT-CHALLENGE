from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    BigInteger,
    DateTime,
    func,
    JSON,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Sound(Base):
    __tablename__ = "sounds"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(50), index=True)
    relative_path: Mapped[str] = mapped_column(String(1024), unique=True)
    is_folder: Mapped[bool] = mapped_column(Boolean, default=False)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), index=True, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, index=True, nullable=True)
    tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self) -> str:
        return f"<Sound(id={self.id} path={self.relative_path})>"


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
