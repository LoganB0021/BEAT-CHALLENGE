import os
import random
import hashlib
from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import BEAT_DIR
from beat_challenge_generator.models import Sound

def get_random_item_from_folder(folder_path):
    """Returns a random file or folder from the given folder."""
    try:
        items = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)) or os.path.isfile(os.path.join(folder_path, f))]
        if not items:
            logger.warning(f"⚠️ No files or folders found in {folder_path}")
            return None
        return random.choice(items)  # Return either a file or a folder
    except Exception as e:
        logger.error(f"🚨 Error selecting item from {folder_path}: {e}")
        return None

def generate_beat_challenge():
    """Selects a random beat challenge configuration."""
    categories = ["drum_kits", "fx", "samples"]
    selected_items = {}

    for category in categories:
        folder_path = os.path.join(BEAT_DIR, category)
        selected_item = get_random_item_from_folder(folder_path)
        if selected_item:
            selected_items[category] = selected_item  # Can be a file or folder

    logger.info(f"✅ Generated beat challenge: {selected_items}")
    return selected_items

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
