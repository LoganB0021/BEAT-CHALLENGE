import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beat_challenge_generator.models import Base, Sound
from beat_challenge_generator.file_selector import deterministic_select_by_date


# --------------------------
# Database Fixtures
# --------------------------

@pytest.fixture
def test_db():
    """Create an in-memory SQLite DB with the Sound table."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)

    # Create tables
    Base.metadata.create_all(engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def populated_db(test_db):
    """Populate DB with sample Sound entries for each category."""
    sounds = [
        Sound(name="kick.wav",     category="drum_kits", relative_path="kick.wav",     is_folder=False),
        Sound(name="snare.wav",    category="drum_kits", relative_path="snare.wav",    is_folder=False),
        Sound(name="boom.wav",     category="fx",         relative_path="boom.wav",     is_folder=False),
        Sound(name="crash.wav",    category="fx",         relative_path="crash.wav",    is_folder=False),
        Sound(name="melody1.wav",  category="samples",    relative_path="melody1.wav",  is_folder=False),
        Sound(name="melody2.wav",  category="samples",    relative_path="melody2.wav",  is_folder=False),
    ]

    test_db.add_all(sounds)
    test_db.commit()

    return test_db

# --------------------------
# Tests
# --------------------------

def test_deterministic_same_date_same_results(populated_db):
    """Calling deterministic_select_by_date with the same date must return identical results."""

    target_date = date(2024, 5, 17)

    first = deterministic_select_by_date(populated_db, target_date)
    second = deterministic_select_by_date(populated_db, target_date)

    assert first.keys() == second.keys()
    for category in first:
        assert first[category].name == second[category].name


def test_deterministic_different_dates_different_results(populated_db):
    """Two different dates should (usually) return different selections."""

    date1 = date(2024, 5, 17)
    date2 = date(2024, 5, 18)

    result1 = deterministic_select_by_date(populated_db, date1)
    result2 = deterministic_select_by_date(populated_db, date2)

    # It's possible but unlikely they collide, so use inequality OR fallback
    differences = sum(
        result1[cat].name != result2[cat].name
        for cat in result1.keys()
    )

    # At least ONE category should differ
    assert differences >= 1


def test_returns_all_categories(populated_db):
    """Ensure that all categories return a selected item."""
    result = deterministic_select_by_date(populated_db)

    assert set(result.keys()) == {"drum_kits", "fx", "samples"}

    for sound in result.values():
        assert isinstance(sound, Sound)
        assert sound.name.endswith(".wav")