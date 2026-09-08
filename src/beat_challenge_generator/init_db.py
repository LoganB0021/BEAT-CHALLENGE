import click

from beat_challenge_generator.db import init_db


@click.command()
def main() -> None:
    init_db()
    click.echo("Database tables initialized.")


if __name__ == "__main__":
    main()
