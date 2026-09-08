from datetime import datetime, timedelta, timezone
import hashlib
import uuid

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from beat_challenge_generator.challenge_service import generate_challenge
from beat_challenge_generator.config import JOB_STALE_AFTER_SECONDS
from beat_challenge_generator.models import ChallengeJob, JobQuota


def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def create_job(db: Session, mode: str, api_key: str) -> ChallengeJob:
    job = ChallengeJob(
        id=str(uuid.uuid4()),
        mode=mode,
        status="pending",
        api_key_hash=hash_api_key(api_key),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def count_recent_jobs(db: Session, api_key: str, since: datetime) -> int:
    return (
        db.query(ChallengeJob)
        .filter(
            ChallengeJob.api_key_hash == hash_api_key(api_key),
            ChallengeJob.created_at >= since,
            ChallengeJob.status.in_(("pending", "processing", "completed")),
        )
        .count()
    )


def reserve_job_slot(
    db: Session,
    api_key: str,
    window_seconds: int,
    limit: int,
) -> bool:
    if limit < 1 or window_seconds < 1:
        raise ValueError("job quota settings must be positive")

    key_hash = hash_api_key(api_key)
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=window_seconds)
    quota = db.get(JobQuota, key_hash)

    if quota is None:
        try:
            db.add(
                JobQuota(
                    api_key_hash=key_hash,
                    window_started_at=now,
                    admitted_count=1,
                )
            )
            db.flush()
            return True
        except IntegrityError:
            db.rollback()
            quota = db.get(JobQuota, key_hash)

    quota_window_started_at = quota.window_started_at
    if quota_window_started_at.tzinfo is None:
        quota_window_started_at = quota_window_started_at.replace(tzinfo=timezone.utc)

    if quota_window_started_at < window_start:
        updated = db.execute(
            update(JobQuota)
            .where(
                JobQuota.api_key_hash == key_hash,
                JobQuota.window_started_at == quota.window_started_at,
            )
            .values(window_started_at=now, admitted_count=1)
        )
        db.flush()
        return updated.rowcount == 1

    if quota.admitted_count >= limit:
        return False

    updated = db.execute(
        update(JobQuota)
        .where(
            JobQuota.api_key_hash == key_hash,
            JobQuota.window_started_at == quota.window_started_at,
            JobQuota.admitted_count < limit,
        )
        .values(admitted_count=JobQuota.admitted_count + 1)
    )
    db.flush()
    return updated.rowcount == 1


def claim_next_job(db: Session) -> ChallengeJob | None:
    now = datetime.now(timezone.utc)
    stale_before = now - timedelta(seconds=JOB_STALE_AFTER_SECONDS)
    stale_jobs = (
        db.query(ChallengeJob)
        .filter(
            ChallengeJob.status == "processing",
            ChallengeJob.started_at < stale_before,
        )
        .all()
    )
    for job in stale_jobs:
        job.status = "pending"
        job.started_at = None
        job.error = "Requeued after stale worker lease"

    job = (
        db.query(ChallengeJob)
        .filter(ChallengeJob.status == "pending")
        .order_by(ChallengeJob.created_at)
        .first()
    )
    if not job:
        db.commit()
        return None

    job.status = "processing"
    job.started_at = now
    job.error = None
    db.commit()
    db.refresh(job)
    return job


def process_job(db: Session, job: ChallengeJob) -> ChallengeJob:
    try:
        pack = generate_challenge(db, mode=job.mode)
        if not pack:
            raise RuntimeError("No indexed sounds are available to package")
        job.status = "completed"
        job.pack_id = pack.id
        job.completed_at = datetime.now(timezone.utc)
        job.error = None
    except Exception as exc:
        db.rollback()
        job = db.get(ChallengeJob, job.id)
        job.status = "failed"
        job.error = str(exc)[:2000]
        job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return job
