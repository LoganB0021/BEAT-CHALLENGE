import os
import pytest
from beat_challenge_generator.file_selector import get_random_item_from_folder
from beat_challenge_generator.config import BEAT_DIR

@pytest.fixture
def sample_beat_folders():
    """Create sample folders for testing."""
    test_folder = os.path.join(BEAT_DIR, "Test_Drum_Kit")
    os.makedirs(test_folder, exist_ok=True)
    
    sample_file = os.path.join(test_folder, "kick.wav")
    with open(sample_file, "w") as f:
        f.write("test")

    yield test_folder  # Provide to test, then cleanup

    os.remove(sample_file)
    os.rmdir(test_folder)

def test_random_item_selection(sample_beat_folders):
    """Ensure a file or folder is selected without errors."""
    selected_item = get_random_item_from_folder(BEAT_DIR)
    assert selected_item is not None