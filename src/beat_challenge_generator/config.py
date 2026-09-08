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

# Public API behavior is configured through environment variables so local and
# hosted deployments can share the same code without hard-coded secrets.
SECRET_KEY = os.getenv("SECRET_KEY")
BEAT_API_KEY = os.getenv("BEAT_API_KEY")
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
ALLOW_RANDOM_CHALLENGES = os.getenv("ALLOW_RANDOM_CHALLENGES", "false").lower() == "true"
ALLOW_ASYNC_CHALLENGES = os.getenv("ALLOW_ASYNC_CHALLENGES", "false").lower() == "true"
JOB_RATE_LIMIT_SECONDS = int(os.getenv("JOB_RATE_LIMIT_SECONDS", "60"))
MAX_JOBS_PER_RATE_WINDOW = int(os.getenv("MAX_JOBS_PER_RATE_WINDOW", "1"))
JOB_STALE_AFTER_SECONDS = int(os.getenv("JOB_STALE_AFTER_SECONDS", "1800"))
TRUSTED_HOSTS = [
    host.strip()
    for host in os.getenv("TRUSTED_HOSTS", "").split(",")
    if host.strip()
]
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024)))

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