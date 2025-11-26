import click
from beat_challenge_generator import db
from beat_challenge_generator.services.ingest_service import ingest_beats

@click.command()
@click.option("--dry-run", is_flag=True, help="Report changes without committing")
@click.option("--category", type=str, default=None, help="Ingest only this category")
def main(dry_run: bool, category: str):
    """CLI entrypoint for ingesting beats into DB."""
    with db.get_session() as session:
        # pass session into service layer
        stats = ingest_beats(session, dry_run, category)

        print(
            f"Ingest finished: scanned={stats['scanned']} added={stats['added']} "
            f"updated={stats['updated']} unchanged={stats['unchanged']}"
        )

if __name__ == "__main__":
    main()
