import os
from beat_challenge_generator.logger import logger

# Base directory (the root of the project)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Directory where beat files are stored
BEAT_DIR = os.path.join(BASE_DIR, "beats")

# Output directory for generated beat packs
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# Logs directory
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Ensure necessary directories exist
for directory in [BEAT_DIR, OUTPUT_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)
