"""
Main CLI entrypoint for the Beat Challenge Generator.

This file allows running core functionality of the generator *without the API*.
The API will import and reuse the same services.
"""

import click
from datetime import date

from beat_challenge_generator.db.session import get_session
from beat_challenge_generator.services.ingest_service import ingest_beats
from beat_challenge_generator.services.file_selector import deterministic_select_by_date
from beat_challenge_generator.services.file_manager import create_pack
from beat_challenge_generator.logging.logger import logger


@click.group()
def cli():
    """Beat Challenge Generator CLI"""
    pass


# ---------------------------------------------------------
# INGEST COMMAND
# ---------------------------------------------------------
@cli.command()
@click.option("--dry-run", is_flag=True, help="Scan files but do not modify database")
@click.option("--category", type=str, default=None, help="Only ingest a specific category")
def ingest(dry_run: bool, category: str):
    """Ingest beat folders into the database."""
    with get_session() as session:
        stats = ingest_beats(session=session, dry_run=dry_run, category=category)

        click.echo(
            f"Ingest finished:\n"
            f"  scanned:   {stats['scanned']}\n"
            f"  added:     {stats['added']}\n"
            f"  updated:   {stats['updated']}\n"
            f"  unchanged: {stats['unchanged']}"
        )


# ---------------------------------------------------------
# SELECT DAILY BEAT ITEMS
# ---------------------------------------------------------
@cli.command()
@click.option("--date", "date_str", type=str, default=None, help="Generate for this date (YYYY-MM-DD)")
def select(date_str: str):
    """Run deterministic selection for a given date."""
    target_date = date.fromisoformat(date_str) if date_str else None

    with get_session() as session:
        selected = deterministic_select_by_date(session, target_date)

        click.echo("Selected items:")
        for cat, sound in selected.items():
            click.echo(f"  {cat}: {sound.name}")


# ---------------------------------------------------------
# GENERATE PACK (ZIP + DB RECORD)
# ---------------------------------------------------------
@cli.command()
@click.option("--zip2db", "date_str", type=str, default=None, help="Generate pack for this date (YYYY-MM-DD)")
def generate(date_str: str):
    """Create the daily pack zip and DB record."""
    target_date = date.fromisoformat(date_str) if date_str else None

    with get_session() as session:
        selected = deterministic_select_by_date(session, target_date)
        zip_path = create_pack(selected, session)

    click.echo(f"Pack generated at: {zip_path}")


# ---------------------------------------------------------
# ENTRYPOINT
# ---------------------------------------------------------
if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        logger.exception(f"Unhandled error: {e}")
        raise
