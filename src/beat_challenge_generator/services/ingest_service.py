from pathlib import Path
from typing import Optional, Dict
from sqlalchemy.orm import Session
from beat_challenge_generator import models, config
from beat_challenge_generator.logging import logger
from beat_challenge_generator.utils.file_checksums import file_checksum_and_size, directory_checksum_and_size

def ingest_beats(session: Session, dry_run: bool = False, category: Optional[str] = None) -> Dict[str, int]:
    stats = {"scanned": 0, "added": 0, "updated": 0, "unchanged": 0}
    base_beats = Path(config.BEAT_DIR)

    categories_to_ingest = [category] if category else config.BEAT_SUBDIRS
    if category and category not in config.BEAT_SUBDIRS:
        logger.warning(f"Category '{category}' not in BEAT_SUBDIRS {config.BEAT_SUBDIRS}")
        return stats

    for cat in categories_to_ingest:
        cat_dir = base_beats / cat
        if not cat_dir.exists():
            logger.debug(f"Skipping missing category folder: {cat_dir}")
            continue

        for entry in sorted(cat_dir.iterdir(), key=lambda p: p.name):
            stats["scanned"] += 1
            rel = entry.relative_to(cat_dir).as_posix()
            is_folder = entry.is_dir()

            try:
                checksum, size = (
                    directory_checksum_and_size(entry) if is_folder else file_checksum_and_size(entry)
                )
            except Exception as exc:
                logger.error(f"Failed to checksum {entry}: {exc}")
                continue

            existing = session.query(models.Sound).filter_by(category=cat, relative_path=rel).one_or_none()

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
                logger.info(f"[DRY_RUN] Added Sound: {cat}/{rel}" if dry_run else f"Added Sound: {cat}/{rel}")
            else:
                changed = False
                if existing.checksum != checksum:
                    existing.checksum = checksum
                    changed = True
                if existing.size_bytes != size:
                    existing.size_bytes = size
                    changed = True
                if existing.is_folder != is_folder:
                    existing.is_folder = is_folder
                    changed = True

                if changed:
                    stats["updated"] += 1
                    logger.info(f"[DRY_RUN] Updated Sound: {cat}/{rel}" if dry_run else f"Updated Sound: {cat}/{rel}")
                else:
                    stats["unchanged"] += 1
                    logger.debug(f"No changes for: {cat}/{rel}")

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
