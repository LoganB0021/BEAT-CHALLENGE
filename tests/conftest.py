from contextlib import contextmanager

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beat_challenge_generator import config, ingest, models
from beat_challenge_generator import cleanup as cleanup_module
from beat_challenge_generator import file_manager
from api import routes


@pytest.fixture
def isolated_paths(tmp_path, monkeypatch):
    """Point filesystem-dependent modules at a private beat/output tree."""
    beats = tmp_path / "beats"
    packs = tmp_path / "packs"
    output = tmp_path / "output"
    for category in config.BEAT_SUBDIRS:
        (beats / category).mkdir(parents=True)
    packs.mkdir()
    output.mkdir()

    monkeypatch.setattr(config, "BEAT_DIR", str(beats))
    monkeypatch.setattr(config, "OUTPUT_DIR", str(output))
    monkeypatch.setattr(config, "PACKS_DIR", str(packs))
    monkeypatch.setattr(file_manager, "BEAT_DIR", str(beats))
    monkeypatch.setattr(file_manager, "OUTPUT_DIR", str(output))
    monkeypatch.setattr(file_manager, "PACKS_DIR", str(packs))
    monkeypatch.setattr(models, "BEAT_DIR", str(beats))
    monkeypatch.setattr(cleanup_module, "PACKS_DIR", str(packs))
    return {"root": tmp_path, "beats": beats, "packs": packs, "output": output}


@pytest.fixture
def asset_tree(isolated_paths):
    """Create a small but representative beat tree, including a nested kit."""
    beats = isolated_paths["beats"]
    kit = beats / "drum_kits" / "Kit Alpha"
    (kit / "nested").mkdir(parents=True)
    (kit / "kick.wav").write_bytes(b"kick")
    (kit / "nested" / "hat.wav").write_bytes(b"hat")
    (beats / "drum_kits" / "Kit Beta").mkdir()
    (beats / "drum_kits" / "Kit Beta" / "snare.wav").write_bytes(b"snare")
    (beats / "fx" / "reverb.wav").write_bytes(b"reverb")
    (beats / "fx" / "delay.wav").write_bytes(b"delay")
    (beats / "samples" / "melody.wav").write_bytes(b"melody")
    (beats / "samples" / "bass.wav").write_bytes(b"bass")
    return beats


@pytest.fixture
def database(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'beat-test.db'}",
        connect_args={"check_same_thread": False},
    )
    models.Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(database):
    return sessionmaker(bind=database, expire_on_commit=False)


@pytest.fixture
def db_session(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture
def ingested_assets(asset_tree, database, session_factory, monkeypatch):
    """Run the real ingest path and return the resulting indexed sounds."""
    monkeypatch.setattr(ingest.db, "init_db", lambda: None)
    monkeypatch.setattr(ingest, "create_engine", lambda *args, **kwargs: database)
    stats = ingest.ingest_beats()
    with session_factory() as session:
        sounds = session.query(models.Sound).all()
    return {"stats": stats, "sounds": sounds}


@pytest.fixture
def api_app(monkeypatch, session_factory):
    """Factory for Flask apps whose routes use the isolated test database."""

    @contextmanager
    def session_context():
        with session_factory() as session:
            yield session

    monkeypatch.setattr(routes, "get_session", session_context)

    def make_app(**overrides):
        settings = {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "ALLOWED_ORIGINS": [],
            "ALLOW_RANDOM_CHALLENGES": False,
            "ALLOW_ASYNC_CHALLENGES": False,
            "BEAT_API_KEY": None,
            "JOB_RATE_LIMIT_SECONDS": 60,
            "MAX_JOBS_PER_RATE_WINDOW": 1,
            "TRUSTED_HOSTS": None,
            "MAX_CONTENT_LENGTH": 16 * 1024,
        }
        settings.update(overrides)
        config_object = type("TestConfig", (), settings)
        from api.app import create_app

        return create_app(config_object)

    return make_app


@pytest.fixture
def sounds_by_category(ingested_assets):
    sounds = {
        sound.relative_path: sound for sound in ingested_assets["sounds"]
    }
    return {
        "drum_kits": sounds["Kit Alpha"],
        "fx": sounds["delay.wav"],
        "samples": sounds["bass.wav"],
    }
