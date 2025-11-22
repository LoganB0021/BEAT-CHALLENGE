from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    BigInteger,
    DateTime,
    func,
    JSON,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sound(Base):
    __tablename__ = "sounds"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    relative_path = Column(String(1024), nullable=False, unique=True)
    is_folder = Column(Boolean, nullable=False, default=False)
    checksum = Column(String(128), index=True, nullable=True)
    size_bytes = Column(BigInteger, index=True, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Sound(id={self.id} path={self.relative_path})>"


class Pack(Base):
    __tablename__ = "packs"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    date = Column(String(20), nullable=False, unique=True)
    seed = Column(String(64), nullable=False)
    zip_path = Column(String(1024), nullable=False)
    size_bytes = Column(BigInteger, nullable=True)
    checksum = Column(String(128), nullable=True)
    items = Column(JSON, nullable=True)
    status = Column(String(30), index=True, nullable=False, default="pending")
    generated_by = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Pack(id={self.id} name={self.name} date={self.date})>"
