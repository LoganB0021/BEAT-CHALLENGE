import os
from beat_challenge_generator.config import BEAT_DIR, OUTPUT_DIR, initialize_beat_folders
from beat_challenge_generator.logger import LOG_DIR

def test_directories_exist():
    """Ensure that required directories are created."""
    initialize_beat_folders()
    assert os.path.exists(BEAT_DIR)
    assert os.path.exists(OUTPUT_DIR)
    assert os.path.exists(LOG_DIR)
