import os
import zipfile
from pathlib import Path
from beat_challenge_generator.logging.logger import logger

def write_sounds_zip(selected_sounds: dict, output_path: str):
    """
    Write selected sounds to a zip file.
    
    Args:
        selected_sounds (dict): {category: Sound instance}
        output_path (str): Path to write the zip file
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for category, sound in selected_sounds.items():
            if not os.path.exists(sound.file_path):
                logger.warning(f"⚠️ File/folder does not exist: {sound.file_path}")
                continue

            if sound.is_folder:
                for root, _, files in os.walk(sound.file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.join(category, os.path.relpath(full_path, sound.file_path))
                        zf.write(full_path, arcname)
            else:
                arcname = os.path.join(category, os.path.basename(sound.file_path))
                zf.write(sound.file_path, arcname)
    logger.info(f"✅ Zip file created at {output_path}")