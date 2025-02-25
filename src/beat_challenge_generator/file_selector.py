import os
import random
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import BEAT_DIR

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
