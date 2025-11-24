import hashlib
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from beat_challenge_generator.logger import logger
from beat_challenge_generator.models import Sound

def deterministic_select_by_date(db: Session, target_date: Optional[date] = None):
    """
    Select one item per category deterministically based on a date.
    If no date is provided, uses today's date.
    Returns a dict: {category: Sound instance}
    """
    selected = {}
    categories = ["drum_kits", "fx", "samples"]

    # Default to today's date
    if target_date is None:
        target_date = date.today()

    # Use date as seed for deterministic selection
    date_seed = int(target_date.strftime("%Y%m%d"))

    for cat in categories:
        items = db.query(Sound).filter(Sound.category == cat).all()
        if not items:
            logger.warning(f"⚠️ No items found in category {cat}")
            continue

        # Sort items deterministically by SHA256(filename)
        items.sort(key=lambda x: hashlib.sha256(x.name.encode()).hexdigest())

        # Use the date seed to pick an item deterministically
        index = date_seed % len(items)
        selected[cat] = items[index]

    logger.info(
        f"✅ Deterministic beat challenge for {target_date}: "
        f"{{ {', '.join(f'{k}: {v.name}' for k, v in selected.items())} }}"
    )
    return selected
