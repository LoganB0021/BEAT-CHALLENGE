import os
import zipfile
import random
import string
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import BEAT_DIR, OUTPUT_DIR

def generate_random_name(length=8):
    """Generate a random string of fixed length."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def create_beat_pack(selected_files):
    """Creates a zip file with the selected beat components."""
    
    if not selected_files:
        logger.warning("No files selected for beat pack.")
        return None

    # Generate a random name for the beat pack (e.g., "beat_ABC12345.zip")
    pack_name = f"beat_{generate_random_name()}.zip"
    pack_path = os.path.join(OUTPUT_DIR, pack_name)

    try:
        with zipfile.ZipFile(pack_path, 'w') as zipf:
            for category, filename in selected_files.items():
                # Get the full path of the selected file
                file_path = os.path.join(BEAT_DIR, category, filename)
                
                if os.path.exists(file_path):
                    # Add the file to the zip, using category as the folder structure
                    zipf.write(file_path, os.path.join(category, filename))
                    logger.info(f"Added {filename} to {pack_name}")
                else:
                    logger.error(f"File not found: {file_path}")
        
        logger.info(f"Beat pack created successfully: {pack_path}")
        return pack_path
    
    except Exception as e:
        logger.error(f"Error creating beat pack: {e}")
        return None
