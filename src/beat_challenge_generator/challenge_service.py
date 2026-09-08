from datetime import date, datetime
import os
import random
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from beat_challenge_generator.file_manager import create_pack
from beat_challenge_generator.file_selector import deterministic_select_by_date
from beat_challenge_generator.logger import logger
from beat_challenge_generator.models import Pack, Sound


def random_select(db: Session):
    """Select one random indexed sound from each configured category."""
    selected = {}
    for category in ("drum_kits", "fx", "samples"):
        items = db.query(Sound).filter(Sound.category == category).all()
        if items:
            selected[category] = random.choice(items)
        else:
            logger.warning(f"No indexed sounds found in category {category}")
    return selected


def generate_challenge(
    db: Session,
    mode: str = "daily",
    target_date: Optional[date] = None,
    overwrite: bool = False,
):
    """Select, package, and persist a challenge using the shared workflow."""
    if mode not in {"daily", "random"}:
        raise ValueError("mode must be 'daily' or 'random'")

    target_date = target_date or date.today()
    daily_date = target_date.isoformat()

    if mode == "daily":
        existing_pack = db.query(Pack).filter(Pack.date == daily_date).first()
        if existing_pack and not overwrite and os.path.exists(existing_pack.zip_path):
            return existing_pack
        previous_zip_path = existing_pack.zip_path if existing_pack else None
        if existing_pack:
            db.delete(existing_pack)
            db.flush()
        selected = deterministic_select_by_date(db, target_date)
        pack_date = daily_date
    else:
        selected = random_select(db)
        pack_date = datetime.now().strftime("random-%Y%m%d-%H%M%S-%f")
        previous_zip_path = None

    if not selected:
        return None

    try:
        zip_path = create_pack(selected, db, pack_date=pack_date, mode=mode)
    except IntegrityError:
        db.rollback()
        if mode == "daily":
            winner = db.query(Pack).filter(Pack.date == daily_date).first()
            if winner and os.path.exists(winner.zip_path):
                return winner
        raise
    if mode == "daily" and previous_zip_path and previous_zip_path != zip_path:
        try:
            if os.path.exists(previous_zip_path):
                os.remove(previous_zip_path)
        except OSError:
            logger.warning(f"Could not remove superseded pack: {previous_zip_path}")
    return db.query(Pack).filter(Pack.zip_path == zip_path).one()