from datetime import datetime, timedelta, timezone

from beat_challenge_generator import jobs


def test_job_creation_rate_count_and_claim():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from beat_challenge_generator import models

    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        job = jobs.create_job(session, "random", "test-secret")
        assert job.status == "pending"
        assert job.api_key_hash == jobs.hash_api_key("test-secret")
        since = datetime.now(timezone.utc) - timedelta(minutes=1)
        assert jobs.count_recent_jobs(session, "test-secret", since) == 1
        claimed = jobs.claim_next_job(session)
        assert claimed.id == job.id
        assert claimed.status == "processing"


def test_worker_processes_successful_and_failed_jobs(db_session, ingested_assets):
    jobs.create_job(db_session, "daily", "secret")
    claimed = jobs.claim_next_job(db_session)
    result = jobs.process_job(db_session, claimed)
    assert result.status == "completed"
    assert result.pack_id is not None

    from beat_challenge_generator.models import Sound

    db_session.query(Sound).delete()
    db_session.commit()
    jobs.create_job(db_session, "random", "secret")
    claimed_failed = jobs.claim_next_job(db_session)
    result = jobs.process_job(db_session, claimed_failed)
    assert result.status == "failed"
    assert result.error == "No indexed sounds are available to package"


def test_claim_requeues_stale_processing_job(db_session, monkeypatch):
    monkeypatch.setattr(jobs, "JOB_STALE_AFTER_SECONDS", 1)
    jobs.create_job(db_session, "random", "secret")
    stale = jobs.claim_next_job(db_session)
    stale.started_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    db_session.commit()

    claimed = jobs.claim_next_job(db_session)
    assert claimed.id == stale.id
    assert claimed.status == "processing"
    assert claimed.error is None


def test_reserve_job_slot_enforces_and_resets_quota(db_session):
    assert jobs.reserve_job_slot(db_session, "secret", 60, 1)
    assert not jobs.reserve_job_slot(db_session, "secret", 60, 1)
    quota = db_session.get(jobs.JobQuota, jobs.hash_api_key("secret"))
    quota.window_started_at = datetime.now(timezone.utc) - timedelta(seconds=61)
    db_session.commit()
    assert jobs.reserve_job_slot(db_session, "secret", 60, 1)
