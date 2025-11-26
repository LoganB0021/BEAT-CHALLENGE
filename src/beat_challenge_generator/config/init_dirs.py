import os
from beat_challenge_generator.logging.logger import logger
from beat_challenge_generator.config.paths import (
    BEAT_DIR,
    OUTPUT_DIR,
    DATA_DIR,
    BEAT_SUBDIRS,
)

def initialize_directories():
    """Ensure required directory structure exists."""
    # Root directories
    for directory in [BEAT_DIR, OUTPUT_DIR, DATA_DIR]:
        os.makedirs(directory, exist_ok=True)

    # Beat subdirectories
    for subdir in BEAT_SUBDIRS:
        path = os.path.join(BEAT_DIR, subdir)
        os.makedirs(path, exist_ok=True)
        logger.info(f"Initialized directory: {path}")
