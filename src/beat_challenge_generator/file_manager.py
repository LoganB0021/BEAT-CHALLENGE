import os
import zipfile
import random
import string
from beat_challenge_generator.logger import logger
from beat_challenge_generator.config import BEAT_DIR, OUTPUT_DIR

def generate_random_name(length=8):
    """Generate a random string for the zip file name."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def add_to_zip(zipf, file_path, arcname):
    """Adds a file or an entire folder to the zip archive."""
    if os.path.isdir(file_path):  # If it's a folder, add all its contents
        for root, _, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, BEAT_DIR)  # Preserve folder structure
                zipf.write(full_path, relative_path)
                logger.info(f"📂 Added folder file: {relative_path}")
    else:  # If it's a file, add it normally
        zipf.write(file_path, arcname)
        logger.info(f"📄 Added file: {arcname}")

def create_beat_pack(selected_files):
    """Creates a zip file with the selected beat components, including folders."""
    if not selected_files:
        logger.warning("⚠️ No files selected for beat pack.")
        return None

    pack_name = f"beat_{generate_random_name()}.zip"
    pack_path = os.path.join(OUTPUT_DIR, pack_name)

    try:
        with zipfile.ZipFile(pack_path, 'w') as zipf:
            for category, item in selected_files.items():
                item_path = os.path.join(BEAT_DIR, category, item)

                if os.path.exists(item_path):
                    add_to_zip(zipf, item_path, os.path.join(category, item))
                else:
                    logger.error(f"❌ Item not found: {item_path}")

        logger.info(f"🎉 Beat pack created: {pack_path}")
        return pack_path

    except Exception as e:
        logger.error(f"🚨 Error creating beat pack: {e}")
        return None
