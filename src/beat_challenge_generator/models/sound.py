from datetime import datetime
import os
from typing import Optional
from sqlalchemy import (
    String,
    BigInteger,
    DateTime,
    Boolean,
    func,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column
from beat_challenge_generator.db import Base
from beat_challenge_generator.config import BEAT_DIR

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
    
    @property
    def file_path(self) -> str:
        """
        Return the absolute path to the sound file or folder on disk.
        """
        return os.path.join(BEAT_DIR, self.category, self.relative_path)