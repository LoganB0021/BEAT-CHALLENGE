import os
import hashlib
from pathlib import Path
from typing import Tuple, Optional

import click
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beat_challenge_generator import config, models, db
from beat_challenge_generator.logger import logger

CHUNK_SIZE = 8192


def file_checksum_and_size(path: Path) -> Tuple[str, int]:
    """Return (sha256_hex, size_bytes) for a file."""
    h = hashlib.sha256()
    total = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
            total += len(chunk)
    return h.hexdigest(), total


def directory_checksum_and_size(dirpath: Path) -> Tuple[str, int]:
    """
    Deterministic checksum for a directory:
    - Walk files sorted by relative path
    - For each file include: relative_path + NUL + file_sha256 + NUL + file_size
    - Hash the concatenation with sha256
    Also returns the total size (sum of file sizes).
    """
    entries = []
    total = 0
    for root, _, files in os.walk(dirpath):
        for fn in files:
            full = Path(root) / fn
            rel = full.relative_to(dirpath).as_posix()
            chksum, size = file_checksum_and_size(full)
            entries.append((rel, chksum, size))
            total += size
    entries.sort(key=lambda t: t[0])
    h = hashlib.sha256()
    for rel, chksum, size in entries:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(chksum.encode("ascii"))
        h.update(b"\0")
        h.update(str(size).encode("ascii"))
        h.update(b"\0")
    return h.hexdigest(), total


def ensure_db_session():
    """
    Ensure DB tables exist via db.init_db() and return a SQLAlchemy Session instance.
    db.init_db() is called for side-effects (create tables). We then create our own engine/session
    using the same DATABASE_URL to perform upserts.
    """
    # Ensure db module creates tables / metadata
    try:
        db.init_db()
    except Exception as exc:
        logger.warning(f"db.init_db() raised: {exc} — continuing to create session directly")

    connect_args = {}
    if config.DATABASE_URL.startswith("sqlite"):
        # For SQLite in-process, allow same-thread checks to be disabled for some test setups
        connect_args = {"check_same_thread": False}

    engine = create_engine(config.DATABASE_URL, connect_args=connect_args, future=True)
    Session = sessionmaker(bind=engine, future=True)
    return Session


def ingest_beats(dry_run: bool = False, category: Optional[str] = None):
    """
    Walk config.BEAT_DIR / subdirs and upsert Sound records:
      - category: subdir name (drum_kits, fx, samples)
      - filename: path relative to the category folder (files or nested paths)
      - checksum, size, is_folder
    
    Args:
        dry_run: if True, report changes but do not commit.
        category: if set, ingest only this category (e.g., 'drum_kits'); otherwise ingest all.
    """
    Session = ensure_db_session()

    stats = {"scanned": 0, "added": 0, "updated": 0, "unchanged": 0}
    base_beats = Path(config.BEAT_DIR)

    # Determine which categories to ingest
    categories_to_ingest = [category] if category else config.BEAT_SUBDIRS
    if category and category not in config.BEAT_SUBDIRS:
        logger.warning(f"Category '{category}' not in BEAT_SUBDIRS {config.BEAT_SUBDIRS}")
        return stats

    # use a context-managed session so it is closed cleanly
    with Session() as session:
        for cat in categories_to_ingest:
            cat_dir = base_beats / cat
            if not cat_dir.exists():
                logger.debug(f"Skipping missing category folder: {cat_dir}")
                continue

            # iterate only immediate children (files or folders) to preserve folder-as-item semantics
            for entry in sorted(cat_dir.iterdir(), key=lambda p: p.name):
                stats["scanned"] += 1
                rel = entry.relative_to(cat_dir).as_posix()  # filename stored relative to category folder
                is_folder = entry.is_dir()

                try:
                    if is_folder:
                        checksum, size = directory_checksum_and_size(entry)
                    else:
                        checksum, size = file_checksum_and_size(entry)
                except Exception as exc:
                    logger.error(f"Failed to checksum {entry}: {exc}")
                    continue

                # Try to find existing Sound by category + relative_path
                existing = (
                    session.query(models.Sound)
                    .filter_by(category=cat, relative_path=rel)
                    .one_or_none()
                )

                if existing is None:
                    new = models.Sound(
                        name=Path(rel).name,
                        category=cat,
                        relative_path=rel,
                        checksum=checksum,
                        size_bytes=size,
                        is_folder=is_folder,
                    )
                    session.add(new)
                    stats["added"] += 1
                    logger.info(f"[DRY_RUN] Added Sound: {cat}/{rel} (folder={is_folder})" if dry_run else f"Added Sound: {cat}/{rel} (folder={is_folder})")
                else:
                    changed = False
                    if getattr(existing, "checksum", None) != checksum:
                        existing.checksum = checksum
                        changed = True
                    if getattr(existing, "size_bytes", None) != size:
                        existing.size_bytes = size
                        changed = True
                    if getattr(existing, "is_folder", None) != is_folder:
                        existing.is_folder = is_folder
                        changed = True

                    if changed:
                        stats["updated"] += 1
                        logger.info(f"[DRY_RUN] Updated Sound: {cat}/{rel}" if dry_run else f"Updated Sound: {cat}/{rel}")
                    else:
                        stats["unchanged"] += 1
                        logger.debug(f"No changes for: {cat}/{rel}")

        # commit once after processing all categories; rollback on error or dry_run
        try:
            if dry_run:
                session.rollback()
                logger.info("Dry-run mode: changes rolled back")
            else:
                session.commit()
        except Exception as exc:
            logger.exception(f"Commit failed during ingest: {exc}")
            session.rollback()
            raise

    logger.info(
        f"Ingest complete — scanned={stats['scanned']} added={stats['added']} "
        f"updated={stats['updated']} unchanged={stats['unchanged']}"
    )
    return stats


@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Report changes without committing to the database."
)
@click.option(
    "--category",
    type=str,
    default=None,
    help=f"Ingest only this category. Choices: {', '.join(config.BEAT_SUBDIRS)}"
)
def main(dry_run: bool, category: Optional[str]):
    """Ingest beats/ directory tree into the database."""
    stats = ingest_beats(dry_run=dry_run, category=category)
    print(
        f"Ingest finished: scanned={stats['scanned']} added={stats['added']} "
        f"updated={stats['updated']} unchanged={stats['unchanged']}"
    )


if __name__ == "__main__":
    main()