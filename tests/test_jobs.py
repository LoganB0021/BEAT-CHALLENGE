from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beat_challenge_generator import models
from beat_challenge_generator.jobs import (
    claim_next_job,
    count_recent_jobs,
    create_job,
    hash_api_key,
)


def test_job_creation_rate_count_and_claim():
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        job = create_job(session, "random", "test-secret")
        assert job.status == "pending"
        assert job.api_key_hash == hash_api_key("test-secret")

        since = datetime.now(timezone.utc) - timedelta(minutes=1)
        assert count_recent_jobs(session, "test-secret", since) == 1

        claimed = claim_next_job(session)
        assert claimed is not None
        assert claimed.id == job.id
        assert claimed.status == "processing"
