import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from beat_challenge_generator.models import Base
from beat_challenge_generator.config import DATABASE_URL as DEFAULT_DATABASE_URL

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)

# For SQLite we need check_same_thread=False for threaded servers
connect_args = {}
if DATABASE_URL.startswith("sqlite:"):
    connect_args = {"check_same_thread": False, "timeout": 10}

engine_options = {"connect_args": connect_args}
if DATABASE_URL.startswith(("mysql://", "mysql+pymysql://")):
    engine_options.update({"pool_recycle": 280, "pool_pre_ping": True})

engine = create_engine(DATABASE_URL, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
