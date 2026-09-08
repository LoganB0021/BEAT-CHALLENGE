from pathlib import Path
from datetime import datetime, timedelta, timezone

import click

from beat_challenge_generator.config import PACKS_DIR
from beat_challenge_generator.db import get_session
from beat_challenge_generator.models import ChallengeJob, Pack


def cleanup_packs(keep: int = 5, temp_age_hours: int = 24) -> tuple[int, int]:
    if keep < 0:
        raise ValueError("keep must be non-negative")

    root = Path(PACKS_DIR)
    cutoff = datetime.now(timezone.utc).timestamp() - temp_age_hours * 3600
    removed_temps = 0
    for path in root.glob(".pack-*.tmp"):
        if path.is_file() and path.stat().st_mtime < cutoff:
            path.unlink()
            removed_temps += 1

    with get_session() as db:
        referenced = {
            pack.zip_path
            for pack in db.query(Pack).all()
            if pack.zip_path
            and (
                db.query(ChallengeJob)
                .filter(
                    ChallengeJob.pack_id == pack.id,
                    ChallengeJob.status.in_(("pending", "processing", "completed")),
                )
                .first()
                or pack.date == datetime.now().date().isoformat()
            )
        }

    files = sorted(
        (path for path in Path(PACKS_DIR).glob("*.zip") if path.is_file()),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    removed = 0
    kept = 0
    for path in files:
        if str(path) in referenced:
            continue
        if kept < keep:
            kept += 1
            continue
        path.unlink()
        removed += 1
    return removed, removed_temps


@click.command()
@click.option("--keep", type=click.IntRange(min=0), default=5, show_default=True)
@click.option("--temp-age-hours", type=click.IntRange(min=1), default=24, show_default=True)
def main(keep: int, temp_age_hours: int) -> None:
    removed, removed_temps = cleanup_packs(keep, temp_age_hours)
    click.echo(
        f"Removed {removed} pack archive(s) and {removed_temps} temporary file(s)."
    )


if __name__ == "__main__":
    main()
