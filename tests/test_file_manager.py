# import os
# import shutil
# import zipfile
# import pytest
# from beat_challenge_generator.file_manager import create_beat_pack
# from beat_challenge_generator.config import OUTPUT_DIR

# @pytest.fixture
# def sample_files(tmpdir):
#     """Set up and clean up sample files for zipping, using temporary directories."""
#     test_files = {
#         "drum_kits": "Test_Drum_Kit",
#         "fx": "fx.wav",
#         "samples": "melody.wav"
#     }

#     # Create necessary temporary directories
#     drum_kit_dir = tmpdir / "drum_kits" / "Test_Drum_Kit"
#     fx_dir = tmpdir / "fx"
#     samples_dir = tmpdir / "samples"

#     os.makedirs(drum_kit_dir)
#     os.makedirs(fx_dir)
#     os.makedirs(samples_dir)

#     # Create sample files in the temporary directories
#     for category, filename in test_files.items():
#         file_path = tmpdir / category / filename
#         with open(file_path, "w") as f:
#             f.write("test")
    
#     yield test_files  # Provide test data to test function

#     # Cleanup
#     for category, filename in test_files.items():
#         os.remove(tmpdir / category / filename)

#     # Use shutil to remove directories
#     shutil.rmtree(tmpdir / "drum_kits")
#     shutil.rmtree(tmpdir / "fx")
#     shutil.rmtree(tmpdir / "samples")

# def test_zip_creation(sample_files, tmpdir):
#     """Ensure zip file is created when given valid files."""
#     zip_path = create_beat_pack(sample_files)

#     assert zip_path is not None
#     assert zipfile.is_zipfile(zip_path)

#     os.remove(zip_path)  # Cleanup zip file
