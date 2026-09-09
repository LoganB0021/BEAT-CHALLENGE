from datetime import datetime, timedelta, timezone
from contextlib import contextmanager

from beat_challenge_generator import cleanup
from beat_challenge_generator.models import ChallengeJob, Pack


def _write_pack(path, content):
    path.write_bytes(content)
    return str(path)


def test_cleanup_retains_recent_archives_and_daily_reference(
    isolated_paths, session_factory, monkeypatch
):
    @contextmanager
    def session_context():
        with session_factory() as db:
            yield db

    monkeypatch.setattr(cleanup, "get_session", session_context)
    packs_dir = isolated_paths["packs"]
    old = packs_dir / "old.zip"
    recent = packs_dir / "recent.zip"
    daily = packs_dir / "daily.zip"
    _write_pack(old, b"old")
    _write_pack(recent, b"recent")
    _write_pack(daily, b"daily")
    old.touch()
    daily_pack = Pack(
        name="pack-daily",
        date=datetime.now().date().isoformat(),
        seed="1",
        zip_path=str(daily),
        status="generated",
    )
    with session_factory() as db:
        db.add(daily_pack)
        db.commit()
    old_time = (datetime.now() - timedelta(days=3)).timestamp()
    import os

    os.utime(old, (old_time, old_time))
    removed, temps = cleanup.cleanup_packs(keep=1, temp_age_hours=24)
    assert removed == 1
    assert temps == 0
    assert not old.exists()
    assert recent.exists()
    assert daily.exists()


def test_cleanup_preserves_active_job_reference_and_stale_temp(
    isolated_paths, session_factory, monkeypatch
):
    @contextmanager
    def session_context():
        with session_factory() as db:
            yield db

    monkeypatch.setattr(cleanup, "get_session", session_context)
    packs_dir = isolated_paths["packs"]
    referenced = packs_dir / "referenced.zip"
    removable = packs_dir / "removable.zip"
    temp = packs_dir / ".pack-stale.tmp"
    _write_pack(referenced, b"referenced")
    _write_pack(removable, b"removable")
    _write_pack(temp, b"partial")
    import os

    old_time = (datetime.now() - timedelta(days=3)).timestamp()
    os.utime(referenced, (old_time, old_time))
    os.utime(removable, (old_time, old_time))
    os.utime(temp, (old_time, old_time))
    with session_factory() as db:
        pack = Pack(
            name="pack-referenced",
            date="2026-01-01",
            seed="1",
            zip_path=str(referenced),
            status="generated",
        )
        db.add(pack)
        db.flush()
        db.add(
            ChallengeJob(
                id="job-reference",
                mode="random",
                status="processing",
                api_key_hash="hash",
                pack_id=pack.id,
            )
        )
        db.commit()
    removed, temps = cleanup.cleanup_packs(keep=0, temp_age_hours=24)
    assert removed == 1
    assert temps == 1
    assert referenced.exists()
    assert not removable.exists()
    assert not temp.exists()
