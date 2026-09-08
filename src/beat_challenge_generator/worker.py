import time

import click

from beat_challenge_generator.db import get_session
from beat_challenge_generator.jobs import claim_next_job, process_job


def run_once() -> bool:
    with get_session() as db:
        job = claim_next_job(db)
        if not job:
            return False
        process_job(db, job)
        return True


@click.command()
@click.option("--once", is_flag=True, help="Process at most one queued job.")
@click.option("--poll-seconds", type=click.FloatRange(min=0.1), default=5.0, show_default=True)
def main(once: bool, poll_seconds: float) -> None:
    if once:
        run_once()
        return

    while True:
        if not run_once():
            time.sleep(poll_seconds)


if __name__ == "__main__":
    main()
