import click

from beat_challenge_generator.db import get_session
from beat_challenge_generator.logger import logger
from beat_challenge_generator.challenge_service import generate_challenge


@click.command()
@click.option("--mode", type=click.Choice(["daily", "random"]), default="daily", show_default=True)
@click.option(
    "--overwrite",
    is_flag=True,
    help="Regenerate the daily pack even if today's archive already exists.",
)
def main(mode: str = "daily", overwrite: bool = False):
    logger.info("🎵 Starting Beat Challenge Generator...")

    try:
        with get_session() as db:
            pack = generate_challenge(db, mode=mode, overwrite=overwrite)
            if not pack:
                raise RuntimeError("No indexed sounds are available to package")
            logger.info(f"🎵 Beat challenge ready: {pack.zip_path}")
            click.echo(f"🎵 Beat challenge ready: {pack.zip_path}")

    except Exception as e:
        logger.error(f"🚨 An error occurred: {e}")
        raise click.ClickException(str(e)) from e

if __name__ == "__main__":
    main()
