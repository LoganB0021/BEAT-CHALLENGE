import os
import importlib
from pathlib import Path

def test_db_init_and_basic_insert(tmp_path, monkeypatch):
    """Set DATABASE_URL to a temp sqlite file, initialize DB, and insert a Sound."""
    db_file = tmp_path / "test_beat.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_file}")

    # Reload db module so it picks up the env var
    import beat_challenge_generator.db as db_module
    importlib.reload(db_module)

    # Initialize database tables
    db_module.init_db()

    # Import models and session
    from beat_challenge_generator.models import Sound
    from beat_challenge_generator.db import SessionLocal

    session = SessionLocal()
    try:
        sound = Sound(
            name="test_kick",
            category="fx",
            relative_path="fx/test_kick.wav",
            is_folder=False,
            checksum="abc123",
            size_bytes=1234,
        )
        session.add(sound)
        session.commit()

        q = session.query(Sound).filter_by(relative_path="fx/test_kick.wav").one_or_none()
        assert q is not None
        assert q.checksum == "abc123"
    finally:
        session.close()
