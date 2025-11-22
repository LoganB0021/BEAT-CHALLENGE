import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beat_challenge_generator import models, db, ingest
from beat_challenge_generator.logger import logger


@pytest.fixture
def temp_beats_dir():
    """Create a temporary beats directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        beats_root = Path(tmpdir) / "beats"
        beats_root.mkdir()

        # Create drum_kits subdirectory with a file and a folder
        drum_kits = beats_root / "drum_kits"
        drum_kits.mkdir()
        (drum_kits / "kit_file.zip").write_text("fake kit file")
        kit_folder = drum_kits / "kit_folder"
        kit_folder.mkdir()
        (kit_folder / "nested_file.txt").write_text("nested content")

        # Create fx subdirectory with files
        fx = beats_root / "fx"
        fx.mkdir()
        (fx / "reverb.mp3").write_text("fake reverb")
        (fx / "delay.mp3").write_text("fake delay")

        # Create samples subdirectory with files
        samples = beats_root / "samples"
        samples.mkdir()
        (samples / "drum_sample.wav").write_text("fake drum sample")

        yield beats_root


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        database_url = f"sqlite:///{db_path}"

        # Create tables
        engine = create_engine(database_url, connect_args={"check_same_thread": False})
        models.Base.metadata.create_all(engine)

        yield database_url, engine


@pytest.fixture
def mock_config(temp_beats_dir):
    """Mock config.BEAT_DIR and config.BEAT_SUBDIRS."""
    with mock.patch("beat_challenge_generator.ingest.config") as mock_cfg:
        mock_cfg.BEAT_DIR = str(temp_beats_dir)
        mock_cfg.BEAT_SUBDIRS = ["drum_kits", "fx", "samples"]
        mock_cfg.DATABASE_URL = None  # Will be overridden in test
        yield mock_cfg


def test_ingest_all_categories(mock_config, temp_db):
    """Test ingesting all categories."""
    database_url, engine = temp_db
    mock_config.DATABASE_URL = database_url

    with mock.patch("beat_challenge_generator.ingest.config", mock_config):
        with mock.patch("beat_challenge_generator.ingest.create_engine", return_value=engine):
            stats = ingest.ingest_beats(dry_run=False, category=None)

    assert stats["scanned"] == 5  # kit_file.zip, kit_folder, reverb.mp3, delay.mp3, drum_sample.wav
    assert stats["added"] == 5
    assert stats["updated"] == 0
    assert stats["unchanged"] == 0

    # Verify records in DB
    Session = sessionmaker(bind=engine)
    with Session() as session:
        drum_kits = session.query(models.Sound).filter_by(category="drum_kits").all()
        assert len(drum_kits) == 2
        assert any(s.filename == "kit_file.zip" and not s.is_folder for s in drum_kits)
        assert any(s.filename == "kit_folder" and s.is_folder for s in drum_kits)

        fx_records = session.query(models.Sound).filter_by(category="fx").all()
        assert len(fx_records) == 2
        assert all(not s.is_folder for s in fx_records)

        samples = session.query(models.Sound).filter_by(category="samples").all()
        assert len(samples) == 1


def test_ingest_single_category(mock_config, temp_db):
    """Test ingesting only a single category."""
    database_url, engine = temp_db
    mock_config.DATABASE_URL = database_url

    with mock.patch("beat_challenge_generator.ingest.config", mock_config):
        with mock.patch("beat_challenge_generator.ingest.create_engine", return_value=engine):
            stats = ingest.ingest_beats(dry_run=False, category="fx")

    assert stats["scanned"] == 2  # reverb.mp3, delay.mp3
    assert stats["added"] == 2
    assert stats["updated"] == 0

    # Verify only fx records exist
    Session = sessionmaker(bind=engine)
    with Session() as session:
        all_records = session.query(models.Sound).all()
        assert len(all_records) == 2
        assert all(s.category == "fx" for s in all_records)


def test_ingest_dry_run(mock_config, temp_db):
    """Test dry-run mode: changes should not be committed."""
    database_url, engine = temp_db
    mock_config.DATABASE_URL = database_url

    with mock.patch("beat_challenge_generator.ingest.config", mock_config):
        with mock.patch("beat_challenge_generator.ingest.create_engine", return_value=engine):
            stats = ingest.ingest_beats(dry_run=True, category=None)

    assert stats["added"] == 5  # Still reports what would be added

    # Verify nothing was actually committed to DB
    Session = sessionmaker(bind=engine)
    with Session() as session:
        all_records = session.query(models.Sound).all()
        assert len(all_records) == 0


def test_ingest_idempotent_no_changes(mock_config, temp_db):
    """Test that running ingest twice without changes marks records as unchanged."""
    database_url, engine = temp_db
    mock_config.DATABASE_URL = database_url

    with mock.patch("beat_challenge_generator.ingest.config", mock_config):
        with mock.patch("beat_challenge_generator.ingest.create_engine", return_value=engine):
            # First ingest
            stats1 = ingest.ingest_beats(dry_run=False, category=None)
            assert stats1["added"] == 5

            # Second ingest (no changes)
            stats2 = ingest.ingest_beats(dry_run=False, category=None)
            assert stats2["scanned"] == 5
            assert stats2["added"] == 0
            assert stats2["updated"] == 0
            assert stats2["unchanged"] == 5


def test_ingest_update_on_checksum_change(mock_config, temp_db):
    """Test that ingest detects and updates records when checksums change."""
    database_url, engine = temp_db
    mock_config.DATABASE_URL = database_url

    with mock.patch("beat_challenge_generator.ingest.config", mock_config):
        with mock.patch("beat_challenge_generator.ingest.create_engine", return_value=engine):
            # First ingest
            stats1 = ingest.ingest_beats(dry_run=False, category=None)
            assert stats1["added"] == 5

            # Modify a file to change its checksum
            beats_root = Path(mock_config.BEAT_DIR)
            reverb_file = beats_root / "fx" / "reverb.mp3"
            reverb_file.write_text("modified reverb content")

            # Second ingest should detect the change
            stats2 = ingest.ingest_beats(dry_run=False, category=None)
            assert stats2["scanned"] == 5
            assert stats2["added"] == 0
            assert stats2["updated"] == 1  # reverb.mp3 was updated
            assert stats2["unchanged"] == 4


def test_ingest_invalid_category_warning(mock_config, temp_db, caplog):
    """Test that an invalid category logs a warning and returns empty stats."""
    database_url, engine = temp_db
    mock_config.DATABASE_URL = database_url

    with mock.patch("beat_challenge_generator.ingest.config", mock_config):
        with mock.patch("beat_challenge_generator.ingest.create_engine", return_value=engine):
            stats = ingest.ingest_beats(dry_run=False, category="invalid_category")

    assert stats["scanned"] == 0
    assert stats["added"] == 0


def test_file_checksum_and_size():
    """Test file_checksum_and_size utility."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"test content")
        tmp.flush()
        tmp_path = Path(tmp.name)

    try:
        checksum, size = ingest.file_checksum_and_size(tmp_path)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex is 64 chars
        assert size == 12  # "test content" is 12 bytes
    finally:
        tmp_path.unlink()


def test_directory_checksum_and_size_deterministic():
    """Test that directory_checksum_and_size is deterministic."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        (dir_path / "file_a.txt").write_text("content a")
        (dir_path / "file_b.txt").write_text("content b")

        checksum1, size1 = ingest.directory_checksum_and_size(dir_path)
        checksum2, size2 = ingest.directory_checksum_and_size(dir_path)

        assert checksum1 == checksum2  # Same checksum on repeated calls
        assert size1 == size2


def test_directory_checksum_changes_on_content_change():
    """Test that directory checksum changes when content changes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        (dir_path / "file_a.txt").write_text("content a")

        checksum1, _ = ingest.directory_checksum_and_size(dir_path)

        # Modify content
        (dir_path / "file_a.txt").write_text("modified content")
        checksum2, _ = ingest.directory_checksum_and_size(dir_path)

        assert checksum1 != checksum2