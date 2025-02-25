import os
import random
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import BEAT_DIR  # Import BEAT_DIR from config.py

def get_random_file_from_folder(folder_path):
    """Returns a random file from the given folder."""
    try:
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            logger.warning(f"No files found in {folder_path}")
            return None
        return random.choice(files)
    except Exception as e:
        logger.error(f"Error selecting file from {folder_path}: {e}")
        return None

def generate_beat_challenge():
    """Selects a random beat challenge configuration."""
    categories = ["drum_kits", "fx", "samples"]
    selected_files = {}

    for category in categories:
        folder_path = os.path.join(BEAT_DIR, category)
        selected_file = get_random_file_from_folder(folder_path)
        if selected_file:
            selected_files[category] = selected_file

    logger.info(f"Generated beat challenge: {selected_files}")
    return selected_files
