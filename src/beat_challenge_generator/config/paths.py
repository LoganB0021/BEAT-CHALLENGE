import os

# Root of the project ("beat_challenge_generator" package parent)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

BEAT_DIR = os.path.join(BASE_DIR, "beats")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Subdirectories for beat components
BEAT_SUBDIRS = ["drum_kits", "fx", "samples"]

# Logs directory
LOG_DIR = os.path.join(BASE_DIR, "logs")

