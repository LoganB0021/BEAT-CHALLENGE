from datetime import date

import pytest

from beat_challenge_generator.challenge_service import (
    generate_challenge,
    random_select,
)
from beat_challenge_generator.file_selector import deterministic_select_by_date
from beat_challenge_generator.models import Pack


def test_deterministic_selector_is_repeatable(db_session, ingested_assets):
    first = deterministic_select_by_date(db_session, date(2026, 9, 9))
    second = deterministic_select_by_date(db_session, date(2026, 9, 9))
    assert {key: value.id for key, value in first.items()} == {
        key: value.id for key, value in second.items()
    }


def test_random_selector_returns_at_most_one_item_per_category(
    db_session, ingested_assets, monkeypatch
):
    monkeypatch.setattr(
        "beat_challenge_generator.challenge_service.random.choice",
        lambda values: values[-1],
    )
    selected = random_select(db_session)
    assert set(selected) == {"drum_kits", "fx", "samples"}
    indexed_ids = {sound.id for sound in ingested_assets["sounds"]}
    assert all(sound.id in indexed_ids for sound in selected.values())


def test_daily_generation_reuses_existing_pack(
    db_session, ingested_assets, monkeypatch
):
    target = date(2026, 9, 9)
    first = generate_challenge(db_session, target_date=target)
    second = generate_challenge(db_session, target_date=target)
    assert first.id == second.id
    assert first.zip_path == second.zip_path
    assert db_session.query(Pack).count() == 1


def test_daily_generation_regenerates_missing_archive(
    db_session, ingested_assets
):
    target = date(2026, 9, 9)
    first = generate_challenge(db_session, target_date=target)
    import os

    os.remove(first.zip_path)
    second = generate_challenge(db_session, target_date=target)
    assert second.zip_path != first.zip_path
    assert os.path.exists(second.zip_path)
    assert db_session.query(Pack).count() == 1


def test_daily_overwrite_replaces_archive(db_session, ingested_assets):
    target = date(2026, 9, 9)
    first = generate_challenge(db_session, target_date=target)
    old_path = first.zip_path
    second = generate_challenge(db_session, target_date=target, overwrite=True)
    import os

    assert second.zip_path != old_path
    assert not os.path.exists(old_path)
    assert os.path.exists(second.zip_path)
    assert db_session.query(Pack).count() == 1


def test_invalid_generation_mode_is_rejected(db_session):
    with pytest.raises(ValueError, match="mode"):
        generate_challenge(db_session, mode="invalid")
