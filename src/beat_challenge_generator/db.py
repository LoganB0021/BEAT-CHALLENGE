import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from beat_challenge_generator.models import Base
from beat_challenge_generator.config import DATA_DIR

# Determine database URL from env or config
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # default sqlite file inside data dir
    db_path = os.path.join(DATA_DIR, "beat_challenge.db")
    DATABASE_URL = f"sqlite:///{db_path}"

# For SQLite we need check_same_thread=False for threaded servers
connect_args = {}
if DATABASE_URL.startswith("sqlite:"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
