import os
from beat_challenge_generator.logger import logger

# Base directory (the root of the project)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Directory where beat files are stored
BEAT_DIR = os.path.join(BASE_DIR, "beats")

# Output directory for generated beat packs
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Data directory for persistent artifacts (database, etc.)
DATA_DIR = os.path.join(BASE_DIR, "data")

# Directory for generated pack zips
PACKS_DIR = os.path.join(OUTPUT_DIR, "packs")

# Subdirectories for beat components
BEAT_SUBDIRS = ["drum_kits", "fx", "samples"]

# Default database URL (can be overridden with env var DATABASE_URL)
_default_db_path = os.path.join(DATA_DIR, "beat_challenge.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_default_db_path}")

# Ensure necessary directories exist
for directory in [BEAT_DIR, OUTPUT_DIR, DATA_DIR, PACKS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Initialize beat subdirectories
def initialize_beat_folders():
    """Ensure the beat subdirectories exist."""
    for subdir in BEAT_SUBDIRS:
        subdir_path = os.path.join(BEAT_DIR, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        logger.info(f"Initialized folder: {subdir_path}")


# Run the initialization function to set up directories
initialize_beat_folders()